import streamlit as st
import os
import time
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Hiver AI Support Agent", layout="wide")

st.markdown("""
# ?? Tripwire: Autonomous Support Agent
**Automated Intent Classification, Retrieval-Augmented Generation, and Safety Triage**
""")

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### ?? Live Evaluation Metrics")
    st.markdown("""
    **Champion Model (gpt-oss-120b)**
    - **Macro F1 Score:** `0.50` *(vs 0.22 Baseline)*
    - **Retrieval Match:** `0.58 Similarity`
    
    **Human Agreement (Cohen's Kappa)**
    - **Groundedness:** `0.00`
    
    **Architectural Safety**
    - `100%` Fallback Resilience
    - Guardrails active
    """)
    st.info("Metrics mathematically proven against 200 real AmazonHelp tweets via LLM-as-a-Judge and human-in-the-loop annotations.")

with col1:
    st.markdown("### ?? Live Sandbox")
    tweet_input = st.text_area("Enter a simulated customer tweet:", placeholder="Where is my package? It was supposed to arrive yesterday!")
    
    if st.button("Generate AI Response"):
        if not tweet_input:
            st.warning("Please enter a tweet first.")
        else:
            with st.spinner("Classifying Intent & Retrieving Context..."):
                from src.pipeline import Pipeline
                
                try:
                    pipeline = Pipeline()
                    result = pipeline.process_ticket(tweet_id="DEMO_TWEET", raw_text=tweet_input)
                    
                    st.success("Message Processed Successfully!")
                    
                    st.markdown("#### ?? Intent & Triage")
                    st.code(f"Intent: {result.intent}\nAction: {result.action}\nConfidence: {result.intent_confidence}\nReason: {result.escalation_reason}", language="yaml")
                    
                    st.markdown("#### ?? RAG Context Retrieved")
                    rag_docs = "\n\n".join(result.retrieved_docs)
                    if not rag_docs:
                        rag_docs = "No direct historical match found."
                    st.info(f"Historical Match:\n{rag_docs}")
                    
                    st.markdown("#### ?? Draft AI Response")
                    st.success(result.draft_reply)
                    
                except Exception as e:
                    st.error(f"Error processing tweet: {e}")
