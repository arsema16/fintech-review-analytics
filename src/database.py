"""
PostgreSQL Database Module for Bank Reviews
Creates tables and inserts processed review data
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "dbname": "bank_reviews",
    "user": "postgres",
    "password": "1234",  # Change this to your PostgreSQL password
    "host": "localhost",
    "port": "5432"
}

# SQL Schema
SCHEMA_SQL = """
-- Create database (run manually in pgAdmin first)
-- CREATE DATABASE bank_reviews;

-- Banks table
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(100) PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label VARCHAR(10) CHECK (sentiment_label IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    sentiment_score DECIMAL(4,3),
    identified_theme VARCHAR(50),
    source VARCHAR(50) DEFAULT 'Google Play',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_theme ON reviews(identified_theme);

-- View for aggregated analytics
CREATE OR REPLACE VIEW review_analytics AS
SELECT 
    b.bank_name,
    COUNT(r.review_id) as total_reviews,
    AVG(r.rating)::DECIMAL(3,2) as avg_rating,
    COUNT(CASE WHEN r.sentiment_label = 'POSITIVE' THEN 1 END) * 100.0 / COUNT(*) as positive_pct,
    COUNT(CASE WHEN r.sentiment_label = 'NEGATIVE' THEN 1 END) * 100.0 / COUNT(*) as negative_pct,
    COUNT(CASE WHEN r.rating >= 4 THEN 1 END) * 100.0 / COUNT(*) as promoter_pct,
    COUNT(CASE WHEN r.rating <= 2 THEN 1 END) * 100.0 / COUNT(*) as detractor_pct
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
GROUP BY b.bank_name;
"""


class ReviewDatabase:
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.engine = None
        self.connection = None
    
    def connect(self):
        """Create database connection."""
        try:
            conn_string = f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['dbname']}"
            self.engine = create_engine(conn_string)
            self.connection = self.engine.connect()
            logger.info(f"Connected to database: {self.config['dbname']}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create tables if they don't exist."""
        try:
            with self.connection as conn:
                conn.execute(text(SCHEMA_SQL))
                conn.commit()
            logger.info("Tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            return False
    
    def insert_banks(self, df):
        """Insert bank metadata."""
        banks = df['bank'].unique()
        
        with self.connection as conn:
            for bank in banks:
                try:
                    conn.execute(
                        text("INSERT INTO banks (bank_name, app_name) VALUES (:bank, :bank) ON CONFLICT (bank_name) DO NOTHING"),
                        {"bank": bank}
                    )
                    conn.commit()
                except Exception as e:
                    logger.error(f"Failed to insert bank {bank}: {e}")
        
        logger.info(f"Inserted {len(banks)} banks")
    
    def get_bank_mapping(self):
        """Get bank_name to bank_id mapping."""
        result = self.connection.execute(text("SELECT bank_id, bank_name FROM banks"))
        return {row[1]: row[0] for row in result.fetchall()}
    
    def insert_reviews(self, df):
        """Insert reviews into database."""
        # First ensure banks exist
        self.insert_banks(df)
        bank_mapping = self.get_bank_mapping()
        
        inserted = 0
        skipped = 0
        
        with self.connection as conn:
            for _, row in df.iterrows():
                bank_name = row['bank']
                if bank_name not in bank_mapping:
                    logger.warning(f"Bank not found: {bank_name}")
                    skipped += 1
                    continue
                
                try:
                    conn.execute(
                        text("""
                            INSERT INTO reviews 
                            (review_id, bank_id, review_text, rating, review_date, 
                             sentiment_label, sentiment_score, identified_theme, source)
                            VALUES (:review_id, :bank_id, :review_text, :rating, :review_date,
                                    :sentiment_label, :sentiment_score, :identified_theme, :source)
                            ON CONFLICT (review_id) DO UPDATE SET
                                sentiment_label = EXCLUDED.sentiment_label,
                                sentiment_score = EXCLUDED.sentiment_score,
                                identified_theme = EXCLUDED.identified_theme
                        """),
                        {
                            "review_id": row.get('review_id', f"review_{_}"),
                            "bank_id": bank_mapping[bank_name],
                            "review_text": row['review'][:10000],
                            "rating": int(row['rating']),
                            "review_date": row.get('date') if pd.notna(row.get('date')) else None,
                            "sentiment_label": row.get('sentiment_label'),
                            "sentiment_score": row.get('sentiment_score'),
                            "identified_theme": row.get('identified_theme'),
                            "source": "Google Play"
                        }
                    )
                    conn.commit()
                    inserted += 1
                    
                    if inserted % 100 == 0:
                        logger.info(f"Inserted {inserted} reviews...")
                        
                except Exception as e:
                    logger.error(f"Failed to insert review: {e}")
                    skipped += 1
        
        logger.info(f"Inserted {inserted} reviews, skipped {skipped}")
        return inserted
    
    def run_verification(self):
        """Run verification queries."""
        queries = {
            "Total reviews": "SELECT COUNT(*) as total FROM reviews",
            "Reviews per bank": """
                SELECT b.bank_name, COUNT(r.review_id) as review_count
                FROM banks b
                LEFT JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_name
            """,
            "Average rating per bank": """
                SELECT b.bank_name, AVG(r.rating)::DECIMAL(3,2) as avg_rating
                FROM banks b
                JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_name
            """,
            "Sentiment distribution": """
                SELECT sentiment_label, COUNT(*) as count
                FROM reviews
                GROUP BY sentiment_label
            """,
            "Theme distribution": """
                SELECT identified_theme, COUNT(*) as count
                FROM reviews
                WHERE identified_theme IS NOT NULL
                GROUP BY identified_theme
                ORDER BY count DESC
            """
        }
        
        print("\n" + "="*50)
        print("VERIFICATION RESULTS")
        print("="*50)
        
        for name, query in queries.items():
            print(f"\n{name}:")
            result = self.connection.execute(text(query))
            for row in result.fetchall():
                print(f"  {row}")
        
        return True
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connection closed")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("TASK 3: POSTGRESQL DATABASE SETUP")
    print("="*60)
    
    # Load the final analytics data
    try:
        df = pd.read_csv("data/final_analytics.csv")
        logger.info(f"Loaded {len(df)} reviews from data/final_analytics.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("data/thematic_reviews.csv")
            logger.info(f"Loaded {len(df)} reviews from data/thematic_reviews.csv")
        except FileNotFoundError:
            df = pd.read_csv("data/cleaned_reviews.csv")
            logger.info(f"Loaded {len(df)} reviews from data/cleaned_reviews.csv")
    
    # Ensure required columns exist
    if 'review_id' not in df.columns:
        df['review_id'] = [f"review_{i}" for i in range(len(df))]
    
    # Initialize database
    db = ReviewDatabase()
    
    if not db.connect():
        logger.error("Cannot connect to PostgreSQL. Please check:")
        logger.error("  1. PostgreSQL is installed")
        logger.error("  2. Service is running")
        logger.error("  3. Password in DB_CONFIG is correct")
        return
    
    # Create tables
    db.create_tables()
    
    # Insert data
    db.insert_reviews(df)
    
    # Run verification
    db.run_verification()
    
    # Close connection
    db.close()
    
    print("\n" + "="*60)
    print("✅ TASK 3 COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
