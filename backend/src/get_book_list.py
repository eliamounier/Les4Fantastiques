import requests
import csv
import os


def query_books(nb_books: int = 100):
    """Query Gutendex API and return a list of books (id, name_author, language)."""
    books = []
    url = "https://gutendex.com/books/"

    while len(books) < nb_books and url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for book in data["results"]:
            book_id = book["id"]
            name_author = f"{book['title']} - {', '.join(a['name'] for a in book['authors'])} - {book['languages'][0]}"
            books.append({"id": book_id, "name_author": name_author})

            if len(books) >= nb_books:
                break

        print(f"Prepared {len(books)} books so far...")

    return books


def save_books(books, csv_file: str):
    """Save list of books to CSV file."""
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name_author", "language"])
        writer.writeheader()
        writer.writerows(books)

    print(f"Saved {len(books)} books to {csv_file}")


def main():
    books = query_books(nb_books=100)
    save_books(books, "../../data/books.csv")


if __name__ == "__main__":
    main()
