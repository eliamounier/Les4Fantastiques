import re
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter

MAX_WORDS = 6000
CHAPTER_SPLIT = re.compile(r"\n{4,}")
TEXT_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? "]


def _split_into_chapters(text: str):
    """
    Split text into chapters using 4+ newlines as a delimiter.
    """
    # Normalize Windows-style newlines
    text = text.replace("\r\n", "\n")
    
    # Split on 4 or more consecutive newlines
    parts = [p.strip() for p in CHAPTER_SPLIT.split(text) if p.strip()]
    n_chapters = len(parts)
    chapters = {"Chapter " + str(i): parts[i] for i in range(n_chapters)}
    return chapters


def _split_chapters(chapter_content: str, max_words: int):
    """
    Split chapter content into smaller chunks with a maximum number of words.
    """
    # RecursiveCharacterTextSplitter lets you split hierarchically
    splitter = RecursiveCharacterTextSplitter(
        separators=TEXT_SEPARATORS,  # hierarchy of separators
        chunk_size=max_words,       # maximum words per chunk
        chunk_overlap=0,        # no overlap
        length_function=lambda x: len(x.split())  # count words instead of chars
    )
    chunks = splitter.split_text(chapter_content)
    return chunks


def create_chunks(book: str):
    """
    Create list of chunks from the book text.
    Each chunk is a dictionary with 'Chapter', 'Part', and 'Content'.
    """
    chapters = _split_into_chapters(book)
    chunks = []

    for chapter, content in chapters.items():
        splitted = _split_chapters(content, MAX_WORDS)
        chunks += [
            {
                "Chapter": chapter,
                "Part": "Part " + str(i),
                "Content": splitted[i],
                }
            for i in range(len(splitted))]

    return chunks
