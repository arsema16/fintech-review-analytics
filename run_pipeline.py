"""
Master Pipeline - Runs Tasks 1-4 End-to-End
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    print(f"✅ Completed: {description}")
    return True


def main():
    print("\n" + "="*60)
    print("COMPLETE PIPELINE: TASKS 1-4")
    print("="*60)
    
    # Check if cleaned data exists
    if not os.path.exists("data/cleaned_reviews.csv"):
        print("\n❌ Please run Task 1 first to generate data/cleaned_reviews.csv")
        print("   Run: python src/preprocess.py")
        return
    
    # Task 2: Sentiment Analysis
    if not run_command("python src/sentiment_analysis.py", "Task 2: Sentiment Analysis"):
        return
    
    # Task 2: Thematic Analysis
    if not run_command("python src/thematic_analysis.py", "Task 2: Thematic Analysis"):
        return
    
    # Task 3: PostgreSQL Database
    if not run_command("python src/postgres_loader.py", "Task 3: PostgreSQL Database"):
        print("\n⚠️ Task 3 skipped - PostgreSQL may not be installed")
        print("   Continue with Tasks 2 and 4 only")
    
    # Task 4: Insights and Visualizations
    if not run_command("python src/insights_visualizations.py", "Task 4: Insights & Visualizations"):
        return
    
    print("\n" + "="*60)
    print("🎉 ALL TASKS COMPLETE!")
    print("="*60)
    print("\nOutput files:")
    print("  - data/sentiment_results.csv")
    print("  - data/thematic_results.csv")
    print("  - fig1_sentiment_distribution.png")
    print("  - fig2_avg_rating_by_bank.png")
    print("  - fig3_sentiment_by_bank.png")
    print("  - fig4_theme_distribution.png")
    print("\nPostgreSQL database: bank_reviews")


if __name__ == "__main__":
    main()