# FT2D Rev B：STUSB4500 NVM 与首板安全上电方案

**性质：投板前必须落实的工序方案，不是已经完成的烧录/性能测试。**

## 为什么不能直接用 STUSB4500 出厂默认值

ST 官方 `STUSB4500` 数据表 5.2 节：出厂默认 `PDO1=5V/1.5A`、
`PDO2=15V/1.5A`、`PDO3=20V/1.0A`；`POWER_ONLY_ABOVE_5V` 默认为 **0**，
即 `VBUS_EN_SNK` 在普通 5V 附着时也可使能。**只靠器件出厂设置，不能得到
本板目标的 20V/3A 输入条件。**

参见：

- [ST STUSB4500 官方数据手册，第 5.2 节](https://www.st.com/resource/en/datasheet/stusb4500.pdf)
- [ST 官方 STSW-STUSB002 GUI](https://www.st.com/en/embedded-software/stsw-stusb002.html)
- [ST 官方 UM2650 软件编程指南](https://www.st.com/resource/en/user_manual/um2650-the-stusb4500-software-programing-guide-stmicroelectronics.pdf)

## 首板建议 NVM 目标配置（尚未烧入、尚未读取验证）

| 字段 | 建议目标值 | 理由 |
| --- | --- | --- |
| `SNK_PDO_NUMB` | **2** | 只保留必需的 5V PDO1 和工作用 20V PDO2，避免 15V 回退后负载供电不可预期 |
| `PDO1` | `5V / 1.5A` | USB PD 必有第一个 5V PDO；**不供 FT2D 使用** |
| `PDO2` | `20V / 3.0A` | 对应 60W 等级 PD 电源；本板输出 12.5V×3A=37.5W |
| `POWER_ONLY_ABOVE_5V` | **1** | ST 官方说明：仅成功建立 PDO2/PDO3 的显式合同才使能 `VBUS_EN_SNK`，可避免 5V 默认路径打开 |
| 其他 PDO/NVM 字段 | 先保留原厂值，再复核 OVP/UVLO/输入时序 | 避免未经审查地整块复制他人 NVM 镜像 |

注意：**这是配置目标表，不是有效的 NVM 原始二进制。** 需要用 ST 官方工具对具体器件
写入、读回、断电重新上电验证；不要把一次 I²C 寄存器临时写入当成永久写 NVM。
选择 20V PD 电源额定至少 3A（60W）；65W 适配器往往提供 20V/3.25A，仍须读取实际合同。

## J2 触点网络核对（由 KiCad Rev B XML netlist 导出）

| J2 焊盘号 | 网络 | 操作警告 |
| --- | --- | --- |
| 1 | `/GND` | 编程器公共地 |
| 2 | `/SCL` | I²C 时钟，R2=4.7k 上拉至板上 `/PD_2V7` |
| 3 | `/SDA` | I²C 数据，R3=4.7k 上拉至板上 `/PD_2V7` |
| 4 | `/PD_2V7` | **器件内部 2.7V 电源输出/逻辑参考；禁止由编程器强行灌入 3.3V/5V** |
| 5 | `/VBUS_RAW` | **危险：可出现 USB PD 20V，绝对不能连到编程器 3.3V/5V 电源脚** |
| 6 | `/PD_RESET` | STUSB4500 复位信号；注意有效电平、外部电路和电压范围 |

**务必在 KiCad 和实体焊盘上确认 Pin 1 朝向。** J2 是裸 PCB 编程焊盘而非可直接插线的标准排针。
本板已经自带 SCL/SDA → `/PD_2V7` 的上拉，不要接入 5V I²C 转接器；
使用与 2.7V 电平兼容的开漏/双向电平适配器，外接编程器不得反向供电。

## 操作顺序（板厂 SMT 完毕之后，且**不连接电台**）

1. 万用表断电检查 J1 VBUS/GND、J3 VOUT/GND 有无硬短路，实测 J2 焊盘号/电平。
2. 使用**限流 5V Type-C 电源**单独给板供电，复核 U1 `/PD_2V7`、I²C 通信；
   不要加载 J3，未经配置的 eFuse/Buck 状态不可预期。
3. ST 官方 GUI（STSW-STUSB002）配合支持的 Nucleo I²C 接口/工装，**先备份原 NVM**，
   再写入上述目标设置；读回比对，完全断电后再读回。
4. 换用有 USB PD 20V/≥3A 固定 PDO 的合规适配器，先用独立 PD 分析仪或 I²C
   `RDO` 合同寄存器确认实际协商 **20V、≥3A**；如果只得到 5V/15V/20V1A，立即停止 J3 加载。
5. J3 连接可调电子负载，依序 0A→0.5A→1A→2A→3A；
   测输出稳态目标 12.5V、纹波、压降、启动/拔插浪涌和热像温升；
   超过 13.0V、持续重启、过热、异常噪声即断电排查。至少保持 3A 15 分钟
   观测 U2/U3/L1/F1/C18/C23 与铜箔/接头热点，记录环境温度。
6. 在安全电子负载台完成短路、低电压、PD 断连、电台发射脉冲模拟及 RF 干扰检查；
   最后才接 FT2D，**先用万用表确认 J3 pin1=`+VOUT`、pin2=`GND` 及整根线束的电台端极性**。

本计划不能代替首件热验证。最终 NVM 参数、读回记录、JLC 实贴方向和测试数据须在
`RELEASE_APPROVAL` 工程评审后归档；不得以 `ERC/DRC=0` 视为上述事项完成。
