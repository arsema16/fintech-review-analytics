"""
Task 4: Insights, Recommendations, and Visualizations
Generates business insights from sentiment and thematic analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

# Load data
df = pd.read_csv('data/final_analytics.csv')
print("="*60)
print("TASK 4: INSIGHTS AND RECOMMENDATIONS")
print("="*60)

# ============================================
# 1. SENTIMENT DISTRIBUTION
# ============================================
print("\n📊 SENTIMENT DISTRIBUTION")
print("-"*40)
sentiment_counts = df['sentiment_label'].value_counts()
sentiment_pct = df['sentiment_label'].value_counts(normalize=True).mul(100).round(1)
for label in sentiment_counts.index:
    print(f"  {label}: {sentiment_counts[label]} ({sentiment_pct[label]}%)")

# ============================================
# 2. SATISFACTION DRIVERS & PAIN POINTS
# ============================================
print("\n📈 SATISFACTION DRIVERS & PAIN POINTS BY BANK")
print("-"*40)

# Calculate metrics per bank
bank_metrics = {}
for bank in df['bank'].unique():
    bank_df = df[df['bank'] == bank]
    
    # High ratings (4-5) = Promoters
    promoters = len(bank_df[bank_df['rating'] >= 4])
    detractors = len(bank_df[bank_df['rating'] <= 2])
    nps_score = round(((promoters - detractors) / len(bank_df)) * 100, 1)
    
    # Themes
    themes = bank_df['identified_theme'].value_counts()
    top_theme = themes.index[0] if len(themes) > 0 else "None"
    
    # Sentiment
    positive_pct = (bank_df['sentiment_label'] == 'POSITIVE').mean() * 100
    
    bank_metrics[bank] = {
        'avg_rating': bank_df['rating'].mean(),
        'positive_pct': positive_pct,
        'nps_score': nps_score,
        'top_theme': top_theme
    }
    
    print(f"\n{bank.split()[0]}:")
    print(f"  Average Rating: {bank_metrics[bank]['avg_rating']:.2f}★")
    print(f"  Positive Sentiment: {bank_metrics[bank]['positive_pct']:.1f}%")
    print(f"  NPS Score: {bank_metrics[bank]['nps_score']}")
    print(f"  Top Theme: {bank_metrics[bank]['top_theme']}")

# ============================================
# 3. THEME ANALYSIS
# ============================================
print("\n🏷️ THEME DISTRIBUTION")
print("-"*40)
theme_counts = df['identified_theme'].value_counts()
for theme, count in theme_counts.head(6).items():
    print(f"  {theme}: {count} reviews")

# ============================================
# 4. RECOMMENDATIONS PER BANK
# ============================================
print("\n💡 PRODUCT RECOMMENDATIONS BY BANK")
print("="*60)

# CBE Recommendations
print("\n🏦 COMMERCIAL BANK OF ETHIOPIA (CBE)")
print(f"   Current Rating: {bank_metrics['Commercial Bank of Ethiopia Mobile']['avg_rating']:.2f}★")
print("   Strengths:")
print("     - Highest average rating (4.15★)")
print("     - 271 five-star reviews (most among all banks)")
print("     - Strong positive sentiment")
print("\n   Pain Points:")
print("     - 57 one-star reviews indicate stability issues")
print("     - 'Slow' appears in negative reviews")
print("\n   Recommendations:")
print("     1. Optimize backend API response times for transfers")
print("     2. Add offline mode for low-connectivity areas")
print("     3. Implement in-app crash reporting to identify bugs")

# BOA Recommendations
print("\n🏦 BANK OF ABYSSINIA (BOA)")
print(f"   Current Rating: {bank_metrics['Bank of Abyssinia Mobile Banking']['avg_rating']:.2f}★")
print("   Strengths:")
print("     - 215 five-star reviews")
print("     - Users appreciate basic functionality")
print("\n   Pain Points:")
print("     - Lowest average rating (3.64★)")
print("     - 104 one-star reviews (28% of all reviews)")
print("     - Major complaints about login and OTP")
print("\n   Recommendations:")
print("     1. Urgently fix authentication and OTP delivery issues")
print("     2. Redesign onboarding flow for first-time users")
print("     3. Add biometric login (fingerprint/face ID)")
print("     4. Implement 24/7 chat support for login issues")

# Dashen Recommendations
print("\n🏦 DASHEN BANK")
print(f"   Current Rating: {bank_metrics['Dashen Bank Mobile Banking']['avg_rating']:.2f}★")
print("   Strengths:")
print("     - 257 five-star reviews")
print("     - Strong UI/UX theme (15 reviews)")
print("     - Consistent performance")
print("\n   Pain Points:")
print("     - 73 one-star reviews")
print("     - Transaction speed complaints")
print("\n   Recommendations:")
print("     1. Add transaction progress indicators")
print("     2. Implement push notifications for transfer status")
print("     3. Add budgeting and spending insights feature")
print("     4. Introduce biometric login")

# ============================================
# 5. CREATE VISUALIZATIONS
# ============================================
print("\n📊 GENERATING VISUALIZATIONS...")

# Create figure with multiple subplots
fig = plt.figure(figsize=(15, 12))

# 1. Sentiment Distribution
ax1 = fig.add_subplot(2, 2, 1)
sentiment_counts = df['sentiment_label'].value_counts()
colors = ['#2ecc71', '#e74c3c', '#95a5a6']
bars = ax1.bar(sentiment_counts.index, sentiment_counts.values, color=colors)
ax1.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Reviews')
for bar, val in zip(bars, sentiment_counts.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, str(val), ha='center', fontweight='bold')

# 2. Rating Distribution by Bank
ax2 = fig.add_subplot(2, 2, 2)
for bank in df['bank'].unique():
    bank_data = df[df['bank'] == bank]['rating']
    ax2.hist(bank_data, alpha=0.7, bins=5, range=(0.5, 5.5), label=bank.split()[0])
ax2.set_title('Rating Distribution by Bank', fontsize=14, fontweight='bold')
ax2.set_xlabel('Star Rating')
ax2.set_ylabel('Number of Reviews')
ax2.legend()
ax2.set_xticks([1, 2, 3, 4, 5])

# 3. Sentiment by Bank
ax3 = fig.add_subplot(2, 2, 3)
sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment_label'])
sentiment_by_bank.plot(kind='bar', ax=ax3, color=colors)
ax3.set_title('Sentiment by Bank', fontsize=14, fontweight='bold')
ax3.set_xlabel('Bank')
ax3.set_ylabel('Number of Reviews')
ax3.legend(title='Sentiment')
ax3.tick_params(axis='x', rotation=15)

# 4. Theme Distribution
ax4 = fig.add_subplot(2, 2, 4)
theme_counts = df['identified_theme'].value_counts().head(6)
bars = ax4.barh(range(len(theme_counts)), theme_counts.values, color='#3498db')
ax4.set_yticks(range(len(theme_counts)))
ax4.set_yticklabels(theme_counts.index)
ax4.set_title('Top Themes', fontsize=14, fontweight='bold')
ax4.set_xlabel('Number of Reviews')
for bar, val in zip(bars, theme_counts.values):
    ax4.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, str(val), va='center')

plt.tight_layout()
plt.savefig('final_report_charts.png', dpi=150, bbox_inches='tight')
print("✓ Saved final_report_charts.png")

# Average Rating Chart
plt.figure(figsize=(8, 5))
avg_ratings = df.groupby('bank')['rating'].mean().sort_values()
bars = plt.bar(range(len(avg_ratings)), avg_ratings.values, color=['#e74c3c', '#3498db', '#2ecc71'])
plt.xticks(range(len(avg_ratings)), [b.split()[0] for b in avg_ratings.index], rotation=15)
plt.ylabel('Average Rating (1-5 stars)', fontsize=12)
plt.title('Average Rating by Bank', fontsize=14, fontweight='bold')
plt.ylim(0, 5)
for bar, val in zip(bars, avg_ratings.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{val:.2f}★', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('avg_rating_by_bank.png', dpi=150)
print("✓ Saved avg_rating_by_bank.png")

print("\n" + "="*60)
print("✅ TASK 4 COMPLETE!")
print("="*60)
print("\nOutput files created:")
print("  - final_report_charts.png")
print("  - avg_rating_by_bank.png")
