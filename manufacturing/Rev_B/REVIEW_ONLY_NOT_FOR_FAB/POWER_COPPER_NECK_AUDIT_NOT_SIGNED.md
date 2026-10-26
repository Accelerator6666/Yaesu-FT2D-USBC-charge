# Rev B 功率铜箔狭颈复核（2026-10-26）

**结论：仍需工程复核，3 A 功率/温升 NOT APPROVED。** 本轮在全新安装的 KiCad 10.0.7 上再次运行：ERC **0**、DRC violations **0**、unconnected **0**、schematic parity **0**。静态规则全通过不等于 3 A 负载或电台供电安全保证。

## 重新核查的功率网

下面为 `engineering_tools/audit_power_copper_rev_b.py` 读取的当前 KiCad PCB 顶层填铜面积与原走线最小宽度；**原走线可能已被同网络宽铜部分覆盖**。

| 功率网 | F.Cu 填铜 mm² | 原走线最窄 mm | 本轮按 50 µm 栅格抽样得到的局部最窄铜截面 mm* | 抽样低于 1.0 mm 的点数* |
| --- | ---: | ---: | ---: | ---: |
| `/USB_VBUS` | 24.4 | 0.60 | 0.60 | 9/40 |
| `/VBUS_RAW` | 143.3 | 0.25 | 0.60 | 36/155 |
| `/VBUS_SW` | 109.5 | 0.60 | 0.60 | 11/170 |
| `/SW` | 14.6 | 0.60 | 0.95 | 2/20 |
| `/V12P5` | 174.3 | 0.30 | 0.30 | 2/160 |
| `/VOUT` | 79.4 | 0.30 | 0.30 | 17/75 |

*抽样算法 `engineering_tools/audit_power_necks_rev_b.py`：沿每段顶层走线在 15/35/50/65/85% 处横向扫描**同网络已填充铜皮**，并以原走线宽度作下限。它不计器件焊盘金属扩散、相邻合流、铜厚公差、内层并流、电流实际分布、孔热、接插件、器件本体电阻或热扩散，所以**不是完整最小截面证明或载流规格测试**。对填铜前后区域的数值只是供人工定位狭颈。

### 需要优先人工审查的实体位置

1. **U3 TPS259474A Pin 5、Pin 6 的输出关口（X≈107.75/108.25，Y≈43–45 mm）**：`/V12P5` 从 Pin 5 `(107.75,43.0)` 出来的 **0.2998 mm** 原线段长约 **2.85 mm**；`/VOUT` 从 Pin 6 `(108.25,43.0)` 出来的 **0.2998 mm** 原线段长约 **1.49 mm**。局部抽样仍见 0.3 mm 狭颈。**这是 eFuse 本体附近的功率输入/输出；不能仅以总填铜面积 174/79 mm² 判断 3 A 可用。**先核对 TI RPW 推荐焊盘、电流封装温升与散热，勿在 0.5 mm 引脚间距处盲目加宽短线造成桥连。
2. **J1 附近 USB 20 V 输入**：`/USB_VBUS` 在约 `(28.3,39.6)` 等位置仍有 0.6 mm 采样段；需要核对实际输入最大电流、连接器焊端和机械固定脚。
3. **`/VBUS_RAW` 与 `/VBUS_SW` 边界**：分别在 `(43.7,38.0)` 和 U2 `(79.55,44.7)` 处存在 0.6 mm 采样段，需结合输入电流、Q1/F1、U2 pin 8/12 真实电流分摊复核。
4. **`/SW` U2–L1**：约 `(81.61,44.3)` 处 0.95 mm；这是高速开关节点，面积不能简单追求越大越好。需按照 TI 的 EMI 与热环路布局原则共同优化。

## 工程解释和下一步

- 嘉立创 4 层板默认内层常为 **0.5 oz**，当前 Rev B 规划外层 **1 oz**；最终铜厚、堆叠、孔铜与订单配置要统一。面积不能替代电流通道最小宽度和铜厚。[JLC 官方 Copper Weight](https://jlcpcb.com/help/article/jlcpcb-copper-weight)
- 输入/输出完整电流路径、相邻 pads 与焊锡实际截面、回流/地过孔、器件封装降额、散热环境以及 I²R 压降/最大温升需要由工程审查确认。3 A 电台电源还应评估发射脉冲、线束电阻和短路瞬态。
- U2 Buck 高频输入回路特别依赖输入电容与 PGND 最小环路，而 SW 铜区过大会影响 EMI；参考 [TI LM61460-Q1 原厂 Layout 指南](https://www.ti.com/lit/ds/symlink/lm61460-q1.pdf)。U3 对应 [TI TPS25947 原厂规格](https://www.ti.com/lit/ds/symlink/tps25947.pdf)。
- 在明确电流路径、实际铜厚并复核 0.3 mm U3 pad escape 后才能决定加铜/加过孔、调整 U3 位置或对铜厚升档；**当前不得把检测报告视为制造签字**。

重跑命令（须用 KiCad 10 的 `/usr/bin/python3` / `pcbnew`）：

```sh
/usr/bin/python3 engineering_tools/audit_power_copper_rev_b.py hardware/Rev_B/FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb
/usr/bin/python3 engineering_tools/audit_power_necks_rev_b.py hardware/Rev_B/FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb
```
