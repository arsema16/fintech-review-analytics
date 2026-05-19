"""
High-Quality Visualizations for Final Report
Publication-ready charts with proper sizing and labels
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set high-quality figure parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 11

# Load data
df = pd.read_csv('data/final_analytics.csv')

# ============================================
# CHART 1: Sentiment Distribution (Large, Clear)
# ============================================
fig1, ax1 = plt.subplots(figsize=(12, 8))
sentiment_counts = df['sentiment_label'].value_counts()
colors = ['#2ecc71', '#e74c3c', '#95a5a6']
bars = ax1.bar(sentiment_counts.index, sentiment_counts.values, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_title('Sentiment Distribution Across All Reviews', fontsize=18, fontweight='bold', pad=20)
ax1.set_xlabel('Sentiment', fontsize=14)
ax1.set_ylabel('Number of Reviews', fontsize=14)
ax1.tick_params(axis='both', labelsize=12)

# Add value labels on bars
for bar, val in zip(bars, sentiment_counts.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
             f'{val}\n({val/len(df)*100:.1f}%)', ha='center', va='bottom', 
             fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('report_chart_1_sentiment.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 1 saved: report_chart_1_sentiment.png')

# ============================================
# CHART 2: Average Rating by Bank (Clear, Large)
# ============================================
fig2, ax2 = plt.subplots(figsize=(10, 7))
avg_ratings = df.groupby('bank')['rating'].mean().sort_values()
bank_names = [b.split()[0] for b in avg_ratings.index]
colors_bar = ['#e74c3c', '#3498db', '#2ecc71']
bars = ax2.bar(bank_names, avg_ratings.values, color=colors_bar, edgecolor='black', linewidth=2)
ax2.set_ylim(0, 5)
ax2.set_ylabel('Average Rating (Stars)', fontsize=14)
ax2.set_title('Average Rating by Bank', fontsize=18, fontweight='bold', pad=20)
ax2.tick_params(axis='both', labelsize=12)

# Add value labels
for bar, val in zip(bars, avg_ratings.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, 
             f'{val:.2f}★', ha='center', va='bottom', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('report_chart_2_avg_rating.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 2 saved: report_chart_2_avg_rating.png')

# ============================================
# CHART 3: Rating Distribution by Bank (Histogram)
# ============================================
fig3, ax3 = plt.subplots(figsize=(12, 7))
banks = df['bank'].unique()
colors_hist = ['#2ecc71', '#e74c3c', '#3498db']
for i, bank in enumerate(banks):
    bank_data = df[df['bank'] == bank]['rating']
    ax3.hist(bank_data, alpha=0.7, bins=[1, 2, 3, 4, 5, 6], 
             label=bank.split()[0], color=colors_hist[i], edgecolor='black', linewidth=1)
ax3.set_title('Rating Distribution by Bank', fontsize=18, fontweight='bold', pad=20)
ax3.set_xlabel('Star Rating', fontsize=14)
ax3.set_ylabel('Number of Reviews', fontsize=14)
ax3.set_xticks([1.5, 2.5, 3.5, 4.5, 5.5])
ax3.set_xticklabels(['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])
ax3.legend(fontsize=12, loc='upper left')
ax3.tick_params(axis='both', labelsize=12)
plt.tight_layout()
plt.savefig('report_chart_3_rating_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 3 saved: report_chart_3_rating_distribution.png')

# ============================================
# CHART 4: Sentiment by Bank (Stacked Bar)
# ============================================
fig4, ax4 = plt.subplots(figsize=(12, 7))
sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment_label'])
sentiment_by_bank.index = [idx.split()[0] for idx in sentiment_by_bank.index]
sentiment_by_bank.plot(kind='bar', stacked=True, ax=ax4, color=['#2ecc71', '#e74c3c', '#95a5a6'], 
                       edgecolor='black', linewidth=1)
ax4.set_title('Sentiment Distribution by Bank', fontsize=18, fontweight='bold', pad=20)
ax4.set_xlabel('Bank', fontsize=14)
ax4.set_ylabel('Number of Reviews', fontsize=14)
ax4.legend(title='Sentiment', fontsize=11, title_fontsize=12)
ax4.tick_params(axis='both', labelsize=12)
ax4.tick_params(axis='x', rotation=0)

# Add value labels on bars
for container in ax4.containers:
    ax4.bar_label(container, label_type='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('report_chart_4_sentiment_by_bank.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 4 saved: report_chart_4_sentiment_by_bank.png')

# ============================================
# CHART 5: Theme Distribution (Horizontal Bar)
# ============================================
fig5, ax5 = plt.subplots(figsize=(12, 7))
theme_counts = df['identified_theme'].value_counts().head(6)
theme_colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(theme_counts)))[::-1]
bars = ax5.barh(range(len(theme_counts)), theme_counts.values, color=theme_colors, edgecolor='black', linewidth=1.5)
ax5.set_yticks(range(len(theme_counts)))
ax5.set_yticklabels(theme_counts.index, fontsize=12)
ax5.set_xlabel('Number of Reviews', fontsize=14)
ax5.set_title('Most Frequent Themes in User Reviews', fontsize=18, fontweight='bold', pad=20)
ax5.invert_yaxis()
ax5.tick_params(axis='both', labelsize=12)

# Add value labels
for bar, val in zip(bars, theme_counts.values):
    ax5.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
             f'{val}', va='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('report_chart_5_themes.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 5 saved: report_chart_5_themes.png')

# ============================================
# CHART 6: One-Star vs Five-Star Comparison
# ============================================
fig6, ax6 = plt.subplots(figsize=(10, 7))
bank_labels = ['CBE', 'BOA', 'Dashen']
five_star = [271, 215, 257]
one_star = [57, 104, 73]
x = np.arange(len(bank_labels))
width = 0.35

bars1 = ax6.bar(x - width/2, five_star, width, label='5-Star Reviews', color='#2ecc71', edgecolor='black')
bars2 = ax6.bar(x + width/2, one_star, width, label='1-Star Reviews', color='#e74c3c', edgecolor='black')

ax6.set_ylabel('Number of Reviews', fontsize=14)
ax6.set_title('Promoters (5-Star) vs Detractors (1-Star)', fontsize=18, fontweight='bold', pad=20)
ax6.set_xticks(x)
ax6.set_xticklabels(bank_labels, fontsize=12)
ax6.legend(fontsize=12)
ax6.tick_params(axis='both', labelsize=12)

for bars in [bars1, bars2]:
    for bar in bars:
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, 
                f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('report_chart_6_promoters_detractors.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ Chart 6 saved: report_chart_6_promoters_detractors.png')

print('\n' + '='*50)
print('✅ All 6 publication-ready charts created!')
print('='*50)
print('\nFiles saved:')
print('  - report_chart_1_sentiment.png')
print('  - report_chart_2_avg_rating.png')
print('  - report_chart_3_rating_distribution.png')
print('  - report_chart_4_sentiment_by_bank.png')
print('  - report_chart_5_themes.png')
print('  - report_chart_6_promoters_detractors.png')
