# FT2D Rev B — 嘉立创报价与 SMT 在线预览包（未签核）

**这一目录仅用于上传后核对 Gerber/钻孔/物料/贴装在线预览，不是授权下单。**
生成命令：`python3 engineering_tools/build_rev_b_jlc_quote_preview.py`。

## 三个上传文件

1. `FT2D_RevB_4L_Gerber_Drill_QUOTE_ONLY.zip`：同一个 ZIP 内含 4 层铜、两面阻焊、
   丝印、焊膏、外形、PTH/NPTH 钻孔与 Gerber job；不要删除钻孔文件。
2. `FT2D_RevB_JLC_BOM_QUOTE_ONLY_NOT_APPROVED.csv`：53 位号 / 37 种候选物料，
   格式为 `Comment,Designator,Footprint,JLCPCB Part #`。
3. `FT2D_RevB_JLC_CPL_QUOTE_ONLY_NOT_APPROVED.csv`：53 个顶层 SMT 坐标；
   KiCad 原生 `Mid Y` 是**负数**，旋转角尚未在 JLC 预览里人工确认。

`PREVIEW_MANIFEST.json` 保留上述文件的 SHA-256、ERC/DRC/Parity 结果和源工程校验值。

## 在 JLCPCB 下单页必须逐步核对

- PCB：**4 层，FR-4，1.6 mm，外层 1 oz**；内层常见 0.5 oz，最终需以板厂的实际层叠、铜厚和预览为准；板子外形约 **105.05 × 65.05 mm**。
- Gerber：4 铜层顺序 `F.Cu / In1.Cu / In2.Cu / B.Cu`、钻孔位置和数量、板边 USB-C 开口、丝印遮挡、焊膏/阻焊是否正常。
- SMT：只选择**顶面**；J2 是裸编程焊盘，J3 是手工焊接输出线，**不计入 53 件 SMT 料**。C11/R14 为 DNP。
- 在线 BOM：逐项确认 `C-code` 仍可由 JLC **当次订单**供料和装配，尤其 R22
  `C861068`（102 kΩ，JLC 目录标注 SMT）当次库存；检查 C18/C23/F1 降额和
  C14–17/C20–22/C25/C26 的 DC-bias 与封装。
- 在线 CPL：手动看清 **J1 -90°** USB-C 插口是否朝板外，U1/U2/U3/Q1/D1/D2
  pin1 与取放角度，**C18/C23 正负极**及 J1 四个通孔外壳固定脚如何焊接。
- 首板目标建议先订 **5 片**，先要求 JLC 工厂确认 USB-C 混合 SMT/通孔结构的
  装配工艺；还应确认特定器件是否需加价/预订/代购。

## 仍然未满足的投板门槛

PCB/ERC/DRC 和 53 行候选 BOM/CPL **静态验证通过**，但在线预览、实时物料供料、
功率/热、线束极性、STUSB4500 NVM 写入和实际 3A/射频测试未签核。
特别注意 **STUSB4500 出厂 20V PDO 只有 1A**，且默认 5V 也可能开放电源路径；
见相邻目录的 [`PD_NVM_AND_FIRST_POWER_ON_PLAN.md`](../PD_NVM_AND_FIRST_POWER_ON_PLAN.md)。

**只有人工确认 JLC Gerber 与 SMT 贴装预览、解决物料拒单，并认可首板风险后，才可确认付费订单。**
正式 `RELEASE_READY` 仍由 `export_jlcpcb_release_rev_b.sh` 严格门禁，
不得用此目录绕过签核。
