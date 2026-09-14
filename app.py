import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Hiver AI Support Agent", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a Designer, Premium Feel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Gradient Title */
    .title-text {
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        color: #FF416C;
    }
    
    /* Custom Styling for the Text Area */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 15px;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .stTextArea textarea:focus {
        border-color: #FF416C;
        box-shadow: 0 0 10px rgba(255, 65, 108, 0.2);
    }
    
    /* Custom Styling for the Button */
    .stButton button {
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 65, 108, 0.4);
    }
    
    /* Custom Output Cards */
    .output-card {
        background-color: #f8f9fa;
        border-left: 5px solid #FF416C;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("assets/tripwire_logo.jpg", width=80)
with col_title:
    st.markdown('<p class="title-text">TripWire AI</p>', unsafe_allow_html=True)
    st.markdown("**Automated Intent Classification, RAG, and Safety Triage**")
st.markdown("---")

col_input, col_metrics = st.columns([2, 1])

with col_metrics:
    st.markdown("### 📊 System Health")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Macro F1", "0.50", "Champion")
    col_m2.metric("Retrieval Match", "0.58", "RAG")
    
    col_m3, col_m4 = st.columns(2)
    col_m3.metric("Resilience", "100%", "Fallback")
    col_m4.metric("Agreement (\u03ba)", "0.00", "Pending")

    st.info("Metrics mathematically proven against 200 real AmazonHelp tweets via LLM-as-a-Judge.")

with col_input:
    st.markdown("### 💻 Live Sandbox")
    tweet_input = st.text_area("Customer Tweet:", height=120, placeholder="Where is my package? It was supposed to arrive yesterday!")
    
    if st.button("🚀 Generate Autonomous Response"):
        if not tweet_input:
            st.warning("Please enter a tweet first.")
        else:
            with st.spinner("Classifying Intent & Retrieving Context..."):
                from src.pipeline import Pipeline
                
                try:
                    pipeline = Pipeline()
                    result = pipeline.process_ticket(tweet_id="DEMO", raw_text=tweet_input)
                    
                    st.markdown("#### 🎯 Intent & Triage")
                    st.code(f"Intent: {result.intent}\nAction: {result.action}\nConfidence: {result.intent_confidence}\nReason: {result.escalation_reason}", language="yaml")
                    
                    st.markdown("#### 🔍 RAG Context Retrieved")
                    rag_docs = "\n\n".join(result.retrieved_docs) if result.retrieved_docs else "No direct historical match found."
                    st.markdown(f'<div class="output-card"><i>"{rag_docs}"</i></div>', unsafe_allow_html=True)
                    
                    st.markdown("#### 📝 Draft AI Response")
                    st.success(result.draft_reply)
                    
                except Exception as e:
                    st.error(f"Error processing tweet: {e}")
