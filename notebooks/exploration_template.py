"""
Books to Scrape - Data Exploration Script
Run this in a Jupyter notebook or as a standalone script
"""

import pandas as pd
import os

# Load the most recent CSV file
data_dir = '../data/raw'
csv_files = [f for f in os.listdir(data_dir) if f.startswith('books_raw_') and f.endswith('.csv')]
csv_files.sort(reverse=True)

if csv_files:
    latest_file = csv_files[0]
    filepath = os.path.join(data_dir, latest_file)
    print(f"Loading: {filepath}")
    df = pd.read_csv(filepath)
    print(f"\nLoaded {len(df)} rows\n")
    
    # 1. Basic inspection
    print("=" * 60)
    print("FIRST 5 ROWS:")
    print("=" * 60)
    print(df.head())
    
    # 2. Data info
    print("\n" + "=" * 60)
    print("DATA INFO:")
    print("=" * 60)
    print(df.info())
    
    # 3. Category analysis
    print("\n" + "=" * 60)
    print("TOP 10 CATEGORIES BY BOOK COUNT:")
    print("=" * 60)
    print(df['category'].value_counts().head(10))
    
    # 4. Price statistics
    print("\n" + "=" * 60)
    print("PRICE STATISTICS (GBP):")
    print("=" * 60)
    print(df['price_gbp'].describe())
    
    # 5. Rating distribution
    print("\n" + "=" * 60)
    print("RATING DISTRIBUTION:")
    print("=" * 60)
    print(df['rating'].value_counts().sort_index())
    print(f"\nAverage Rating: {df['rating'].mean():.2f}")
    
    # 6. Availability
    print("\n" + "=" * 60)
    print("AVAILABILITY ANALYSIS:")
    print("=" * 60)
    stock_df = df[df['stock_quantity'] > 0]
    print(f"Books with known stock: {len(stock_df)}")
    print(f"Books with unknown stock (-1): {(df['stock_quantity'] == -1).sum()}")
    print(f"Books out of stock (0): {(df['stock_quantity'] == 0).sum()}")
    
    # 7. Description coverage
    print("\n" + "=" * 60)
    print("DESCRIPTION COVERAGE:")
    print("=" * 60)
    has_description = df['description'].notna() & (df['description'] != '')
    print(f"Books with descriptions: {has_description.sum()} ({has_description.sum()/len(df)*100:.1f}%)")
    print(f"Books without descriptions: {(~has_description).sum()} ({(~has_description).sum()/len(df)*100:.1f}%)")
    
    # 8. Data quality checks
    print("\n" + "=" * 60)
    print("DATA QUALITY CHECKS:")
    print("=" * 60)
    print(f"Total rows: {len(df)}")
    print(f"Duplicate titles: {df['title'].duplicated().sum()}")
    print(f"Duplicate UPCs: {df['upc'].duplicated().sum()}")
    print(f"Missing categories: {df['category'].isna().sum()}")
    print(f"Missing UPCs: {df['upc'].isna().sum() + (df['upc'] == '').sum()}")
    print(f"Zero prices: {(df['price_gbp'] == 0).sum()}")
    print(f"Zero ratings: {(df['rating'] == 0).sum()}")
    
    # 9. Sample records
    print("\n" + "=" * 60)
    print("SAMPLE RECORDS (3 random books):")
    print("=" * 60)
    for idx in df.sample(min(3, len(df))).index:
        book = df.loc[idx]
        print(f"\nTitle: {book['title']}")
        print(f"Category: {book['category']}")
        print(f"Price: £{book['price_gbp']:.2f}")
        print(f"Rating: {book['rating']} stars")
        print(f"UPC: {book['upc']}")
        print(f"Stock: {book['availability']}")
        desc = book['description'][:100] if book['description'] else 'N/A'
        print(f"Description: {desc}...")
        print("-" * 60)
    
else:
    print("No CSV files found. Please run the scraper first.")

