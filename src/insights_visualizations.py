"""
Task 4: Insights, Recommendations, and Visualizations
Generates business insights from sentiment and thematic analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set high-quality plotting
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 11


def load_data():
    """Load the final thematic results."""
    try:
        df = pd.read_csv("data/thematic_results.csv")
        logger.info(f"Loaded {len(df)} reviews")
        return df
    except FileNotFoundError:
        logger.error("Please run Task 2 first: python src/sentiment_analysis.py")
        raise


def create_visualizations(df):
    """Create all publication-ready visualizations."""
    
    # Figure 1: Sentiment Distribution
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sentiment_counts = df['sentiment_label'].value_counts()
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    bars = ax1.bar(sentiment_counts.index, sentiment_counts.values, color=colors, edgecolor='black')
    ax1.set_title('Sentiment Distribution Across All Reviews', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Reviews', fontsize=12)
    for bar, val in zip(bars, sentiment_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                f'{val} ({val/len(df)*100:.1f}%)', ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('fig1_sentiment_distribution.png', bbox_inches='tight', facecolor='white')
    logger.info("Saved: fig1_sentiment_distribution.png")
    plt.close()
    
    # Figure 2: Average Rating by Bank
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    avg_ratings = df.groupby('bank')['rating'].mean().sort_values()
    bank_labels = [b.split()[0] for b in avg_ratings.index]
    colors_bar = ['#e74c3c', '#3498db', '#2ecc71']
    bars = ax2.bar(bank_labels, avg_ratings.values, color=colors_bar, edgecolor='black')
    ax2.set_ylim(0, 5)
    ax2.set_ylabel('Average Rating (Stars)', fontsize=12)
    ax2.set_title('Average Rating by Bank', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, avg_ratings.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, 
                f'{val:.2f}★', ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('fig2_avg_rating_by_bank.png', bbox_inches='tight', facecolor='white')
    logger.info("Saved: fig2_avg_rating_by_bank.png")
    plt.close()
    
    # Figure 3: Sentiment by Bank (Stacked)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment_label'])
    sentiment_by_bank.index = [idx.split()[0] for idx in sentiment_by_bank.index]
    sentiment_by_bank.plot(kind='bar', stacked=True, ax=ax3, 
                          color=['#2ecc71', '#e74c3c', '#95a5a6'], edgecolor='black')
    ax3.set_title('Sentiment by Bank', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Bank', fontsize=12)
    ax3.set_ylabel('Number of Reviews', fontsize=12)
    ax3.legend(title='Sentiment')
    ax3.tick_params(axis='x', rotation=0)
    for container in ax3.containers:
        ax3.bar_label(container, label_type='center', fontsize=9)
    plt.tight_layout()
    plt.savefig('fig3_sentiment_by_bank.png', bbox_inches='tight', facecolor='white')
    logger.info("Saved: fig3_sentiment_by_bank.png")
    plt.close()
    
    # Figure 4: Theme Distribution
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    theme_counts = df['identified_theme'].value_counts().head(8)
    theme_colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(theme_counts)))[::-1]
    bars = ax4.barh(range(len(theme_counts)), theme_counts.values, color=theme_colors, edgecolor='black')
    ax4.set_yticks(range(len(theme_counts)))
    ax4.set_yticklabels(theme_counts.index, fontsize=11)
    ax4.set_xlabel('Number of Reviews', fontsize=12)
    ax4.set_title('Theme Distribution', fontsize=14, fontweight='bold')
    ax4.invert_yaxis()
    for bar, val in zip(bars, theme_counts.values):
        ax4.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, str(val), va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('fig4_theme_distribution.png', bbox_inches='tight', facecolor='white')
    logger.info("Saved: fig4_theme_distribution.png")
    plt.close()


def generate_insights(df):
    """Generate bank-specific insights and recommendations."""
    
    print("\n" + "="*60)
    print("BANK-SPECIFIC INSIGHTS")
    print("="*60)
    
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        avg_rating = bank_df['rating'].mean()
        positive_pct = (bank_df['sentiment_label'] == 'POSITIVE').mean() * 100
        negative_pct = (bank_df['sentiment_label'] == 'NEGATIVE').mean() * 100
        one_star_pct = (bank_df['rating'] == 1).mean() * 100
        five_star_pct = (bank_df['rating'] == 5).mean() * 100
        top_theme = bank_df['identified_theme'].mode().iloc[0] if not bank_df['identified_theme'].mode().empty else "OTHER"
        
        print(f"\n{'='*40}")
        print(f"{bank.split()[0]}")
        print(f"{'='*40}")
        print(f"Average Rating: {avg_rating:.2f}★")
        print(f"Positive Sentiment: {positive_pct:.1f}%")
        print(f"Negative Sentiment: {negative_pct:.1f}%")
        print(f"5-Star Reviews: {five_star_pct:.1f}%")
        print(f"1-Star Reviews: {one_star_pct:.1f}%")
        print(f"Top Theme: {top_theme}")
        
        # Satisfaction Drivers
        print(f"\n📈 SATISFACTION DRIVERS:")
        if five_star_pct > 60:
            print("  • High user satisfaction with core functionality")
        if top_theme == "UI_UX":
            print("  • Users appreciate the interface design")
        if positive_pct > 60:
            print("  • Strong overall positive sentiment")
        
        # Pain Points
        print(f"\n⚠️ PAIN POINTS:")
        if one_star_pct > 20:
            print(f"  • HIGH DETRACTOR RATE: {one_star_pct:.1f}% one-star reviews")
        if top_theme == "TRANSACTION_SPEED":
            print("  • Slow transfer speeds affecting user experience")
        if top_theme == "LOGIN_ACCESS":
            print("  • Login and OTP issues causing frustration")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if bank == "Bank of Abyssinia Mobile Banking":
            print("  1. [CRITICAL] Fix OTP delivery and login authentication")
            print("  2. Redesign onboarding flow for new users")
            print("  3. Implement biometric login (fingerprint/face ID)")
        elif bank == "Commercial Bank of Ethiopia Mobile":
            print("  1. Optimize API response times for transfers")
            print("  2. Add offline mode for low-connectivity areas")
            print("  3. Implement in-app crash reporting")
        else:  # Dashen
            print("  1. Add transaction progress indicators")
            print("  2. Implement push notifications for transfer status")
            print("  3. Add biometric login for security")


def run_insights_pipeline():
    """Complete Task 4 pipeline."""
    print("\n" + "="*60)
    print("TASK 4: INSIGHTS, RECOMMENDATIONS, AND VISUALIZATIONS")
    print("="*60)
    
    df = load_data()
    create_visualizations(df)
    generate_insights(df)
    
    print("\n" + "="*60)
    print("✅ TASK 4 COMPLETE!")
    print("="*60)
    print("\nOutput files created:")
    print("  - fig1_sentiment_distribution.png")
    print("  - fig2_avg_rating_by_bank.png")
    print("  - fig3_sentiment_by_bank.png")
    print("  - fig4_theme_distribution.png")


if __name__ == "__main__":
    run_insights_pipeline()