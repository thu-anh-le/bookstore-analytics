# Book Store Analytics Dashboard

Web scraping, data analysis, and dashboard project using Books to Scrape.

## Project Overview

This project demonstrates a complete data analytics pipeline:
1. **Web Scraping**: Scrape book data from [Books to Scrape](https://books.toscrape.com/)
2. **Data Storage**: Store data in SQL Server
3. **Data Analysis**: Analyze data using Python/Pandas
4. **Visualization**: Create interactive dashboards in Power BI

## Data Source

**Books to Scrape** (https://books.toscrape.com/) is a demo website explicitly designed for web scraping practice. The site states "We love being scraped!" and contains ~1000 books with realistic ecommerce data.

### Data Collected:
- Book title
- Price (GBP)
- Rating (1-5 stars)
- Stock availability
- Category
- UPC (Universal Product Code)
- Product description
- Product page URL

## Project Structure

```
bookstore-analytics/
├── data/
│   └── raw/              # Raw scraped data (CSV files)
├── docs/                 # Documentation
│   └── scraping-notes.md # Web scraping documentation
├── notebooks/            # Jupyter notebooks for exploration
│   └── exploration_template.py
├── src/
│   └── scraper/          # Web scraping code
│       ├── __init__.py
│       └── books_scraper.py
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Scraper

```bash
# From project root
cd src/scraper
python books_scraper.py
```

The scraper will:
- Crawl all 50 pages (~1000 books)
- Extract data from listing and detail pages
- Save to `data/raw/books_raw_YYYYMMDD.csv`
- Display summary statistics

**Expected runtime**: ~8-10 minutes (with 0.5s delay between requests)

### 4. Explore the Data

```bash
# Run exploration script
cd notebooks
python exploration_template.py
```

Or use Jupyter notebook for interactive analysis:
```bash
jupyter notebook exploration.ipynb
```

## Features

### Web Scraper (`src/scraper/books_scraper.py`)

- **Pagination handling**: Automatically crawls all 50 pages
- **Detail page scraping**: Visits each book's detail page for additional info
- **Rate limiting**: Respectful 0.5s delay between requests
- **Error handling**: Graceful handling of missing data
- **Data validation**: Extracts and cleans prices, ratings, stock quantities
- **CSV export**: Saves data with timestamp for version control

### Data Schema

| Column | Type | Description |
|--------|------|-------------|
| title | str | Book title |
| category | str | Book category/genre |
| price_gbp | float | Price in British Pounds |
| rating | int | Rating (1-5 stars) |
| availability | str | Stock availability text |
| stock_quantity | int | Number of units in stock |
| upc | str | Universal Product Code |
| product_page_url | str | URL to product detail page |
| description | str | Book description (nullable) |

## Data Quality

- **Total books**: ~1000
- **Categories**: 50+ unique categories
- **Price range**: £10-£60 GBP
- **All books have**: title, price, rating, UPC, category
- **Some books missing**: descriptions (~50% have descriptions)

## Next Steps

1. ✅ Web scraping (Complete)
2. 🔲 Set up SQL Server database
3. 🔲 Create ETL pipeline to load data into SQL Server
4. 🔲 Perform SQL-based analysis
5. 🔲 Build Power BI dashboard
6. 🔲 Implement data refresh automation

## Requirements

- Python 3.8+
- See `requirements.txt` for Python packages
- SQL Server (for future phases)
- Power BI Desktop (for dashboard phase)

## Legal & Ethics

Books to Scrape is explicitly designed for web scraping practice and education. The website states:
> "Warning! This is a demo website for web scraping purposes. Use it to learn web scraping."

No real products, prices, or commercial data is involved.

## License

Educational project - use for learning purposes.

