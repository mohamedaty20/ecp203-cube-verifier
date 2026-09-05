import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import tempfile
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Page configuration
st.set_page_config(page_title="ECP 203 Quality & AI Hub", layout="wide")

# Create top-level navigation tabs
tab1, tab2 = st.tabs(["📊 ECP 203 Cube Verifier", "🤖 AI Lab Report & PDF Auditor"])

with tab1:
    st.header("Egyptian Code (ECP 203) Concrete Cube Verifier")
    st.write("Your original cube verification tool will live here safely.")
    st.info("Tip: Once you verify this tab works, we can place your original calculator logic right here.")

with tab2:
    st.header("🤖 AI ECP 203 Document & Lab Report Auditor")
    st.write(
        "Upload a lab report, concrete mix design submittal, or site log (PDF or Image). "
        "The AI will scan the text, cross-check it against ECP 203 standards, and catch any technical mismatches."
    )

    # API Key handling
    api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

    if not api_key:
        api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")

    if api_key:
        client = genai.Client(api_key=api_key)

        uploaded_file = st.file_uploader(
            "Upload Lab Report / Submittal Paper", 
            type=["pdf", "png", "jpg", "jpeg"]
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_type = uploaded_file.type

            if "image" in file_type:
                st.image(uploaded_file, caption="Uploaded Document Preview", use_container_width=True)
            else:
                st.info(f"Uploaded PDF: {uploaded_file.name} (Ready for analysis)")

            if st.button("🔍 Analyze Document against ECP 203", type="primary"):
                with st.spinner("AI is analyzing text and cross-referencing ECP 203 compliance..."):
                    try:
                        suffix = "." + uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(file_bytes)
                            tmp_path = tmp.name

                        gemini_file = client.files.upload(file=tmp_path)

                        prompt = (
                            "You are an expert Senior Civil QA/QC Engineer specializing in the Egyptian Code of Practice "
                            "for Design and Construction of Reinforced Concrete Structures (ECP 203). "
                            "Analyze the attached document. Extract technical data (compressive strengths, "
                            "cement content, water-cement ratio, testing days like 7 or 28). "
                            "Check them strictly against ECP 203 specifications. Provide:\n"
                            "1. Summary of extracted data.\n"
                            "2. Any engineering mismatches, non-conformities, or red flags.\n"
                            "3. Clear recommendations for the site engineer."
                        )

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[gemini_file, prompt]
                        )

                        st.session_state['ai_analysis_result'] = response.text
                        st.session_state['document_analyzed'] = True
                        st.success("Analysis Complete!")

                    except Exception as e:
                        st.error(f"An error occurred during analysis: {e}")

        if st.session_state.get('document_analyzed', False):
            st.markdown("---")
            st.subheader("📋 Audit Findings & Report")
            st.markdown(st.session_state['ai_analysis_result'])

            def generate_audit_pdf(text_content):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = [Paragraph("<b>ECP 203 AI Compliance Audit Report</b>", styles['Title']), Spacer(1, 12)]
                
                for line in text_content.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 4))
                        
                doc.build(story)
                buffer.seek(0)
                return buffer.getvalue()

            pdf_data = generate_audit_pdf(st.session_state['ai_analysis_result'])
            st.download_button(
                label="📥 Download Audit Report as PDF",
                data=pdf_data,
                file_name="ECP_203_AI_Audit_Report.pdf",
                mime="application/pdf"
            )

            st.markdown("---")
            st.subheader("💬 Chat with AI about this Report")
            
            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []

            user_chat_input = st.text_input("Ask a follow-up question (e.g., 'What should we do if the 7-day result is low?'):")
            if st.button("Send Query") and user_chat_input:
                with st.spinner("Thinking..."):
                    chat_prompt = f"Based on the previous document analysis, answer this engineering question according to ECP 203: {user_chat_input}"
                    chat_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[chat_prompt]
                    )
                    st.session_state['chat_history'].append({"user": user_chat_input, "ai": chat_response.text})

            for chat in reversed(st.session_state.get('chat_history', [])):
                st.markdown(f"**You:** {chat['user']}")
                st.markdown(f"**AI Auditor:** {chat['ai']}")
                st.markdown("---")
    else:
        st.warning("Please enter your Google AI Studio API key above to unlock the AI Auditor.")
