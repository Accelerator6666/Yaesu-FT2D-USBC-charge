# FT2D Rev P：USB-C PD 模块＋洞洞板工程样机

> **工程试验设计／未实测／禁止直接连接 FT2D。** Rev P 是为了减少首台原型的 SMT 费用而新增的独立路线；不覆盖原 KiCad Rev B，也不授权现有嘉立创订单付款。
>
> 2026-10-26 方案初选。模块实际型号、接口标识、实测温升、RF 噪声和保护关断还没有签字。

## 一句话方案

用**成品模块实现高速电路**，仅在洞洞板上固定和连接低频 DC 电源线。绝不把原 Rev B 的 STUSB4500、LM61460 和细间距电源芯片裸装到洞洞板上。

**本版目标改为 12.0 V / 3 A 连续（36 W）**，而不是原 Rev B 的 12.5 V / 3 A。FT2DR/DE 官方规定外接 **11–16 V DC、供电能力 ≥3 A**；12 V 固定输出的模块容易采购且没有可误触的调压电位器。输入依然为 USB-C PD 固定 20 V / ≥3 A（≥60 W）。

示意图：[Rev P 实际接线图](wiring.svg)，检验程序：[台架测试和放行清单](TEST_PLAN.md)。

## 两个成本等级，不能混用放行标准

| 路线 | 降压模块 | 独立输出 OVP | 允许用于 |
|---|---|---|---|
| **Rev P0：低价实验版** | XL4016E1 类**已经焊好的**可调降压模块，20 V→12.0 V | 仍应安装；如没有可靠的 OVP，只能做电子负载实验 | **只允许电子负载**，不得接电台 |
| **Rev P1：保护优先版（参考组合）** | Pololu **D42V55F12**，固定 12 V，厂家标称典型 4.5 A（实际随热条件而变） | PN Labs **Protect** 5–30 V 调整为 14.3 V 关断 | 通过完整验收之后才可考虑连接 FT2D |

这两个版本共享同一接线拓扑，**但 P0 未经认证的廉价模块不能自动升级为 P1**。成品模块价格和库存会变化；保护优先版可能仍需数十美元，因此采购前应对照嘉立创 SMT 的最终报价。选用 P1 品牌仅作为可验证参考，**并非厂家为 FT2D 应用背书**。

## 选料表（首台，各 1 件，线材按需）

| 编号 | 功能 / 候选 | 必须核对的指标 | 状态和资料 |
|---|---|---|---|
| PDS1（优先） | **Adafruit #5807 HUSB238 USB-C PD Dummy Breakout**，厂家装好细间距元件，仍需要剪开/焊接大焊桥并自行装接线端子 | USB-C 母座；电源端 `V+` 和 `GND` / 端子 `+` 和 `−`。**剪开默认 `5V` 焊桥、其他电压焊桥全部保持断开＝选择 20 V / 最高可用档；剪开默认 `1A` 焊桥、`2A` 保持断开＝请求 3 A。**切勿靠默认出厂 5 V / 1 A 设置试机 | [Adafruit #5807 商品](https://www.adafruit.com/product/5807)；[原厂引脚/焊桥指南](https://learn.adafruit.com/adafruit-husb238-usb-type-c-power-delivery-breakout/pinouts)，**20 V 档是否成功必须实际量 TP1** |
| PDS1（选配） | **Adafruit #5991 HUSB238 Switchable Breakout** | 成品螺丝端子、拨码选择 20 V；厂家说明 `ISet` 焊桥默认为 **1.25 A**，剪开才是 **3.25 A 请求档**；需要实测充电器是否接受该请求，不能以铭牌 3 A 自动推断 | [Adafruit #5991 商品](https://www.adafruit.com/product/5991)、[原厂引脚指南](https://learn.adafruit.com/adafruit-usb-type-c-power-delivery-switchable-breakout/pinouts) |
| PDS1（通用低价备选） | **CH224K 已装配 20 V PD 触发板** | 必须有真实品牌/卖家 SKU、USB-C 插座及清楚的 `VOUT+ / GND`，证明板级走线/焊盘可连续 ≥3 A；不单买裸芯片 | [WCH CH224 原厂芯片资料](https://www.wch-ic.com/downloads/CH224DS1.PDF.html?type=en)；**尚未核对特定商品，不作为直接购买型号** |
| REG1（P1） | **Pololu D42V55F12**，#5577 | 固定 12 V ±3%，输入涵盖 20 V；厂家给出 3.5–6.5 A 典型最大连续输出范围，实际值需按散热/输入电压确认 | [Pololu 原厂规格](https://www.pololu.com/product/5577)；品牌参考件，不保证当地库存 |
| REG1（P0） | **XLSEMI XL4016E1 预装降压模块** | 输入覆盖 20 V，调压范围覆盖 12 V，实测 3 A/30 min 热性能、启动尖峰、纹波及器件真假；需锁住调压旋钮 | [XLSEMI 原厂芯片数据](https://www.xlsemi.com/datasheet/XL4016-EN.pdf)。**芯片额定值不等于网上模块持续能力；未通过完整验收不得接电台** |
| OVP1 | **PN Labs Protect**（5–30 V，SKU 9800） | **置于降压模块后面**、电子负载/电台前面，校准到**14.3 V**附近切断；有实际过压断开测试结果；红正黑负输入/输出按模块丝印核对 | [PN Labs 官方说明及公式](https://pnlabs.ca/shop/protect-5-30v-dc-power-protection-module)；可改用其他有同等可验证快速切断能力的成品 OVP，不可用普通 TVS/低压断电板直接替代 |
| F1 | **20 V 输入保险丝：3 A 延时型**和保险丝座 | 直流额定电压 ≥32 V、分断能力满足 PD 源；规格经启动浪涌测试复核 | 候选，未指定不可替代的厂商料号 |
| F2 | **12 V 输出保险丝：4 A 延时型**和保险丝座 | 直流额定电压 ≥32 V，实际升温、负载阶跃和短路测试后复核；不能代替 OVP | 候选，未指定不可替代的厂商料号 |
| J_OUT | 八重洲 E-DC-6 兼容电源线，尽量采用已做好的尾线 | 原厂规定带红线/白黑线为正极、黑线负极；**最终仍须逐线做万用表通断测量**，不能凭插头外观猜测 | [FT2DR/DE 官方使用说明](https://yaesu.com/Files/DFDF4D53-1B78-7375-E6C7A6E4B192BE13/FT2DR_DE_EH060M203_1608Y-EM-1.pdf) |
| W1 | 红/黑 **18 AWG** 柔性电源线、热缩管和应力消除 | 载流段尽量短（目标每段 <20 cm）；机械固定，绝缘完整；**不借用洞洞板细铜环承载 3 A** | 通用耗材 |
| BASE | ≥120×80 mm FR-4 洞洞板、绝缘柱、散热和外壳 | 只作为机械固定和低电流辅助连接；模块之间的 **+12V/GND** 采用单独电线点到点连接 | 按实际模块外形二次选尺寸 |
| PS1 | USB-C PD 充电器和额定 ≥3 A 的 USB-C 线 | 充电器铭牌需要有 **20 V / 3 A** 档，不能只看总功率“65 W”字样 | 实物待确认 |

### 保护级的接线原则

1. `PD_TRIGGER.20V+ → F1 → BUCK.VIN+`；`PD_TRIGGER.GND → BUCK.GND`。
2. `BUCK.VOUT+ → OVP.IN+`；`BUCK.GND → OVP.IN−`。
3. `OVP.OUT+ → F2 → E_DC6_正极`；`OVP.OUT− → E_DC6_负极`。
4. 必须保留三处量测：**TP1：20 V 原始协商电源**、**TP2：12 V 降压后/OVP 前**、**TP3：OVP+保险丝后的电台接口**；所有电压对各自负端测量。
5. F1/F2 都放在正极；正负线成对走线、可局部绞合。不同模块端子不能靠示意图的左右位置猜测，需要以**所购买实物丝印及厂家说明**确认。
6. **OVP 模块必须是高边快速断开的成品模块**。只装 15 V TVS 并不能保证异常输入时电台端小于 16 V；普通延时继电器板也不能假定可防住启动过冲。

对 **Adafruit #5807 + Pololu D42V55F12** 这一明确组合，第一条线路实际写成：

`#5807 V+ → F1 → Pololu VIN`，`#5807 GND → Pololu GND`；Pololu `VOUT → OVP IN+`，`GND → OVP IN−`。Pololu 真正的丝印是 **`VIN / VOUT / GND`**，没有独立 `VIN− / VOUT−` 引脚；其 `EN`、`PG` 和 `VRP` 保持厂家默认连接/悬空状态，**不要把它们当电源负极或随意并联**。PN Labs Protect 采用 **XT60** 接口，需要自配同规格、正确极性配对件及应力消除，不能当作裸焊盘接线。

### OVP 设置示例（PN Labs Protect）

厂家提供的换算关系：`R_OVC [kΩ] = (V_CUTOFF [V] - 1.95) / 2.89`。选择目标 14.3 V，约 **4.27 kΩ**。**断电时**按照厂家方法调电位器/量阻值；上电必须用可调实验电源实际测断开点。目标实测断开区间 **14.0–14.8 V**，且在故障中测得 `TP3` 不得出现 16 V 或更高的尖峰。实测不到这点，禁止接电台。

该模块会在过压恢复后自动重新接通；因此还需要验证在持续异常输入下不会反复向电台端送高压脉冲。保险丝只处理过流/线材保护，**不是精密 3 A 恒流器件**。

### 不建议的简化

- 不使用 LM2596 小板作为“保证连续 3 A”的已签核方案；额定边缘、热、纹波均不够明确。
- 不把 USB-C 的 20 V 直接接 FT2D：**官方上限 16 V，20 V 有损坏风险**。
- 不直接用 PD 15 V 档省去降压：虽可能落在工作电压内，但对 PD 容差和瞬态的安全余量变小。
- 若你**已经有实测可提供固定 12 V / ≥3 A PDO 的 PD 充电器**，可另设计“12 V 触发器＋OVP＋保险丝”的短链版本；不能假设所有 PD 充电器都支持固定 12 V。
- 不将 XL4016 的“8 A / 200 W”等营销标签视为最终连续额定值。

## 装配顺序

1. 把每个模块先固定在绝缘底座，不要在任何模块背面打孔。预留散热、USB-C 插拔方向、E-DC-6 电缆固定点。
2. 先不安装最终的 E-DC-6 插头，使用接线柱作为**电子负载端**，接好 PD → F1 → BUCK，单独测输出。
3. 关闭所有电源后，再将 OVP1 接入降压后端并调整、验证阈值；只有过压试验完成后装 F2/最终尾线。
4. 任一时刻把 20 V 原始电源线与 12 V 电台输出线分开放置，使用醒目标签，避免误插。
5. **P1 参考组合**先通过 [TEST_PLAN.md](TEST_PLAN.md) 的 **A–D 全部强制台架项目**，审核尾线极性及 3 A 温升；再按 E 章先接收、后短时发射，单独评价 RF 干扰。**P0 未经核对并升级保护与验收前保持不接电台。**

## 与现有 Rev B 的关系

- 原 `hardware/Rev_B/` 是完整集成式 PCB，**冻结保留**以便日后做紧凑正式版。
- 原 `manufacturing/Rev_B/QUOTE_PREVIEW_ONLY_NOT_RELEASED/` 只是嘉立创报价/在线预览包，**不可作为本方案可直接下单的证明**。
- 已建立的嘉立创 **5 片 PCB 待付款订单**不会因建立 Rev P 自动取消；如果确定放弃 Rev B，用户应在嘉立创确认订单状态并自行决定是否撤销。这里**没有进行任何付款或撤单**。
- FT2D 使用外部 DC 时，是否给已装电池充电及持续充电限制，依照八重洲手册处理；**Rev P 只是外部稳压电源，不是独立的锂电池充电管理器**。

## 重要原始资料

- [Yaesu FT2DR/DE 官方使用手册](https://yaesu.com/Files/DFDF4D53-1B78-7375-E6C7A6E4B192BE13/FT2DR_DE_EH060M203_1608Y-EM-1.pdf)
- [WCH CH224 系列资料](https://www.wch-ic.com/downloads/CH224DS1.PDF.html?type=en)
- [Adafruit #5807：HUSB238 已装配 PD 触发板及设置方法](https://learn.adafruit.com/adafruit-husb238-usb-type-c-power-delivery-breakout/pinouts)
- [Pololu D42V55F12](https://www.pololu.com/product/5577)
- [PN Labs Protect](https://pnlabs.ca/shop/protect-5-30v-dc-power-protection-module)
- [XLSEMI XL4016](https://www.xlsemi.com/datasheet/XL4016-EN.pdf)
- [TI：高频降压电路的 EMI 与回路布局](https://www.ti.com/document-viewer/lit/html/SSZT090)
