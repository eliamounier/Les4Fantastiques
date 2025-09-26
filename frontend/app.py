import streamlit as st
from io import BytesIO
import tempfile
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# -------------------------------
# Helper functions
# -------------------------------


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


def process_text_with_llm(text, level):
    """
    Simulated LLM processing.
    In production, replace with a call to an actual LLM API.
    """
    # import os
    # import openai

    # client = openai.OpenAI(
    #     api_key="icPsVlyhOnw2vmGCBvkJFv6pxfh6",
    #     base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1",
    # )

    # stream = client.chat.completions.create(
    #     model="swiss-ai/Apertus-70B",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a travel agent. Be descriptive and helpful",
    #         },
    #         {
    #             "role": "user",
    #             "content": "What are the best places to visit in Switzerland?",
    #         },
    #     ],
    #     stream=True,
    # )

    # # Collect streamed content into a single string so we can display it in the app
    # response_text = ""
    # for chunk in stream:
    #     # try attribute access first, fall back to dict-style access
    #     try:
    #         content = chunk.choices[0].delta.content or ""
    #     except Exception:
    #         try:
    #             content = chunk["choices"][0]["delta"].get("content", "") or ""
    #         except Exception:
    #             content = ""
    #     response_text += content
    #     # keep printing for debugging / logs as before
    #     print(content, end="", flush=True)

    # # Fallback if the stream returned nothing
    # if not response_text:
    #     response_text = f"Processed text for level {level}:\n\n{text}"

    return text


def create_pdf(output_text):
    """Generate a PDF with the processed text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Process text in chunks to avoid memory overhead
    chunk_size = 1000  # Number of characters per chunk
    for i in range(0, len(output_text), chunk_size):
        chunk = output_text[i : i + chunk_size]
        elements.append(Paragraph(chunk, styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📘 Learn from your favorite books")

st.write("Upload a book that you like in their original language to learn new vocabulary and grammar." \
"The app will adapt the content to your language level and generate a PDF for you to download.")

uploaded_file = st.file_uploader("Upload your file", type=["md", "docx", "txt", "pdf"])

level = st.selectbox("Choose language level", ["A1", "A2", "B1", "B2", "C1", "C2"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

if st.button("Do your magic! ✨"):
    if uploaded_file is not None:
        # Extract text
        text = read_file(uploaded_file)

        if not text:
            st.error("Could not read the file content. Please check the format.")
        else:
            st.info("Processing with LLM...")

            # Simulated LLM call
            processed_text = process_text_with_llm(text, level)

            # Show processed text in the app so users can read it
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
    else:
        st.warning("Please upload a file before processing.")
