import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key securely from the environment
api_key = os.getenv("GEMINI_API_KEY")

# Page Config
st.set_page_config(page_title="AI Electronics Website Auditor", page_icon="⚡", layout="centered")

st.title("⚡ AI-Assisted Website Quality Auditor")
st.subheader("Task Line 286: Electronics Websites Focus")
st.write("Scrape a live electronics URL and get a quick score and concise quality audit.")

# Main Input Form
url_input = st.text_input("Target Electronics Website URL", placeholder="https://example-electronics-store.com")

if st.button("Run Quick Electronics Audit"):
    if not url_input:
        st.warning("Please enter a valid website URL.")
    elif not api_key:
        st.error("GEMINI_API_KEY not found. Please ensure your environment variable is set up.")
    else:
        with st.spinner("Analyzing website quality..."):
            try:
                # 1. Fetch Webpage Content via Requests
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url_input, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # 2. Parse HTML using BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    page_title = soup.title.string if soup.title else "No Title Found"
                    raw_text = " ".join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'span'])])
                    trimmed_text = raw_text[:8000] # Shorter text limit for speed and conciseness
                    
                    # 3. Short & Punchy Prompt for Gemini
                    prompt_text = f"""
                    You are an expert e-commerce auditor for electronics websites.
                    Analyze this scraped webpage data:
                    - URL: {url_input}
                    - Title: {page_title}
                    - Content: {trimmed_text}
                    
                    Provide a short, concise audit report formatted strictly like this:
                    - **Overall Electronics Quality Score:** [Give a score out of 100, e.g., 75/100]
                    - **Key Findings (Max 3 brief bullet points focusing on specs, pricing/warranty trust signals, and user experience):**
                    - **Quick Recommendation:** [One short sentence on how to improve]
                    
                    Keep it brief, direct, and avoid long paragraphs.
                    """
                    
                    # 4. Call Gemini REST API
                    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt_text}]
                        }]
                    }
                    
                    ai_response = requests.post(gemini_url, json=payload, timeout=20)
                    
                    if ai_response.status_code == 200:
                        res_json = ai_response.json()
                        audit_report = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        
                        st.success("Audit Completed!")
                        
                        # 5. Display Results
                        st.markdown("### 📊 Audit Results")
                        st.write(f"**Target:** {url_input}")
                        st.markdown(audit_report)
                    else:
                        st.error(f"Gemini API Error: {ai_response.status_code} - {ai_response.text}")
                        
                else:
                    st.error(f"Failed to fetch the URL. HTTP Status Code: {response.status_code}")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")