"""
Task 2: Sentiment Analysis using VADER
Classifies reviews as POSITIVE, NEUTRAL, or NEGATIVE
"""

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_sentiment_analysis(input_file="data/cleaned_reviews.csv", output_file="data/sentiment_results.csv"):
    """
    Run VADER sentiment analysis on cleaned reviews.
    
    Args:
        input_file: Path to cleaned CSV with 'review' column
        output_file: Path to save results with sentiment labels
    
    Returns:
        DataFrame with added sentiment_label and sentiment_score columns
    """
    logger.info(f"Loading data from {input_file}")
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} reviews")
    
    # Initialize VADER
    analyzer = SentimentIntensityAnalyzer()
    
    def get_sentiment(text):
        if not isinstance(text, str) or len(text.strip()) < 3:
            return "NEUTRAL", 0.0
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        if compound >= 0.05:
            return "POSITIVE", compound
        elif compound <= -0.05:
            return "NEGATIVE", compound
        else:
            return "NEUTRAL", compound
    
    # Apply sentiment analysis
    logger.info("Running sentiment analysis on all reviews...")
    results = df['review'].apply(lambda x: pd.Series(get_sentiment(x), index=['sentiment_label', 'sentiment_score']))
    
    df['sentiment_label'] = results['sentiment_label']
    df['sentiment_score'] = results['sentiment_score']
    
    # Summary statistics
    logger.info("\n=== Sentiment Distribution ===")
    sentiment_counts = df['sentiment_label'].value_counts()
    for label, count in sentiment_counts.items():
        pct = count / len(df) * 100
        logger.info(f"  {label}: {count} ({pct:.1f}%)")
    
    # Save results
    df.to_csv(output_file, index=False)
    logger.info(f"Saved sentiment results to {output_file}")
    
    return df


if __name__ == "__main__":
    run_sentiment_analysis()