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
    import os
    import openai

    client = openai.OpenAI(
        api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
        base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
    )

    stream = client.chat.completions.create(
        model="swiss-ai/Apertus-70B",
        messages=[
            {"role": "system", "content": "You are a travel agent. Be descriptive and helpful"},
            {"role": "user", "content": "What are the best places to visit in Switzerland?"}
        ],
        stream=True
    )

    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)

    return f"Processed text for level {level}:\n\n{text}"

def create_pdf(output_text):
    """Generate a PDF with the processed text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(output_text, styles['Normal'])]
    elements.append(Spacer(1, 12))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📘 Language Level Text Processor")

st.write("Upload a file, select a language level, and process it with the LLM.")

uploaded_file = st.file_uploader(
    "Upload your file",
    type=["md", "docx", "txt", "pdf"]
)

level = st.selectbox(
    "Choose language level",
    ["A1", "A2", "B1", "B2", "C1", "C2"]
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

if st.button("Run Processing"):
    if uploaded_file is not None:
        # Extract text
        text = read_file(uploaded_file)
        
        if not text:
            st.error("Could not read the file content. Please check the format.")
        else:
            st.info("Processing with LLM...")

            # Simulated LLM call
            processed_text = process_text_with_llm(text, level)

            # Generate PDF
            pdf_file = create_pdf(processed_text)

            st.success("Processing complete! Download your file below:")

            st.download_button(
                label="📥 Download Processed PDF",
                data=pdf_file,
                file_name="processed_output.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please upload a file before processing.")
