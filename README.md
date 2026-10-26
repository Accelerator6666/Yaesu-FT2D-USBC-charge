# FT2D USB-C PD 外接电源适配器（工程评审版）

为 Yaesu FT2DR / FT2DE 手持电台设计的 USB-C PD 转外接直流电源原型工程，使用 KiCad 10。**本工程尚未完成量产前的电气、PCB 和实物验证，请勿直接投板后连接电台。**

**最新进展（2026-10-25）：** [PCB Rev B 工作版](hardware/Rev_B/README.md) 已将 J1 改为 HRO `TYPE-C-31-M-12`（JLC **C165948**）、L1 改为 JIERR `SRG1260-100-M`（**C53463013**），并向电感移动 Buck U2、重建走线和局部加宽顶层功率铜皮。KiCad 检查 **ERC 0 / DRC 违规 0 / 原理图对照 0，但仍有 5 项 GND 未连接**。这些是实质性接地问题，**NO-GO，不能下单**。

嘉立创用的 [BOM/CPL 原生导出及 SMT 供料评审](manufacturing/Rev_B/README.md) 已更新到 **57 行 BOM / 53 个实际 SMT 坐标**，J1/L1 数据手册和焊盘已比对；剩余供料、GND、载流和 SMT 预览待签核。放行脚本已确认会拒绝导出不安全的 Gerber。原始评审 PCB 的 [基线检查](FAB_READINESS.md) 继续保留。

## 目标参数

| 项目 | 规格 |
| --- | --- |
| 输入 | USB-C PD 固定 20 V / ≥3 A（至少 60 W） |
| 输出 | 标称 12.5 V / 连续 3 A（37.5 W） |
| 设备端 | Yaesu E-DC-6 兼容尾线，使用前必须核对极性和尺寸 |
| 主控制器 | STUSB4500QTR（PD 协商）、LM61460-Q1（同步降压）、TPS259474A（eFuse） |
| PCB | 四层，含初始原型布局与自动布线评审版 |

FT2D 的电池充电由电台内部管理；此工程**不是**独立的锂电池充电器。

## 文件索引

- `FT2D_PD20V_12V5_3A_评审原理图.kicad_sch`：KiCad 原理图。
- `FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb`：已导入自动布线的评审 PCB。
- `FT2D_PD20V_12V5_3A_原型板.kicad_pcb`：早期原型板布局版本。
- 两份 `.kicad_pro`：各自的工程设置；`.kicad_prl` 属于本地用户界面状态，没有纳入版本控制。
- `FT2D.kicad_sym`、`FT2D.pretty/`、`sym-lib-table`、`fp-lib-table`：自定义符号和封装库。
- `FT2D_PD20V_12V5_3A_BOM.csv`：元件清单。
- `FT2D_PD20V_12V5_3A_评审原理图.pdf`、`FT2D_PD20V_12V5_3A_评审.net`：评审导出资料。
- `FT2D_USB-C_PD_3A_设计说明.md`、`FT2D_PD20V_12V5_3A_原理图连接表.md`：设计要求、连接表及测试计划。
- `FT2D_PD20V_12V5_3A_ERC.txt`：提供的 ERC 检查记录（0 errors / 0 warnings；不能替代板级验证）。
- `generate_schematic.py`、`generate_pcb.py`、`make_footprints.py`、`postprocess_route.py`：设计辅助脚本。

## 打开方式

1. 安装 KiCad 10，下载或克隆本仓库。
2. **当前工作版**：打开 `hardware/Rev_B/FT2D_PD20V_12V5_3A_评审原理图.kicad_pro`，对应 `.kicad_sch` 和 `.kicad_pcb`；原始根目录文件保留为此前的评审基线。
3. `hardware/Rev_B/README.md` 有当前实际检查结果；`manufacturing/Rev_B/` 有不可投板的供料/CPL 预览与放行门禁。
4. 如需重新生成自定义封装，运行 `python make_footprints.py`。仓库已包含脚本生成的七个自定义封装。

部分其他自动生成脚本含有原开发环境的本地路径以及未附带的临时网络表输入，**不是**开箱即用的跨平台构建流程；直接阅读和编辑现有 KiCad 文件不依赖运行这些脚本。

## 投板与上机前必须确认

- 按厂家数据手册复核所有芯片、USB-C 连接器及自定义封装的引脚、焊盘和焊膏开窗。
- 重新运行 ERC / DRC、检查所有连接与四层铜皮，审查 Gerber / 钻孔。
- **Rev B 虽已有 1.6–2.0 mm 目标宽度的局部功率铜皮，但受限处仍有 0.3–0.6 mm 细颈，不等于全路径可连续承载 3 A。**需要完成电流通道截面、过孔与温升签核。
- 正确烧录、读回并验证 STUSB4500 NVM 的 PD 请求参数，确认非 20 V / 3 A 电源不会向电台供电。
- 不接 FT2D，先用电子负载验证输出电压、纹波、温升、负载阶跃、短路、过流、过压以及射频噪声影响。
- 实测电台端插头的正负极、机械匹配与满载电压后，才考虑连接真机。

更完整的参数和验收流程参见两份中文设计说明文档。当前工程没有提供足以证明安全可投板或已完成实测的资料。
