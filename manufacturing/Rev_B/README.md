# 嘉立创 JLCPCB 4 层 PCB + SMT 制造准备

**状态：NO-GO（2026-10-25）**。

此目录只存放 `REVIEW_ONLY_NOT_FOR_FAB` 的采购/坐标核对数据，目前没有可下单的正式 Gerber + Excellon 钻孔包。真正放行条件见 `../../hardware/Rev_B/README.md`。

放行门禁脚本：`../../engineering_tools/export_jlcpcb_release_rev_b.sh`。它会先执行 ERC/DRC/Parity 检查，且要求完整的 `BOM_APPROVED.csv`、已目视确认的 `CPL_APPROVED.csv` 与三项工程签核。当前已运行验证：**ERC 0 / DRC violations 0 / GND unconnected 5 / parity 0，按预期拒绝生成正式 Gerber/钻孔文件**。

## 当前可用的非下单文件

| 文件 | 用途 | 限制 |
| --- | --- | --- |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_bom_unverified.csv` | KiCad 10 原生 **57 行物料项** | 非 JLC 成品 BOM；缺大量立创料号，包含 DNP/人工工序项 |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_positions_unverified.csv` | 原生 **53 个 SMT 非 DNP** 器件位置和方向，含之前被漏掉的 L1、Q1、U2、U3、D1；`audit_jlc_cpl_rev_b.py` 已确认与 PCB 位号/坐标全集相符 | KiCad Y 为负，J1 显示 `-90°`，格式/旋转未按 JLC 在线预览核准 |
| `REVIEW_ONLY_NOT_FOR_FAB/FT2D_RevB_SMT_sourcing_DRAFT.xlsx` | 汇总现有可对应的 LCSC 料号、风险、BOM 与位置对照，另附正 Y 预览列 | 整份工作簿**禁止**当作最终 SMT 下单资料 |
| `REVIEW_ONLY_NOT_FOR_FAB/RevB_top_copper_REVIEW_ONLY.png` | 当前 PCB 顶层走线/局部宽铜和丝印审阅图 | 仅供工程复核，不能当 Gerber 或制造数据 |

## 主器件目前对应的立创料号（需下单时复核实时库存）

| 位号 | 制造商型号 | LCSC/JLC 候选料号 | 当前问题 |
| --- | --- | --- | --- |
| U1 | STUSB4500QTR | C2678061 | SMT；必须配置 20V PDO NVM |
| U2 | LM61460AASQRJRRQ1 | C1855832 | SMT；RJR 封装待签核 |
| U3 | TPS259474ARPWR | C3662807 | SMT；RPW 封装及限流公差待签核 |
| Q1 | STL6P3LLH6 | C457492 | SMT；PowerFLAT 封装待签核 |
| J1 | **HRO TYPE-C-31-M-12** | **C165948** | 已核对厂家 20 V/5 A、CC 引脚映射及 KiCad 官方 land pattern。嘉立创列 SMT，但 **4 个穿孔屏蔽脚**的焊接方式、`-90°` 方向和板边安装须由装配商确认 |
| L1 | **JIERR SRG1260-100-M** | **C53463013** | 已核对 10 µH、Isat 14 A typ、Idc 11 A typ、DCR 25 mΩ max、3.6×4.8 mm 双焊盘及 6 mm 高度；动态纹波/实装净空需复核 |
| F1 | 1206SFS300F/32 | 待定 | 料号可得性、额定电流及 I²t 待核实 |
| C18 | EEHZL1V470R | 待定 | 替代须核对 ESR、温度和安装尺寸 |
| C23 | 250AVHT221M0608 | 待定 | 替代须核对 ESR、纹波电流和 DC-DC 稳定性 |

通用 R/C 都需要选择具体 LCSC 物料号，包括 0.1% 阻值和电容直流偏压性能；不能在整板审核前自动套用“任意 0603”。J2 是 PCB 编程焊盘，J3 为电台输出线束手工焊接位置；R14、C11 为 DNP。

## 预定制板参数（正式下单前锁定）

- 4 层 FR-4，板厚 **1.6 mm**；设定与 JLC 实际报价栈叠一致。
- 当前设计外形约 **105 × 65 mm**，未为最低价格或最小尺寸重新布局。U2 已向 L1 靠近 7 mm。
- 计划外层铜厚 **1 oz**；内层铜厚、层间介质厚度及板厂栈叠须按 JLC 实时报价/能力确认。
- F.Cu / In1.Cu / In2.Cu / B.Cu；阻焊双面，双面丝印，焊膏开窗前后按需要生成。
- 偏向顶层 SMT；实际 CPL 已纳入之前未标 `attr smd` 的 5 个自定义封装，排除了 C11/R14 DNP；J1 屏蔽柱混合工艺、J3 手工接线和所有器件的装配方向须单独确定。
- 检查板边、USB-C 机械干涉、保险丝与输入/输出电容耐压、丝印/SMT 中心点、细焊盘漏锡风险。

## 下单前的清晰步骤

1. **修完 5 项 GND 未连接**；小焊盘若采用 via-in-pad 等工艺，先与 JLC 确认可贴片与成本。完成 3 A 铜箔实际狭颈、功率环路、接地回流和温升复核。
2. KiCad ERC、DRC 和 Schematic Parity 全部通过，且 **unconnected = 0**。
3. 对照各原厂 land pattern、核实 BOM 的每个 LCSC 型号与实时库存；特别补齐 F1、C18、C23 及通用 R/C 的物料号；确认 J1 固定脚装配工艺。
4. 生成 Gerber X2 / Excellon / BOM / CPL；在 KiCad Gerber Viewer 与 JLC 在线预览中交叉检查钻孔和器件朝向，特别是 KiCad 导出的位置 Y 方向。
5. 先做少量工程板，在未接电台状态用电子负载完成输入 PD 协商、12.5V 稳态、0–3A、过压/短路/热与射频噪声测试。

### 本轮换料原厂资料

- J1 C165948 [HRO TYPE-C-31-M-12 数据手册](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948)
- L1 C53463013 [SRG1260-100-M 数据手册](https://datasheet.lcsc.com/datasheet/pdf/970397481256e0f4304d2971057c0f55.pdf?productCode=C53463013)

参考：JLCPCB 官方 [KiCad 10 BOM/CPL 导出说明](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)、[PCBA FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) 和 [铜厚指南](https://jlcpcb.com/help/article/jlcpcb-copper-weight)。
