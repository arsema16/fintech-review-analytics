"""
Complete Pipeline for Task 2: Sentiment and Thematic Analysis
Runs both analyses sequentially and produces final output
"""

import pandas as pd
import logging
from sentiment_vader import SentimentAnalyzer
from thematic import ThemeExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_sentiment_pipeline():
    """Run sentiment analysis on cleaned reviews."""
    logger.info("=" * 50)
    logger.info("STEP 1: Sentiment Analysis (VADER)")
    logger.info("=" * 50)
    
    df = pd.read_csv("data/cleaned_reviews.csv")
    logger.info(f"Loaded {len(df)} reviews from data/cleaned_reviews.csv")
    
    analyzer = SentimentAnalyzer()
    df = analyzer.add_sentiment_to_df(df)
    
    df.to_csv("data/sentiment_reviews.csv", index=False)
    logger.info("Saved sentiment results to data/sentiment_reviews.csv")
    
    return df


def run_thematic_pipeline():
    """Run thematic analysis on sentiment results."""
    logger.info("\n" + "=" * 50)
    logger.info("STEP 2: Thematic Analysis (TF-IDF)")
    logger.info("=" * 50)
    
    try:
        df = pd.read_csv("data/sentiment_reviews.csv")
        logger.info(f"Loaded {len(df)} reviews from data/sentiment_reviews.csv")
    except FileNotFoundError:
        df = pd.read_csv("data/cleaned_reviews.csv")
        logger.info(f"Loaded {len(df)} reviews from data/cleaned_reviews.csv")
    
    extractor = ThemeExtractor(df)
    df = extractor.assign_themes_to_reviews()
    summary = extractor.analyze_all_banks()
    theme_counts = extractor.get_theme_summary()
    
    df.to_csv("data/thematic_reviews.csv", index=False)
    summary.to_csv("data/theme_summary.csv", index=False)
    
    logger.info("\nTheme Distribution by Bank:")
    print(theme_counts)
    
    return df, summary, theme_counts


def generate_report(df, theme_counts):
    """Generate final report summary."""
    logger.info("\n" + "=" * 50)
    logger.info("FINAL REPORT SUMMARY")
    logger.info("=" * 50)
    
    # Basic stats
    total = len(df)
    sentiment_covered = df['sentiment_label'].notna().sum()
    themes_assigned = df['identified_theme'].notna().sum()
    
    print(f"\nTotal reviews processed: {total}")
    print(f"Sentiment coverage: {sentiment_covered}/{total} ({sentiment_covered/total*100:.1f}%)")
    print(f"Themes assigned: {themes_assigned}/{total} ({themes_assigned/total*100:.1f}%)")
    
    # Sentiment distribution
    print("\n--- SENTIMENT DISTRIBUTION ---")
    sentiment_dist = df['sentiment_label'].value_counts()
    sentiment_pct = df['sentiment_label'].value_counts(normalize=True).mul(100).round(1)
    for label in sentiment_dist.index:
        print(f"  {label}: {sentiment_dist[label]} ({sentiment_pct[label]}%)")
    
    # Sentiment by bank
    print("\n--- SENTIMENT BY BANK ---")
    sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment_label'])
    print(sentiment_by_bank)
    
    # Theme distribution
    print("\n--- THEME DISTRIBUTION BY BANK ---")
    print(theme_counts)
    
    # Top themes overall
    print("\n--- TOP THEMES OVERALL ---")
    top_themes = df['identified_theme'].value_counts()
    for theme, count in top_themes.head(5).items():
        print(f"  {theme}: {count} reviews")
    
    return sentiment_by_bank, top_themes


def main():
    """Run complete Task 2 pipeline."""
    print("\n" + "=" * 60)
    print("TASK 2: SENTIMENT AND THEMATIC ANALYSIS PIPELINE")
    print("=" * 60)
    
    # Run both pipelines
    df_sentiment = run_sentiment_pipeline()
    df_thematic, summary, theme_counts = run_thematic_pipeline()
    
    # Generate report
    sentiment_by_bank, top_themes = generate_report(df_thematic, theme_counts)
    
    # Save final combined data
    df_thematic.to_csv("data/final_analytics.csv", index=False)
    logger.info("\nSaved final combined data to data/final_analytics.csv")
    
    print("\n" + "=" * 60)
    print("✅ TASK 2 COMPLETE!")
    print("=" * 60)
    print("\nOutput files created:")
    print("  - data/sentiment_reviews.csv (sentiment analysis)")
    print("  - data/thematic_reviews.csv (thematic analysis)")
    print("  - data/theme_summary.csv (per-bank theme summary)")
    print("  - data/final_analytics.csv (combined results)")
    
    return df_thematic


if __name__ == "__main__":
    df = main()
