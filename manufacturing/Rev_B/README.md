# 嘉立创 JLCPCB 4 层 PCB + SMT 制造准备

**状态：NO-GO（2026-10-25）**。

此目录只存放 `REVIEW_ONLY_NOT_FOR_FAB` 的采购/坐标核对数据，目前没有可下单的正式 Gerber + Excellon 钻孔包。真正放行条件见 `../../hardware/Rev_B/README.md`。

放行门禁脚本：`../../engineering_tools/export_jlcpcb_release_rev_b.sh`。它会先执行 ERC/DRC/Parity 检查，且要求完整的 `BOM_APPROVED.csv`、已目视确认的 `CPL_APPROVED.csv` 与三项工程签核。当前已运行验证：**ERC 0 / DRC 1 / GND unconnected 4 / parity 0，正常拒绝生成 Gerber**。

## 当前可用的非下单文件

| 文件 | 用途 | 限制 |
| --- | --- | --- |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_bom_unverified.csv` | KiCad 10 原生 55 行物料项 | 非 JLC 成品 BOM；缺大量立创料号 |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_positions_unverified.csv` | 原生 47 个 SMT 器件位置和方向 | KiCad Y 为负，格式/旋转未按 JLC 预览核准 |
| `REVIEW_ONLY_NOT_FOR_FAB/FT2D_RevB_SMT_sourcing_DRAFT.xlsx` | 汇总现有可对应的 LCSC 料号、风险、BOM 与位置对照，另附正 Y 预览列 | 整份工作簿**禁止**当作最终 SMT 下单资料 |

## 主器件目前对应的立创料号（需下单时复核实时库存）

| 位号 | 制造商型号 | LCSC/JLC 候选料号 | 当前问题 |
| --- | --- | --- | --- |
| U1 | STUSB4500QTR | C2678061 | SMT；必须配置 20V PDO NVM |
| U2 | LM61460AASQRJRRQ1 | C1855832 | SMT；RJR 封装待签核 |
| U3 | TPS259474ARPWR | C3662807 | SMT；RPW 封装及限流公差待签核 |
| Q1 | STL6P3LLH6 | C457492 | SMT；PowerFLAT 封装待签核 |
| J1 | USB4085-GF-A | C7095263 | **JLC 列为插件/波峰焊件**，不在标准 SMT 代贴内；须确认混合工艺或更换为可采 SMT 母座 |
| L1 | SRP1238A-100M | C2041734 | **缺货风险**；不能仅因 10µH 就直接代换，需核对 Isat/Irms/DCR/焊盘 |
| F1 | 1206SFS300F/32 | 待定 | 料号可得性、额定电流及 I²t 待核实 |
| C18 | EEHZL1V470R | 待定 | 替代须核对 ESR、温度和安装尺寸 |
| C23 | 250AVHT221M0608 | 待定 | 替代须核对 ESR、纹波电流和 DC-DC 稳定性 |

通用 R/C 都需要选择具体 LCSC 物料号，包括 0.1% 阻值和电容直流偏压性能；不能在整板审核前自动套用“任意 0603”。J2 是 PCB 编程焊盘，J3 为电台输出线束手工焊接位置；R14、C11 为 DNP。

## 预定制板参数（正式下单前锁定）

- 4 层 FR-4，板厚 **1.6 mm**；设定与 JLC 实际报价栈叠一致。
- 当前设计外形约 **105 × 65 mm**，未为最低价格或最小尺寸重新布局。
- 计划外层铜厚 **1 oz**；内层铜厚、层间介质厚度及板厂栈叠须按 JLC 实时报价/能力确认。
- F.Cu / In1.Cu / In2.Cu / B.Cu；阻焊双面，双面丝印，焊膏开窗前后按需要生成。
- 偏向顶层 SMT，但 J1 混合工艺、J3 手工接线和所有器件的装配方向须单独确定。
- 检查板边、USB-C 机械干涉、保险丝与输入/输出电容耐压、丝印/SMT 中心点、细焊盘漏锡风险。

## 下单前的清晰步骤

1. 修完 3 A 铜箔/功率环路/接地回路，并由硬件工程复核。
2. KiCad ERC、DRC 和 Schematic Parity 全部通过，且 **unconnected = 0**。
3. 对照各原厂 land pattern、核实 BOM 的每个 LCSC 型号与实时库存；确认 J1 是 JLC 可接单的 SMT/THT 混合工艺，或换型。
4. 生成 Gerber X2 / Excellon / BOM / CPL；在 KiCad Gerber Viewer 与 JLC 在线预览中交叉检查钻孔和器件朝向，特别是 KiCad 导出的位置 Y 方向。
5. 先做少量工程板，在未接电台状态用电子负载完成输入 PD 协商、12.5V 稳态、0–3A、过压/短路/热与射频噪声测试。

参考：JLCPCB 官方 [KiCad 10 BOM/CPL 导出说明](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)、[PCBA FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) 和 [铜厚指南](https://jlcpcb.com/help/article/jlcpcb-copper-weight)。
