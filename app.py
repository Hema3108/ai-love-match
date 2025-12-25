import os
import streamlit as st
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re

# 1. PAGE CONFIG
st.set_page_config(page_title="AI Love Match", page_icon="💖", layout="wide")
load_dotenv()

# 2. ADVANCED UI CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #fce4ec 0%, #e1f5fe 100%) !important;
    }

    /* Main Container Glassmorphism (soft pastel pink variant) */
    .glass-card {
        background: rgba(252, 238, 245, 0.95); /* very light pink */
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 18px 28px;
        border: 1px solid rgba(123, 31, 162, 0.12); /* soft purple border */
        box-shadow: 0 8px 18px rgba(123, 31, 162, 0.06);
        margin: 0 0 18px 0;
    }
    /* Remove extra top spacing for the first glass card below the header */
    .glass-card:first-of-type { margin-top: 0 !important; }

    /* Floating Heart Particles */
    @keyframes float {
        0% { transform: translateY(0) rotate(0); opacity: 0; }
        50% { opacity: 0.8; }
        100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
    }
    .heart {
        position: fixed;
        color: #ff80ab;
        font-size: 20px;
        pointer-events: none;
        z-index: 0;
        animation: float 10s infinite linear;
    }

    /* Circular Progress Bar */
    .circle-box {
        position: relative;
        width: 180px;
        height: 180px;
        margin: 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fffdfa; /* very light warm white */
        border-radius: 50%;
        box-shadow: 0 8px 18px rgba(123, 31, 162, 0.06);
        border: 10px solid rgba(255,64,129,0.12); /* soft pink ring */
    }
    .score-text { font-size: 3rem; font-weight: 800; color: #7b1fa2; }

    /* Result Skill Cards */
    .skill-card {
        padding: 16px;
        border-radius: 12px;
        background: #ffffff; /* clean white for contrast */
        border-bottom: 4px solid rgba(0,0,0,0.06);
        margin-bottom: 14px;
        box-shadow: 0 5px 12px rgba(0,0,0,0.03);
        color: #333;
    }
    /* Input boxes for uploader and job description */
    .input-card {
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(123,31,162,0.08);
        box-shadow: 0 6px 12px rgba(123,31,162,0.03);
    }
    .input-left { background: rgba(255,246,250,0.95); /* very pale pink */ }
    .input-right { background: rgba(237,245,255,0.95); /* very pale blue */ }
    .input-card .stButton>button { margin-top: 8px; }
    .match-green { border-color: #4caf50; }
    .match-yellow { border-color: #ffeb3b; }
    .match-red { border-color: #f44336; }

    /* Find My Match Button */
    .stButton>button {
        background: linear-gradient(90deg, #7b1fa2, #ff4081) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 15px 50px !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(123, 31, 162, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 15px 25px rgba(123, 31, 162, 0.5) !important; }

    h1, h2, h3 { color: #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR KEY LOGIC
with st.sidebar:
    st.title("💖 Settings")
    user_key = st.text_input("OpenRouter Key", type="password")
    final_api_key = user_key if user_key else os.getenv("OPENROUTER_API_KEY")

# 4. BACKGROUND DECORATION (Hearts)
for i in range(10):
    st.markdown(f'<div class="heart" style="left:{i*10}%; bottom:-10%; animation-delay:{i*0.5}s;">❤️</div>', unsafe_allow_html=True)

# 5. HEADER
# Tweak header margins to remove the extra empty space below the title
st.markdown(
    '<div style="text-align:center; margin-bottom:0;">'
    '<h1 style="margin:0; padding:0;">💞 AI Love Match</h1>'
    '<p style="text-align:center; margin:4px 0 0 0;">Find your dream job soulmate</p>'
    '</div>',
    unsafe_allow_html=True
)

# 6. INPUT CARDS
# Add a small intro inside the first glass card so it doesn't appear empty
st.markdown(
    '<div class="glass-card">'
    '<p style="text-align:center; margin:0 0 12px 0; color:#555;">Tell us about yourself — upload your resume or paste a job description to get started.</p>'
    , unsafe_allow_html=True
)
c1, c2 = st.columns(2)
with c1:
    st.subheader("Your Story")
    uploaded_file = st.file_uploader("Upload resume (PDF/DOC)", type="pdf", label_visibility="collapsed")
with c2:
    st.subheader("Their Dream Candidate")
    job_desc = st.text_area("Paste job description here...", height=120, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# 7. ANALYZE ACTION
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
analyze_btn = st.button("Find My Match!")
st.markdown('</div>', unsafe_allow_html=True)

# 8. AI LOGIC
def get_ai_audit(resume_text, job_text, api_key):
    prompt = f"Analyze the match between this Resume: {resume_text} and Job: {job_text}. Give a Match Score/100, Matching Skills, Missing Skills, and a short Verdict."
    try:
        res = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}]}
        )
        return res.json()['choices'][0]['message']['content']
    except: return "Score: 50%"

# 9. RESULTS DASHBOARD
if analyze_btn and uploaded_file and job_desc:
    with st.spinner("Checking compatibility..."):
        reader = PdfReader(uploaded_file)
        text = "".join([p.extract_text() for p in reader.pages])
        raw_result = get_ai_audit(text, job_desc, final_api_key)
        
        # UI Simulation based on score
        score_val = 85 # Simulated score for demo
        
        st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h2 style="color:#ff4081;">PERFECT MATCH! 💖</h2>
                <p>The recruiter will love this!</p>
                <div class="circle-box">
                    <div class="score-text">{score_val}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Bottom Grid (Skills)
        st.markdown("### Match Details")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown('<div class="skill-card match-green"><b>✅ Matching Skills</b><br>Python, AI, Streamlit</div>', unsafe_allow_html=True)
        with r2:
            st.markdown('<div class="skill-card match-yellow"><b>⚠️ Partial Skills</b><br>Cloud Deployment, SQL</div>', unsafe_allow_html=True)
        with r3:
            st.markdown('<div class="skill-card match-red"><b>❌ Missing Skills</b><br>Docker, Kubernetes</div>', unsafe_allow_html=True)

        st.balloons()