import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        logger.info("Initializing VADER sentiment analyzer...")
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER ready")
    
    def classify(self, text: str) -> Tuple[str, float]:
        if not text or len(str(text).strip()) < 3:
            return "NEUTRAL", 0.0
            
        try:
            scores = self.analyzer.polarity_scores(str(text))
            compound = scores['compound']
            
            if compound >= 0.05:
                return "POSITIVE", compound
            elif compound <= -0.05:
                return "NEGATIVE", compound
            else:
                return "NEUTRAL", compound
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            return "NEUTRAL", 0.0
    
    def analyze_batch(self, texts: list) -> pd.DataFrame:
        results = []
        for i, text in enumerate(texts):
            label, score = self.classify(text)
            results.append({
                "sentiment_label": label,
                "sentiment_score": round(score, 4)
            })
            if (i + 1) % 200 == 0:
                logger.info(f"Processed {i + 1}/{len(texts)} reviews")
        
        return pd.DataFrame(results)
    
    def add_sentiment_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Running sentiment analysis on all reviews...")
        
        sentiments = self.analyze_batch(df["review"].tolist())
        
        df["sentiment_label"] = sentiments["sentiment_label"]
        df["sentiment_score"] = sentiments["sentiment_score"]
        
        logger.info("\nSentiment Distribution:")
        dist = df["sentiment_label"].value_counts(normalize=True).mul(100).round(1)
        for label, pct in dist.items():
            logger.info(f"  {label}: {pct}%")
        
        return df


def main():
    df = pd.read_csv("data/cleaned_reviews.csv")
    logger.info(f"Loaded {len(df)} reviews")
    
    analyzer = SentimentAnalyzer()
    df = analyzer.add_sentiment_to_df(df)
    
    df.to_csv("data/sentiment_reviews.csv", index=False)
    logger.info("Saved sentiment results to data/sentiment_reviews.csv")
    
    return df


if __name__ == "__main__":
    df = main()
