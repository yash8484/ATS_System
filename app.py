from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure API Key
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ Google API key not found. Set it in .env or Streamlit secrets.")
else:
    genai.configure(api_key=API_KEY)

# Function to Get Response from Gemini
def get_gemini_response(prompt_text, pdf_content, job_description):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt_text, pdf_content[0], job_description])
        return response.text
    except Exception as e:
        return f"❌ Error generating response: {e}"

# Function to Convert PDF to Image (First Page)
def input_pdf_setup(uploaded_file):
    try:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        if not images:
            raise ValueError("No images extracted from PDF.")
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        return [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {e}")

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("📄 ATS Resume Analysis Tool")

# User Inputs
input_text = st.text_area("🔹 Job Description:", key="input")
uploaded_file = st.file_uploader("📂 Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

# Define Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as a percentage, then keywords missing, and lastly, final thoughts.
"""

# Form for Submission
with st.form(key="resume_form"):
    submit1 = st.form_submit_button("📄 Tell Me About the Resume")
    submit3 = st.form_submit_button("📊 Percentage Match")

if submit1 or submit3:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            prompt_text = input_prompt1 if submit1 else input_prompt3
            response = get_gemini_response(prompt_text, pdf_content, input_text)
            st.subheader("📌 ATS Analysis Result:")
            st.write(response)
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.warning("⚠️ Please upload a resume first!")
