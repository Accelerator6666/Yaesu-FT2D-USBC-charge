# Rev B 关键 SMT 器件替代评审（2026-10-26）

**仅供采购/工程校对；没有签字的料号不能进入 `BOM_APPROVED.csv`。** 嘉立创物料目录实时库存/装配费和替代件批次须在订单确认。当前已选定 J1 C165948、L1 C53463013；此页跟踪最容易阻碍 SMT 的 F1、C18、C23。

| 位号 | 原设计 / 原电气约束 | 嘉立创候选 | 是否更新 PCB/BOM | 放行结论 |
| --- | --- | --- | --- | --- |
| **F1** | Littelfuse `1206SFS300F/32`，1206、3 A、32 V、50 A 分断、1.20 A²s I²t、标称 0.032 Ω、**−55～125°C** | Littelfuse **`0468003.NRHF` C41342**，1206、3 A、32 V、50 A、1.27 A²s I²t、约 0.0195 Ω、**−55～90°C** | **未更新**：仍为原型，板上 1206 焊盘尺寸可作为初步候选 | **待审**：3 A 工作电流对熔丝额定值/温度降额及浪涌时间、电流预期需复核；90°C 等级下降，不能用 I²t 接近代替工程验证 |
| **C18** | Panasonic **`EEH-ZL1V470R`**，47 µF/35 V、ESR 60 mΩ @100 kHz，原尺寸 **D5×5.8 mm**，**135°C**；约 550 mA 高频纹波（温度条件见厂家数据） | Panasonic **`EEH-ZA1V470P` C178639**，47 µF/35 V、**ESR 60 mΩ @100 kHz**、**1.3 A @100 kHz**，**D6.3×5.8 mm**，**105°C / 10000h** | **已更新到 Rev B 候选 PCB/原理图/符号库**：C18 的 6.3 mm 焊盘左移 0.5 mm；极性 pad1=`/VBUS_SW`、pad2=`/GND`；ERC0、DRC0、unconnected0、Parity0。新 KiCad BOM/CPL 已同步 | **待审**：温度降低 30°C，须按最高环境、相邻 Q1/U2 发热和实际输入纹波复核；原厂推荐 land pattern 和 JLC 取放中心/极性预览仍待人工确认 |
| **C23** | APAQ `250AVHT221M0608`，220 µF/25 V，ESR **24 mΩ**，纹波电流与温度须按厂家表格理解，**D6.3×约7.5 mm / 125°C** | jieerrui **`MA25V220M6X8` C46550464**，220 µF/25 V、ESR **28 mΩ @100 kHz**、**2.9 A @100 kHz**、D6.3×L7.7 mm、**105°C** | **未更新**：保留原设计值，现有 `CP_Elec_6.3x7.7` 是几何候选、未完成原厂推荐焊盘实测 | **待审**：温度、ESR 和开关电源稳定性，输出纹波、电台射频干扰风险；不能未经验证直接标为等效 |

## 不通过的替代项

- **C18 `RX1V470M0506` / C25170683（JARSON）**：虽然也是 47 µF、35 V、D5×5.8 mm，但 ESR **360 mΩ**、纹波仅 **240 mA**，与原 Panasonic 的 60 mΩ / 高纹波能力差别过大。**明确不采用**。

## 仍需要的人工/实验结果

1. F1 3 A 保险丝在 USB 20 V 输入最大电流、室温与最高环境温度的熔断曲线、冲击电流和温升。3 A 熔丝额定值不等于可长期在任意高温承受 3 A。
2. C18 从 135°C 到 105°C 的降额评估；近 Buck 大电流电容位置的实际热温升、输入电容纹波和等效 ESR/频率范围。
3. C23 输出聚合电容低 ESR 对 LM61460 反馈稳定、浪涌和纹波的影响。
4. 已整理 53/53 SMT **候选** C-code，见 `SMT_CANDIDATE_REVIEW.md`；还必须主动核对 10 µF/50 V 与 47 µF/25 V 1210 MLCC 的**厂家 DC bias 曲线与有效容值**、R12/R13 0.1% 的实得阻值/功率/温漂，以及 36 种候选在 **JLC SMT** 服务中的真实供货和装配兼容性。
5. J1 HRO USB-C 的 4 个屏蔽固定通孔能否由 JLC SMT 代贴片订单接受、是否需要插件/手焊；C18/C23 的极性及 U2/U3/Q1/J1/L1 的角度和吸嘴取放中心。

## 一手来源

- [Littelfuse 原 F1 1206SFS300F/32 datasheet](https://www.littelfuse.com/assetdocs/fuse-1206sfs300f-product-specification?assetguid=b5e41466-f419-4196-8c91-0a4a48ba1eb9)
- [Littelfuse 候选 F1 在 JLC C41342 页面](https://jlcpcb.com/partdetail/Littelfuse-0468003NRHF/C41342)（特性还须结合原厂完整熔断曲线）
- [Panasonic 原 C18 EEH-ZL1V470R](https://industrial.panasonic.com/ww/products/pt/hybrid-aluminum/models/EEHZL1V470R)
- [Panasonic 候选 C18 EEH-ZA1V470P](https://industrial.panasonic.com/ww/products/pt/hybrid-aluminum/models/EEHZA1V470P) 和 [JLC C178639](https://jlcpcb.com/partdetail/PANASONIC-EEHZA1V470P/C178639)
- [APAQ 原 C23 250AVHT221M0608](https://www.apaq.com.tw/en/product/250AVHT221M0608_AP-CON-SMD.html)
- [JLC 候选 C23 C46550464](https://jlcpcb.com/partdetail/jieerrui-MA25V220M6X8/C46550464)
- [JLC 被排除的 C18 C25170683](https://jlcpcb.com/partdetail/JARSON-47uF_20_35V/C25170683)

本表以 2026-10-26 检索的厂商公开参数为基准。动态库存、最小采购量、封装照片和 SMT 工艺兼容性仍按最终订单页面为准。
