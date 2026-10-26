# FT2D USB-C PD 外接电源适配器（工程评审版）

为 Yaesu FT2DR / FT2DE 手持电台设计的 USB-C PD 转外接直流电源原型工程，使用 KiCad 10。**本工程尚未完成量产前的电气、PCB 和实物验证，请勿直接投板后连接电台。**

**最新进展（2026-10-26）：** [PCB Rev B 工作版](hardware/Rev_B/README.md) 已更换 J1 为 HRO `TYPE-C-31-M-12`（JLC **C165948**）、L1 为 JIERR `SRG1260-100-M`（**C53463013**），并完成接地回流修复、局部 1.6–2.0 mm 目标功率铜皮、重新填铜。C18 已采用 Panasonic `EEH-ZA1V470P`（**C178639**）的匹配 6.3 mm 焊盘作为候选，取代原 5 mm 焊盘型号，仍须核定温度等级。**本轮 U3 新增 4 颗标准功率过孔和 In2 两个独立局部宽铜岛；C26 从 100 nF 升级为 2.2 µF/25 V X7R 候选（C415535），0603 焊盘不变。** 更新后 KiCad 10.0.7 **ERC 0 / DRC 违规 0 / 未连接 0 / 原理图对照 0**，3 A 温升仍未签核。

嘉立创用的 [BOM/CPL 原生导出及 SMT 供料评审](manufacturing/Rev_B/README.md) 已更新到 **57 行原生 BOM / 53 个实际 SMT 坐标 / 53 个候选 JLC 物料号（37 种料）**；候选 JLC 四列 BOM、五列 CPL 与逐项来源追溯表都在 `REVIEW_ONLY_NOT_FOR_FAB`，并已通过 53/53 本地 BOM/CPL 位号和坐标审计。**4 层 Gerber、焊膏、钻孔已随本轮新增过孔/内层铜重新导出。** 另新增 [嘉立创报价/贴片在线预览三件套](manufacturing/Rev_B/QUOTE_PREVIEW_ONLY_NOT_RELEASED/README_FIRST.md)：平铺 Gerber+钻孔 ZIP、53 位号 BOM 和 CPL，可以立即上传**预览/询价**，仍不能直接确认订单。同步生成了 [U3 3A 铜线保守损耗估算](manufacturing/Rev_B/PREFLIGHT/power_path_screening.json) 和 [STUSB4500 NVM/首板上电方案](manufacturing/Rev_B/PD_NVM_AND_FIRST_POWER_ON_PLAN.md)。尤其注意 STUSB4500 **出厂 20V PDO 只有 1A，且默认 5V 时可使能电源路径**，必须在首板测试前重新配置并验证。**当前仍 NO-GO，不要直接下单**：待完成 3 A 电热及 Buck 回路复核、全部候选元件真实 SMT 供货/兼容性确认、JLC 贴片预览和工程签核。正式放行脚本继续拦截未签核订单；原始评审 PCB 的 [基线检查](FAB_READINESS.md) 保留。

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
