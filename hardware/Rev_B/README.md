# FT2D PCB Rev B（JLCPCB 首板工作版，未放行）

检查日期：2026-10-25；KiCad 10.0.7；目标板厂：嘉立创 JLCPCB；目标工艺：4 层 PCB + SMT 代贴片。

> **NO-GO：不得直接根据这个 PCB 生成订单。** 本目录可在 KiCad 10 打开；已完成 J1/L1 兼容换料、U2 功率级局部重排、全板重新布线、加宽铜皮设计和 SMT 输出纠错，但 **5 项 GND 未连接未解决**，尚未具备投板条件。

## 当前可复现检查

```sh
kicad-cli sch erc --format json -o erc_rev_b.json FT2D_PD20V_12V5_3A_评审原理图.kicad_sch
kicad-cli pcb drc --schematic-parity --refill-zones --format json -o drc_rev_b.json FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb
```

| 检查 | 实际结果 | 说明 |
| --- | --- | --- |
| 原理图 ERC | **0** | 仅表示静态 ERC 通过 |
| 异网短路 / 铜间距违规 | **0** | KiCad 本次静态规则检查未发现硬性违规 |
| DRC violations | **0** | U1 已用系统库相同 29 焊盘封装刷新；局部无效热焊盘连接已处理 |
| DRC unconnected | **5** | F.Cu 局部 GND 铜岛、U2/U1 功能地焊盘和 R25/R26 周边仍有回流连接缺口，**不能放行** |
| schematic parity | **0** | PCB 与当前 Rev B 原理图一致；DNP 设置同步 |

上述结果按此目录所附 `erc_rev_b.json` 和 `drc_rev_b.json` 为准。**KiCad 的“DRC violations 0”不等于“DRC 通过”**：`unconnected_items = 5` 属实质未连接，必须继续修复。

## 本轮已核对并替换的 JLC 物料

| 位号 | 新器件及嘉立创料号 | 原厂/焊盘验证 | 装配保留事项 |
| --- | --- | --- | --- |
| **J1** | HRO `TYPE-C-31-M-12`，**C165948** | 标称 **20 V / 5 A**；KiCad 10 标准 `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`；按产品引脚表保持 CC1/CC2、VBUS、GND 网络，中心 `(24.15,42)`，转角 `-90°` | 立创标为 SMT，但带 **4 个穿孔屏蔽固定脚**；必须由 JLC 订单预览确认这种混合结构可贴装及固定脚焊接方式，并确认板边插拔可达性 |
| **L1** | JIERR `SRG1260-100-M`，**C53463013** | **10 µH ±20%**，Isat **14 A typ**，Idc **11 A typ**，DCR **25 mΩ max**；原厂落地尺寸 14.6 mm 总跨距、7.4 mm 焊盘间隙、4.8 mm 焊盘高度，生成 `FT2D:JIERR_SRG1260_100M`；器件高度 **6 mm max** | 数据表只是额定能力，不是开关纹波/温升实测；尤其要确认电台安装净高 |

J1 原厂 [PDF](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948)，L1 原厂 [PDF](https://datasheet.lcsc.com/datasheet/pdf/970397481256e0f4304d2971057c0f55.pdf?productCode=C53463013)。立创供料库存会变化，投单时须再次确认。

## 主要阻止打板的问题（按优先级）

1. **GND 仍有 5 项未连接**：已给 7 个有明确铜箔净距的分离 GND 区域加 0.6/0.3 mm 过孔，与 In1.Cu GND 连接；U1/QFN 局部、U2 GND 细焊盘和 R25/R26 周边仍未全部连通。尝试在狭缝中强加过孔会被 KiCad 指派到邻近的 `/PD_1V2`、`/VBUS_SW`、`/PGTH_U3` 等异网并产生违规，**这种失败的过孔方案已回退**。需要重排邻近铜线或核准有特殊 SMT 工艺要求的埋/填孔设计，不能强行短接。
2. **3 A 功率铜尚未签核**：已在顶层以并集多边形沿 `/USB_VBUS`、`/VBUS_RAW`、`/VBUS_SW`、`/SW`、`/V12P5`、`/VOUT` 走线增加 **1.6–2.0 mm 目标宽度**的局部铜皮。KiCad 会对异网铜自动裁切，部分受限引出仍保持 0.3–0.6 mm，不能宣称全线拥有目标宽度。需实测连续瓶颈截面、功率回路/回流面积、压降和温升。
3. **BUCK 功率布局仍待复核**：U2 由 `(72,43)` 移至 `(79,43)`，L1 SW 端位于 `(83.5,43)`，U2 SW 焊盘到 L1 同网焊盘直距约 **3.7 mm**；但输入高频去耦、输出电容和反馈 Kelvin 引线仍需结合 TI 指南逐项复审，SW 追踪铜皮面积须评估 EMI。
4. **JLC 全板供料不完整**：J1 和 L1 已锁定候选并核过原厂焊盘图，但 F1、C18、C23 及多种 R/C 的最终 SKU、稳定性/电压降额、库存均未签核；J1 固定脚混合工艺仍须确认。
5. **功能级风险**：STUSB4500 NVM 需编程并验 20 V PDO；eFuse 限流、DC-DC 环路、输出线束电台端极性、热和射频噪声尚无实测。

## 已完成的布线/设计动作

- 原评审 PCB 不变；此目录保留 Rev B 的独立原理图、PCB、工程设置和封装库。
- 保持 `POWER_REV_B` netclass 0.6 mm 路由过渡值，同时用 `power_pours_rev_b.py` 增加局部宽铜；**铜宽仍需实体连续性和发热签核**。
- 用两个新物料封装替换 J1/L1，并将 U2 SW 与 L1 SW 缩至约 3.7 mm；全部原走线重建并验证无异网硬短路。
- 已修复 U1 KiCad 系统库封装不一致告警，增加经净距校验的 GND 过孔；7 个安全过孔保留，3 个问题候选被撤销。
- 把两段自动布线占用 `In1.Cu` GND 参考面的 `/VBUS_SW` 导线转到 `In2.Cu`，避免在 Buck 下方切割地平面；重新填铜并通过间距 DRC（GND 未连接数仍为 5）。
- **修复贴片坐标漏项**：将 L1、Q1、U2、U3、D1 自定义封装标为 `attr smd`；C11/R14 DNP 排除，实际预览 CPL 为 **53 个位置**。
- 原理图和 PCB 的 DNP 与 BOM 属性一致，PD 协商和电台输出的电气定义未修改。

可审计工具在 `../../engineering_tools/`；未通过 DRC 的局部接地布线实验已从 PCB 与提交文件中移除。

## 投板门槛

- [ ] 全面优化 U2–L1–电容功率环路，宽铜/铜皮与热设计通过工程复核。
- [ ] ERC 0、DRC 0 实质违规、**DRC 0 未连接**、Parity 0（当前未连接为 5）。
- [ ] U1、U2、U3、Q1、J1、L1 的封装与厂家 land pattern 对照签核。
- [ ] JLC 物料号逐颗落实，DNP/人工焊接料与 SMT 文件匹配，SMT 预览方向正确。
- [ ] PD NVM 烧录工装、12.5V 无电台电子负载测试计划完备。

`../../manufacturing/Rev_B/REVIEW_ONLY_NOT_FOR_FAB/` 提供 **57 行 BOM、53 行 CPL、供料表和顶层铜预览图**。经实际运行，`export_jlcpcb_release_rev_b.sh` 因 5 项未连接按预期拒绝 Gerber/Excellon 放行。**正式制造文件暂未生成。**

## 关键一手资料

- [JLCPCB KiCad 10 BOM / Pick-and-Place 指南](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [ST STUSB4500](https://www.st.com/resource/en/datasheet/stusb4500.pdf)
- [TI LM61460-Q1](https://www.ti.com/lit/ds/symlink/lm61460-q1.pdf)
- [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
