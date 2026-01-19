# Intel 近期 CPU 架构与命名体系梳理

本文的目标是把几条线“对齐”——代际（营销口径）、Lake（平台/代号）、桌面 vs 笔记本（低压/标压）、以及常见型号到底怎么读。

结论先说：从 10 代开始，“同一代”里并行多条 Lake 是常态；到 2023–2024 又叠加了品牌重命名（Core / Core Ultra / Series），因此直觉上会觉得“越来越乱”。

## 两个核心概念：代（Gen）≠ Lake（平台代号）

- **“第 10/11/12/13/14 代”**更多是消费者熟悉的营销代际。
- **“Ice Lake / Comet Lake / Tiger Lake / Rocket Lake / Alder Lake / Raptor Lake / Arrow Lake …”**是平台代号（Code Name）。

最关键的实操建议：当你看到具体型号，最靠谱的“终局答案”来自 Intel 产品规格页（ARK / Intel.com Specifications）里的两行

- **Code Name（Products formerly …）**
- **Vertical Segment（Desktop / Mobile）**

例如同为“10 代 i7”：
- i7-1065G7：Code Name = Ice Lake；Vertical Segment = Mobile。
- i7-10710U：Code Name = Comet Lake；Vertical Segment = Mobile。

## “命名越来越不清晰”，根源在哪里？

### 10 代的“分裂式命名”
10 代时期，你会同时遇到两种风格：
- **1065G7** 这种“尾部带 Gx”的轻薄本型号，常对应 10nm 的 Ice Lake。
- **10710U / 10750H / 10700K** 这种更传统的 10xxx + 后缀（U/H/K）型号，常对应 14nm 的 Comet Lake。

这会导致“同为 10 代 i7，但架构、制程、核显侧重点完全不同”。

### 2023 起的品牌重构：Core / Core Ultra + Series
Intel 在 Meteor Lake 上线前宣布了重大的客户端品牌更新，引入 **Intel Core Ultra** 与 **Intel Core** 两个品牌层级，并以新的标识体系帮助区分“最新技术”和“主流产品”。

行业报道也指出：新体系会弱化/移除过去用户非常熟悉的“Core i3/i5/i7/i9”的“i”字样（至少在对外传播中会更突出 Core / Core Ultra 的分层）。

与此同时，Intel 又用 **Series 1 / 2 / 3** 来推动 Core Ultra 的代际滚动（Meteor Lake ≈ Series 1；Arrow/Lunar ≈ Series 2；Panther Lake ≈ Series 3）。

![Press Kit: Intel Core Ultra Processors (Series 2) - Newsroom](http://public.file.lvshuhuai.cn/images\newsroom-arl-infographic-2v2-1024x576.jpg)

## 一张总表：代、年份、Lake、桌面/笔记本（低压/标压）、典型型号

说明：
- “年份”按**集中发布/上市窗口**理解（会跨季度甚至跨年）。
- “低压/标压”是市场习惯用语。严格功耗请以 Intel 规格页的 **Processor Base Power / Maximum Turbo Power** 为准（同一颗 CPU 也会被 OEM 配不同功耗档）。
- “典型型号”是帮助建立直觉的例子，不是完整 SKU 清单。

| 代/系列（消费者常说法）                    |  主要年份 | Lake（平台代号）                                   | 桌面（例）                                                   | 笔记本低压（例）                                             | 笔记本标压（例）                                             | 关键点                                                       |
| ------------------------------------------ | --------: | -------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 10 代（并行多线）                          | 2019–2020 | Ice Lake（移动） + Comet Lake（桌面/移动）         | i7-10700K：Comet Lake，Desktop，Q2’20。                      | i7-1065G7：Ice Lake，Mobile，Q3’19。；i7-10710U：Comet Lake，Mobile。 | i7-10750H（常见 45W 档）属于 Comet Lake-H（思路同上，查 Code Name）。 | 同代不同 Lake 是“命名混乱”的起点。                           |
| 11 代（桌面与移动分家明显）                | 2020–2021 | Tiger Lake（移动） + Rocket Lake-S（桌面）         | （11 代桌面主线是 Rocket Lake-S，消费者常见如 11700K/11900K） | i7-1165G7 属于 11 代移动端主流（同类逻辑：看 Code Name/Segment）。 | 轻薄高性能/游戏本会出现 Tiger Lake-H 系列（例如 H35 形态），依然应以规格页为准。 | 这一代“桌面 Rocket / 移动 Tiger”的分离很典型。               |
| 12 代                                      | 2021–2022 | Alder Lake                                         | （典型：12900K 系）                                          | U / P 系列覆盖轻薄本                                         | H / HX 覆盖游戏本与移动工作站                                | Intel 在 2021-10-27 公告 12 代桌面解锁版，11-04 广泛开售。   |
| 13 代                                      | 2022–2023 | Raptor Lake                                        | 13 代桌面 K 系 2022-10-20 起上市。                           | （同代移动端会有 P/U 等形态，具体 SKU 以机型为准）           | （同代移动端也有 HX/H 等形态）                               | 13 代桌面发布时间与渠道供货时间有明确公告口径。              |
| 14 代（旧 Core i 命名末期）                | 2023–2024 | Raptor Lake（Refresh/延续）                        | i7-14700K：Products formerly Raptor Lake，Desktop，Launch Q4’23。 | （轻薄本侧开始更常与“Core / Core Ultra”并行出现在市场叙事中） | i9-14900HX：Products formerly Raptor Lake，Launch Q1’24。    | 14 代桌面与移动 HX 的上市窗口不同步，且与新品牌叙事重叠。    |
| Core Ultra Series 1（移动首发）            | 2023–2024 | Meteor Lake                                        | —                                                            | U 系（轻薄）                                                 | H 系（性能）                                                 | Intel 在 2023-12-14 发布 Core Ultra 移动处理器家族（首代 AI PC 叙事）。 |
| Core Ultra Series 2（两条最重要分支）      |      2024 | Lunar Lake（200V，移动）+ Arrow Lake（200S，桌面） | 285K：Series 2，Code Name = Arrow Lake，Desktop。            | 200V（Lunar Lake）：Intel Press Kit 明确 200V = Lunar Lake，并在 2024-09-03 的 Launch Event 引入。 | （性能本/游戏本的 Arrow Lake 移动线在后续集中出货）          | Series 2 不是单一平台：同属 Series 2，但 200V 与 200S 面向完全不同的笔记本/桌面。 |
| Core Ultra Series 2（移动性能/主流线出货） |      2025 | Arrow Lake（200U/200H/200HX，移动）                | （桌面仍属 200S）                                            | 265H：Series 2，Code Name = Arrow Lake，Mobile（16 核：6P+8E+…）。 | 200HX 同属 Series 2，面向更高性能移动平台                    | Intel 官方商业端信息指出：200U/200H/200HX/200S 系统将于 2025 年 3 月下旬出货。 |
| Core Ultra Series 3                        |      2026 | Panther Lake                                       | （以移动为主的节奏）                                         | —                                                            | —                                                            | Intel CES 2026 公告：Series 3 为首个基于 Intel 18A 的平台；预售 2026-01-06，开售 2026-01-27。 |

## “低压/标压/桌面”如何快速判断（读后缀 + 看 Segment）

### 旧 Core i（10–14 代常见）后缀的直觉
- **K**：桌面高性能/可超频倾向（典型 i7-10700K）。
- **U**：笔记本低压/轻薄本常见（典型 i7-10710U）。
- **H / HX**：笔记本高性能（游戏本/移动工作站常见，HX 通常更激进）。

但注意：后缀只能给你“形态直觉”，最终功耗（如 15W、28W、45W、55W）要看规格页或具体整机设定。

### Core Ultra 的后缀与“Series”的组合更关键
- **Series 1（Meteor Lake）**：以移动为主，U/H 双线。 
- **Series 2**：至少包含  
  - **200V（Lunar Lake，移动超轻薄取向）**
  - **200S（Arrow Lake，桌面）**
  - **Arrow Lake 移动线（例如 265H）**
- **Series 3（Panther Lake）**：2026-01 开售节奏明确。

<img src="http://public.file.lvshuhuai.cn/images\newsroom-intel-core-ultra-200v-series-6.jpg" alt="New Core Ultra Processors Deliver Breakthrough Performance, Efficiency ..." style="zoom:50%;" />