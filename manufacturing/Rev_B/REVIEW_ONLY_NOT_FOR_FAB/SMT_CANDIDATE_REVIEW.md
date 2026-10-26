# FT2D Rev B SMT 候选料号与 JLC 预览交接单（2026-10-26）

> **NO-GO：禁止直接下单。** 当前是 53 个器件对应的 **36 种 LCSC/JLC 候选编号**，不代表 36 种都已进入嘉立创可代贴片供料目录，更不代表封装、极性、温度、纹波和长期供货批准。

## 现有可复用文件

| 文件 | 内容 | 限制 |
| --- | --- | --- |
| `JLC_CANDIDATE_BOM_NOT_APPROVED.csv` | 嘉立创 `Comment, Designator, Footprint, JLCPCB Part #`；**53/53** SMT 位号有 C-code | **NOT APPROVED**，不能将文件更名成 `BOM_APPROVED.csv` 就当作工程签字 |
| `JLC_CANDIDATE_CPL_NOT_APPROVED.csv` | 嘉立创 `Designator, Mid X, Mid Y, Rotation, Layer`；53 个顶层 SMT | 未进行嘉立创 PCB Assembly 在线预览；Y 坐标沿用 KiCad 原生负值 |
| `SMT_CANDIDATE_TRACEABILITY_NOT_APPROVED.csv` | 53 个位号、原设计值、候选 MPN、LCSC C-code、风险标签与物料网页 | 供应目录展示不代表库存/工艺实时确认 |
| `FT2D_RevB_SMT_sourcing_DRAFT.xlsx` | 可筛选逐器件工作簿；DNP 和人工工序单独列出 | 53/53 是候选覆盖率，**正式批准数量为 0** |

以上候选可使用仓库的 `engineering_tools/build_rev_b_smt_candidate_review.py` 从 KiCad 原始 BOM/坐标重新生成，且已通过 `engineering_tools/validate_jlc_smt_release_rev_b.py`：**53 BOM = 53 CPL = 53 KiCad SMT 位号，C-code 无缺失；坐标 X/Y 绝对值一致、无重复、单顶层**。这个检查不会检测 3 A 载流、器件极性、电容有效容值或嘉立创实时库存。

## 本轮找到的关键候选

| 位号 | 设计参数 | 候选 MPN / C-code | 待明确核对 |
| --- | --- | --- | --- |
| **R22** | **101 kΩ，0603** | KOA [`RN73H1JTTD1013F100` / C4016651](https://www.lcsc.com/product-detail/C4016651.html) | 查到**原阻值**，不应把电路值随意改成 100 kΩ；但 LCSC 物料未证明 JLC 可代贴片、实时库存及采购量 |
| D1 | 原 ST ESD TVS、DFN1610-2 | ST [`ESDA25P35-1U1M` / C1974707](https://www.lcsc.com/product-detail/C1974707.html) | Pin 1 极性、反向工作电压、焊盘尺寸 |
| D2 | 原 ST `ESDA25W`、SOT-323 | ST [`ESDA25W` / C2935152](https://www.lcsc.com/product-detail/C2935152.html) | 3 引脚方向、封装与反向参数 |
| C1/C2 | 1 µF、0603、原 6.3 V | TDK [`C1608X7R1A105K080AC` / C5332007](https://www.lcsc.com/product-detail/C5332007.html)（10 V） | 额定电压提升不等于偏压有效容量已核实 |
| C3/C5 | 1 µF、25 V、0805 | Samsung [`CL21B105KAFNFNE` / C1712](https://www.lcsc.com/product-detail/C1712.html) | X7R、负载偏压和封装可用性 |
| C27/C28 | 3.3 nF / 2.2 nF、0603 | Murata [`C77036`](https://www.lcsc.com/product-detail/C77036.html) / [`C77033`](https://www.lcsc.com/product-detail/C77033.html) | 均选 50 V C0G 候选，确认原 PCB 信号引脚 |
| R12/R13 | 100 kΩ / 8.66 kΩ、0.1% | `C122538` / `C861591` | 1/10% 公差、电压/功耗、温漂和 SMT 库存不能降级 |
| C14–C17 | 10 µF、50 V、1210 | Murata `GRM32ER71H106KA12L` / `C77102` | **输入约 20 V DC-bias 后有效容值**，关乎 Buck 输入环路 |
| C20–C22/C25 | 47 µF、25 V、1210 | Walsin `1210X476M250CT` / `C3848311` | **输出约 12.5 V DC-bias 后有效容值**，关乎输出纹波/稳定性 |

其他 0603 电阻/电容（R1–R26 中所有非 DNP、C4/C10/C12/C13/C19/C24/C26）已逐颗列在追溯 CSV 和工作簿；不存在用“任意 0603”替代的自动批准。J1/L1/F1/C18/C23 的规格差异见 [关键替代审阅](CRITICAL_SMT_PARTS_REVIEW.md)。

## 必须在嘉立创订单前完成的现场验证

1. 用 JLCPCB PCB Assembly 的真实 BOM 解析结果核对 **36 种 C-code**：每行显示正确 MPN、封装、生产状态、备货/扩展料费和能否贴装；缺货的重新选型及必要时改封装。优先检查 `C4016651` 是否受理 **101 kΩ**，以及 J1 通孔屏蔽固定脚是否需要插件/手焊。
2. 在真实 JLC 贴装预览中逐颗核对 **53 个**坐标与角度，特别是 J1 `−90°`、U1/U2/U3/Q1 的 Pin 1、D1/D2、C18/C23 有极性标志、L1 朝向。**不要假设 KiCad 负 Y 一定能正确显示**；线上预览有异则修正 CPL，并同步存档理由。
3. 用厂家额定曲线签字：F1 3 A 熔丝 90°C 降额、C18 105°C vs 原 135°C、C23 105°C/ESR 28 mΩ vs 原 125°C/24 mΩ、电容随 DC-bias 降容及 Buck 环路稳定性。
4. 核对 J3 电台插头线束的机械拉力保护、极性、短路保护，以及输入 20 V PDO NVM 配置和首板不接电台的电子负载测试方案。
5. 在 3 A 功率通道/接地回流与热仿真或有效保守截面审核通过后，**另由负责人**准备 `manufacturing/Rev_B/BOM_APPROVED.csv`、`CPL_APPROVED.csv` 和 `RELEASE_APPROVAL.txt`，再触发 `export_jlcpcb_release_rev_b.sh` 生成真正的 `RELEASE_READY`。这些批准文件**不能**由候选脚本自动生成。

## 查询与工艺依据

- [JLC 官方 KiCad 10 的 BOM / CPL 列名与在线预览指南](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [JLC PCB Assembly FAQ（需进一步核实通孔+SMT 混合工艺）](https://jlcpcb.com/help/article/pcb-assembly-faqs)
- [LCSC KOA 101 kΩ 精确原值 C4016651](https://www.lcsc.com/product-detail/C4016651.html)；[另一颗 KOA 0.1% 101 kΩ C4027009](https://www.lcsc.com/product-detail/C4027009.html) 为备选，未自动换料

选料检索日期：2026-10-26。库存、可代贴片标记、JLC 订单价格具有时效性，不能将文档中的历史数据当成即时承诺。
