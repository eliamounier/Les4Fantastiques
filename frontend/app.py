import streamlit as st
import tempfile
import requests
import pandas as pd
import os
import re
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from pathlib import Path
from difflib import SequenceMatcher
from backend.simplification_gen import stream_response
from backend.chunk_creation import create_chunks
from backend.text_to_speech import text_to_audio
from backend.ask_user_on_text import generate_question, provide_feedback

import streamlit as st
import streamlit.components.v1 as components



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


def create_pdf(output_text):
    """Generate a PDF with the processed text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Combine all chunks into a single paragraph to avoid line breaks
    elements.append(Paragraph(output_text, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def download_book(book_id, title, fmt="txt", save_dir="./data/books"):
    """Download a book from Project Gutenberg and clean it up."""
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{sanitize_filename(title)}.{fmt}"
    filepath = Path(save_dir) / filename

    # Helper function to preprocess text
    def preprocess_gutenberg_text(text):
        """
        Keep only the text between the START and END markers
        of a Project Gutenberg book.
        """
        start_marker = "START OF THE PROJECT GUTENBERG"
        end_marker = "END OF THE PROJECT GUTENBERG"

        # Find positions of the start and end markers
        start_idx = text.find(start_marker)
        end_idx = text.find(end_marker)

        if start_idx != -1 and end_idx != -1:
            return text[start_idx + len(start_marker) : end_idx].strip()
        else:
            # If markers not found, return original text
            return text.strip()

    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.{fmt}",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.{fmt}",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.{fmt}",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Decode and clean the text before saving
            raw_text = response.content.decode("utf-8", errors="replace")
            cleaned_text = preprocess_gutenberg_text(raw_text)

            # Save the cleaned text
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            return filepath
        except requests.RequestException:
            continue

    st.error(f"Failed to download: {title}")
    return None


def similarity_score(a, b):
    """Compute a similarity score between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# -------------------------------
# Load book list
# -------------------------------


def load_books_from_csv(csv_path="../data/books.csv"):
    # Get the folder where the app.py file is located
    base_dir = Path(__file__).parent
    file_path = base_dir / csv_path
    return pd.read_csv(file_path)


# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(layout="wide")

st.title("📘 Learn from your favorite books")

st.write(
    "Upload a book that you like **OR** choose from a curated list of classic books "
    "to learn new vocabulary and grammar. The app will adapt the content to your "
    "language level and generate a PDF for you to download."
)

# Initialize session state
if "pages" not in st.session_state:
    st.session_state.pages = [""]

if "page" not in st.session_state:
    st.session_state.page = 0

if "can_process" not in st.session_state:
    st.session_state.can_process = False

selected_book_id = None
selected_book_title = None

# Part: Choose a book OR upload one

with st.container(border=True):
    st.subheader("Choose a book")

    col_list, col_empty, col_own = st.columns([4, 1, 4])  # Left column is narrower

    # --- TAB 1: Select from list ---
    with col_list:
        st.markdown("#### From Project Gutenberg list")

        # Load CSV
        books_df = load_books_from_csv("../data/books.csv")

        # Search bar
        search_query = st.text_input("Search for a book or author")

        if search_query:
            # Compute similarity score for each book
            books_df["relevance"] = books_df["name_author"].apply(
                lambda x: similarity_score(search_query, x)
            )

            # Filter by some threshold and sort
            books_df = books_df[books_df["relevance"] > 0.2]  # Filter low-relevance results
            books_df = books_df.sort_values(by="relevance", ascending=False)
        else:
            # If no search query, just show the default list
            books_df["relevance"] = 1.0

        # Create options dynamically
        book_options = {row["id"]: row["name_author"] for _, row in books_df.iterrows()}

        # Streamlit selectbox for book selection
        selected_book_id = st.selectbox(
            "Select a book",
            options=list(book_options.keys()),
            format_func=lambda x: book_options[x],
        )

        if st.button("Download Book"):
            with st.spinner("Downloading book..."):
                filepath = download_book(selected_book_id, book_options[selected_book_id])
                if filepath:
                    st.success(f"Downloaded: {book_options[selected_book_id]}")
                    selected_book_title = book_options[selected_book_id]
                    st.session_state["book_text"] = read_text_file(filepath)
                    st.session_state["selected_book_id"] = selected_book_id
                    st.session_state["selected_book_title"] = book_options[selected_book_id]
                    st.session_state["book_title"] = (
                        selected_book_title  # Save title in session state
                    )
            st.session_state.page = 0  # Reset to first page

    with col_empty:
        st.markdown("#### or")

    # --- TAB 2: Upload file ---
    with col_own:
        st.markdown("#### Upload your own book")

        uploaded_file = st.file_uploader(
            "Upload your file", type=["md", "docx", "txt", "pdf"]
        )
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
            st.session_state["book_text"] = read_file(uploaded_file)
            st.session_state["book_title"] = uploaded_file.name.rsplit(".", 1)[0]
            st.session_state["selected_book_id"] = None
            st.session_state["selected_book_title"] = uploaded_file.name
            st.session_state.page = 0  # Reset to first page

# --- Language level and translation target ---
with st.container(border=True):
    st.write("### Choose Processing Options")

    col1, col2 = st.columns([1, 2])  # Left column is narrower

    with col1:
        level = st.selectbox(
            "Language Level",
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            help="Choose the language proficiency level for simplification",
        )

    with col2:
        target_language = st.text_input(
            "Target Language",
            placeholder="e.g., Spanish, French, German",
            help="Enter the language to translate the text into",
        )

    # Ensure target_language is never empty
    if not target_language.strip():
        target_language = "original language of the provided text"

    # --- Process button ---
    if st.button("Do your magic! ✨"):
        if "book_text" not in st.session_state or not st.session_state["book_text"]:
            st.warning("Please select or upload a book before processing.")
            st.session_state.can_process = False
        else:
            st.info(
                f"Processing text for level {level} and translating to {target_language}..."
            )
            st.session_state.can_process = True


if st.session_state.can_process:
    # Stream the processed text incrementally
    text = st.session_state["book_text"].strip()
    chunks = create_chunks(text)

    learning_mode = True
    if learning_mode:
        simplified_chunk = ""

        n_chunks = len(chunks)
        st.session_state.pages = [""] * n_chunks

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            if st.session_state.page > 0 and st.button("⬅ Previous") :
                    st.session_state.page -= 1

        with col2:
            st.write(f"### Page {st.session_state.page + 1}")

        with col3:
            if st.session_state.page < n_chunks - 1 and st.button("Next ➡"):
                st.session_state.page += 1

        # Display the current page
        page_idx = st.session_state.page
        if st.session_state.pages[page_idx] == "":
            # First time visiting this page → stream & collect
            placeholder = st.empty()
            
            for token in stream_response(
                [chunks[page_idx]],
                level,
                target_language
            ):
                simplified_chunk += token
                # placeholder.write(simplified_chunk)
                placeholder.markdown(f"<span style='color:white'>{simplified_chunk}</span>", unsafe_allow_html=True)
            
            st.session_state.pages[page_idx] = simplified_chunk    
            

        else:
            # Already processed → just show stored result
            simplified_chunk = st.session_state.pages[page_idx]
            st.write(simplified_chunk)


        if simplified_chunk:
            
            # --- Audio Playback ---

            if st.button("🎵 Listen"):
                with st.spinner("Creating audio..."):
                    
                    output_file = "./data/generated_audio.mp3"
                    
                    # Generate audio (will auto-detect language)
                    text_to_audio(simplified_chunk, language=None, output_file=output_file)
                    
                    with open(output_file, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mpeg")
                        st.success("Audio generated!")


            if st.button("🧠 Ask me a question"):
                with st.spinner("Generating question..."):
                    question = generate_question(text, target_language) 
                    print(f"DEBUG: Generated question: {question}")
                    st.session_state["generated_question"] = question
                    st.write(f"*Question:* {question}")

            if "generated_question" in st.session_state:
                user_response = st.text_area("Your answer:", placeholder="Type your answer here...")  # Added label
                if st.button("Get Feedback"):
                    if user_response.strip():
                        with st.spinner("Providing feedback..."):
                            feedback = provide_feedback(text, st.session_state["generated_question"], user_response, target_language)
                            st.write(f"*Feedback:* {feedback}")
                    else:
                        st.warning("Please provide a response before getting feedback.")      


        #-------------------------------------


    else:
        st.write_stream(stream_response(chunks, level, target_language))

    # Generate PDF
    pdf_file = create_pdf(simplified_chunk)  # Use the full text directly for PDF generation

    st.success("Processing complete! Download your simplified book below:")
    # Build filename dynamically
    base_name = sanitize_filename(
        st.session_state.get("book_title", "processed_book")
    )
    file_name = f"{base_name}_level_{level}_{target_language}.pdf"

    st.download_button(
        label="📥 Download Processed PDF",
        data=pdf_file,
        file_name=file_name,
        mime="application/pdf",
    )
