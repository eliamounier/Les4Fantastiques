import streamlit as st
from io import BytesIO
from pathlib import Path
import tempfile
import requests
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import re
from pathlib import Path

# -------------------------------
# Helper functions
# -------------------------------

def sanitize_filename(name):
    """Sanitize file names to avoid invalid characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def read_file(file):
    """Reads file content and returns text."""
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    elif file.name.endswith(".md"):
        return file.read().decode("utf-8")

    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file.name.endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])

    else:
        return None

def read_text_file(filepath):
    """Reads text from a saved .txt file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def process_text_with_llm(text, level):
    """
    Simulated LLM processing.
    Replace with a real LLM API call in production.
    """
    return f"[Simplified to level {level}]\n\n" + text

def create_pdf(output_text):
    """Generate a PDF with the processed text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Process text in chunks to avoid memory overhead
    chunk_size = 1000  # Number of characters per chunk
    for i in range(0, len(output_text), chunk_size):
        chunk = output_text[i: i + chunk_size]
        elements.append(Paragraph(chunk, styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def download_book(book_id, title, fmt='txt', save_dir='./data/books'):
    """Download a book from Project Gutenberg."""
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{sanitize_filename(title)}.{fmt}"
    filepath = Path(save_dir) / filename

    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.{fmt}",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.{fmt}",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.{fmt}"
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        except requests.RequestException:
            continue

    st.error(f"Failed to download: {title}")
    return None

# -------------------------------
# Load book list
# -------------------------------

@st.cache_data
def load_books_from_csv(csv_path="../data/books.csv"):
    # Get the folder where the app.py file is located
    base_dir = Path(__file__).parent
    file_path = base_dir / csv_path
    return pd.read_csv(file_path)


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📘 Learn from your favorite books")

st.write(
    "Upload a book that you like **OR** choose from a curated list of classic books "
    "to learn new vocabulary and grammar. The app will adapt the content to your "
    "language level and generate a PDF for you to download."
)

# Tabs: Choose a book OR upload one
tab1, tab2 = st.tabs(["Choose from list", "Upload your own"])

selected_book_id = None
selected_book_title = None

# --- TAB 1: Select from list ---
with tab1:
    st.subheader("Choose a book from Project Gutenberg list")

    # Load CSV
    books_df = load_books_from_csv("../data/books.csv")
    
    # Create selection
    book_options = {
        row["id"]: row["name_author"] for _, row in books_df.iterrows()
    }
    selected_book_id = st.selectbox("Select a book", options=list(book_options.keys()), format_func=lambda x: book_options[x])

    if st.button("Download Book"):
        with st.spinner("Downloading book..."):
            filepath = download_book(selected_book_id, book_options[selected_book_id])
            if filepath:
                st.success(f"Downloaded: {book_options[selected_book_id]}")
                selected_book_title = book_options[selected_book_id]
                text = read_text_file(filepath)
                st.session_state["book_text"] = text

# --- TAB 2: Upload file ---
with tab2:
    uploaded_file = st.file_uploader("Upload your file", type=["md", "docx", "txt", "pdf"])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        st.session_state["book_text"] = read_file(uploaded_file)

# --- Language level ---
level = st.selectbox("Choose language level", ["A1", "A2", "B1", "B2", "C1", "C2"])

# --- Process button ---
if st.button("Do your magic! ✨"):
    if "book_text" not in st.session_state or not st.session_state["book_text"]:
        st.warning("Please select or upload a book before processing.")
    else:
        text = st.session_state["book_text"]
        st.info("Processing with LLM...")

        # Process text
        processed_text = process_text_with_llm(text, level)

        # Display processed text
        st.text_area("Processed Text", value=processed_text, height=300)

        # Generate PDF
        pdf_file = create_pdf(processed_text)

        st.success("Processing complete! Download your simplified book below:")
        st.download_button(
            label="📥 Download Processed PDF",
            data=pdf_file,
            file_name="processed_book.pdf",
            mime="application/pdf",
        )
