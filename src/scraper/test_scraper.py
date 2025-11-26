"""
Quick test script to verify the scraper works
Scrapes only 2 pages (~40 books) for testing
"""

import sys
from books_scraper import BooksToScrapeScraper

def main():
    """Test scraper with just 2 pages"""
    print("Books to Scrape - TEST RUN (2 pages only)")
    print("=" * 60)
    
    # Initialize scraper
    scraper = BooksToScrapeScraper(delay=0.3)
    
    # Scrape only 2 pages for testing
    df = scraper.scrape_all_books(max_pages=2)
    
    # Save to CSV
    filepath = scraper.save_to_csv(df)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("TEST SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Total books scraped: {len(df)}")
    print(f"Categories found: {df['category'].nunique()}")
    print(f"Price range: £{df['price_gbp'].min():.2f} - £{df['price_gbp'].max():.2f}")
    print(f"Average price: £{df['price_gbp'].mean():.2f}")
    print(f"Books with descriptions: {df['description'].notna().sum()}")
    print(f"Average rating: {df['rating'].mean():.1f}")
    print("=" * 60)
    
    # Show first few books
    print("\nFirst 3 books:")
    print("-" * 60)
    for idx in range(min(3, len(df))):
        book = df.iloc[idx]
        print(f"{idx+1}. {book['title']}")
        print(f"   Category: {book['category']}")
        print(f"   Price: £{book['price_gbp']:.2f} | Rating: {book['rating']} stars")
        print(f"   UPC: {book['upc']}")
        print("-" * 60)
    
    print("\n✅ Test completed successfully!")
    print(f"Data saved to: {filepath}")
    print("\nTo scrape all books, run: python books_scraper.py")
    
    return df

if __name__ == "__main__":
    df = main()

