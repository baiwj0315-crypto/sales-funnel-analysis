import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 2000  # 线索数量

# 销售人员
sales_reps = ['张伟', '李娜', '王芳', '刘洋', '陈静', '赵磊', '周敏', '吴强']

# 产品线
products = ['企业版', '专业版', '基础版']

# 行业
industries = ['制造业', '零售业', '金融业', '教育', '医疗', '互联网', '房地产']

# 线索来源
sources = ['官网表单', '电话外呼', '转介绍', '市场活动', '社交媒体']

start_date = datetime(2024, 1, 1)

def random_date(start, days_range):
    return start + timedelta(days=random.randint(0, days_range))

leads = []
for i in range(N):
    lead_date = random_date(start_date, 364)
    rep = random.choice(sales_reps)
    product = random.choice(products)
    industry = random.choice(industries)
    source = random.choice(sources)

    # 各阶段转化概率（模拟真实漏斗）
    contacted = random.random() < 0.78
    demo = contacted and random.random() < 0.55
    proposal = demo and random.random() < 0.50
    negotiation = proposal and random.random() < 0.60
    closed_won = negotiation and random.random() < 0.45

    # 阶段
    if closed_won:
        stage = '成交'
    elif negotiation:
        stage = '谈判中'
    elif proposal:
        stage = '已发方案'
    elif demo:
        stage = '已演示'
    elif contacted:
        stage = '已联系'
    else:
        stage = '未接触'

    # 合同金额
    price_map = {'企业版': (50000, 200000), '专业版': (20000, 80000), '基础版': (5000, 30000)}
    lo, hi = price_map[product]
    amount = round(random.uniform(lo, hi), -2) if closed_won else 0

    # 销售周期（天）
    cycle_days = random.randint(7, 120) if closed_won else random.randint(1, 90)

    # 季度
    month = lead_date.month
    quarter = f"Q{(month - 1) // 3 + 1}"

    leads.append({
        'lead_id': f'L{i+1:04d}',
        'lead_date': lead_date.strftime('%Y-%m-%d'),
        'quarter': quarter,
        'sales_rep': rep,
        'product': product,
        'industry': industry,
        'source': source,
        'stage': stage,
        'amount': amount,
        'cycle_days': cycle_days if closed_won else None,
        'is_closed_won': int(closed_won)
    })

df = pd.DataFrame(leads)
df.to_csv('data/crm_leads.csv', index=False, encoding='utf-8-sig')
print(f"数据生成完成：{len(df)} 条线索")
print(df['stage'].value_counts())
print(f"\n总成交金额：{df['amount'].sum():,.0f} 元")
