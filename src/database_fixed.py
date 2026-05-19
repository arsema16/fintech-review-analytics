"""
PostgreSQL Database Module for Bank Reviews (Fixed Version)
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "bank_reviews",
    "user": "postgres",
    "password": "1234",  # CHANGE THIS TO YOUR PASSWORD
    "host": "localhost",
    "port": "5432"
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label);
"""


def main():
    print("\n" + "="*60)
    print("TASK 3: POSTGRESQL DATABASE SETUP")
    print("="*60)
    
    # Load data
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
    
    # Ensure review_id exists
    if 'review_id' not in df.columns:
        df['review_id'] = [f"review_{i}" for i in range(len(df))]
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        conn.autocommit = False
        cur = conn.cursor()
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        logger.info("\nMake sure:")
        logger.info("  1. PostgreSQL is running")
        logger.info("  2. Database 'bank_reviews' exists")
        logger.info("  3. Password is correct")
        return
    
    # Create tables
    try:
        cur.execute(SCHEMA_SQL)
        conn.commit()
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        conn.rollback()
    
    # Insert banks
    banks = df['bank'].unique()
    for bank in banks:
        try:
            cur.execute(
                "INSERT INTO banks (bank_name, app_name) VALUES (%s, %s) ON CONFLICT (bank_name) DO NOTHING",
                (bank, bank)
            )
        except Exception as e:
            logger.error(f"Failed to insert bank {bank}: {e}")
    conn.commit()
    logger.info(f"Inserted {len(banks)} banks")
    
    # Get bank mapping
    cur.execute("SELECT bank_id, bank_name FROM banks")
    bank_mapping = {row[1]: row[0] for row in cur.fetchall()}
    
    # Insert reviews
    inserted = 0
    skipped = 0
    
    for _, row in df.iterrows():
        bank_name = row['bank']
        if bank_name not in bank_mapping:
            skipped += 1
            continue
        
        try:
            cur.execute("""
                INSERT INTO reviews 
                (review_id, bank_id, review_text, rating, review_date, 
                 sentiment_label, sentiment_score, identified_theme, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (review_id) DO UPDATE SET
                    sentiment_label = EXCLUDED.sentiment_label,
                    sentiment_score = EXCLUDED.sentiment_score,
                    identified_theme = EXCLUDED.identified_theme
            """, (
                row.get('review_id', f"review_{_}"),
                bank_mapping[bank_name],
                row['review'][:10000],
                int(row['rating']),
                row.get('date') if pd.notna(row.get('date')) else None,
                row.get('sentiment_label'),
                row.get('sentiment_score'),
                row.get('identified_theme'),
                "Google Play"
            ))
            inserted += 1
            
            if inserted % 100 == 0:
                conn.commit()
                logger.info(f"Inserted {inserted} reviews...")
                
        except Exception as e:
            logger.error(f"Failed to insert review: {e}")
            skipped += 1
    
    conn.commit()
    logger.info(f"Inserted {inserted} reviews, skipped {skipped}")
    
    # Verification queries
    print("\n" + "="*50)
    print("VERIFICATION RESULTS")
    print("="*50)
    
    cur.execute("SELECT COUNT(*) FROM reviews")
    print(f"\nTotal reviews in database: {cur.fetchone()[0]}")
    
    cur.execute("""
        SELECT b.bank_name, COUNT(r.review_id) as review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
    """)
    print("\nReviews per bank:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    cur.execute("""
        SELECT sentiment_label, COUNT(*) as count
        FROM reviews
        WHERE sentiment_label IS NOT NULL
        GROUP BY sentiment_label
    """)
    print("\nSentiment distribution:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    cur.execute("""
        SELECT identified_theme, COUNT(*) as count
        FROM reviews
        WHERE identified_theme IS NOT NULL
        GROUP BY identified_theme
        ORDER BY count DESC
    """)
    print("\nTheme distribution:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ TASK 3 COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
