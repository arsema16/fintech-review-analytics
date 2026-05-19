"""
Task 3: PostgreSQL Database Engineering (Fixed)
"""

import pandas as pd
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "bank_reviews",
    "user": "postgres",
    "password": "1234",  # CHANGE THIS to your password
    "host": "localhost",
    "port": "5432"
}

SCHEMA_SQL = """
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS banks CASCADE;

CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label VARCHAR(10),
    sentiment_score DECIMAL(4,3),
    identified_theme VARCHAR(50),
    source VARCHAR(50) DEFAULT 'Google Play',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment_label);
CREATE INDEX idx_reviews_theme ON reviews(identified_theme);
"""


def run_postgres_pipeline():
    print("\n" + "="*60)
    print("TASK 3: POSTGRESQL DATABASE ENGINEERING")
    print("="*60)
    
    # Load data
    df = pd.read_csv("data/thematic_results.csv")
    logger.info(f"Loaded {len(df)} reviews")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        
        # Create tables
        cur.execute(SCHEMA_SQL)
        conn.commit()
        logger.info("Tables created")
        
        # Insert banks
        banks = df['bank'].unique()
        for bank in banks:
            cur.execute("INSERT INTO banks (bank_name, app_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (bank, bank))
        conn.commit()
        logger.info(f"Inserted {len(banks)} banks")
        
        # Get bank mapping
        cur.execute("SELECT bank_id, bank_name FROM banks")
        bank_map = {row[1]: row[0] for row in cur.fetchall()}
        
        # Insert reviews
        count = 0
        for _, row in df.iterrows():
            bank_id = bank_map.get(row['bank'])
            if bank_id:
                cur.execute("""
                    INSERT INTO reviews 
                    (bank_id, review_text, rating, review_date, sentiment_label, sentiment_score, identified_theme, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    bank_id,
                    row['review'][:5000],
                    int(row['rating']),
                    row.get('date') if pd.notna(row.get('date')) else None,
                    row.get('sentiment_label'),
                    row.get('sentiment_score'),
                    row.get('identified_theme'),
                    "Google Play"
                ))
                count += 1
                if count % 100 == 0:
                    conn.commit()
                    logger.info(f"Inserted {count} reviews...")
        
        conn.commit()
        logger.info(f"Inserted {count} reviews")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM reviews")
        print(f"\nTotal reviews in database: {cur.fetchone()[0]}")
        
        cur.execute("""
            SELECT b.bank_name, COUNT(r.review_id) 
            FROM banks b LEFT JOIN reviews r ON b.bank_id = r.bank_id 
            GROUP BY b.bank_name
        """)
        print("\nReviews per bank:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cur.close()
        conn.close()
        print("\n✅ Task 3 Complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print("\nTo fix PostgreSQL:")
        print("  1. Open pgAdmin")
        print("  2. Create database: bank_reviews")
        print("  3. Update password in DB_CONFIG")
        print("\nOr skip Task 3 - Tasks 2 and 4 are complete!")


if __name__ == "__main__":
    run_postgres_pipeline()
