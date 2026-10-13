# 销售漏斗分析（模拟 CRM 线索）

用 **合成 CRM 线索表** 演示漏斗转化、销售达成与线索来源归因：Pandas 聚合 + Matplotlib/Seaborn 出图。

> **数据说明**：`data/crm_leads.csv` 由 `generate_data.py` 随机生成（默认约 2000 条）。阶段转化率、来源成交率、销售配额完成度都来自这套模拟数据，**不是**真实公司 CRM 导出。适合讲清漏斗/归因分析思路，不宜当作真实业务结论。

## 要解决什么问题

销售团队常用表格盯漏斗，难以及时看到「哪一阶段掉得最狠、哪条线索渠道更值钱、谁离配额最远」。本仓库把这三类视图做成一次可复现的脚本，方便作品集展示；真实落地需要接 CRM API/导出，并加上权限与数据刷新。

## 分析模块

| 模块 | 做法 | 局限 |
|------|------|------|
| 漏斗转化 | 按阶段计人数与转化率 | 阶段顺序与概率写在生成脚本里 |
| 销售达成 | 成交率、金额 vs 年度配额 | 配额为脚本内写死假设（如每人 100 万） |
| 来源归因 | 各渠道成交率与均单 | 渠道名与概率为演示设定 |
| 季度趋势 | 按季聚合成交量/金额 | 季节波动来自随机过程，无真实旺季含义 |

## 项目结构

```
sales-funnel-analysis/
├── generate_data.py   # 合成 crm_leads.csv
├── analysis.py        # 漏斗 / 达成 / 归因 / 出图
├── requirements.txt
├── data/
│   └── crm_leads.csv
└── output/
    └── sales_analysis_report.png
```

## 环境与运行

需要 Python 3.10+。

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python generate_data.py
python analysis.py
```

## 样例结论怎么读

README 或图表里出现的转化率、均单、人名表现，都会随 `generate_data.py` 的随机种子变化。把它们当作「管道能算、图能画」的示例即可；面试时主动说明数据是模拟的，再讲你会如何换成真实 CRM 字段与口径。

## 面试可讲的点

- 漏斗要先对齐业务阶段定义（含不算转化的无效状态）。
- 归因别只看成交率：还要看量、均单、销售成本与周期。
- 达成率分析要区分「机会质量」与「执行力」，避免只点名低成交率销售。
- 生产环境：定时拉取、口径文档、异常阶段占比告警。

## 技术栈

Python · Pandas · NumPy · Matplotlib · Seaborn

## License

MIT（演示代码；合成数据可自由改参数重跑）。
