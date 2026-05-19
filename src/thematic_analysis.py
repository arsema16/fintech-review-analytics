"""
Task 2: Thematic Analysis using TF-IDF
Extracts keywords and assigns themes to reviews
"""

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Theme keywords mapping
THEME_KEYWORDS = {
    "TRANSACTION_SPEED": ["slow", "fast", "transfer", "loading", "timeout", "speed", "processing", "wait"],
    "LOGIN_ACCESS": ["login", "password", "otp", "fingerprint", "biometric", "access", "locked", "forgot"],
    "UI_UX": ["ui", "interface", "design", "layout", "navigation", "menu", "confusing", "intuitive"],
    "CUSTOMER_SUPPORT": ["support", "help", "customer service", "agent", "complaint", "contact"],
    "STABILITY": ["crash", "freeze", "error", "bug", "glitch", "unstable", "restart"]
}


def assign_theme(review_text):
    """Assign a theme to a single review based on keyword matching."""
    if not isinstance(review_text, str):
        return "OTHER"
    text_lower = review_text.lower()
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return theme
    return "OTHER"


def extract_keywords(df, bank_name, n=10):
    """Extract top TF-IDF keywords for a specific bank."""
    bank_reviews = df[df['bank'] == bank_name]['review'].dropna().tolist()
    if not bank_reviews:
        return []
    
    vectorizer = TfidfVectorizer(max_features=n, stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(bank_reviews)
    feature_names = vectorizer.get_feature_names_out()
    
    return feature_names.tolist()


def run_thematic_analysis(input_file="data/sentiment_results.csv", output_file="data/thematic_results.csv"):
    """
    Run thematic analysis on sentiment results.
    
    Args:
        input_file: Path to CSV with sentiment labels
        output_file: Path to save results with themes
    
    Returns:
        DataFrame with added identified_theme column
    """
    logger.info(f"Loading data from {input_file}")
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} reviews")
    
    # Assign themes
    logger.info("Assigning themes to reviews...")
    df['identified_theme'] = df['review'].apply(assign_theme)
    
    # Extract keywords per bank
    logger.info("\n=== Top Keywords by Bank ===")
    for bank in df['bank'].unique():
        keywords = extract_keywords(df, bank, n=5)
        logger.info(f"  {bank.split()[0]}: {', '.join(keywords)}")
    
    # Theme distribution
    logger.info("\n=== Theme Distribution ===")
    theme_counts = df['identified_theme'].value_counts()
    for theme, count in theme_counts.head(10).items():
        pct = count / len(df) * 100
        logger.info(f"  {theme}: {count} ({pct:.1f}%)")
    
    # Save results
    df.to_csv(output_file, index=False)
    logger.info(f"Saved thematic results to {output_file}")
    
    return df


if __name__ == "__main__":
    # Run thematic analysis only (assumes sentiment_results.csv already exists)
    print("\n" + "="*60)
    print("TASK 2: THEMATIC ANALYSIS")
    print("="*60)
    
    df_thematic = run_thematic_analysis()
    
    print("\n✅ Thematic Analysis Complete!")
