import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

#configuration 
BASE_URL = "https://books.toscrape.com/"

#Create a BeautifulSoup object
def get_soup(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


#soup = get_soup(BASE_URL)

#print("Page title:", soup.title.text)


#Get all available categories
def get_categories():
    soup = get_soup(BASE_URL)

    categories = []

    category_links = soup.select(
        "div.side_categories ul li ul li a"
    )

    for link in category_links:
        category_name = link.get_text(strip=True)
        category_url = BASE_URL + link["href"]

        categories.append({
            "category": category_name,
            "url": category_url
        })

    return categories

#Test

# if __name__ == "__main__":
#     categories = get_categories()

#     for category in categories:
#         print(category["category"])
#         print(category["url"])
#         print()
        

#Rating conversion
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


#Extract book information
def parse_book(article, category):
    title = article.h3.a["title"]

    price_text = article.select_one(
        ".price_color"
    ).get_text(strip=True)

    rating_text = article.select_one(
        "p.star-rating"
    )["class"][1]

    rating = RATING_MAP.get(rating_text, 0)

    availability = article.select_one(
        ".availability"
    ).get_text(" ", strip=True)

    return {
        "title": title,
        "price": price_text,
        "star_rating": rating_text,
        "availability": availability,
        "category": category
    }   

#Scrape one category
def scrape_category(category_name, category_url):
    books = []
    url = category_url

    while url:
        soup = get_soup(url)

        articles = soup.select("article.product_pod")

        for article in articles:
            try:
                book = parse_book(article, category_name)
                books.append(book)
            except Exception as error:
                print(
                    f"Skipping book because of parsing error: {error}"
                )

        next_button = soup.select_one("li.next a")

        if next_button:
            next_url = next_button.get("href")
            url = urljoin(url, next_url)
        else:
            url = None

    return books

def scrape_books(min_categories=3):
    categories = get_categories()

    all_books = []

    selected_categories = categories[:min_categories]

    for item in selected_categories:
        print(f"Scraping: {item['category']}")

        books = scrape_category(
            item["category"],
            item["url"]
        )

        all_books.extend(books)

    return pd.DataFrame(all_books)


#Test
if __name__ == "__main__":
    df = scrape_books()

    print(df.head())
    print(f"Total books: {len(df)}")
    print(f"Categories: {df['category'].nunique()}")

    df.to_csv(
        "data_pipeline/data/scraped_data.csv",
        index=False, encoding="utf-8"
    )

    print("Scraped data saved successfully.")