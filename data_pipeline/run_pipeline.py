from scraper import scrape_books
from cleaning import clean_books
from database import create_database, insert_data
from queries import run_queries


# Scrape
df = scrape_books(min_categories=3)

print("\n--- RAW DATA ---")
print(df.head())


# Clean
df = clean_books(df)

print("\n--- CLEANED DATA ---")
print(df.head())


# Step 10 — Verify the data
print("\n--- DATA INFORMATION ---")
print(df.info())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- INVALID PARSED VALUES ---") 
print("Invalid price rows:", df["price_gbp"].isna().sum()) 
print("Invalid rating rows:", df["rating"].isna().sum())

print("\n--- RATING COUNTS ---")
print(df["rating"].value_counts(dropna=False))

print("\n--- STOCK STATUS ---")
print(df["in_stock"].value_counts())

print("\n--- CATEGORY COUNTS ---")
print(df["category"].value_counts())


#Database storage

print("\n" + "=" * 70)
print("STEP 4: DATABASE STORAGE")
print("=" * 70)

connection = create_database()

insert_data(connection, df)

connection.close()

print("Data successfully stored in SQLite database.")


#SQL QUERIES AND PANDAS VALIDATION
print("\n" + "=" * 70)
print("STEP 5: SQL QUERIES AND PANDAS VALIDATION")
print("=" * 70)
run_queries()

# PIPELINE COMPLETE
print("\n" + "=" * 70)
print("COMPLETE MODULE 1 PIPELINE FINISHED SUCCESSFULLY")
print("=" * 70)