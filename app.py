import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image
from io import BytesIO
from gemini import generate_json
import json
import re

# Use centered layout
st.set_page_config(page_title="Fieldoc", layout="centered")
st.title("Fieldoc")
st.header("AI Document Field Extractor")

uploaded_file = st.file_uploader("Upload your file", type=['jpg', 'jpeg', 'png'])

# Checkbox to toggle preview
show_preview = st.checkbox("Show uploaded document preview", value=True)

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')

    # Convert to PDF
    pdf_bytes = BytesIO()
    image.save(pdf_bytes, format="PDF")
    pdf_bytes.seek(0)

    with open("img2pdf.pdf", "wb") as f:
        f.write(pdf_bytes.getbuffer())

    # Show small preview if toggled
    if show_preview:
        st.markdown("**Document Preview:**")
        pdf_viewer("img2pdf.pdf", width=400, height=400)

    fields = st.text_input("Enter the required Fields (comma-separated)")

    if fields:
        # OCR and processing
        with st.spinner("🔍 Performing OCR..."):
            pdf = DocumentFile.from_pdf(BytesIO(pdf_bytes.getvalue()))
            model = ocr_predictor(pretrained=True)
            result = model(pdf)

        # Extract text
        exported = result.export()
        text_output = ""
        for block in exported["pages"][0]["blocks"]:
            for line in block["lines"]:
                line_text = " ".join([word["value"] for word in line["words"]])
                text_output += line_text + "\n"

        # Use Gemini to generate JSON
        with st.spinner("🧠 Generating structured JSON..."):
            json_str_output = generate_json(text_output, fields)
            json_str_output = re.sub(r"^```json|```$", "", json_str_output.strip(), flags=re.MULTILINE).strip()

        try:
            json_data = json.loads(json_str_output)
        except json.JSONDecodeError:
            st.error("❌ Failed to parse JSON. Check formatting or Gemini response.")
            json_data = {}

        # Display JSON output
        st.subheader("🧾 Extracted JSON Output")
        st.json(json_data)

        # Download option
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(json_data, indent=2),
            "extracted_fields.json",
            "application/json",
            key='download-json'
        )