import google.generativeai as genai
from constants import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def generate_json(extracted_text, fields):
    """Generate output in JSON format for the extracted text."""
    if not extracted_text:
        return "Error: Text Extraction Failed."

    prompt = f"""
        You are an intelligent document extractor. Given the OCR extracted text {extracted_text} there may be spelling mistakes and wrong OCR extractions fix the spellings and then, and the required fields {fields}, extract and return ONLY the {fields} as JSON.

        Given is the example output format 

        Output:
        {{
            "Invoice Number": "INV-8322",
            "Date": "23 April 2025",
            "Amount": "₹4,300/-"
        }}

        Please follow these instructions carefully:\n\n :

        1. **No Extra Content:** Do not include any additional text, comments, or explainations in your response.
        2. **Empty Response:** If no information matches the description, return an empty string ('').
        3. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text.
        4. Only return the JSON format output without explanations.

    """

    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else "Error: No response from AI."