# Module 1 — Data Pipeline

## Overview

This module implements an end-to-end data pipeline using [Books to Scrape](https://books.toscrape.com/).

The pipeline performs:

1. Web scraping
2. Data cleaning
3. Type conversion
4. GBP to INR conversion
5. SQLite database loading
6. SQL querying
7. Pandas analysis and validation

## Data Source

Source:

https://books.toscrape.com/

Three book categories are scraped:

* Travel
* Mystery
* Historical Fiction

The pipeline produces **69 books** across the three categories.

## Cleaning Decisions

### Price

The GBP currency symbol is removed and the value is converted to a numeric `float`.

### Rating

Text ratings are mapped as:

* One → 1
* Two → 2
* Three → 3
* Four → 4
* Five → 5

### Availability

Availability is converted into a Boolean value:

* `In stock` → `True`
* `Out of stock` → `False`

Unexpected or unrecognized stock values are excluded because they cannot be safely inferred.

### Missing Numeric Values

Numeric parsing failures are handled using median imputation.

## Currency Conversion

The project uses a fixed exchange rate:

**1 GBP = 105.50 INR**

The `price_inr` column is calculated as:

```text
price_inr = price_gbp × 105.50
```

No external currency API is required.

## Database Design

The SQLite database contains two normalized tables.

### categories

* `category_id` — primary key
* `category_name` — unique

### books

* `book_id` — primary key
* `title`
* `price_gbp`
* `price_inr`
* `rating`
* `in_stock`
* `category_id` — foreign key

## SQL Queries

The project demonstrates the following SQL operations:

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `DISTINCT`
* `BETWEEN`
* `JOIN`

The query results are stored in:

```text
outputs/query_results/
```

The output files include:

```text
books_with_categories.csv
categories.csv
expensive_books.csv
pandas_merge.csv
price_range.csv
top_books.csv
```

## Pandas Validation

SQL query results are read into Pandas using `pd.read_sql()`.

The SQL JOIN result is independently reproduced using `pd.merge()` to demonstrate equivalent relational operations in Pandas.

The SQL JOIN and Pandas merge results are validated to ensure they match.

## Project Structure

```text
data_pipeline/
├── README.md
├── scraper.py
├── cleaning.py
├── database.py
├── queries.py
├── run_pipeline.py
├── data/
│   ├── scraped_data.csv
│   └── cleaned_data.csv
└── outputs/
    └── query_results/
        ├── books_with_categories.csv
        ├── categories.csv
        ├── expensive_books.csv
        ├── pandas_merge.csv
        ├── price_range.csv
        └── top_books.csv
```

## How to Run

From the repository root, install the dependencies:

```bash
pip install -r requirements.txt
```

Run the complete Module 1 pipeline:

```bash
python data_pipeline/run_pipeline.py
```

The pipeline will:

1. Scrape the three selected categories.
2. Generate the raw scraped dataset.
3. Clean and transform the data.
4. Generate GBP and INR price fields.
5. Load the data into SQLite.
6. Execute the SQL queries.
7. Validate the SQL JOIN using Pandas merge.
8. Save the query results to `data_pipeline/outputs/query_results/`.
