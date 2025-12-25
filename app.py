import os
import streamlit as st
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="CareerSynergy AI Audit", page_icon="⚖️", layout="wide")
load_dotenv()

# 2. PROFESSIONAL CORPORATE UI (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc !important;
    }

    /* Professional Header */
    .header-box {
        background-color: #0f172a;
        padding: 40px 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Dashboard Cards */
    .dashboard-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Metric Circle */
    .metric-circle {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        border: 6px solid #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        background: #f1f5f9;
    }

    /* Analysis Badges */
    .status-badge {
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    .badge-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-danger { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    /* Button Styling */
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 18px 0 !important;
        font-size: 1.05rem !important;
        min-height: 56px !important;
        min-width: 520px !important;
        width: auto !important;
        font-weight: 700 !important;
        border: none !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        transition: background 0.2s, transform 0.08s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR CONFIGURATION
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3850/3850285.png", width=80)
    st.title("System Controls")
    user_key = st.text_input("API Authorization Key", type="password")
    final_api_key = user_key if user_key else os.getenv("OPENROUTER_API_KEY")
    st.divider()
    st.markdown("### Audit Parameters")
    st.caption("Engine: Llama-3.3-70B")
    st.caption("Methodology: Semantic Gap Analysis")

# 4. MAIN INTERFACE HEADER
st.markdown("""
    <div class="header-box">
        <h1 style="margin:0; color:white; font-size: 2.5rem;">CareerSynergy AI Audit</h1>
        <p style="opacity:0.8; font-size: 1.1rem; margin-top:10px;">Automated Semantic Alignment & Technical Compatibility Verification</p>
    </div>
    """, unsafe_allow_html=True)

# 5. INPUT SECTIONS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Candidate Profile")
    uploaded_file = st.file_uploader("Upload technical resume for parsing (PDF)...", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.info("Document successfully staged for audit.")

with col2:
    st.subheader("Target Specification")
    job_desc = st.text_area("Provide the job description or technical requirements here...", height=128, label_visibility="collapsed")
    if job_desc:
        st.caption("Requirement parameters received.")

# 6. EXECUTION TRIGGER
# Changed the button text to a more professional action
if st.button("Check Match"):
    if not final_api_key:
        st.error("Authentication Error: API Key required.")
    elif uploaded_file and job_desc:
        with st.spinner("Executing neural semantic analysis..."):
            # Extract PDF Text
            reader = PdfReader(uploaded_file)
            resume_text = "".join([p.extract_text() for p in reader.pages])
            
            # AI API Call
            prompt = f"""
            Analyze the following resume against the job description for a professional audit.
            Resume: {resume_text[:2000]}
            Job Description: {job_desc[:2000]}
            
            Format response as:
            SCORE: [Integer]
            MATCHING: [3 skills]
            MISSING: [3 skills]
            VERDICT: [1 sentence executive summary]
            """
            
            try:
                res = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {final_api_key}"},
                    json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}]}
                )
                output = res.json()['choices'][0]['message']['content']
                
                # Parsing Results
                score = re.search(r"SCORE:\s*(\d+)", output).group(1) if re.search(r"SCORE:\s*(\d+)", output) else "0"
                matching = re.search(r"MATCHING:\s*(.*)", output).group(1) if re.search(r"MATCHING:\s*(.*)", output) else "Unknown"
                missing = re.search(r"MISSING:\s*(.*)", output).group(1) if re.search(r"MISSING:\s*(.*)", output) else "Unknown"
                verdict = re.search(r"VERDICT:\s*(.*)", output).group(1) if re.search(r"VERDICT:\s*(.*)", output) else "Audit successful."

                # 7. RESULTS DASHBOARD
                st.markdown("---")
                st.markdown("### Audit Findings")
                
                res_col_left, res_col_right = st.columns([1, 2])
                
                with res_col_left:
                    st.markdown(f"""
                        <div class="dashboard-card" style="text-align:center;">
                            <p style="font-weight:600; color:#64748b;">Alignment Index</p>
                            <div class="metric-circle">{score}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with res_col_right:
                    st.markdown(f"""
                        <div class="dashboard-card">
                            <p style="font-weight:600; margin-bottom:10px;">Executive Summary</p>
                            <p style="color:#334155; line-height:1.6;">{verdict}</p>
                            <hr style="margin: 15px 0; border:0; border-top:1px solid #e2e8f0;">
                            <div style="margin-bottom:12px;">
                                <b style="font-size:0.9rem; color:#64748b;">CORE PROFICIENCIES IDENTIFIED:</b><br>
                                <span class="status-badge badge-success">{matching}</span>
                            </div>
                            <div>
                                <b style="font-size:0.9rem; color:#64748b;">IDENTIFIED TECHNICAL GAPS:</b><br>
                                <span class="status-badge badge-danger">{missing}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Audit System Failure: {str(e)}")
    else:
        st.warning("Prerequisite missing: Please ensure both Candidate Profile and Target Specification are provided.")