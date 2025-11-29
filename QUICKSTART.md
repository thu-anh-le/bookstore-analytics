# Quick Start Guide

## Setup Complete! ✅

Your Books to Scrape analytics project is ready to go. Here's what's been set up:

### ✅ Completed Setup Steps

1. **Project Structure Created**
   - `data/raw/` - for storing scraped data
   - `docs/` - documentation including scraping notes
   - `src/scraper/` - scraper implementation
   - `notebooks/` - data exploration scripts

2. **Virtual Environment**
   - `.venv/` created
   - All dependencies installed:
     - requests
     - beautifulsoup4
     - pandas
     - lxml

3. **Scraper Implementation**
   - Full-featured scraper: `src/scraper/books_scraper.py`
   - Test scraper (2 pages only): `src/scraper/test_scraper.py`
   - Handles pagination, detail pages, error handling

4. **Documentation**
   - `docs/scraping-notes.md` - website structure analysis
   - `README.md` - comprehensive project documentation
   - This quickstart guide

5. **Exploration Tools**
   - `notebooks/exploration_template.py` - data sanity checks

## Running the Scraper

### Option 1: Test Run (Quick - 2 pages, ~40 books, 1-2 minutes)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run test scraper
cd src/scraper
python test_scraper.py
```

This will scrape just 2 pages to verify everything works correctly.

### Option 2: Full Scrape (Complete - 50 pages, ~1000 books, 8-10 minutes)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run full scraper
cd src/scraper
python books_scraper.py
```

This will scrape all 1000 books from the website.

### What the Scraper Does

1. **Scrapes listing pages** (page-1.html through page-50.html)
   - Extracts: title, price, rating, availability, product URL

2. **Visits each product detail page**
   - Extracts: UPC, category, description

3. **Saves to CSV**
   - Location: `data/raw/books_raw_YYYYMMDD.csv`
   - Format: UTF-8 encoded CSV with headers

4. **Displays summary statistics**
   - Total books, categories, price ranges, etc.

### Features

- ✅ **Rate limiting**: 0.5s delay between requests (respectful scraping)
- ✅ **Error handling**: Gracefully handles missing data
- ✅ **Progress tracking**: Shows progress as it scrapes
- ✅ **Data validation**: Cleans prices, ratings, stock quantities
- ✅ **Timestamped output**: Each run creates a new CSV file

## After Scraping

### Explore the Data

```bash
# Run exploration script
cd notebooks
python exploration_template.py
```

This will show:
- Basic data statistics
- Category distribution
- Price analysis
- Rating distribution
- Data quality checks
- Sample records

### Expected Output

The CSV will contain these columns:

| Column | Description | Example |
|--------|-------------|---------|
| title | Book title | "A Light in the Attic" |
| category | Book category | "Poetry" |
| price_gbp | Price in GBP | 51.77 |
| rating | Rating (1-5 stars) | 3 |
| availability | Stock text | "In stock (22 available)" |
| stock_quantity | Number in stock | 22 |
| upc | Product code | "a897fe39b1053632" |
| product_page_url | Detail page URL | "https://books.toscrape.com/..." |
| description | Book description | "It's hard to imagine..." |

### Data Quality Expectations

- **Total books**: ~1000
- **Unique categories**: 50+
- **Price range**: £10-£60
- **All books have**: title, price, rating, UPC, category
- **Some books missing**: descriptions (~50% coverage)
- **No duplicates**: Each UPC is unique

## Troubleshooting

### If scraper fails to start:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Verify dependencies
pip list | grep -E "requests|beautifulsoup|pandas"
```

### If getting connection errors:

- Check internet connection
- The website might be temporarily down
- Try again in a few minutes

### If scraper is too slow:

Edit `books_scraper.py` and reduce the delay:
```python
scraper = BooksToScrapeScraper(delay=0.3)  # Change from 0.5 to 0.3
```

## Next Steps

1. **Run the scraper** (test or full)
2. **Explore the data** using the exploration script
3. **Set up SQL Server** for data storage
4. **Load data into database**
5. **Perform SQL analysis**
6. **Build Power BI dashboard**

## Project Status

- ✅ Phase 1: Web Scraping Setup (COMPLETE)
- 🔲 Phase 2: SQL Server Setup
- 🔲 Phase 3: Data Loading
- 🔲 Phase 4: Analysis
- 🔲 Phase 5: Dashboard

## Need Help?

- See `README.md` for detailed documentation
- See `docs/scraping-notes.md` for website structure details
- Check the code comments in `src/scraper/books_scraper.py`

---

**Ready to scrape?** Run: `source .venv/bin/activate && cd src/scraper && python test_scraper.py`

