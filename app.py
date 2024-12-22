"""
PDF is converted to text using PyPDF2
Text is passed to API to get response
"""

import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import re

from dotenv import load_dotenv

load_dotenv() #to load env variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

def pdf_to_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text=""
    # print(reader.pages)
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text+= str(page.extract_text())
    return text

input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech fields such as software engineering, data science, 
data analysis, and big data engineering. Your task is to evaluate the resume based on 
the given job description. Consider the job market's competitive nature and provide 
best assistance for improving the resume. Assign the percentage match based on the JD 
and identify missing keywords with high accuracy.
resume:{text}
description:{jd}

You need to return:
1. JD Match: percentage
2. Missing Keywords: list of missing keywords,
3. Profile Summary: a summary of the profile based on the uploaded PDF file
"""


#app

st.set_page_config(page_title="Smart ATS", page_icon="📝")
st.title("Smart ATS")
st.markdown("### Optimize your resume for job applications")
st.write("Upload your resume and paste the job description to identify missing keywords and enhance your match!")
jd = st.text_area("Paste your job description here", placeholder="Enter the job description...")
uploaded_pdf_file = st.file_uploader("Upload resume in PDF format",type="pdf",help="Accepted format: PDF only")

submit = st.button("Submit")

if submit:
    if jd and uploaded_pdf_file:
        with st.spinner("Processing your resume..."):
            resume_text = pdf_to_text(uploaded_pdf_file)
            formatted_prompt = input_prompt.format(text=resume_text, jd=jd)
            response= get_gemini_response(formatted_prompt)
            # st.text(response)
            
        try:

            jd_match_search = re.search(r"(\d+%)", response.strip(), re.IGNORECASE)
            jd_match = jd_match_search.group(1)

            missing_keywords_search = re.search(r"Missing Keywords\s*:\s*([\s\S]*?)3\.", response, re.IGNORECASE)
            missing_keywords = missing_keywords_search.group(1).strip() if missing_keywords_search else "N/A"

            profile_summary_search = re.search(r"Profile Summary\s*:\s*([\s\S]*)", response, re.IGNORECASE)
            profile_summary = profile_summary_search.group(1).strip() if profile_summary_search else "N/A"

            st.success("✅ Results Ready!")
            st.header("ATS Scan Results")
            st.metric(label="Job Description Match (%)", value=jd_match)
            missing_keywords = missing_keywords.replace("**", "").strip()
            profile_summary = profile_summary.replace("**", "").strip()
            st.markdown(f"**Missing Keywords:** \n{missing_keywords}")
            st.markdown(f"**Profile Summary:** \n{profile_summary}")   


        except Exception as e:
            st.error(f"⚠️ Error parsing the response: {e}")

    else:
        st.error("⚠️ Please upload a PDF and paste the job description.")
else:
    st.info("Hit the **Submit** button to process your resume!")