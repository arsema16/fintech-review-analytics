"""
Data Preprocessing Pipeline for Google Play Store Reviews
Cleans and standardizes scraped review data
"""

import pandas as pd
import re
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReviewPreprocessor:
    """
    Clean and standardize review data.
    
    Operations:
    - Remove duplicates
    - Handle missing values
    - Normalize dates
    - Clean text
    - Validate ratings
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize preprocessor with DataFrame.
        
        Args:
            df: Raw DataFrame from scraper
        """
        self.df = df.copy()
        self.initial_count = len(df)
        self.stats = {}
        
    def remove_duplicates(self) -> 'ReviewPreprocessor':
        """Remove duplicate reviews based on review_id."""
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=["review_id"])
        after = len(self.df)
        
        removed = before - after
        self.stats['duplicates_removed'] = removed
        logger.info(f"Removed {removed} duplicate reviews")
        return self
    
    def handle_missing_values(self) -> 'ReviewPreprocessor':
        """Handle missing values in critical columns."""
        before = len(self.df)
        
        # Drop rows missing review text or rating (critical)
        self.df = self.df.dropna(subset=["review_text", "rating"])
        
        # Fill optional fields
        self.df["app_version"] = self.df["app_version"].fillna("unknown")
        self.df["review_text"] = self.df["review_text"].fillna("")
        self.df["author"] = self.df["author"].fillna("anonymous")
        
        after = len(self.df)
        removed = before - after
        
        self.stats['missing_removed'] = removed
        self.stats['missing_rate_pct'] = (removed / self.initial_count) * 100
        
        logger.info(f"Removed {removed} rows with missing critical data")
        logger.info(f"Missing data rate: {self.stats['missing_rate_pct']:.1f}%")
        return self
    
    def normalize_dates(self) -> 'ReviewPreprocessor':
        """Convert dates to YYYY-MM-DD format."""
        def parse_date(date_val):
            if pd.isna(date_val):
                return None
            if isinstance(date_val, str):
                # Try different date formats
                try:
                    # ISO format with timezone
                    if 'T' in date_val:
                        return datetime.fromisoformat(
                            date_val.replace('Z', '+00:00')
                        ).date().isoformat()
                    # Simple date format
                    else:
                        return pd.to_datetime(date_val).date().isoformat()
                except:
                    return None
            return None
        
        self.df["review_date"] = self.df["review_date"].apply(parse_date)
        
        # Drop rows with invalid dates (if any)
        before = len(self.df)
        self.df = self.df.dropna(subset=["review_date"])
        after = len(self.df)
        
        if before - after > 0:
            logger.info(f"Removed {before - after} rows with invalid dates")
        
        return self
    
    def clean_text(self) -> 'ReviewPreprocessor':
        """Clean review text."""
        def clean(text):
            if not isinstance(text, str):
                return ""
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\-\'\"]', '', text)
            
            # Normalize unicode to ASCII
            text = text.encode('ascii', 'ignore').decode('ascii')
            
            # Strip leading/trailing spaces
            return text.strip()
        
        self.df["review_text"] = self.df["review_text"].apply(clean)
        
        # Remove empty reviews after cleaning
        before = len(self.df)
        self.df = self.df[self.df["review_text"].str.len() > 0]
        after = len(self.df)
        
        if before - after > 0:
            logger.info(f"Removed {before - after} empty reviews after cleaning")
        
        return self
    
    def validate_ratings(self) -> 'ReviewPreprocessor':
        """Ensure ratings are within valid range (1-5)."""
        before = len(self.df)
        self.df = self.df[(self.df["rating"] >= 1) & (self.df["rating"] <= 5)]
        after = len(self.df)
        
        if before - after > 0:
            logger.info(f"Removed {before - after} rows with invalid ratings")
        
        return self
    
    def add_text_length(self) -> 'ReviewPreprocessor':
        """Add text length column for analysis."""
        self.df["review_length"] = self.df["review_text"].str.len()
        return self
    
    def execute(self) -> pd.DataFrame:
        """
        Run all preprocessing steps in sequence.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("\n" + "="*50)
        logger.info("STARTING DATA PREPROCESSING")
        logger.info("="*50)
        
        self.remove_duplicates()
        self.handle_missing_values()
        self.normalize_dates()
        self.clean_text()
        self.validate_ratings()
        self.add_text_length()
        
        logger.info("\n" + "="*50)
        logger.info("PREPROCESSING COMPLETE")
        logger.info(f"Final dataset size: {len(self.df)} reviews")
        logger.info(f"Retained: {(len(self.df)/self.initial_count)*100:.1f}% of original data")
        logger.info("="*50)
        
        return self.df
    
    def get_required_columns(self) -> pd.DataFrame:
        """
        Return DataFrame with only the required columns for Task 1.
        
        Required columns: review, rating, date, bank, source
        """
        required_cols = {
            "review_text": "review",
            "rating": "rating",
            "review_date": "date",
            "bank": "bank",
            "source": "source"
        }
        
        output_df = self.df[list(required_cols.keys())].copy()
        output_df = output_df.rename(columns=required_cols)
        
        return output_df
    
    def save_clean_data(self, output_path: str = "data/cleaned_reviews.csv"):
        """Save cleaned dataset to CSV."""
        clean_df = self.get_required_columns()
        clean_df.to_csv(output_path, index=False)
        logger.info(f"Saved cleaned data to {output_path}")
        logger.info(f"Columns: {list(clean_df.columns)}")
        return clean_df


def main():
    """Main execution function."""
    import os
    
    # Load raw data
    raw_path = "data/raw_reviews.csv"
    
    if not os.path.exists(raw_path):
        logger.error(f"Raw data file not found: {raw_path}")
        logger.info("Please run scraper.py first to collect reviews")
        return None
    
    logger.info(f"Loading raw data from {raw_path}")
    raw_df = pd.read_csv(raw_path)
    logger.info(f"Loaded {len(raw_df)} raw reviews")
    
    # Preprocess
    preprocessor = ReviewPreprocessor(raw_df)
    cleaned_df = preprocessor.execute()
    final_df = preprocessor.save_clean_data()
    
    # Print summary
    print("\n" + "="*50)
    print("DATA QUALITY SUMMARY")
    print("="*50)
    print(f"Original reviews: {len(raw_df)}")
    print(f"Final reviews: {len(final_df)}")
    print(f"Missing data rate: {preprocessor.stats.get('missing_rate_pct', 0):.1f}%")
    
    print("\nReviews per bank:")
    print(final_df['bank'].value_counts())
    
    return final_df


if __name__ == "__main__":
    df = main()