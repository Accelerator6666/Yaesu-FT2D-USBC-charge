# FT2D PCB Rev B（JLCPCB 首板工作版，未放行）

检查日期：2026-10-25；KiCad 10.0.7；目标板厂：嘉立创 JLCPCB；目标工艺：4 层 PCB + SMT 代贴片。

> **NO-GO：不得直接根据这个 PCB 生成订单。** 本目录是真实可打开的 KiCad Rev B 工作版，包含重新布线、关键焊盘扇出、地铜过孔和原理图 BOM/DNP 属性修正，但不是可投板制造数据。

## 当前可复现检查

```sh
kicad-cli sch erc --format json -o erc_rev_b.json FT2D_PD20V_12V5_3A_评审原理图.kicad_sch
kicad-cli pcb drc --schematic-parity --refill-zones --format json -o drc_rev_b.json FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb
```

| 检查 | 实际结果 | 说明 |
| --- | --- | --- |
| 原理图 ERC | **0** | 仅表示静态 ERC 通过 |
| 异网短路 / 铜间距违规 | **0** | 原始板中的 OVLO/UVLO/电源铜短路已清除 |
| DRC violations | **1** | U1 QFN 封装与当前 KiCad 标准库不一致警告；板上 29 个焊盘的编号、相对坐标、尺寸、形状、层集合与本机标准库逐项一致，但丝印/图形差异未获硬件复审豁免 |
| DRC unconnected | **4** | F.Cu 地铜局部片区仍不连通，不能放行 |
| schematic parity | **0** | C11、R14 的 DNP/BOM 属性以及 TP1 不列 BOM 已统一 |

上述结果按此目录所附 `erc_rev_b.json` 和 `drc_rev_b.json` 为准。**未连接的 GND 铜不是装饰性警告**：需要完成具体地焊盘（如 U2/U3/C2 周边）至内层地参考面的低阻可靠回路设计。

## 主要阻止打板的问题（按优先级）

1. **3 A 电源铜宽**：自动布线的 `/SW`、`/USB_VBUS`、`/VBUS_RAW`、`/VBUS_SW`、`/V12P5`、`/VOUT` 大部分仍是 **0.6 mm**，局部细引出最窄 **0.15 mm**；未完成连续宽铜/铜皮、并联过孔和温升/压降校核。不能把“DRC 没有报线宽错”等同于能够承载 3 A。
2. **BUCK 功率布局**：U2 到 L1 的 SW 路径仍约厘米级，输入去耦、开关环路和 FB/Kelvin 取样尚需按 TI 数据手册布局建议缩短/隔离；存在开关尖峰、稳定性和 EMI 风险。
3. **GND 连通**：仍有四处区域，已尝试狭缝走线但会与 VBUS_RAW、FB_U2、PD_2V7、ILM_U3 短接；这些失败方案没有保留在本 PCB。建议实质局部重排后重建回流，不要强行跨线。
4. **JLC 贴片供料/工艺**：J1 GCT USB4085-GF-A 被列为插件/波峰焊；原 Bourns L1 当前有缺货风险；F1、C18、C23 等尚未落实立创可采料号和等效性。只用现有材料清单无法构成可下单的 SMT BOM。
5. **功能级风险**：STUSB4500 NVM 需烧录并验 20V PDO；eFuse 限流、DC-DC 环路、输入及输出电容有效容量、输出线束电台端极性均未实测。

## 已完成的布线/设计动作

- 原评审 PCB 不变；此目录保留 Rev B 的独立原理图、PCB、工程设置和封装库。
- 将功率网络引入 `POWER_REV_B` netclass（主干目标宽 0.6 mm，**这是过渡值而非载流放行值**）。
- 对 USB-C CC1/四个 VBUS 引脚、U3 OVLO 与 eFuse 供电引脚做可复现的短距离细引出。
- 完成全板重新布线；补入多颗确认有净空的 GND stitching via；改进受限地焊盘连接；修复两处 VOUT 过孔孔净空与丝印重叠。
- 原理图与 PCB 的 DNP 和 BOM 属性一致。DP/输出接口未改电气定义。

可审计工具在 `../../engineering_tools/`；未通过 DRC 的局部接地布线实验已从 PCB 与提交文件中移除。

## 投板门槛

- [ ] 全面优化 U2–L1–电容功率环路，宽铜/铜皮与热设计通过工程复核。
- [ ] DRC 0 实质违规、0 未连接、0 未审定警告、ERC 0、Parity 0。
- [ ] U1、U2、U3、Q1、J1、L1 的封装与厂家 land pattern 对照签核。
- [ ] JLC 物料号逐颗落实，DNP/人工焊接料与 SMT 文件匹配，SMT 预览方向正确。
- [ ] PD NVM 烧录工装、12.5V 无电台电子负载测试计划完备。

`../../manufacturing/Rev_B/REVIEW_ONLY_NOT_FOR_FAB/` 提供非下单用途的原生 BOM、位置数据与供料跟踪表。**最终 Gerber/Excellon 放行包暂未生成。**

## 关键一手资料

- [JLCPCB KiCad 10 BOM / Pick-and-Place 指南](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [ST STUSB4500](https://www.st.com/resource/en/datasheet/stusb4500.pdf)
- [TI LM61460-Q1](https://www.ti.com/lit/ds/symlink/lm61460-q1.pdf)
- [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
