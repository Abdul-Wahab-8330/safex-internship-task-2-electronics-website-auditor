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
st.subheader("Electronics Websites Focus")
st.write("Scrape a live electronics URL, inspect extracted HTML components, and get a concise quality audit.")

# Main Input Form
url_input = st.text_input("Target Electronics Website URL", placeholder="https://example-electronics-store.com")

if st.button("Run Quick Electronics Audit"):
    if not url_input:
        st.warning("Please enter a valid website URL.")
    elif not api_key:
        st.error("GEMINI_API_KEY not found. Please ensure your environment variable is set up.")
    else:
        # Variables to store results outside the status block
        audit_report = None
        page_title = ""
        trimmed_text = ""
        
        # Use st.status to show step-by-step execution visibility
        with st.status("🚀 Executing Audit Pipeline...", expanded=True) as status:
            try:
                # Step 1: Fetching Webpage
                st.write("🌐 Step 1: Sending HTTP request to target URL...")
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url_input, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    status.update(label="❌ Failed to fetch webpage!", state="error")
                    st.error(f"Failed to fetch the URL. HTTP Status Code: {response.status_code}")
                else:
                    st.write(f"✅ Successfully fetched webpage! (Status Code: {response.status_code})")
                    
                    # Step 2: Parsing HTML & Extracting Tags
                    st.write("🍜 Step 2: Parsing HTML structure using BeautifulSoup...")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    page_title = soup.title.string if soup.title else "No Title Found"
                    
                    # Count specific element tags for visibility
                    h1_count = len(soup.find_all('h1'))
                    h2_count = len(soup.find_all('h2'))
                    h3_count = len(soup.find_all('h3'))
                    p_count = len(soup.find_all('p'))
                    li_count = len(soup.find_all('li'))
                    
                    st.write(f"🏷️ Extracted Tags Breakdown: **{h1_count}** H1s | **{h2_count}** H2s | **{h3_count}** H3s | **{p_count}** Paragraphs | **{li_count}** List Items")
                    
                    raw_text = " ".join([elem.get_text() for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'span'])])
                    trimmed_text = raw_text[:8000] # Shorter text limit for speed and conciseness
                    
                    st.write("✂️ Step 3: Text cleaned and trimmed for AI analysis.")
                    
                    # Step 3: Calling Gemini API
                    st.write("🤖 Step 4: Sending data to Gemini AI for evaluation...")
                    
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
                        status.update(label="✨ Audit Completed Successfully!", state="complete", expanded=False)
                    else:
                        status.update(label="❌ Gemini API Error", state="error")
                        st.error(f"Gemini API Error: {ai_response.status_code} - {ai_response.text}")
                        
            except Exception as e:
                status.update(label="❌ Execution Error", state="error")
                st.error(f"An error occurred: {e}")

        # Display Results Outside the Status Box (Prevents nesting errors)
        if audit_report:
            st.markdown("---")
            st.markdown("### 🔍 Inspected Page Breakdown")
            st.info(f"**Page Title:** {page_title}")
            
            with st.expander("📄 View Raw Extracted Text Sent to AI (Preview)"):
                st.text(trimmed_text[:1500] + "\n... [Rest of text truncated for display]")
            
            st.markdown("### 📊 Audit Results")
            st.write(f"**Target URL:** {url_input}")
            st.markdown(audit_report)