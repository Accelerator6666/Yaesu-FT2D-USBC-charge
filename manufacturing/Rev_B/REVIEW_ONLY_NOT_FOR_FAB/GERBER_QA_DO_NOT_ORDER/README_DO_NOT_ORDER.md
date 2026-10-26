# QA-only Gerber / Drill files — DO NOT ORDER

本目录按 **2026-10-26 KiCad 10.0.7 Rev B** 导出，只用于工艺预览和检查；**还没有获得 PCB+SMT 制造放行**。

- F.Cu / In1.Cu / In2.Cu / B.Cu：四层铜；`Edge_Cuts.gm1`：板形。
- F/B_Mask：阻焊；F/B_Silkscreen：丝印；F/B_Paste：SMT 钢网。
- `-PTH.drl`、`-NPTH.drl`：镀通孔/非镀通孔钻孔（毫米）。
- 完成的静态检查：ERC **0**、DRC 违规 **0**、未连接 **0**、PCB/原理图一致性 **0**。
- 尚缺：全面的 LCSC BOM、已人工目视核对的 JLC CPL 和混合贴装可行性（J1），3 A 铜及散热、高频回流、C18 的 105°C 降额等工程签核。

**本目录可用于 Gerber Viewer/JLC 预览，但禁止点击下单。** 完成全部门禁后使用仓库的 `engineering_tools/export_jlcpcb_release_rev_b.sh` 生成独立 `manufacturing/Rev_B/RELEASE_READY/` 正式制造包。
