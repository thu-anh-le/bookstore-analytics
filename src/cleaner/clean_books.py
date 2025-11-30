"""
Data Cleaning Script for Books to Scrape
Cleans and validates the scraped book data with specific requirements:
- Handle missing descriptions
- Clean description text (remove "...more", extra whitespace)
- Convert GBP to USD
- Remove duplicates
- Validate data types
- Standardize categories (Default -> Adult)
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import os
import requests


class BookDataCleaner:
    """Clean and validate book data from web scraping"""
    
    def __init__(self, input_file, gbp_to_usd_rate=None):
        """
        Initialize the cleaner
        
        Args:
            input_file: Path to the raw CSV file
            gbp_to_usd_rate: Exchange rate (if None, will fetch current rate)
        """
        self.input_file = input_file
        self.df = None
        self.gbp_to_usd_rate = gbp_to_usd_rate
        self.cleaning_report = {
            'initial_rows': 0,
            'final_rows': 0,
            'duplicates_removed': 0,
            'missing_descriptions_filled': 0,
            'descriptions_cleaned': 0,
            'categories_changed': 0,
            'exchange_rate': 0
        }
    
    def load_data(self):
        """Load the raw CSV data"""
        print("Loading data...")
        self.df = pd.read_csv(self.input_file)
        self.cleaning_report['initial_rows'] = len(self.df)
        print(f"✓ Loaded {len(self.df)} rows")
        return self
    
    def check_missing_values(self):
        """Report missing values before cleaning"""
        print("\n" + "=" * 60)
        print("MISSING VALUES REPORT (BEFORE CLEANING)")
        print("=" * 60)
        
        # Check for NaN values
        missing = self.df.isnull().sum()
        
        # Check for empty strings
        for col in ['description', 'category', 'upc']:
            if col in self.df.columns:
                empty = (self.df[col] == '').sum()
                nan_count = missing[col]
                total_missing = empty + nan_count
                if total_missing > 0:
                    print(f"{col}: {total_missing} missing ({(total_missing/len(self.df)*100):.1f}%)")
                    print(f"  - NaN: {nan_count}, Empty strings: {empty}")
        
        return self
    
    def remove_duplicates(self):
        """Remove duplicate books based on title and UPC"""
        print("\n" + "=" * 60)
        print("REMOVING DUPLICATES")
        print("=" * 60)
        
        initial_count = len(self.df)
        
        # Remove exact duplicates based on title and UPC
        self.df = self.df.drop_duplicates(subset=['title', 'upc'], keep='first')
        
        duplicates_removed = initial_count - len(self.df)
        self.cleaning_report['duplicates_removed'] = duplicates_removed
        
        if duplicates_removed > 0:
            print(f"✓ Removed {duplicates_removed} duplicate records")
        else:
            print("✓ No duplicates found")
        
        return self
    
    def handle_missing_descriptions(self):
        """Handle missing descriptions"""
        print("\n" + "=" * 60)
        print("HANDLING MISSING DESCRIPTIONS")
        print("=" * 60)
        
        # Count missing (NaN or empty strings)
        missing_mask = self.df['description'].isna() | (self.df['description'] == '')
        missing_count = missing_mask.sum()
        
        print(f"Found {missing_count} books without descriptions")
        
        # Fill missing descriptions with a placeholder
        self.df.loc[missing_mask, 'description'] = "Description not available"
        
        self.cleaning_report['missing_descriptions_filled'] = missing_count
        print(f"✓ Filled {missing_count} missing descriptions with placeholder text")
        
        return self
    
    def clean_descriptions(self):
        """Clean description text - remove '...more' and extra whitespace"""
        print("\n" + "=" * 60)
        print("CLEANING DESCRIPTION TEXT")
        print("=" * 60)
        
        cleaned_count = 0
        
        def clean_desc(text):
            if pd.isna(text) or text == "Description not available":
                return text
            
            nonlocal cleaned_count
            original = text
            
            # Remove "...more" at the end (with optional whitespace)
            text = re.sub(r'\s*\.\.\.more\s*$', '', text, flags=re.IGNORECASE)
            
            # Remove extra whitespace (multiple spaces, tabs, newlines)
            text = ' '.join(text.split())
            
            # Remove multiple periods (more than 3)
            text = re.sub(r'\.{4,}', '...', text)
            
            if text != original:
                cleaned_count += 1
            
            return text.strip()
        
        self.df['description'] = self.df['description'].apply(clean_desc)
        
        self.cleaning_report['descriptions_cleaned'] = cleaned_count
        print(f"✓ Cleaned text in {cleaned_count} descriptions")
        print("  - Removed '...more' suffixes")
        print("  - Removed extra whitespace")
        
        return self
    
    def fetch_exchange_rate(self):
        """Fetch current GBP to USD exchange rate"""
        if self.gbp_to_usd_rate is not None:
            print(f"Using provided exchange rate: 1 GBP = {self.gbp_to_usd_rate} USD")
            return self.gbp_to_usd_rate
        
        print("Fetching current GBP to USD exchange rate...")
        
        try:
            # Try Open Exchange Rates API (free, no key required)
            response = requests.get('https://open.er-api.com/v6/latest/GBP', timeout=10)
            data = response.json()
            
            if data['result'] == 'success':
                rate = data['rates']['USD']
                print(f"✓ Current rate: 1 GBP = {rate:.4f} USD")
                self.gbp_to_usd_rate = rate
                return rate
        except Exception as e:
            print(f"Warning: Could not fetch exchange rate: {e}")
        
        # Fallback to approximate rate (as of Nov 2025)
        fallback_rate = 1.27
        print(f"Using fallback rate: 1 GBP = {fallback_rate} USD")
        self.gbp_to_usd_rate = fallback_rate
        return fallback_rate
    
    def convert_to_usd(self):
        """Convert GBP prices to USD"""
        print("\n" + "=" * 60)
        print("CONVERTING GBP TO USD")
        print("=" * 60)
        
        # Fetch exchange rate
        rate = self.fetch_exchange_rate()
        self.cleaning_report['exchange_rate'] = rate
        
        # Create new USD column
        self.df['price_usd'] = (self.df['price_gbp'] * rate).round(2)
        
        print(f"✓ Created 'price_usd' column")
        print(f"  Example: £{self.df['price_gbp'].iloc[0]:.2f} = ${self.df['price_usd'].iloc[0]:.2f}")
        
        return self
    
    def standardize_categories(self):
        """Standardize categories - change 'Default' to 'Adult'"""
        print("\n" + "=" * 60)
        print("STANDARDIZING CATEGORIES")
        print("=" * 60)
        
        # Count 'Default' categories before change
        default_count = (self.df['category'] == 'Default').sum()
        
        if default_count > 0:
            print(f"Found {default_count} books with 'Default' category")
            
            # Replace 'Default' with 'Adult'
            self.df['category'] = self.df['category'].replace('Default', 'Adult')
            
            self.cleaning_report['categories_changed'] = default_count
            print(f"✓ Changed {default_count} 'Default' categories to 'Adult'")
        else:
            print("✓ No 'Default' categories found")
        
        # Handle empty categories
        empty_categories = (self.df['category'] == '').sum() + self.df['category'].isna().sum()
        if empty_categories > 0:
            self.df.loc[self.df['category'].isna() | (self.df['category'] == ''), 'category'] = 'Uncategorized'
            print(f"✓ Filled {empty_categories} empty categories with 'Uncategorized'")
        
        print(f"\nTotal unique categories: {self.df['category'].nunique()}")
        print("Top 5 categories:")
        print(self.df['category'].value_counts().head())
        
        return self
    
    def validate_datatypes(self):
        """Validate and convert data types"""
        print("\n" + "=" * 60)
        print("VALIDATING DATA TYPES")
        print("=" * 60)
        
        # Ensure numeric columns are proper types
        numeric_cols = ['price_gbp', 'price_usd', 'rating', 'stock_quantity']
        
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # String columns
        string_cols = ['title', 'category', 'availability', 'upc', 'product_page_url', 'description']
        for col in string_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str)
        
        print("✓ Data types validated:")
        print(f"  - Numeric: {', '.join(numeric_cols)}")
        print(f"  - String: {', '.join(string_cols)}")
        
        # Check for any conversion issues
        issues = []
        for col in numeric_cols:
            if col in self.df.columns and self.df[col].isna().any():
                na_count = self.df[col].isna().sum()
                issues.append(f"{col}: {na_count} NaN values")
        
        if issues:
            print("\nWarnings:")
            for issue in issues:
                print(f"  - {issue}")
        
        return self
    
    def add_derived_columns(self):
        """Add useful derived columns"""
        print("\n" + "=" * 60)
        print("ADDING DERIVED COLUMNS")
        print("=" * 60)
        
        # Add availability status (boolean)
        self.df['in_stock'] = self.df['availability'].str.contains('In stock', case=False, na=False)
        
        # Price category based on USD price
        self.df['price_category_usd'] = pd.cut(
            self.df['price_usd'],
            bins=[0, 25, 45, 65, 150],
            labels=['Budget', 'Mid-range', 'Premium', 'Luxury']
        )
        
        print("✓ Added derived columns:")
        print("  - in_stock (boolean)")
        print("  - price_category_usd (Budget/Mid-range/Premium/Luxury)")
        
        return self
    
    def get_summary_statistics(self):
        """Print summary statistics"""
        print("\n" + "=" * 60)
        print("DATA SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total books: {len(self.df)}")
        print(f"\nPrice (GBP):")
        print(f"  Range: £{self.df['price_gbp'].min():.2f} - £{self.df['price_gbp'].max():.2f}")
        print(f"  Average: £{self.df['price_gbp'].mean():.2f}")
        print(f"  Median: £{self.df['price_gbp'].median():.2f}")
        print(f"\nPrice (USD):")
        print(f"  Range: ${self.df['price_usd'].min():.2f} - ${self.df['price_usd'].max():.2f}")
        print(f"  Average: ${self.df['price_usd'].mean():.2f}")
        print(f"  Median: ${self.df['price_usd'].median():.2f}")
        print(f"\nRating distribution:")
        print(self.df['rating'].value_counts().sort_index())
        print(f"\nCategories: {self.df['category'].nunique()} unique")
        print(f"Books in stock: {self.df['in_stock'].sum()} ({self.df['in_stock'].mean()*100:.1f}%)")
        
        return self
    
    def save_cleaned_data(self, output_dir=None):
        """Save cleaned data to CSV"""
        print("\n" + "=" * 60)
        print("SAVING CLEANED DATA")
        print("=" * 60)
        
        # Use absolute path relative to project root if not provided
        if output_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            output_dir = os.path.join(project_root, 'src', 'cleaner', 'data', 'clean')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"books_clean_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Reorder columns for better readability
        column_order = [
            'title',
            'category',
            'price_gbp',
            'price_usd',
            'price_category_usd',
            'rating',
            'availability',
            'in_stock',
            'stock_quantity',
            'upc',
            'product_page_url',
            'description'
        ]
        
        # Reorder (only include columns that exist)
        column_order = [col for col in column_order if col in self.df.columns]
        self.df = self.df[column_order]
        
        # Save to CSV
        self.df.to_csv(filepath, index=False, encoding='utf-8')
        
        self.cleaning_report['final_rows'] = len(self.df)
        
        print(f"✓ Cleaned data saved to: {filepath}")
        print(f"✓ Total rows: {len(self.df)}")
        print(f"✓ Total columns: {len(self.df.columns)}")
        
        return filepath
    
    def print_cleaning_report(self):
        """Print final cleaning report"""
        print("\n" + "=" * 60)
        print("DATA CLEANING REPORT")
        print("=" * 60)
        print(f"Initial rows: {self.cleaning_report['initial_rows']}")
        print(f"Duplicates removed: {self.cleaning_report['duplicates_removed']}")
        print(f"Final rows: {self.cleaning_report['final_rows']}")
        print(f"\nDescription handling:")
        print(f"  - Missing descriptions filled: {self.cleaning_report['missing_descriptions_filled']}")
        print(f"  - Descriptions cleaned: {self.cleaning_report['descriptions_cleaned']}")
        print(f"\nCurrency conversion:")
        print(f"  - Exchange rate used: 1 GBP = {self.cleaning_report['exchange_rate']:.4f} USD")
        print(f"  - USD prices added: {self.cleaning_report['final_rows']}")
        print(f"\nCategory standardization:")
        print(f"  - 'Default' changed to 'Adult': {self.cleaning_report['categories_changed']}")
        print("=" * 60)
        
        return self
    
    def clean_all(self):
        """Run all cleaning steps"""
        self.load_data()
        self.check_missing_values()
        self.remove_duplicates()
        self.handle_missing_descriptions()
        self.clean_descriptions()
        self.convert_to_usd()
        self.standardize_categories()
        self.validate_datatypes()
        self.add_derived_columns()
        self.get_summary_statistics()
        filepath = self.save_cleaned_data()
        self.print_cleaning_report()
        
        return self.df, filepath


def main():
    """Main execution function"""
    print("=" * 60)
    print("BOOKS TO SCRAPE - DATA CLEANING")
    print("=" * 60)
    
    # Get the script's directory and construct path relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, 'src', 'scraper', 'data', 'raw', 'books_raw_20251129.csv')
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        print(f"Project root: {project_root}")
        return None
    
    # Initialize cleaner (you can provide a custom exchange rate if needed)
    # cleaner = BookDataCleaner(input_file, gbp_to_usd_rate=1.27)
    cleaner = BookDataCleaner(input_file)
    
    # Run all cleaning steps
    df_clean, output_file = cleaner.clean_all()
    
    print(f"\n{'='*60}")
    print("✓ DATA CLEANING COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ Clean data saved to: {output_file}")
    print(f"✓ Ready for analysis!")
    
    return df_clean


if __name__ == "__main__":
    df = main()

