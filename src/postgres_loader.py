"""
Task 3: PostgreSQL Database Engineering
Loads sentiment and thematic results into PostgreSQL
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration - UPDATE THESE
DB_CONFIG = {
    "dbname": "bank_reviews",
    "user": "postgres",
    "password": "1234",  # CHANGE THIS to your PostgreSQL password
    "host": "localhost",
    "port": "5432"
}

# SQL Schema
CREATE_SCHEMA_SQL = """
-- Create banks table
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reviews table
CREATE TABLE IF NOT EXISTS reviews (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_reviews_theme ON reviews(identified_theme);

-- Create view for analytics
CREATE OR REPLACE VIEW review_analytics AS
SELECT 
    b.bank_name,
    COUNT(r.review_id) as total_reviews,
    AVG(r.rating)::DECIMAL(3,2) as avg_rating,
    SUM(CASE WHEN r.sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as positive_pct,
    SUM(CASE WHEN r.sentiment_label = 'NEGATIVE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as negative_pct
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
GROUP BY b.bank_name;
"""


def create_database():
    """Create the bank_reviews database if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'bank_reviews'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE bank_reviews")
            logger.info("Created database: bank_reviews")
        else:
            logger.info("Database bank_reviews already exists")
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Database creation error: {e}")


def create_tables():
    """Create tables and indexes."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(CREATE_SCHEMA_SQL)
        conn.commit()
        logger.info("Tables created successfully")
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Table creation error: {e}")


def load_banks(df, conn):
    """Load unique banks into banks table."""
    cur = conn.cursor()
    banks = df['bank'].unique()
    for bank in banks:
        cur.execute("""
            INSERT INTO banks (bank_name, app_name) 
            VALUES (%s, %s) 
            ON CONFLICT (bank_name) DO NOTHING
        """, (bank, bank))
    conn.commit()
    logger.info(f"Loaded {len(banks)} banks")
    cur.close()


def load_reviews(df, conn):
    """Load reviews into reviews table."""
    # First, get bank_id mapping
    bank_map = {}
    cur = conn.cursor()
    cur.execute("SELECT bank_id, bank_name FROM banks")
    for row in cur.fetchall():
        bank_map[row[1]] = row[0]
    cur.close()
    
    # Insert reviews
    cur = conn.cursor()
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
    logger.info(f"Loaded {count} reviews")
    cur.close()


def run_verification(conn):
    """Run verification queries and print results."""
    cur = conn.cursor()
    
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
        GROUP BY sentiment_label
    """)
    print("\nSentiment distribution:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    cur.close()


def run_postgres_pipeline():
    """Complete Task 3 pipeline."""
    print("\n" + "="*60)
    print("TASK 3: POSTGRESQL DATABASE ENGINEERING")
    print("="*60)
    
    # Load the thematic results
    try:
        df = pd.read_csv("data/thematic_results.csv")
        logger.info(f"Loaded {len(df)} reviews from data/thematic_results.csv")
    except FileNotFoundError:
        df = pd.read_csv("data/sentiment_results.csv")
        logger.info(f"Loaded {len(df)} reviews from data/sentiment_results.csv")
    
    # Create database and tables
    create_database()
    create_tables()
    
    # Connect and load data
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        load_banks(df, conn)
        load_reviews(df, conn)
        run_verification(conn)
        conn.close()
        print("\n✅ Task 3 Complete!")
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Update DB_CONFIG password to match your PostgreSQL password")
        print("  3. Run: createdb -U postgres bank_reviews")


if __name__ == "__main__":
    run_postgres_pipeline()