import pandas as pd
import sqlite3

import os


# ============================================================
# SQL QUERIES
# ============================================================

QUERIES = {

    # Query 1
    "expensive_books": """
        SELECT *
        FROM books
        WHERE price_gbp > 30
    """,

    # Query 2
    "top_books": """
        SELECT *
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10
    """,

    # Query 3
    "categories": """
        SELECT DISTINCT category_name
        FROM categories
    """,

    # Query 4
    "price_range": """
        SELECT *
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
    """,

    # Query 5 - JOIN
    "books_with_categories": """
        SELECT
            b.title,
            b.rating,
            b.price_inr,
            c.category_name
        FROM books b
        JOIN categories c
        ON b.category_id = c.category_id
    """
}


# CONNECT TO SQLITE DATABASE

connection = sqlite3.connect(
    "data_pipeline/zepto_books.db"
)

# QUERY 1 — EXPENSIVE BOOKS

print("\n" + "=" * 70)
print("QUERY 1: BOOKS WITH PRICE GREATER THAN £30")
print("=" * 70)

result1 = pd.read_sql(
    QUERIES["expensive_books"],
    connection
)

print(result1)


# QUERY 2 — TOP 10 MOST EXPENSIVE BOOKS

print("\n" + "=" * 70)
print("QUERY 2: TOP 10 MOST EXPENSIVE BOOKS")
print("=" * 70)

result2 = pd.read_sql(
    QUERIES["top_books"],
    connection
)

print(result2)


# QUERY 3 — DISTINCT CATEGORIES

print("\n" + "=" * 70)
print("QUERY 3: ALL CATEGORIES")
print("=" * 70)

result3 = pd.read_sql(
    QUERIES["categories"],
    connection
)

print(result3)


# QUERY 4 — BOOKS BETWEEN £20 AND £40

print("\n" + "=" * 70)
print("QUERY 4: BOOKS BETWEEN £20 AND £40")
print("=" * 70)

result4 = pd.read_sql(
    QUERIES["price_range"],
    connection
)

print(result4)


# QUERY 5 — JOIN BOOKS WITH CATEGORIES

print("\n" + "=" * 70)
print("QUERY 5: BOOKS WITH THEIR CATEGORIES - JOIN")
print("=" * 70)

result5 = pd.read_sql(
    QUERIES["books_with_categories"],
    connection
)

print(result5)

# PANDAS MERGE

print("\n" + "=" * 70)
print("PANDAS MERGE: BOOKS + CATEGORIES")
print("=" * 70)

books_df = pd.read_sql(
    "SELECT * FROM books",
    connection
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    connection
)

merged = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)

print(merged)


# VERIFY SQL JOIN AND PANDAS MERGE MATCH

sql_join_compare = result5[
    ["title", "rating", "price_inr", "category_name"]
].sort_values(
    by=["title", "category_name"]
).reset_index(drop=True)

pandas_merge_compare = merged[
    ["title", "rating", "price_inr", "category_name"]
].sort_values(
    by=["title", "category_name"]
).reset_index(drop=True)

print("\n" + "=" * 70)
print("SQL JOIN vs PANDAS MERGE")
print("=" * 70)

print(
    "Do SQL JOIN and Pandas merge match:",
    sql_join_compare.equals(pandas_merge_compare)
)


# SAVE QUERY RESULTS
output_folder = "data_pipeline/outputs/query_results"

os.makedirs(output_folder, exist_ok=True)

result1.to_csv(
    f"{output_folder}/expensive_books.csv",
    index=False
)

result2.to_csv(
    f"{output_folder}/top_books.csv",
    index=False
)

result3.to_csv(
    f"{output_folder}/categories.csv",
    index=False
)

result4.to_csv(
    f"{output_folder}/price_range.csv",
    index=False
)

result5.to_csv(
    f"{output_folder}/books_with_categories.csv",
    index=False
)

merged.to_csv(
    f"{output_folder}/pandas_merge.csv",
    index=False
)

print("\nQuery results saved successfully.")


# CLOSE DATABASE CONNECTION

connection.close()

print("\n" + "=" * 70)
print("ALL 5 SQL QUERIES EXECUTED SUCCESSFULLY")
print("=" * 70)