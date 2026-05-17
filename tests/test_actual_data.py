import pandas as pd
import os
import pytest
import re

@pytest.mark.skipif(not os.path.exists('data/cleaned_reviews.csv'), reason="CSV file not in repo - data is gitignored")
def test_cleaned_data_exists():
    df = pd.read_csv('data/cleaned_reviews.csv')
    assert len(df) >= 1000
    print(f'✓ Cleaned data has {len(df)} reviews')

@pytest.mark.skipif(not os.path.exists('data/cleaned_reviews.csv'), reason="CSV file not in repo - data is gitignored")
def test_required_columns():
    df = pd.read_csv('data/cleaned_reviews.csv')
    required = ['review', 'rating', 'date', 'bank', 'source']
    for col in required:
        assert col in df.columns
    print('✓ All required columns present')

@pytest.mark.skipif(not os.path.exists('data/cleaned_reviews.csv'), reason="CSV file not in repo - data is gitignored")
def test_ratings_valid():
    df = pd.read_csv('data/cleaned_reviews.csv')
    assert df['rating'].between(1, 5).all()
    print('✓ All ratings valid (1-5)')

@pytest.mark.skipif(not os.path.exists('data/cleaned_reviews.csv'), reason="CSV file not in repo - data is gitignored")
def test_no_empty_reviews():
    df = pd.read_csv('data/cleaned_reviews.csv')
    assert df['review'].notna().all()
    assert (df['review'].str.len() > 0).all()
    print('✓ No empty reviews')

@pytest.mark.skipif(not os.path.exists('data/cleaned_reviews.csv'), reason="CSV file not in repo - data is gitignored")
def test_dates_format():
    df = pd.read_csv('data/cleaned_reviews.csv')
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    assert df['date'].astype(str).str.match(pattern).all()
    print('✓ Dates in YYYY-MM-DD format')