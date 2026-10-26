# QA-only Gerber / Drill files — DO NOT ORDER

本目录按 **2026-10-26 KiCad 10.0.7 Rev B** **重新导出**，已纳入 U3 两块 In2.Cu 局部功率铜与 4 颗普通 PTH 功率散热过孔，以及 C26 2.2 µF/25 V（0603 焊盘不变）；只用于工艺预览和检查，**还没有获得 PCB+SMT 制造放行**。

- F.Cu / In1.Cu / In2.Cu / B.Cu：四层铜；`Edge_Cuts.gm1`：板形。
- F/B_Mask：阻焊；F/B_Silkscreen：丝印；F/B_Paste：SMT 钢网。
- `-PTH.drl`、`-NPTH.drl`：镀通孔/非镀通孔钻孔（毫米）。
- 完成的静态检查：ERC **0**、DRC 违规 **0**、未连接 **0**、PCB/原理图一致性 **0**。
- 已备：53/53 位号候选 C-code 的**未批准** JLC BOM/CPL，37 种候选物料；**未证明库存和装配可行性**。
- 尚缺：候选料号逐项正式批准、已人工目视核对的 JLC CPL 和混合贴装可行性（J1），3 A 铜及散热、高频回流、C18 的 105°C 降额、C26 DC-bias 有效容值等工程签核。

**本目录可用于 Gerber Viewer/JLC 预览，但禁止点击下单。** 完成全部门禁后使用仓库的 `engineering_tools/export_jlcpcb_release_rev_b.sh` 生成独立 `manufacturing/Rev_B/RELEASE_READY/` 正式制造包。
