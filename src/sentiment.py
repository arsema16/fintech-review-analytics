"""
Sentiment Analysis Module for Ethiopian Banking App Reviews
Uses DistilBERT for sentiment classification
"""

import pandas as pd
from transformers import pipeline
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analysis using DistilBERT fine-tuned on SST-2.
    
    Why DistilBERT:
    - 60% faster than BERT while retaining 97% of performance
    - Fine-tuned for sentiment (positive/negative classification)
    - Production-ready with Hugging Face pipeline
    """
    
    def __init__(self):
        logger.info("Loading DistilBERT sentiment model...")
        self.classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        logger.info("Model loaded successfully")
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify a single review.
        
        Returns:
            tuple: (label, confidence_score)
            label is "POSITIVE" or "NEGATIVE"
        """
        if not text or len(text.strip()) < 3:
            return "NEUTRAL", 0.0
            
        try:
            # Truncate to 512 tokens (model limit)
            result = self.classifier(text[:512])[0]
            label = result["label"]
            score = result["score"]
            
            return label, score
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            return "NEUTRAL", 0.0
    
    def analyze_batch(self, texts: list) -> pd.DataFrame:
        """Analyze a batch of reviews."""
        results = []
        for i, text in enumerate(texts):
            label, score = self.classify(text)
            results.append({
                "sentiment_label": label,
                "sentiment_score": round(score, 4)
            })
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(texts)} reviews")
        
        return pd.DataFrame(results)
    
    def add_sentiment_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add sentiment columns to existing DataFrame."""
        logger.info("Running sentiment analysis on all reviews...")
        
        sentiments = self.analyze_batch(df["review"].tolist())
        
        df["sentiment_label"] = sentiments["sentiment_label"]
        df["sentiment_score"] = sentiments["sentiment_score"]
        
        # Summary statistics
        logger.info("\nSentiment Distribution:")
        dist = df["sentiment_label"].value_counts(normalize=True).mul(100).round(1)
        for label, pct in dist.items():
            logger.info(f"  {label}: {pct}%")
        
        return df


def main():
    """Test the sentiment analyzer."""
    # Load cleaned data
    df = pd.read_csv("data/cleaned_reviews.csv")
    logger.info(f"Loaded {len(df)} reviews")
    
    # Run sentiment analysis
    analyzer = SentimentAnalyzer()
    df = analyzer.add_sentiment_to_df(df)
    
    # Save results
    df.to_csv("data/sentiment_reviews.csv", index=False)
    logger.info("Saved sentiment results to data/sentiment_reviews.csv")
    
    return df


if __name__ == "__main__":
    df = main()