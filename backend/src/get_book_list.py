import requests
import csv
import os
import argparse


def query_books(nb_books: int = 100, languages: list = ["en", "fr", "it", "de", "es"]):
    """
    Query Gutendex API and return a list of books (id, name_author).
    Fetches an equal number of books for each specified language.
    """
    books = []
    books_per_language = nb_books // len(languages)

    for language in languages:
        url = f"https://gutendex.com/books/?languages={language}"
        language_books = []

        while len(language_books) < books_per_language and url:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for book in data["results"]:
                book_id = book["id"]
                name_author = f"{book['title']} - {', '.join(a['name'] for a in book['authors'])} - {language}"
                language_books.append({"id": book_id, "name_author": name_author})

                if len(language_books) >= books_per_language:
                    break

            print(
                f"Prepared {len(language_books)} books for language '{language}' so far..."
            )
            url = data.get("next")  # Get the next page URL

        books.extend(language_books)

    return books


def save_books(books, csv_file: str):
    """Save list of books to CSV file."""
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name_author"])
        writer.writeheader()
        writer.writerows(books)

    print(f"Saved {len(books)} books to {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch books from Gutendex and save to CSV."
    )
    parser.add_argument(
        "nb_books",
        type=int,
        nargs="?",
        default=100,
        help="Number of books to fetch (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../data/books.csv",
        help="Path to output CSV file (default: ../../data/books.csv)",
    )
    args = parser.parse_args()

    books = query_books(
        nb_books=args.nb_books, languages=["en", "fr", "it", "de", "es"]
    )
    save_books(books, args.output)


if __name__ == "__main__":
    main()
