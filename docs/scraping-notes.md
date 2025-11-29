# Books to Scrape - Web Scraping Notes

## Website Overview
- **Main URL**: https://books.toscrape.com/
- **Purpose**: Demo website for web scraping practice
- **Legal Status**: Explicitly allows scraping ("We love being scraped!")

## Website Structure

### Listing Pages (Pagination)
- **URL Pattern**: `/catalogue/page-{N}.html` where N = 1 to 50
- **First page**: https://books.toscrape.com/index.html or `/catalogue/page-1.html`
- **Total Books**: ~1000 books (20 books per page, 50 pages)
- **Pagination**: "next" button available at bottom of each page

### Product Cards (on listing pages)
Each product card contains:
- **Title**: Book title (in `<h3><a>` tag)
- **Price**: In GBP (£), e.g., "£51.77"
- **Rating**: CSS class format like `star-rating Three` → maps to 1-5 stars
- **Availability**: Text like "In stock (22 available)"
- **Link**: Relative URL to product detail page

### Product Detail Pages
Each product detail page includes:
- **UPC**: Universal Product Code
- **Product Type**: Usually "Books"
- **Price (excl. tax)**: Price without tax
- **Price (incl. tax)**: Price with tax
- **Tax**: Tax amount
- **Availability**: Stock information
- **Number of reviews**: Review count
- **Category**: From breadcrumb navigation (e.g., Books > Fiction > Classics)
- **Product Description**: Paragraph of text (if available, not all books have this)

## Data to Extract

### From Listing Page:
1. Title
2. Price (GBP)
3. Rating (1-5 stars)
4. Availability text
5. Product page URL

### From Detail Page:
6. UPC
7. Category (from breadcrumb)
8. Product description
9. Additional validation of price/availability

## CSS Selectors & HTML Structure

### Listing Page Selectors:
- Product cards: `article.product_pod`
- Title: `h3 > a` (title attribute or text)
- Price: `.price_color`
- Rating: `.star-rating` (class name contains rating)
- Availability: `.availability`
- Product link: `h3 > a[href]`

### Detail Page Selectors:
- UPC: Table row with `th:contains("UPC")`
- Category: Breadcrumb `.breadcrumb li:nth-child(3) a`
- Description: `#product_description + p` or `.product_page > p`
- Product info table: `.table.table-striped`

## Implementation Notes

1. **Rate Limiting**: Be respectful, add small delays between requests (0.5-1 second)
2. **Error Handling**: Some books might not have descriptions
3. **Rating Mapping**: 
   - "star-rating One" → 1
   - "star-rating Two" → 2
   - "star-rating Three" → 3
   - "star-rating Four" → 4
   - "star-rating Five" → 5
4. **Price Cleaning**: Remove '£' symbol and convert to float
5. **Stock Parsing**: Extract number from "In stock (22 available)"

## Expected Output Schema

```python
{
    "title": str,
    "price_gbp": float,
    "rating": int,  # 1-5
    "availability": str,
    "stock_quantity": int,  # parsed from availability
    "category": str,
    "upc": str,
    "product_page_url": str,
    "description": str  # nullable
}
```

## Estimated Runtime
- 50 pages × 20 books = 1000 books
- With 0.5s delay: ~1050 requests × 0.5s = ~8-10 minutes total

