"""
Books to Scrape - Web Scraper
Scrapes book data from https://books.toscrape.com/

This scraper extracts:
- Book title, price, rating, availability
- Category, UPC, product description
- Saves to CSV with timestamp
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import os


class BooksToScrapeScraper:
    """Scraper for Books to Scrape website"""
    
    BASE_URL = "https://books.toscrape.com"
    CATALOGUE_URL = f"{BASE_URL}/catalogue"
    
    # Rating mapping from CSS class to numeric value
    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    
    def __init__(self, delay: float = 0.5):
        """
        Initialize the scraper
        
        Args:
            delay: Delay between requests in seconds (default 0.5)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)  # Be respectful
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_rating(self, product_card) -> int:
        """
        Extract rating from product card
        
        Args:
            product_card: BeautifulSoup element for product
            
        Returns:
            Rating as integer (1-5), or 0 if not found
        """
        rating_element = product_card.find('p', class_='star-rating')
        if rating_element:
            # Get the second class which contains the rating word
            classes = rating_element.get('class', [])
            for cls in classes:
                if cls in self.RATING_MAP:
                    return self.RATING_MAP[cls]
        return 0
    
    def extract_price(self, price_text: str) -> float:
        """
        Extract numeric price from price string
        
        Args:
            price_text: Price string like "£51.77"
            
        Returns:
            Price as float
        """
        # Remove £ symbol and convert to float
        price_cleaned = re.sub(r'[£,]', '', price_text)
        try:
            return float(price_cleaned)
        except ValueError:
            return 0.0
    
    def extract_stock_quantity(self, availability_text: str) -> int:
        """
        Extract stock quantity from availability text
        
        Args:
            availability_text: Text like "In stock (22 available)"
            
        Returns:
            Stock quantity as integer, or 0 if not found
        """
        match = re.search(r'\((\d+) available\)', availability_text)
        if match:
            return int(match.group(1))
        # If just says "In stock" without number, return -1 to indicate unknown quantity
        if "In stock" in availability_text:
            return -1
        return 0
    
    def scrape_product_list_page(self, page_num: int) -> List[Dict]:
        """
        Scrape a single listing page
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            List of book data dictionaries
        """
        if page_num == 1:
            url = f"{self.CATALOGUE_URL}/page-1.html"
        else:
            url = f"{self.CATALOGUE_URL}/page-{page_num}.html"
        
        print(f"Scraping page {page_num}: {url}")
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        books = []
        product_cards = soup.find_all('article', class_='product_pod')
        
        for card in product_cards:
            try:
                # Extract basic info from listing page
                title_element = card.find('h3').find('a')
                title = title_element.get('title', '')
                
                # Get product page URL
                product_link = title_element.get('href', '')
                # Handle both relative paths (../../../) and catalogue paths
                if product_link.startswith('../../../'):
                    product_url = f"{self.BASE_URL}/catalogue/{product_link.replace('../../../', '')}"
                else:
                    product_url = f"{self.CATALOGUE_URL}/{product_link}"
                
                # Price
                price_element = card.find('p', class_='price_color')
                price_text = price_element.text if price_element else '£0'
                price = self.extract_price(price_text)
                
                # Rating
                rating = self.extract_rating(card)
                
                # Availability
                availability_element = card.find('p', class_='availability')
                availability_text = availability_element.text.strip() if availability_element else ''
                stock_quantity = self.extract_stock_quantity(availability_text)
                
                book_data = {
                    'title': title,
                    'price_gbp': price,
                    'rating': rating,
                    'availability': availability_text,
                    'stock_quantity': stock_quantity,
                    'product_page_url': product_url,
                }
                
                books.append(book_data)
                
            except Exception as e:
                print(f"Error parsing product card: {e}")
                continue
        
        return books
    
    def scrape_product_detail_page(self, book_data: Dict) -> Dict:
        """
        Scrape product detail page and add additional info
        
        Args:
            book_data: Dictionary with basic book info including product_page_url
            
        Returns:
            Updated book_data dictionary with additional fields
        """
        url = book_data['product_page_url']
        soup = self.get_page(url)
        
        if not soup:
            book_data['upc'] = ''
            book_data['category'] = ''
            book_data['description'] = ''
            return book_data
        
        try:
            # Extract UPC from product information table
            table = soup.find('table', class_='table-striped')
            upc = ''
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td and th.text.strip() == 'UPC':
                        upc = td.text.strip()
                        break
            
            book_data['upc'] = upc
            
            # Extract category from breadcrumb
            breadcrumb = soup.find('ul', class_='breadcrumb')
            category = ''
            if breadcrumb:
                category_links = breadcrumb.find_all('a')
                if len(category_links) >= 3:
                    # Third link is usually the category (Books > Category > Title)
                    category = category_links[2].text.strip()
            
            book_data['category'] = category
            
            # Extract product description
            description = ''
            # Try to find description after the product_description id
            desc_header = soup.find('div', id='product_description')
            if desc_header:
                desc_p = desc_header.find_next_sibling('p')
                if desc_p:
                    description = desc_p.text.strip()
            
            book_data['description'] = description
            
            # Extract availability with quantity from detail page
            # Detail pages have the full text like "In stock (22 available)"
            # while listing pages only have "In stock"
            availability_element = soup.find('p', class_='availability')
            if availability_element:
                availability_text = availability_element.text.strip()
                # Update both availability text and stock quantity from detail page
                book_data['availability'] = availability_text
                book_data['stock_quantity'] = self.extract_stock_quantity(availability_text)
            
        except Exception as e:
            print(f"Error parsing detail page {url}: {e}")
            book_data['upc'] = ''
            book_data['category'] = ''
            book_data['description'] = ''
        
        return book_data
    
    def scrape_all_books(self, max_pages: int = 50) -> pd.DataFrame:
        """
        Scrape all books from the website
        
        Args:
            max_pages: Maximum number of pages to scrape (default 50)
            
        Returns:
            DataFrame with all book data
        """
        all_books = []
        
        print(f"Starting to scrape {max_pages} pages...")
        print("=" * 60)
        
        # Scrape all listing pages
        for page_num in range(1, max_pages + 1):
            books_on_page = self.scrape_product_list_page(page_num)
            
            if not books_on_page:
                print(f"No books found on page {page_num}, stopping.")
                break
            
            print(f"Found {len(books_on_page)} books on page {page_num}")
            all_books.extend(books_on_page)
        
        print("=" * 60)
        print(f"Total books from listing pages: {len(all_books)}")
        print("=" * 60)
        
        # Now scrape detail pages for each book
        print("Scraping detail pages for additional information...")
        for i, book in enumerate(all_books, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(all_books)} detail pages scraped...")
            
            self.scrape_product_detail_page(book)
        
        print("=" * 60)
        print(f"Completed scraping all {len(all_books)} books!")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_books)
        
        # Reorder columns for better readability
        column_order = [
            'title',
            'category',
            'price_gbp',
            'rating',
            'availability',
            'stock_quantity',
            'upc',
            'product_page_url',
            'description'
        ]
        
        df = df[column_order]
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_dir: str = 'data/raw') -> str:
        """
        Save DataFrame to CSV with timestamp
        
        Args:
            df: DataFrame to save
            output_dir: Directory to save CSV (default: data/raw)
            
        Returns:
            Path to saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"books_raw_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Data saved to: {filepath}")
        print(f"Total rows: {len(df)}")
        
        return filepath


def main():
    """Main execution function"""
    print("Books to Scrape - Data Collection")
    print("=" * 60)
    
    # Initialize scraper
    scraper = BooksToScrapeScraper(delay=0.5)
    
    # Scrape all books
    df = scraper.scrape_all_books(max_pages=10)
    
    # Save to CSV
    filepath = scraper.save_to_csv(df)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Total books scraped: {len(df)}")
    print(f"Categories found: {df['category'].nunique()}")
    print(f"Price range: £{df['price_gbp'].min():.2f} - £{df['price_gbp'].max():.2f}")
    print(f"Average price: £{df['price_gbp'].mean():.2f}")
    print(f"Books with descriptions: {df['description'].notna().sum()}")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    df = main()

