"""
Google Play Store Review Scraper for Ethiopian Banking Apps
Collects reviews for CBE, Bank of Abyssinia, and Dashen Bank
"""

from google_play_scraper import Sort, reviews
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EthiopianBankScraper:
    """
    Scraper for Ethiopian banking apps on Google Play Store.
    
    Apps:
    - Commercial Bank of Ethiopia (CBE)
    - Bank of Abyssinia (BOA)
    - Dashen Bank
    """
    
    # Bank configurations - VERIFY THESE PACKAGE NAMES FIRST!
    BANK_CONFIGS = {
    "CBE": {
        "app_id": "com.combanketh.mobilebanking",  # Corrected
        "app_name": "Commercial Bank of Ethiopia Mobile",
    },
    "BOA": {
        "app_id": "com.boa.boaMobileBanking",      # Corrected
        "app_name": "Bank of Abyssinia Mobile Banking",
    },
    "DASHEN": {
        "app_id": "com.dashen.dashensuperapp",    # Corrected
        "app_name": "Dashen Bank Mobile Banking",
    }
}

    
    def __init__(self, target_reviews_per_bank: int = 400):
        """
        Initialize scraper.
        
        Args:
            target_reviews_per_bank: Minimum number of reviews to collect per bank
        """
        self.target_count = target_reviews_per_bank
        self.source = "Google Play"
        
    def scrape_bank_reviews(self, bank_key: str) -> List[Dict]:
        """
        Scrape reviews for a specific bank.
        
        Args:
            bank_key: Key in BANK_CONFIGS (CBE, BOA, or DASHEN)
            
        Returns:
            List of review dictionaries
        """
        config = self.BANK_CONFIGS[bank_key]
        all_reviews = []
        continuation_token = None
        
        logger.info(f"Starting scrape for {config['app_name']}...")
        logger.info(f"Target: {self.target_count} reviews")
        
        while len(all_reviews) < self.target_count:
            try:
                # Fetch batch of reviews
                result, continuation_token = reviews(
                    config["app_id"],
                    lang="en",
                    country="et",  # Ethiopia
                    sort=Sort.NEWEST,
                    count=min(200, self.target_count - len(all_reviews)),
                    continuation_token=continuation_token
                )
                
                if not result:
                    logger.warning(f"No reviews returned for {config['app_name']}")
                    break
                    
                all_reviews.extend(result)
                logger.info(f"  Collected {len(all_reviews)}/{self.target_count} reviews")
                
                # Rate limiting to avoid being blocked
                time.sleep(2)
                
                # Break if no more reviews available
                if not continuation_token:
                    logger.info(f"  No more reviews available. Final count: {len(all_reviews)}")
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping {config['app_name']}: {e}")
                break
        
        logger.info(f"Completed {config['app_name']}: {len(all_reviews)} reviews collected")
        return all_reviews
    
    def parse_review(self, review_obj: Dict, bank_key: str) -> Dict:
        """
        Parse raw review object into standardized format.
        
        Args:
            review_obj: Raw review from google-play-scraper
            bank_key: Bank identifier
            
        Returns:
            Standardized review dictionary
        """
        config = self.BANK_CONFIGS[bank_key]
        
        return {
            "review_id": review_obj.get("reviewId", ""),
            "review_text": review_obj.get("content", ""),
            "rating": review_obj.get("score", 0),
            "review_date": review_obj.get("at", ""),
            "bank": config["app_name"],
            "source": self.source,
            "author": review_obj.get("userName", ""),
            "thumbs_up_count": review_obj.get("thumbsUpCount", 0),
            "app_version": review_obj.get("reviewCreatedVersion", "unknown")
        }
    
    def scrape_all(self) -> pd.DataFrame:
        """
        Scrape reviews for all three banks.
        
        Returns:
            DataFrame with all collected reviews
        """
        all_reviews_data = []
        
        for bank_key in self.BANK_CONFIGS.keys():
            raw_reviews = self.scrape_bank_reviews(bank_key)
            
            for review in raw_reviews:
                parsed = self.parse_review(review, bank_key)
                all_reviews_data.append(parsed)
                
            logger.info(f"--- {bank_key} complete ---")
        
        df = pd.DataFrame(all_reviews_data)
        logger.info(f"\n{'='*50}")
        logger.info(f"TOTAL REVIEWS COLLECTED: {len(df)}")
        logger.info(f"  CBE: {len(df[df['bank'] == self.BANK_CONFIGS['CBE']['app_name']])}")
        logger.info(f"  BOA: {len(df[df['bank'] == self.BANK_CONFIGS['BOA']['app_name']])}")
        logger.info(f"  DASHEN: {len(df[df['bank'] == self.BANK_CONFIGS['DASHEN']['app_name']])}")
        logger.info(f"{'='*50}")
        
        return df


def main():
    """Main execution function."""
    print("="*60)
    print("ETHIOPIAN BANKING APP REVIEW SCRAPER")
    print("="*60)
    
    # Create scraper instance
    scraper = EthiopianBankScraper(target_reviews_per_bank=400)
    
    # Scrape all reviews
    df = scraper.scrape_all()
    
    # Save raw data
    output_path = "data/raw_reviews.csv"
    df.to_csv(output_path, index=False)
    print(f"\nRaw data saved to {output_path}")
    
    return df


if __name__ == "__main__":
    df = main()