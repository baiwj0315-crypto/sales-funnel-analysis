import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib import rcParams
import warnings
warnings.filterwarnings('ignore')

# 中文字体
rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False

df = pd.read_csv('data/crm_leads.csv')

STAGE_ORDER = ['未接触', '已联系', '已演示', '已发方案', '谈判中', '成交']
COLORS = ['#e8f4f8', '#b8ddf0', '#7ec8e3', '#4a9eca', '#1f6f9f', '#0d3f6e']
ACCENT = '#1f6f9f'

# ── 1. 漏斗转化分析 ─────────────────────────────────────────────────────────────

def get_funnel_counts(data):
    """每个阶段及以上的线索数（漏斗累计）"""
    counts = []
    for stage in STAGE_ORDER:
        idx = STAGE_ORDER.index(stage)
        reached = data[data['stage'].apply(lambda s: STAGE_ORDER.index(s) >= idx)]
        counts.append(len(reached))
    return counts

counts = get_funnel_counts(df)
conv_rates = [counts[i] / counts[i-1] * 100 if i > 0 else 100 for i in range(len(counts))]

print("=" * 55)
print("【漏斗转化分析】")
print("=" * 55)
for i, stage in enumerate(STAGE_ORDER):
    bar = '█' * int(counts[i] / counts[0] * 30)
    rate = f"(上一步转化率: {conv_rates[i]:.1f}%)" if i > 0 else ""
    print(f"  {stage:<6} {counts[i]:>5} 人  {bar:<30} {rate}")

# 最大流失点
losses = [counts[i-1] - counts[i] for i in range(1, len(counts))]
max_loss_idx = losses.index(max(losses)) + 1
print(f"\n  [!] 最大流失节点：{STAGE_ORDER[max_loss_idx-1]} -> {STAGE_ORDER[max_loss_idx]}"
      f"（流失 {losses[max_loss_idx-1]} 人，转化率 {conv_rates[max_loss_idx]:.1f}%）")

# ── 2. 销售人员达成率分析 ──────────────────────────────────────────────────────

print("\n" + "=" * 55)
print("【销售人员达成率分析】")
print("=" * 55)

# 配额（模拟：每人年度目标 100 万）
QUOTA = 1_000_000
rep_stats = df.groupby('sales_rep').agg(
    leads=('lead_id', 'count'),
    closed=('is_closed_won', 'sum'),
    revenue=('amount', 'sum')
).reset_index()
rep_stats['win_rate'] = rep_stats['closed'] / rep_stats['leads'] * 100
rep_stats['quota_pct'] = rep_stats['revenue'] / QUOTA * 100
rep_stats = rep_stats.sort_values('revenue', ascending=False)

for _, row in rep_stats.iterrows():
    status = '[达成]' if row['quota_pct'] >= 100 else '[未达]'
    print(f"  {row['sales_rep']}  成交率{row['win_rate']:.1f}%  "
          f"金额¥{row['revenue']/10000:.1f}万  配额{row['quota_pct']:.0f}%  {status}")

# ── 3. 季度趋势 ────────────────────────────────────────────────────────────────

print("\n" + "=" * 55)
print("【季度成交趋势】")
print("=" * 55)
q_stats = df[df['is_closed_won'] == 1].groupby('quarter').agg(
    deals=('lead_id', 'count'),
    revenue=('amount', 'sum')
).reset_index()
for _, row in q_stats.iterrows():
    print(f"  {row['quarter']}  成交 {row['deals']:>3} 单  ¥{row['revenue']/10000:.1f}万")

# ── 4. 归因分析：哪个来源质量最高 ─────────────────────────────────────────────

print("\n" + "=" * 55)
print("【线索来源归因分析】")
print("=" * 55)
src_stats = df.groupby('source').agg(
    leads=('lead_id', 'count'),
    closed=('is_closed_won', 'sum'),
    revenue=('amount', 'sum')
).reset_index()
src_stats['win_rate'] = src_stats['closed'] / src_stats['leads'] * 100
src_stats['avg_deal'] = src_stats.apply(
    lambda r: r['revenue'] / r['closed'] if r['closed'] > 0 else 0, axis=1)
src_stats = src_stats.sort_values('win_rate', ascending=False)

for _, row in src_stats.iterrows():
    print(f"  {row['source']:<8}  线索{row['leads']:>4}条  "
          f"成交率{row['win_rate']:.1f}%  均单¥{row['avg_deal']/10000:.1f}万")

# ── 5. 可视化输出 ──────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('销售CRM数据分析报告 2024', fontsize=16, fontweight='bold', y=0.98)

# 图1：漏斗图
ax1 = axes[0, 0]
max_w = 0.9
widths = [max_w * c / counts[0] for c in counts]
y_positions = list(range(len(STAGE_ORDER)))[::-1]
for i, (stage, count, width, color) in enumerate(zip(STAGE_ORDER, counts, widths, COLORS)):
    y = y_positions[i]
    ax1.barh(y, width, color=color, edgecolor='white', height=0.6)
    ax1.text(width + 0.01, y, f'{count}人 ({count/counts[0]*100:.1f}%)',
             va='center', fontsize=9)
    ax1.text(0.005, y, stage, va='center', fontsize=10, color='white' if i >= 3 else '#333')
ax1.set_xlim(0, 1.15)
ax1.set_yticks([])
ax1.set_xticks([])
ax1.set_title('销售漏斗转化', fontweight='bold')
for spine in ax1.spines.values():
    spine.set_visible(False)

# 图2：销售人员达成率
ax2 = axes[0, 1]
colors_bar = ['#2ecc71' if q >= 100 else '#e74c3c' for q in rep_stats['quota_pct']]
bars = ax2.bar(rep_stats['sales_rep'], rep_stats['quota_pct'], color=colors_bar, alpha=0.85)
ax2.axhline(100, color='#333', linestyle='--', linewidth=1.2, label='配额目标')
ax2.set_title('销售人员配额达成率 (%)', fontweight='bold')
ax2.set_ylabel('%')
ax2.tick_params(axis='x', rotation=30)
for bar, val in zip(bars, rep_stats['quota_pct']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val:.0f}%', ha='center', fontsize=8)
green_patch = mpatches.Patch(color='#2ecc71', label='已达成')
red_patch = mpatches.Patch(color='#e74c3c', label='未达成')
ax2.legend(handles=[green_patch, red_patch], fontsize=8)

# 图3：季度成交金额趋势
ax3 = axes[1, 0]
ax3.plot(q_stats['quarter'], q_stats['revenue'] / 10000, marker='o',
         color=ACCENT, linewidth=2.5, markersize=8)
ax3.fill_between(q_stats['quarter'], q_stats['revenue'] / 10000, alpha=0.15, color=ACCENT)
for _, row in q_stats.iterrows():
    ax3.text(row['quarter'], row['revenue']/10000 + 5,
             f'¥{row["revenue"]/10000:.0f}万', ha='center', fontsize=9)
ax3.set_title('季度成交金额趋势', fontweight='bold')
ax3.set_ylabel('金额（万元）')
ax3.grid(axis='y', alpha=0.3)
for spine in ['top', 'right']:
    ax3.spines[spine].set_visible(False)

# 图4：线索来源质量矩阵（成交率 vs 线索量）
ax4 = axes[1, 1]
scatter = ax4.scatter(
    src_stats['leads'], src_stats['win_rate'],
    s=src_stats['avg_deal'] / 500, alpha=0.7,
    c=src_stats['win_rate'], cmap='Blues', vmin=5, vmax=25
)
for _, row in src_stats.iterrows():
    ax4.annotate(row['source'],
                 (row['leads'], row['win_rate']),
                 textcoords='offset points', xytext=(6, 4), fontsize=9)
ax4.set_xlabel('线索数量')
ax4.set_ylabel('成交率 (%)')
ax4.set_title('线索来源质量矩阵\n（气泡大小=平均单价）', fontweight='bold')
ax4.grid(alpha=0.3)
for spine in ['top', 'right']:
    ax4.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig('output/sales_analysis_report.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.show()
print("\n[完成] 图表已保存到 output/sales_analysis_report.png")
