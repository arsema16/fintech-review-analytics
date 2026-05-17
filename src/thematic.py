import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ThemeExtractor:
    THEMES = {
        "TRANSACTION_SPEED": [
            "slow", "fast", "transfer", "loading", "timeout", "speed", 
            "processing", "wait", "instant", "quick"
        ],
        "LOGIN_ACCESS": [
            "login", "password", "otp", "fingerprint", "biometric",
            "access", "locked", "forgot", "sign in"
        ],
        "UI_UX": [
            "ui", "interface", "design", "layout", "navigation", "menu",
            "confusing", "intuitive", "user friendly"
        ],
        "CUSTOMER_SUPPORT": [
            "support", "help", "customer service", "agent", "complaint",
            "unresolved", "contact", "call"
        ],
        "STABILITY": [
            "crash", "freeze", "error", "bug", "glitch", "unstable",
            "force close", "not responding", "restart"
        ]
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words="english",
            ngram_range=(1, 2)
        )
    
    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text.lower()
    
    def extract_keywords_by_bank(self) -> dict:
        bank_keywords = {}
        
        for bank in self.df["bank"].unique():
            bank_reviews = self.df[self.df["bank"] == bank]["review"].tolist()
            bank_reviews_clean = [self.clean_text(r) for r in bank_reviews if r]
            
            if bank_reviews_clean:
                try:
                    tfidf_matrix = self.vectorizer.fit_transform(bank_reviews_clean)
                    feature_names = self.vectorizer.get_feature_names_out()
                    
                    avg_scores = tfidf_matrix.mean(axis=0).A1
                    top_indices = avg_scores.argsort()[-10:][::-1]
                    
                    keywords = [(feature_names[i], avg_scores[i]) for i in top_indices]
                    bank_keywords[bank] = keywords
                    logger.info(f"{bank}: Top keywords - {[k for k, _ in keywords[:5]]}")
                except Exception as e:
                    logger.warning(f"Could not extract keywords for {bank}: {e}")
                    bank_keywords[bank] = []
        
        return bank_keywords
    
    def assign_themes_to_reviews(self) -> pd.DataFrame:
        def get_review_theme(review_text):
            if not isinstance(review_text, str):
                return "OTHER"
            text_lower = review_text.lower()
            for theme, theme_words in self.THEMES.items():
                if any(word in text_lower for word in theme_words):
                    return theme
            return "OTHER"
        
        self.df["identified_theme"] = self.df["review"].apply(get_review_theme)
        return self.df
    
    def analyze_all_banks(self) -> pd.DataFrame:
        results = []
        keywords_by_bank = self.extract_keywords_by_bank()
        
        for bank, keywords in keywords_by_bank.items():
            results.append({
                "bank": bank,
                "top_keywords": ", ".join([k for k, _ in keywords[:5]]),
                "top_5_keywords": keywords[:5]
            })
        
        return pd.DataFrame(results)
    
    def get_theme_summary(self) -> pd.DataFrame:
        theme_summary = pd.crosstab(self.df['bank'], self.df['identified_theme'])
        return theme_summary


def main():
    try:
        df = pd.read_csv("data/sentiment_reviews.csv")
        logger.info(f"Loaded sentiment data with {len(df)} reviews")
    except FileNotFoundError:
        df = pd.read_csv("data/cleaned_reviews.csv")
        logger.info(f"Loaded cleaned data with {len(df)} reviews")
    
    extractor = ThemeExtractor(df)
    df = extractor.assign_themes_to_reviews()
    summary = extractor.analyze_all_banks()
    theme_counts = extractor.get_theme_summary()
    
    df.to_csv("data/thematic_reviews.csv", index=False)
    summary.to_csv("data/theme_summary.csv", index=False)
    
    logger.info("\nTheme Distribution by Bank:")
    print(theme_counts)
    
    return df, summary


if __name__ == "__main__":
    df, summary = main()
