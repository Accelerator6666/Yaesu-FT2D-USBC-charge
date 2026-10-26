# FT2D Rev P-D：首台低成本样机采购与装配卡

**版本：2026-10-26｜状态：候选选型已核对，尚未购买／装配／实测，不能直接连接 FT2D。**

这张清单只对应 [12 V 直通接线图](wiring_12v_direct.svg)（**不需要 20→12 V DC-DC 降压板**）。优先利用用户已有的 TA3005U（以 2026-10-26 上传的商品参数截图为依据）：C1/C2 单口标称 `12 V⎓3 A`，C3 只有 `12 V⎓2.5 A`。购买前必须再核对**手中实物的铭牌**，后续先单独占用 C1/C2 并做 3 A 台架试验。

## A. 确认采购清单（首台 1 份）

| 顺序 | 数量 | 编号 | 具体型号 / 选择 | 2026-10-26 所见参考售价 | 是否已确定 |
|---|---:|---|---|---|---|
| 1 | 1 | PDS1 | **Adafruit #5807 HUSB238 USB-C PD Dummy Breakout**；必须剪开默认 `5V/1A` 两处焊桥、**仅闭合 12V 焊桥**且 `2A` 保持断开，形成 12V/3A 请求。两脚电源端子需自行焊装 | 官方 **US$5.95**；Micro Center 曾显示 **US$5.99** | **选型确定，库存随商家变化** |
| 2 | 1 | OVP1 | **PN Labs Protect #9800**，可调 5–30 V 高边 OVP，实际关断点调到 **14.3 V**；XT60 输入/输出，最高连续阻断能力官方称约 40 V | RobotShop / Elecrow **US$24.99** | **选型确定，实际阈值和关断波形待测** |
| 3 | 1＋备件 | F2 | **Littelfuse 0287004.L**，标准 ATO/ATC **4 A、32 V DC** 插片式保险丝 | 采购时看实时价格 | **规格确定，实际温升/动作待复核** |
| 4 | 1 | FH2 | **Littelfuse FHAC0001SXJ**，32 V DC 密封 ATO 串线保险丝座，配 **16 AWG** 引线（可与 18 AWG 主线用合规绝缘端接相连） | 采购时看实时价格 | **规格确定，库存待核实** |
| 5 | 1 | J_OUT | **Yaesu E-DC-6 原厂或注明适配 FT2DR/DE 的真正等效尾线**，选择带**裸线端**、不要整条车载升压电源线 | 部分国际商家约 **US$11–20**（仅供预算） | **插头实际极性与商家来源待确认** |
| 6 | 若干 | W1 | 红／黑 18 AWG 多股柔性线、合格压接/焊接件、热缩管、束线及绝缘材料 | 未报价 | 量测后再裁线，避免接头多次拆焊 |
| 7 | 1 | BASE | 绝缘底板或 FR-4 洞洞板（初选至少约 120×80 mm）、固定柱、可开孔绝缘外壳 | 未报价 | 以模块与 XT60 插拔空间最终定尺寸 |
| 8 | 1 | CABLE | 已有或另购 **≥3 A** 额定 USB-C to USB-C 线，短、接头牢靠 | 若已持有无需购买 | **必须核对线材，不因充电器标称 140 W 就自动视为合格** |

### 已核对的购买/技术页面

- [Adafruit #5807 官方商品](https://www.adafruit.com/product/5807)，[原厂 HUSB238 引脚和焊桥](https://learn.adafruit.com/adafruit-husb238-usb-type-c-power-delivery-breakout/pinouts)。可对照 [Micro Center 商品页](https://www.microcenter.com/product/708828/adafruit-industries-usb-type-c-power-delivery-dummy-breakout-i2c-or-fixed-husb238) 的实际售价/可选门店库存；不要购买只有 HUSB238/CH224K **裸芯片**的商品。
- [PN Labs Protect #9800 原厂](https://pnlabs.ca/shop/protect-5-30v-dc-power-protection-module)，[RobotShop 相关商品](https://www.robotshop.com/products/pn-labs-protect-5-30-v-adjustable-over-voltage-module)。RobotShop 页面写有**配套 XT60 插头随附**，下单前确认包装中包含两侧所需公母配对件；若已附送无需重复采购。
- [Littelfuse 0287004.L（DigiKey）](https://www.digikey.com/en/products/detail/littelfuse-inc/0287004-L/3672096)；[Littelfuse FHAC 系列保险丝座规格](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet.pdf?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79)。**实际 4 A ATO 熔断器不是之前草案的“4 A 慢断玻璃保险丝”**，不可按错误形状选座。
- [Yaesu FT2DR/DE 官方手册](https://yaesu.com/Files/DFDF4D53-1B78-7375-E6C7A6E4B192BE13/FT2DR_DE_EH060M203_1608Y-EM-1.pdf) 指定 E-DC-6；[FT2D 兼容的 E-DC-6 商品参考](https://www.passion-radio.com/yaesu-handheld/edc6-1322.html)。最终仍需万用表测插头真实极性，绝不能凭型号推断引脚接法。

## B. 成本底线（非正式报价）

两块核心成品模块按所见公开售价计算：**$5.95（#5807）＋$24.99（Protect）＝约 US$30.94**，不含税费、运费。还需要电台电源尾线、F2 熔断器及保险丝座、洞洞板、线材和绝缘固定件；若手中没有 USB-C 线或测试仪器，成本会增加。

这路线节约的是**降压板和整套 PCB＋SMT 代贴片成本**，不能把 US$30.94 误当整机报价。**没有可靠的电子过压切断板时，这个直通方案只能使用电子负载测试，不能连 FT2D。**

### 为什么没有进一步用便宜保护板替代？

- PN Labs **Protect Nano #9801** 虽支持 12 V、最高 5 A 连续，但厂家写的**最大 DC 阻断电压仅 25 V**；用户的 TA3005U C1/C2 具备 **28 V PDO**，故不采用 Nano 来覆盖 PD 错档/故障的最坏情况。
- 常见“XH-M609 12–36 V 电池欠压保护板”重点是**欠压断电**，继电器切换速度和启动过冲无法从外形或营销参数证明，不把它当快速 OVP。
- 单个 15 V TVS 或 4 A 保险丝，都**不能单独保证** FT2D 端电压不超过 Yaesu 官方的 16 V 上限。
- 这是基于查得资料的**工程选型结论，不是对模块失效模式的实测认证**。若发现有更低价但明确支持 28 V 故障、高边快速截止、持续 3 A 且具可核实数据的成品 OVP，可在台架测试合格后替换。

## C. 首台组装（必须分段）

1. **不连接 FT2D，不连接 OVP**：先把 #5807 配置为 12 V、3 A，请求 TA3005U **C1 单口**，万用表和电子负载测试 12 V；测试其他电压档或误协商，立即断电。
2. **不连接 FT2D，单独测 OVP**：使用有电流限制的可调台式电源模拟 12→14.3→20 V，以及在能力与额定许可下模拟 28 V，示波器观察关断。不到实际 14.0–14.8 V 范围或关断瞬态出现 ≥16 V，保持 NO-GO。
3. **不连接 FT2D，连接完整链路**：`#5807 V+ → Protect IN+ → Protect OUT+ → FH2/F2 → 电子负载正极`；`#5807 GND → Protect IN−`、`Protect OUT− → 电子负载负极`。3 A 保持 30 min，记录温升与 0↔3 A 阶跃最小/最大电压。
4. **最后才制作 E-DC-6 输出**：F2 后红线为电台供电正极，黑线为负极，实际 E-DC-6 线序由万用表通断确定；所有端子与 XT60 加应力消除。要经过完整的 [TEST_PLAN_12V_DIRECT.md](TEST_PLAN_12V_DIRECT.md) 放行程序，才考虑接 FT2D 接收测试。

## D. 两个采购前确认

- **TA3005U 实物铭牌**：当前仅收到商品规格截图；请确认设备底部印着 TA3005U，C1/C2 单口确实包含 `12V⎓3A`。
- **已有物料**：若你已经有 E-DC-6 尾线、保险丝座、USB-C 线、电子负载或示波器，应先登记，免得重复购买。

本清单既不代表任何商城下单成功，也不会改变嘉立创原 5 片 PCB 待付款订单；Rev B 原工程继续保留。
