# 嘉立创 JLCPCB 4 层 PCB + SMT 制造准备

**状态：KiCad 10.0.7 新一轮 ERC/DRC/Parity 全通过；53/53 SMT 位号有候选 C-code；U3 供电散热补强、C26 去耦升级，但制造 NO-GO（2026-10-26）**。

此目录 `REVIEW_ONLY_NOT_FOR_FAB` 已包含采购/坐标核对数据、完整 4 层 Gerber 和 Excellon 钻孔 **QA 预览**。**不要直接将 QA 文件上传为制造订单**：尚无 BOM/CPL 完整签核与 3 A 工程批准。真正放行条件见 `../../hardware/Rev_B/README.md`。

**本轮加速下单准备**：新建 `QUOTE_PREVIEW_ONLY_NOT_RELEASED/`，把 4 层 Gerber+PTH/NPTH 钻孔封装为一个 JLC 可上传的 ZIP，并提供 JLC 格式 53 位号候选 BOM/CPL 与 SHA-256 校验清单。可先到 JLC 下单页进行**报价、层叠及 SMT 映射预览**，但必须完成下列人工检查后才能确认付款。生成器 `../../engineering_tools/build_rev_b_jlc_quote_preview.py` 重跑 ERC/DRC/Parity 和 BOM/CPL 位号检查，遇到错误自动拒绝生成。另有 `PD_NVM_AND_FIRST_POWER_ON_PLAN.md`：出厂 STUSB4500 的 20V PDO 电流默认仅 1A，建议 20V/3A + `POWER_ONLY_ABOVE_5V` NVM 配置并在首件上电读回核实。`PREFLIGHT/power_path_screening.json` 记录 U3 细线的保守电阻/损耗估算，**不是热性能批准**。

放行门禁脚本：`../../engineering_tools/export_jlcpcb_release_rev_b.sh`。它会先执行 ERC/DRC/Parity 检查，要求经人工核准的 `BOM_APPROVED.csv`、已目视确认的 `CPL_APPROVED.csv` 与三项工程签核，并以 `validate_jlc_smt_release_rev_b.py` **逐位号检查**有无漏件、多件、重复件、无 LCSC 号、错误坐标和非顶面装配。本轮重新独立验证 **ERC 0 / DRC violations 0 / unconnected 0 / parity 0**。非正式候选 BOM/CPL **53/53** 通过结构检查，但**没有一个候选代表已获采购/装配批准**；正式放行门禁仍必须拒绝创建可下单包。

## 当前可用的非下单文件

| 文件 | 用途 | 限制 |
| --- | --- | --- |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_bom_unverified.csv` | KiCad 10 原生 **57 行物料项** | 非 JLC 成品 BOM；缺大量立创料号，包含 DNP/人工工序项 |
| `REVIEW_ONLY_NOT_FOR_FAB/kicad_positions_unverified.csv` | 原生 **53 个 SMT 非 DNP** 器件位置和方向，含之前被漏掉的 L1、Q1、U2、U3、D1；`audit_jlc_cpl_rev_b.py` 已确认与 PCB 位号/坐标全集相符 | KiCad Y 为负，J1 显示 `-90°`，格式/旋转未按 JLC 在线预览核准 |
| `REVIEW_ONLY_NOT_FOR_FAB/FT2D_RevB_SMT_sourcing_DRAFT.xlsx` | 汇总现有可对应的 LCSC 料号、风险、BOM 与位置对照，另附正 Y 预览列 | 整份工作簿**禁止**当作最终 SMT 下单资料 |
| `REVIEW_ONLY_NOT_FOR_FAB/JLC_CANDIDATE_BOM_NOT_APPROVED.csv` | **53 个** SMT 位号的 JLC 4 列候选 BOM，覆盖 37 种不同料号，包含 F1/C18/C23/C26 候选换料 | **不是批准采购单**；实际供应、焊盘、极性、参数尚未签核 |
| `REVIEW_ONLY_NOT_FOR_FAB/JLC_CANDIDATE_CPL_NOT_APPROVED.csv` | 与 KiCad 53 个原生贴装位置一一对应的 JLC 五列候选坐标表，本地静态比对 53/53 | Y 采用 KiCad 原始负值；J1 `-90°` 和所有极性/取放方向待 JLC 在线目视复查 |
| `REVIEW_ONLY_NOT_FOR_FAB/SMT_CANDIDATE_TRACEABILITY_NOT_APPROVED.csv` | 每个位号的原始值、候选 MPN、C-code、风险类别和 LCSC 目录核对入口 | LCSC 目录可查 ≠ JLC 工厂支持 SMT/动态库存 ≠ 工程批准 |
| `REVIEW_ONLY_NOT_FOR_FAB/RevB_top_copper_REVIEW_ONLY.png` | 当前 PCB 顶层走线/局部宽铜和丝印审阅图 | 仅供工程复核，不能当 Gerber 或制造数据 |
| `REVIEW_ONLY_NOT_FOR_FAB/RevB_In2_power_stitch_REVIEW_ONLY.png` | 新增的 In2.Cu 两个局部电源岛（输入/输出相互隔离）及 4 颗穿孔位置 | 仅供审阅；3 A 分流/温升仍未签核 |
| `REVIEW_ONLY_NOT_FOR_FAB/POWER_COPPER_NECK_AUDIT_NOT_SIGNED.md` | 本轮 KiCad 10 独立重测、功率铜/狭颈抽样及 U3 0.3 mm 引脚逃线重点位置 | 仅为 50 µm 栅格局部几何审计，**不是 3 A 电流与热批准** |
| `REVIEW_ONLY_NOT_FOR_FAB/GERBER_QA_DO_NOT_ORDER/` | **本轮随 U3 改板重导**：4 层铜、阻焊/丝印/焊膏、外形、PTH/NPTH 钻孔和 Gerber job 文件 | **仅供审阅；未完成工厂订单预览、丝印位置、CPL 与 BOM 对照** |
| `REVIEW_ONLY_NOT_FOR_FAB/CRITICAL_SMT_PARTS_REVIEW.md` | F1/C18/C23 的原型号与嘉立创替代规格、数据来源及待签核项 | 物料候选，不是采购批准单 |

## 主器件目前对应的立创料号（需下单时复核实时库存）

| 位号 | 制造商型号 | LCSC/JLC 候选料号 | 当前问题 |
| --- | --- | --- | --- |
| U1 | STUSB4500QTR | C2678061 | SMT；必须配置 20V PDO NVM |
| U2 | LM61460AASQRJRRQ1 | C1855832 | SMT；RJR 封装待签核 |
| U3 | TPS259474ARPWR | C3662807 | SMT；RPW 封装及限流公差待签核 |
| Q1 | STL6P3LLH6 | C457492 | SMT；PowerFLAT 封装待签核 |
| J1 | **HRO TYPE-C-31-M-12** | **C165948** | 已核对厂家 20 V/5 A、CC 引脚映射及 KiCad 官方 land pattern。嘉立创列 SMT，但 **4 个穿孔屏蔽脚**的焊接方式、`-90°` 方向和板边安装须由装配商确认 |
| L1 | **JIERR SRG1260-100-M** | **C53463013** | 已核对 10 µH、Isat 14 A typ、Idc 11 A typ、DCR 25 mΩ max、3.6×4.8 mm 双焊盘及 6 mm 高度；动态纹波/实装净空需复核 |
| F1 | 1206SFS300F/32 → Littelfuse `0468003.NRHF` **候选** | **C41342** | 1206 3 A/32 V/50 A，I²t 1.27 A²s；**90°C** 温度限制相较原器件下降，仍须审核熔断曲线及额定散热 |
| C18 | 原 Panasonic `EEH-ZL1V470R` → Panasonic **`EEH-ZA1V470P` 候选已同步到 PCB/原理图** | **C178639** | 47 µF/35 V/60 mΩ/1.3 A；**6.3×5.8 mm** 焊盘已更换且 DRC 0；**105°C** 相较原 **135°C** 的温度等级需复核 |
| C23 | 250AVHT221M0608 → jieerrui `MA25V220M6X8` **候选** | **C46550464** | 220 µF/25 V、ESR 28 mΩ（原 24 mΩ），2.9 A @100kHz；**105°C** 温度等级，需核实 DC-DC 稳定性和尺寸 |

供料工作表还记录了初选型号：**R12/R13** 0.1% 薄膜电阻 `C122538` / `C861591`，**C14–C17** 10 µF/50 V 1210 X7R `C77102`，**C20–C22/C25** 47 µF/25 V 1210 X5R `C3848311`；以上**只是查到同标称参数的候选**，必须分别验证 20 V/12.5 V 偏压后的有效电容、尺寸/功率/容差以及库存。其余通用 R/C、D1/D2 已补齐候选 C-code；**R22 从 101 kΩ 兼容改值为 102 kΩ，Yageo `RT0603BRD07102KL` / `C861068` 在 JLC 目录标注 SMT**，TPS259474A 的 OVLO 标称值由约 13.32 V 改为 13.44 V（未包括阈值容差和瞬态），实际库存未确认。**C26 输出就近陶瓷电容由 100 nF/25 V 改为 2.2 µF/25 V X7R 的 Murata 0603 `C415535`，原理图/PCB/BOM/CPL 已同步，DC-bias 后有效容量未确认**。J2 是 PCB 编程焊盘，J3 为电台输出线束手工焊接位置；R14、C11 为 DNP。

## 预定制板参数（正式下单前锁定）

- 4 层 FR-4，板厚 **1.6 mm**；设定与 JLC 实际报价栈叠一致。
- 当前设计外形约 **105 × 65 mm**，未为最低价格或最小尺寸重新布局。U2 已向 L1 靠近 7 mm。
- 计划外层铜厚 **1 oz**；内层铜厚、层间介质厚度及板厂栈叠须按 JLC 实时报价/能力确认。
- F.Cu / In1.Cu / In2.Cu / B.Cu；阻焊双面，双面丝印，焊膏开窗前后按需要生成。
- 偏向顶层 SMT；实际 CPL 已纳入之前未标 `attr smd` 的 5 个自定义封装，排除了 C11/R14 DNP；J1 屏蔽柱混合工艺、J3 手工接线和所有器件的装配方向须单独确定。
- 检查板边、USB-C 机械干涉、保险丝与输入/输出电容耐压、丝印/SMT 中心点、细焊盘漏锡风险。

## 下单前的清晰步骤

1. ~~修完 5 项 GND 未连接~~：**已完成**，采用常规 GND 穿孔与局部逃线。**U3 input/output 增加 In2 局部电源岛和每网两颗标准过孔，更新后仍 ERC/DRC 0；但 U3 0.3 mm 短逃线与热/EMI 仍未完成签核**。下一步完成 3 A 铜箔实际狭颈、Buck 高频功率环路、接地回流和温升复核。
2. **已完成** KiCad ERC、DRC 和 Schematic Parity 全部通过，且 **unconnected = 0**；如再修改任何封装/线宽需重新验证。
3. 对照各原厂 land pattern、核实候选 BOM 的**53 个** SMT 位号是否均可由 JLC 装配、实时库存和贴装服务；重点解决 F1/C18/C23 的替代降额、1210 MLCC 的 DC-bias、有极性器件方向、J1 穿孔固定脚工艺，并签核后另行制备正式文件。
4. 生成 Gerber X2 / Excellon / BOM / CPL；在 KiCad Gerber Viewer 与 JLC 在线预览中交叉检查钻孔和器件朝向，特别是 KiCad 导出的位置 Y 方向。
5. 先做少量工程板，在未接电台状态用电子负载完成输入 PD 协商、12.5V 稳态、0–3A、过压/短路/热与射频噪声测试。

### 本轮换料原厂资料

- J1 C165948 [HRO TYPE-C-31-M-12 数据手册](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948)
- L1 C53463013 [SRG1260-100-M 数据手册](https://datasheet.lcsc.com/datasheet/pdf/970397481256e0f4304d2971057c0f55.pdf?productCode=C53463013)

参考：JLCPCB 官方 [KiCad 10 BOM/CPL 导出说明](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)、[PCBA FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) 和 [铜厚指南](https://jlcpcb.com/help/article/jlcpcb-copper-weight)。
