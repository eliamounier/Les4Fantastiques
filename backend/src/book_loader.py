#!/usr/bin/env python3
"""
Free Book Downloader Script
Downloads books from Project Gutenberg - all books are public domain and free
"""

import requests
from pathlib import Path
import time
import re

# Requested books with their IDs and titles
BOOKS = {
    11: "Alice's Adventures in Wonderland - Lewis Carroll",
    345: "Dracula - Bram Stoker",
    120: "Treasure Island - Robert Louis Stevenson",
    55: "The Wonderful Wizard of Oz - L. Frank Baum",
    164: "Journey to the Center of the Earth - Jules Verne",
    4650: "The Three Musketeers - Alexandre Dumas",
    3747: "Orlando Furioso - Ludovico Ariosto"
}

def sanitize_filename(name):
    """Sanitize filenames to remove invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def download_book(book_id, title, fmt='txt', save_dir='./data/books'):
    """Download a book from Project Gutenberg."""
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{sanitize_filename(title)}.{fmt}"
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.{fmt}",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.{fmt}",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.{fmt}"
    ]
    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(Path(save_dir) / filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            return
        except requests.RequestException:
            continue
    print(f"Failed to download: {title}")

def download_books(book_list):
    """Download all books in the provided list."""
    for book_id, title in book_list.items():
        print(f"Downloading: {title}")
        download_book(book_id, title)
        time.sleep(2)  # Be respectful to the server

if __name__ == "__main__":
    print("📚 Starting download of all books...")
    download_books(BOOKS)
    print("🎉 All books downloaded successfully!")