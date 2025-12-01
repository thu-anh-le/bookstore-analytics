import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv  
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'bookstore'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306))
}

print(DB_CONFIG)

# Path to cleaned CSV (update this when you generate a new cleaned file)
CSV_PATH = '../cleaner/data/clean/books_clean_20251201.csv'


def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"Connected to MySQL database: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_table(connection):
    """Create books table if not exists"""
    cursor = connection.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(500),
        category VARCHAR(100),
        price_gbp DECIMAL(10, 2),
        price_usd DECIMAL(10, 2),
        price_category_usd VARCHAR(50),
        rating INT,
        availability VARCHAR(100),
        in_stock TINYINT(1),
        stock_quantity INT,
        upc VARCHAR(50),
        product_page_url TEXT,
        description LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'books' created or already exists")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()


def convert_boolean(value):
    """Convert various boolean representations to MySQL TINYINT (1/0)"""
    if pd.isna(value):
        return 0
    if isinstance(value, (bool, int)):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.upper() in ['TRUE', '1', 'YES', 'Y'] else 0
    return 0


def truncate_text(text, max_length=65535):
    """Truncate text to fit within TEXT field limits"""
    if pd.isna(text):
        return None
    text = str(text)
    return text[:max_length] if len(text) > max_length else text


def ingest_data(connection, csv_path):
    """Ingest CSV data into MySQL"""
    cursor = None
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows from CSV")

        # Convert in_stock to boolean (1/0)
        df['in_stock'] = df['in_stock'].apply(convert_boolean)

        # Ensure descriptions fit within limits
        df['description'] = df['description'].apply(truncate_text)
        df['title'] = df['title'].apply(lambda x: truncate_text(x, 500))

        cursor = connection.cursor()

        insert_query = """
        INSERT INTO books 
        (title, category, price_gbp, price_usd, price_category_usd, rating, 
         availability, in_stock, stock_quantity, upc, product_page_url, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Insert data row by row
        inserted = 0
        for _, row in df.iterrows():
            values = (
                row['title'],
                row['category'],
                row['price_gbp'],
                row['price_usd'],
                row['price_category_usd'],
                row['rating'],
                row['availability'],
                int(row['in_stock']),  # Ensure it's an integer 1 or 0
                row['stock_quantity'],
                row['upc'],
                row['product_page_url'],
                row['description'],
            )
            cursor.execute(insert_query, values)
            inserted += 1

        connection.commit()
        print(f"Successfully inserted {inserted} rows into database")

    except Error as e:
        print(f"Error ingesting data: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Error reading CSV: {e}")
    finally:
        if cursor is not None:
            cursor.close()


def main():
    # Create connection
    connection = create_connection()
    if not connection:
        return
    
    try:
        # Create table
        create_table(connection)
        
        # Ingest data
        csv_full_path = os.path.join(os.path.dirname(__file__), CSV_PATH)
        ingest_data(connection, csv_full_path)
        
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed")


if __name__ == "__main__":
    main()