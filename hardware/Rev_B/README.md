# FT2D PCB Rev B（JLCPCB 首板工作版，未放行）

检查日期：2026-10-26；KiCad 10.0.7；目标板厂：嘉立创 JLCPCB；目标工艺：4 层 PCB + SMT 代贴片。

> **规则检查已清零，但制造仍 NO-GO。** 本目录可在 KiCad 10 打开；J1/L1 换料、C18 新候选的焊盘调整、GND 回流布线、局部功率铜、全板 DRC/Parity 均通过。剩余 3 A 功率/散热审查、完整 JLC SMT 供料、元器件和装配方向签核尚不能省略。

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
| DRC unconnected | **0** | 独立顶层 GND 区域通过常规穿孔过孔与内层地面连接，C5 补上局部 GND 逃线 |
| schematic parity | **0** | PCB 与当前 Rev B 原理图一致；DNP 设置同步 |

上述结果按此目录所附 `erc_rev_b.json` 和 `drc_rev_b.json` 为准。**规则检查 0/0/0/0 不是 3 A 载流能力、PD 功能、贴片方向或安全性能的认证。**

## 本轮已核对并替换的 JLC 物料

| 位号 | 新器件及嘉立创料号 | 原厂/焊盘验证 | 装配保留事项 |
| --- | --- | --- | --- |
| **J1** | HRO `TYPE-C-31-M-12`，**C165948** | 标称 **20 V / 5 A**；KiCad 10 标准 `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`；按产品引脚表保持 CC1/CC2、VBUS、GND 网络，中心 `(24.15,42)`，转角 `-90°` | 立创标为 SMT，但带 **4 个穿孔屏蔽固定脚**；必须由 JLC 订单预览确认这种混合结构可贴装及固定脚焊接方式，并确认板边插拔可达性 |
| **L1** | JIERR `SRG1260-100-M`，**C53463013** | **10 µH ±20%**，Isat **14 A typ**，Idc **11 A typ**，DCR **25 mΩ max**；原厂落地尺寸 14.6 mm 总跨距、7.4 mm 焊盘间隙、4.8 mm 焊盘高度，生成 `FT2D:JIERR_SRG1260_100M`；器件高度 **6 mm max** | 数据表只是额定能力，不是开关纹波/温升实测；尤其要确认电台安装净高 |
| **C18** | Panasonic `EEH-ZA1V470P`，**C178639** | 35 V / 47 µF 混合铝电容，**60 mΩ @100 kHz、1.3 A @100 kHz**；与原 EEH-ZL1V470R 的 **60 mΩ** 指标一致；PCB/C18 的封装改为 KiCad `CP_Elec_6.3x5.8`，中心由 `(62,48)` 移至 `(61.5,48)`，保持 pad 1=`/VBUS_SW`、pad 2=`/GND`；替代后 ERC 0、DRC 0、Parity 0 | **温度由原 135°C 降为 105°C**（虽是 10000 h @105°C）；须复核实际环境和热裕量、极性、焊盘尺寸及库存；不能据此自动批准 SMT |

J1 原厂 [PDF](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948)，L1 原厂 [PDF](https://datasheet.lcsc.com/datasheet/pdf/970397481256e0f4304d2971057c0f55.pdf?productCode=C53463013)。立创供料库存会变化，投单时须再次确认。

## 主要阻止打板的问题（按优先级）

1. **3 A 功率铜尚未签核**：顶层沿 `/USB_VBUS`、`/VBUS_RAW`、`/VBUS_SW`、`/SW`、`/V12P5`、`/VOUT` 增加 **1.6–2.0 mm 目标宽度**的合并局部铜皮，但异网净距会裁切狭颈；原细线最小仍为 **0.25–0.60 mm**，并不能宣称全线按 3 A 等效宽度连通。需复查各路径最窄断面、过孔电流、内层地回流、压降与满载升温。
2. **BUCK 高频布局仍待复核**：U2 `(79,43)`，L1 SW 端 `(83.5,43)`，直距约 **3.7 mm**；输入 C12/C13 高频去耦位置、U2 VIN/PGND 回路、输出电容接地/反馈 Kelvin 路径都须按照 TI 指南审查，SW 追踪铜面积仍可能引入 EMI。
3. **JLC 全板供料不完整**：J1/L1/C18 有具体立创型号；F1 `C41342` 和 C23 `C46550464` 为待复核的替代候选；**大量 0603/1210 R/C 无最终 LCSC 号**，且 0.1% 电阻和高压 MLCC 要核准公差与直流偏置。C18 **105°C** 的降额须获工程确认；J1 混合 SMT/通孔固定脚需要装配商确认。
4. **SMT 机器贴装仍未确认**：53 个位置与 PCB 坐标已通过本地审计，但 HRO J1 `-90°`、异形功率器件方向、极性电容、贴片取放中心及 KiCad Y 轴符号必须在 JLC 预览中人工核对。
5. **功能级风险**：STUSB4500 NVM 需编程并验 20 V PDO；eFuse 限流、DC-DC 环路、输出线束电台端极性、热和射频噪声尚无实测。

## 已完成的布线/设计动作

- 原评审 PCB 不变；此目录保留 Rev B 的独立原理图、PCB、工程设置和封装库。
- 保持 `POWER_REV_B` netclass 0.6 mm 路由过渡值，同时用 `power_pours_rev_b.py` 增加局部宽铜；**铜宽仍需实体连续性和发热签核**。
- 用两个新物料封装替换 J1/L1，并将 U2 SW 与 L1 SW 缩至约 3.7 mm；全部原走线重建并验证无异网硬短路。
- 已修复 U1 KiCad 系统库封装不一致告警；优先以常规 **0.6/0.3 mm GND 穿孔过孔**保留回流通路，再全板重布线。U1/U2/R25/R26 周边地与 C5 局部地均已接通，未使用未签核的焊盘盲埋孔。GND 特殊热焊盘局部改为实体连接；全板 DRC **0 违规 / 0 未连接**。
- 把两段自动布线占用 `In1.Cu` GND 参考面的 `/VBUS_SW` 导线转到 `In2.Cu`，避免在 Buck 下方切割连续地平面；重新填铜验证 0/0。
- C18 替换候选 Panasonic C178639 的直径更大，PCB/原理图/符号库同步换成 6.3×5.8 mm 封装，左移 0.5 mm 消除 `/BUCK_VCC` 净距冲突；极性和所有静态规则再次通过。**105°C 温度等级待确认**。
- **修复贴片坐标漏项**：将 L1、Q1、U2、U3、D1 自定义封装标为 `attr smd`；C11/R14 DNP 排除，实际预览 CPL 为 **53 个位置**。
- 原理图和 PCB 的 DNP 与 BOM 属性一致，PD 协商和电台输出的电气定义未修改。

可审计工具在 `../../engineering_tools/`；未通过 DRC 的局部接地布线实验已从 PCB 与提交文件中移除。

## 投板门槛

- [ ] 全面优化 U2–L1–电容功率环路，宽铜/铜皮与热设计通过工程复核。
- [x] ERC 0、DRC 0 实质违规、**DRC 0 未连接**、Parity 0（KiCad 10.0.7）；工程复查仍另计。
- [ ] U1、U2、U3、Q1、J1、L1 的封装与厂家 land pattern 对照签核。
- [ ] JLC 物料号逐颗落实，DNP/人工焊接料与 SMT 文件匹配，SMT 预览方向正确。
- [ ] PD NVM 烧录工装、12.5V 无电台电子负载测试计划完备。

`../../manufacturing/Rev_B/REVIEW_ONLY_NOT_FOR_FAB/` 提供 **57 行 BOM、53 行 CPL、供料工作表、顶层铜预览图和全部 Gerber/Excellon 钻孔 QA 文件**，这些均是**审阅版，不能直接下单**。`export_jlcpcb_release_rev_b.sh` 的静态检查已通过，但正确地停在**没有完整签核 BOM/CPL/工程签字**的下一道门禁。**正式 RELEASE_READY 制造包未生成。**

## 关键一手资料

- [JLCPCB KiCad 10 BOM / Pick-and-Place 指南](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [ST STUSB4500](https://www.st.com/resource/en/datasheet/stusb4500.pdf)
- [TI LM61460-Q1](https://www.ti.com/lit/ds/symlink/lm61460-q1.pdf)
- [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
