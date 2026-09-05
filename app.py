import io
import datetime
import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import qrcode
import pypdf

# Google GenAI for AI Auditor & Chatbot
from google import genai
from google.genai import types

# ReportLab imports for professional PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Image as ReportLabImage,
)

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Multi-Standard Geotechnical, Pavement & Concrete Engineering Auditor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM STYLING (FIXING DROPDOWNS & UI ELEMENTS) ---
dark_style = """
<style>
.stApp {
    background-color: #031338 !important;
    color: #FFFFFF !important;
}
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}
[data-testid="stImage"] {
    width: 100% !important;
    position: relative !important;
    margin-bottom: 1rem !important;
}
[data-testid="stImage"] img {
    max-width: 100% !important;
    border-radius: 6px;
    border: 1px solid #FF8C00;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

[data-testid="stSidebar"], 
section[data-testid="stSidebar"] > div {
    background-color: #1B2A4A !important;
}
[data-testid="stSidebar"] *, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-weight: bold !important;
}
p, span, label, div {
    color: #FFFFFF !important;
}
h1 {
    color: #00BFFF !important;
    font-weight: 700;
}
h2, h3, .stSubheader {
    color: #FF8C00 !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #7e8385 !important;
}
textarea, input {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
    border: 1px solid #FF8C00 !important;
}

/* FIX DROPDOWN AND SELECTBOX TEXT & BACKGROUND ISSUES */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"], div[data-baseweb="calendar"], div[data-baseweb="popover"], div[data-baseweb="menu"] {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
}
div[data-baseweb="input"] input, .stDateInput input, div[data-baseweb="select"] span {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
}
div[data-baseweb="select"] > div {
    background-color: #1E222D !important;
    border: 1px solid #FF8C00 !important;
    color: #FFFFFF !important;
}
div[data-baseweb="popover"] *, div[role="listbox"] *, ul[role="listbox"] li {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
}
ul[role="listbox"] li:hover {
    background-color: #FF8C00 !important;
    color: #031338 !important;
}
.stDateInput div, .stDateInput div[data-baseweb="input"] {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
}

[data-testid="stFileUploader"], div[data-baseweb="file-uploader"] {
    background-color: #1E222D !important;
    border: 1px solid #FF8C00 !important;
    border-radius: 8px !important;
    padding: 10px !important;
    margin-bottom: 10px !important;
}
[data-testid="stFileUploader"] section {
    background-color: #1E222D !important;
    border: none !important;
    padding: 5px !important;
}
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div {
    color: #FFFFFF !important;
}

div.stButton > button, div.stDownloadButton > button, button[kind="secondary"], button[kind="primary"] {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #FF8C00 !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #1E222D !important;
    color: #FF8C00 !important;
    border: 2px solid #00BFFF !important;
}

div[row-widget="stRadio"] label p, .stRadio div[data-baseweb="radio"] label span {
    font-size: 18px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    padding-top: 14px !important;
    padding-bottom: 14px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #00BFFF !important;
}

hr {
    border-color: #262730 !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"], div[data-baseweb="card"] {
    background-color: #1B2A4A !important;
}

/* FIX CHAT INPUT CONTAINER WHITE BOX & PADDING */
[data-testid="stChatInput"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div {
    background-color: #1E222D !important;
    border: 1px solid #FF8C00 !important;
    border-radius: 8px !important;
}

/* BIG COMPANY FOOTER FORMAT */
.corporate-footer {
    background-color: #121E36;
    border-top: 2px solid #FF8C00;
    padding: 30px 40px;
    margin-top: 3rem;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    border-radius: 6px;
}
.corporate-footer-grid {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 30px;
}
.corporate-footer-col {
    flex: 1;
    min-width: 250px;
}
.corporate-footer h4 {
    color: #00BFFF;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.corporate-footer p, .corporate-footer li, .corporate-footer a {
    color: #CBD5E1;
    font-size: 0.88rem;
    line-height: 1.6;
    text-decoration: none;
}
.corporate-footer a:hover {
    color: #FF8C00;
    text-decoration: underline;
}
.corporate-footer-bottom {
    margin-top: 25px;
    padding-top: 15px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.8rem;
    color: #94A3B8;
}
</style>
"""
st.markdown(dark_style, unsafe_allow_html=True)

# --- 3. TOP BANNER / COVER PHOTO ---
if os.path.exists("logo.png"):
    st.image("logo.png")

ticker_html = """
<div style="overflow: hidden; white-space: nowrap; background-color: #FF8C00; color: #031338; padding: 6px 0; font-weight: bold; font-size: 14px; margin-bottom: 15px; border-radius: 4px;">
  <div style="display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite;">
    🚀 Core Compliance Active: ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, ISO &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; ⚠️ Multi-Disciplinary Engineering & Geotechnical QA/QC Verifier &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; 🏗️ Active Site Inspection Portal
  </div>
</div>
<style>
@keyframes marquee {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-100%, 0); }
}
</style>
"""
st.markdown(ticker_html, unsafe_allow_html=True)

st.title("Multi-Disciplinary Civil, Geotechnical & Pavement Engineering Auditor")
st.markdown(
    '<p style="color: #FFFFFF !important; font-size: 1rem; font-weight: bold; margin-top: -15px; margin-bottom: 15px;">Made by Eng. Mohamed Abd Al Aty</p>',
    unsafe_allow_html=True,
)

# --- MAIN APP NAVIGATION (WELL ORGANIZED & CLEARLY AI-POWERED) ---
app_mode = st.radio(
    "📱 App Screen Navigation:",
    [
        "📊 Concrete Verifier Dashboard",
        "🤖 AI Multi-Standard Engineering Auditor (AI-Powered)",
        "🔍 Crack, Pavement & Geotechnical Defect Diagnostic (AI-Powered)",
        "💬 Core-Code Intelligent Assistant Chatbot (AI-Powered)",
        "📖 Multi-Standard Technical Codes Handbook (ECP, ASTM, AASHTO, BS, EN, ISO)",
    ],
    horizontal=True,
)
st.markdown("---")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.markdown(
    """
    <div style="text-align: left; padding: 0px 0px 12px 0px; margin: 0;">
      <p style="color: #00BFFF !important; font-size: 0.78rem; font-weight: normal; margin-bottom: 4px;">Portal Navigation Guide:</p>
      <ul style="color: #CBD5E1 !important; font-size: 0.74rem; padding-left: 14px; margin: 0; line-height: 1.35; font-weight: normal;">
        <li>Select governing standards & input site metadata.</li>
        <li>Audit test results against ECP & international codes.</li>
        <li>Inspect structural, soil & highway compliance instantly.</li>
        <li>Upload documents or photos for automated AI diagnostics.</li>
        <li>Engage with the Core-Code AI Chatbot for instant QA answers.</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("PROJECT & REGULATORY STANDARDS")
project_name = st.sidebar.text_input("Project Name", value="", placeholder="Enter project name")
pour_location = st.sidebar.text_input("Structural Element / Road Chainage", "Highway Section Ch. 12+500 / Slab A1")

st.sidebar.subheader("🌐 Governing Standards Core & Supplement")
st.sidebar.info("Core Fundamental Standards active by default: **ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, ISO**")

supplementary_code = st.sidebar.selectbox("Supplementary / International Code Selector", [
    "None (Strictly Core: ECP 203/202/104 + ASTM/AASHTO/BS/EN/ISO)",
    "ACI 318-25 — Building Code Requirements for Structural Concrete",
    "IBC — International Building Code",
    "BS EN 1990 / BS EN 1992 / Eurocode 2 + UK National Annex",
    "AASHTO LRFD Bridge Design Specifications / Highway Pavements"
])

fcu_spec = st.sidebar.number_input("Specified 28-Day Grade fcu (N/mm²)", min_value=10.0, max_value=100.0, value=30.0, step=5.0)

st.sidebar.subheader("🚚 Batch Plant & Site Logs")
mixer_truck_no = st.sidebar.text_input("Mixer Truck No. / Equipment ID", value="TRK-104")
batch_ticket_id = st.sidebar.text_input("Batch Ticket / Geo-Log ID", value="BT-99482")
casting_date = st.sidebar.date_input("Casting / Inspection Date", value=datetime.date.today() - datetime.timedelta(days=7))

st.sidebar.subheader("⚖️ Mix Design Specifications")
cement_content = st.sidebar.text_input("Cement Content (kg/m³)", value="350.0")
try:
    cement_content_val = float(cement_content)
except ValueError:
    cement_content_val = 350.0

water_content = st.sidebar.text_input("Free Water Content (kg/m³)", value="150.0")
try:
    water_content_val = float(water_content)
except ValueError:
    water_content_val = 150.0

wc_ratio = water_content_val / cement_content_val if cement_content_val > 0 else 0.0
st.sidebar.write(f"• **Calculated W/C Ratio:** `{wc_ratio:.2f}`")

slump_value = st.sidebar.number_input("Slump / Workability Test Value (mm)", min_value=0.0, max_value=300.0, value=150.0, step=5.0)
concrete_temp = st.sidebar.number_input("Concrete / Soil Temp (°C)", min_value=0.0, max_value=60.0, value=28.5, step=0.5)

engineer_name = st.sidebar.text_input("Engineer Name", value="", placeholder="Enter your name")
report_date = st.sidebar.date_input("Report Date", value=datetime.date.today())

st.sidebar.markdown("---")
st.sidebar.header("COMPANY BRANDING")
company_logo_file = st.sidebar.file_uploader("Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
company_logo_bytes = company_logo_file.read() if company_logo_file else None

# --- MIX AUDIT CALCULATIONS ---
max_allowed_wc = 0.45 if fcu_spec >= 30 else 0.50
min_allowed_cement = 300.0
max_allowed_temp = 35.0

wc_compliant = wc_ratio <= max_allowed_wc
cement_compliant = cement_content_val >= min_allowed_cement
temp_compliant = concrete_temp <= max_allowed_temp
mix_overall_pass = wc_compliant and cement_compliant and temp_compliant

mix_audit_rows = [
    {
        "Mix Parameter": "Water-Cement Ratio (W/C)",
        "Actual Value": f"{wc_ratio:.2f}",
        "Standard Limit": f"≤ {max_allowed_wc:.2f} (ECP 203 / ASTM C94)",
        "Status": "PASS" if wc_compliant else "FAIL"
    },
    {
        "Mix Parameter": "Minimum Cement Content",
        "Actual Value": f"{cement_content_val} kg/m³",
        "Standard Limit": f"≥ {min_allowed_cement} kg/m³ (ECP 203)",
        "Status": "PASS" if cement_compliant else "FAIL"
    },
    {
        "Mix Parameter": "Fresh Concrete Temperature",
        "Actual Value": f"{concrete_temp} °C",
        "Standard Limit": f"≤ {max_allowed_temp} °C (ASTM C1064 / ECP 203)",
        "Status": "PASS" if temp_compliant else "FAIL"
    }
]
df_mix_audit = pd.DataFrame(mix_audit_rows)

# --- ADVANCED TEXT CLEANER FOR PDF EXPORTS ---
def format_markdown_for_reportlab(text):
    if not text:
        return ""
    cleaned = re.sub(r'\$(.*?)\$', r'\1', text)
    cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cleaned = re.sub(r'[\-\|\:]+', ' ', cleaned)
    cleaned = re.sub(r'#{1,6}\s*', '', cleaned)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'<i>\1</i>', cleaned)
    cleaned = re.sub(r'^\s*[\*\-]\s+', '&bull; ', cleaned, flags=re.MULTILINE)
    return cleaned

def clean_for_pdf(text):
    return format_markdown_for_reportlab(text)

def build_professional_pdf_header(story, doc_title, subtitle, logo_bytes, engineer, project, location, rep_date):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#1B2A4A"), spaceAfter=4, alignment=1, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#444444"), spaceAfter=10, alignment=1, fontName="Helvetica-Bold")
    meta_style = ParagraphStyle("MetaStyle", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#222222"), leading=12, fontName="Helvetica")

    if logo_bytes:
        try:
            story.append(ReportLabImage(io.BytesIO(logo_bytes), width=90, height=34))
            story.append(Spacer(1, 4))
        except Exception:
            pass

    story.append(Paragraph(clean_for_pdf(doc_title), title_style))
    story.append(Paragraph(clean_for_pdf(subtitle), sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1B2A4A"), spaceAfter=8))

    meta_html = f"""
    <b>Project:</b> {clean_for_pdf(project)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Location/Chainage:</b> {clean_for_pdf(location)}<br/>
    <b>Engineer:</b> {clean_for_pdf(engineer)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {rep_date} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Governing Codes:</b> ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, ISO
    """
    story.append(Paragraph(meta_html, meta_style))
    story.append(Spacer(1, 10))

def build_professional_pdf_footer_and_signatures(story, qr_img_buffer):
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#222222"), leading=11, fontName="Helvetica")
    sec_style = ParagraphStyle("SecTitle", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#1B2A4A"), spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Engineering Approvals & Multi-Standard Compliance Sign-Off</b>", sec_style))
    
    qr_lab_img = ReportLabImage(qr_img_buffer, width=50, height=50)
    sign_cell_1 = Paragraph("<b>Prepared By:</b><br/>Engineer Sign:<br/>___________________", body_style)
    sign_cell_2 = Paragraph("<b>QA/QC Checked:</b><br/>Inspector Sign:<br/>___________________", body_style)
    sign_cell_3 = Paragraph("<b>Consultant Approved:</b><br/>Stamp & Sign:<br/>___________________", body_style)
    qr_cell = [Paragraph("<b>QR Verify:</b>", body_style), qr_lab_img]

    t_sign = Table([[sign_cell_1, sign_cell_2, sign_cell_3, qr_cell]], colWidths=[130, 130, 130, 110])
    t_sign.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F7FA")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (3, 0), (3, 0), "CENTER"),
    ]))
    story.append(t_sign)

# --- AI MODULES & CHATBOT ---
def run_ai_auditor_module():
    st.subheader("🤖 AI Multi-Standard Engineering Auditor (AI-Powered)")
    st.write("Upload any structural, geotechnical, pavement, or material testing document, drawing spec, mix design, or photo. The AI will audit it against **ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, and ISO** standards.")
    
    audit_focus = st.sidebar.selectbox("Engineering Audit Focus", [
        "Multi-Standard Structural & Geotechnical Compliance",
        "Roads, Pavements & Subgrade Materials (ECP 104 & AASHTO)",
        "Soil Mechanics & Foundations (ECP 202 & ASTM / ISO)",
        "Reinforced Concrete Structures & Mix Design (ECP 203 & ACI / BS EN)",
        "Non-Conformance Report (NCR) & Material Testing Review"
    ])

    uploaded_file = st.file_uploader("Upload Engineering Document / Photo (PDF, PNG, JPG, JPEG)", type=["pdf", "png", "jpg", "jpeg"], key="ai_auditor_file_uploader")

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        st.info(f"Uploaded File: {uploaded_file.name}")

        if st.button("Run Multi-Standard Engineering Audit"):
            with st.spinner("Processing file and running multi-standard engineering AI audit..."):
                try:
                    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                    if not api_key:
                        st.error("⚠️ GEMINI_API_KEY is not configured in your Streamlit secrets or environment variables.")
                        return

                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    You are an expert senior civil, geotechnical, and highway engineering consultant specialized in core Egyptian Codes (ECP 203 for structures, ECP 202 for geotechnical/foundations, ECP 104 for roads and pavements) alongside international standards (ASTM, AASHTO, BS, EN, ISO, and supplementary code: {supplementary_code}).
                    Analyze the provided engineering document, technical data sheet, specifications, or image with a focus on: {audit_focus}.
                    
                    Perform a rigorous technical audit checking:
                    1. Correct identification of the element type (Is it a structural concrete element, a geotechnical subgrade/soil layer, or a road pavement layer?).
                    2. Compliance with ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, and ISO clauses, limits, material specifications, and execution rules.
                    3. Identification of any technical discrepancies, code violations, potential structural or geotechnical risks, or missing data requirements.
                    4. Professional recommendations, corrective actions, and required next steps for the site engineering/QC team.
                    """

                    contents = []
                    if file_extension == 'pdf':
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                extracted_text += page_text + "\n"

                        if not extracted_text.strip():
                            st.error("⚠️ Could not extract text from this PDF. Please upload it directly as an image file (PNG/JPG).")
                            return
                        contents = [prompt, f"Extracted PDF Text:\n{extracted_text}"]
                    else:
                        image_part = types.Part.from_bytes(
                            data=uploaded_file.getvalue(),
                            mime_type=uploaded_file.type
                        )
                        contents = [prompt, image_part]

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=contents,
                    )
                    
                    audit_result = response.text
                    st.success("Audit Completed Successfully!")
                    st.markdown("### 📋 Multi-Standard Engineering Audit Findings & Compliance Breakdown")
                    st.markdown(audit_result)

                    # Professional ReportLab PDF Generation
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                    story = []
                    
                    disp_proj = project_name if project_name.strip() else "Unnamed Project"
                    disp_eng = engineer_name if engineer_name.strip() else "Site Engineer"
                    disp_loc = pour_location if pour_location.strip() else "General Site"
                    rep_date_str = report_date.strftime("%Y-%m-%d")

                    build_professional_pdf_header(story, "Multi-Standard Engineering Audit Report", f"Audit Focus: {audit_focus}", company_logo_bytes, disp_eng, disp_proj, disp_loc, rep_date_str)

                    styles = getSampleStyleSheet()
                    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#222222"), leading=14, spaceAfter=6)
                    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading3"], fontSize=11.5, textColor=colors.HexColor("#1B2A4A"), spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")
                    
                    for para in audit_result.split("\n\n"):
                        if para.strip():
                            cleaned_para = clean_for_pdf(para)
                            if para.strip().startswith("###") or para.strip().startswith("**") or (len(para.strip()) < 80 and not para.strip().endswith(".")):
                                title_text = re.sub(r'#{1,6}\s*', '', para.strip()).replace("**", "")
                                story.append(Paragraph(f"<b>{clean_for_pdf(title_text)}</b>", heading_style))
                            else:
                                story.append(Paragraph(cleaned_para.replace('\n', '<br/>'), body_style))

                    qr_data = f"MULTI_CODE_AUDIT | Project: {disp_proj} | Date: {rep_date_str} | Eng: {disp_eng}"
                    qr = qrcode.QRCode(version=1, box_size=4, border=1)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_buf = io.BytesIO()
                    qr_img.save(qr_buf, format="PNG")
                    qr_buf.seek(0)

                    build_professional_pdf_footer_and_signatures(story, qr_buf)
                    doc.build(story)
                    pdf_buffer.seek(0)

                    st.download_button(
                        label="📥 Download Audit Report (PDF)",
                        data=pdf_buffer,
                        file_name="Multi_Standard_Engineering_Audit_Report.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"An error occurred during AI processing: {e}")

def run_crack_defect_analyzer():
    st.subheader("🔍 AI Crack, Pavement & Geotechnical Defect Diagnostic (AI-Powered)")
    st.write("Snap or upload a photo of site defects. The AI automatically distinguishes between **Structural Concrete Members (ECP 203 / ACI / BS EN)**, **Road Pavements & Subbase Layers (ECP 104 / AASHTO)**, and **Geotechnical Soils / Subgrades (ECP 202 / ASTM / ISO)** to provide accurate, context-specific repair protocols.")
    
    defect_image = st.file_uploader("Upload Site Defect Photo (Pavement, Soil, Subgrade, or Concrete)", type=["png", "jpg", "jpeg"], key="crack_uploader")
    
    if defect_image is not None:
        col_img1, col_img2 = st.columns([1, 2])
        with col_img1:
            st.image(defect_image, caption="Uploaded Defect Sample", use_container_width=True)
        with col_img2:
            st.markdown("### 📌 Defect Inspection Ready")
            st.write(f"• **Project:** {project_name if project_name.strip() else 'N/A'}")
            st.write(f"• **Location/Chainage:** {pour_location}")
            st.write(f"• **Inspection Date:** {report_date.strftime('%Y-%m-%d')}")
        
        if st.button("Diagnose Defect & Get Correct Multi-Standard Repair Protocol"):
            with st.spinner("Analyzing defect element type and generating code-compliant repair protocol..."):
                try:
                    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                    if not api_key:
                        st.error("⚠️ GEMINI_API_KEY is not configured in your Streamlit secrets or environment variables.")
                        return

                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    You are an expert forensic civil, geotechnical, and highway repair engineer operating in accordance with ECP 203 (Concrete), ECP 202 (Geotechnical/Soil), ECP 104 (Roads & Pavements), ASTM, AASHTO, BS, EN, and ISO standards (Supplementary Code: {supplementary_code}).
                    
                    Analyze the uploaded site image carefully and determine whether it shows a structural concrete element, a road pavement layer, or a geotechnical soil feature. Provide a structured diagnostic report containing:
                    1. Element Identification & Defect Classification.
                    2. Root Cause Analysis & Severity Assessment.
                    3. Applicable Standards (ECP 203/202/104, ASTM, AASHTO, BS, EN, ISO).
                    4. Correct Materials & Step-by-Step Remediation Procedure.
                    """
                    
                    image_part = types.Part.from_bytes(data=defect_image.getvalue(), mime_type=defect_image.type)
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[prompt, image_part]
                    )
                    
                    diagnostic_text = response.text
                    st.markdown("### 🛠️ Forensic Diagnosis & Multi-Standard Repair Protocol")
                    st.markdown(diagnostic_text)

                    # Generate Professional PDF Report for Defect Diagnosis
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                    story = []

                    disp_proj = project_name if project_name.strip() else "Unnamed Project"
                    disp_eng = engineer_name if engineer_name.strip() else "Site Engineer"
                    disp_loc = pour_location if pour_location.strip() else "General Site"
                    rep_date_str = report_date.strftime("%Y-%m-%d")

                    build_professional_pdf_header(story, "Multi-Standard Defect & Forensic Diagnostic Report", "Geotechnical, Pavement & Concrete Engineering Assessment", company_logo_bytes, disp_eng, disp_proj, disp_loc, rep_date_str)

                    try:
                        story.append(ReportLabImage(io.BytesIO(defect_image.getvalue()), width=140, height=100))
                        story.append(Spacer(1, 6))
                    except Exception:
                        pass

                    styles = getSampleStyleSheet()
                    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#222222"), leading=14, spaceAfter=6)
                    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading3"], fontSize=11.5, textColor=colors.HexColor("#1B2A4A"), spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")

                    for para in diagnostic_text.split("\n\n"):
                        if para.strip():
                            cleaned_para = clean_for_pdf(para)
                            if para.strip().startswith("###") or para.strip().startswith("**") or (len(para.strip()) < 80 and not para.strip().endswith(".")):
                                title_text = re.sub(r'#{1,6}\s*', '', para.strip()).replace("**", "")
                                story.append(Paragraph(f"<b>{clean_for_pdf(title_text)}</b>", heading_style))
                            else:
                                story.append(Paragraph(cleaned_para.replace('\n', '<br/>'), body_style))

                    qr_data = f"DEFECT_DIAGNOSTIC_REPORT | Project: {disp_proj} | Location: {disp_loc} | Date: {rep_date_str}"
                    qr = qrcode.QRCode(version=1, box_size=4, border=1)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_buf = io.BytesIO()
                    qr_img.save(qr_buf, format="PNG")
                    qr_buf.seek(0)

                    build_professional_pdf_footer_and_signatures(story, qr_buf)
                    doc.build(story)
                    pdf_buffer.seek(0)

                    st.download_button(
                        label="📥 Download Defect Report (PDF)",
                        data=pdf_buffer,
                        file_name="Multi_Standard_Defect_Diagnostic_Report.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"Error processing image: {e}")

# --- CHATBOT MODULE ---
def run_core_code_chatbot():
    st.subheader("💬 Core-Code Intelligent Assistant Chatbot (AI-Powered)")
    st.markdown("Ask any engineering, quality control, mix design, geotechnical, or pavement question. The AI answers strictly from our core codes (**ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, ISO**) unless you have selected a specific supplementary code in the sidebar.")

    # Initialize chat history in session state
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = [
            {"role": "assistant", "content": "Hello! I am your Multi-Standard Engineering Assistant. How can I assist you with your civil, geotechnical, pavement, or concrete queries today?"}
        ]

    # Display chat history
    for message in st.session_state.chatbot_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input box
    if user_query := st.chat_input("Ask about ECP, ASTM, AASHTO, mix design, soil compaction, or structural standards..."):
        st.session_state.chatbot_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Consulting core codes & standards..."):
                try:
                    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                    if not api_key:
                        response_text = "⚠️ GEMINI_API_KEY is not configured in your Streamlit secrets or environment variables."
                    else:
                        client = genai.Client(api_key=api_key)
                        
                        system_context = f"""
                        You are an expert AI engineering assistant embedded in a Multi-Standard Civil & Geotechnical QA/QC portal.
                        Your primary knowledge base consists of core standards: ECP 203 (Concrete Structures), ECP 202 (Geotechnical & Foundations), ECP 104 (Roads & Pavements), ASTM, AASHTO, BS, EN, and ISO.
                        The user's currently selected supplementary code is: {supplementary_code}.
                        
                        Provide accurate, professional, concise, and technically rigorous engineering answers citing exact clauses, formulas, limits, and testing protocols from these standards. Always prioritize the core codes unless a supplementary code is specified.
                        """
                        
                        full_prompt = f"{system_context}\n\nUser Question: {user_query}"
                        
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=full_prompt,
                        )
                        response_text = response.text

                    st.markdown(response_text)
                    st.session_state.chatbot_messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    err_msg = f"An error occurred: {e}"
                    st.error(err_msg)
                    st.session_state.chatbot_messages.append({"role": "assistant", "content": err_msg})

# --- CONDITIONAL ROUTING BASED ON APP NAVIGATION SELECTION ---
if app_mode == "🤖 AI Multi-Standard Engineering Auditor (AI-Powered)":
    run_ai_auditor_module()

elif app_mode == "🔍 Crack, Pavement & Geotechnical Defect Diagnostic (AI-Powered)":
    run_crack_defect_analyzer()

elif app_mode == "💬 Core-Code Intelligent Assistant Chatbot (AI-Powered)":
    run_core_code_chatbot()

elif app_mode == "📖 Multi-Standard Technical Codes Handbook (ECP, ASTM, AASHTO, BS, EN, ISO)":
    st.header("📖 Multi-Standard Civil Engineering Technical Handbook")
    st.markdown("Comprehensive reference notes covering **ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, and ISO** standards.")

    tab_hb1, tab_hb2, tab_hb3, tab_hb4 = st.tabs([
        "🏗️ 1. ECP 203 & Structural Concrete", 
        "🌍 2. ECP 202 & Geotechnical Soils", 
        "🛣️ 3. ECP 104 & Roads/Pavements",
        "🌐 4. International Standards (ASTM, AASHTO, BS, EN, ISO)"
    ])

    with tab_hb1:
        st.subheader("Egyptian Code for Reinforced Concrete (ECP 203)")
        st.markdown("""
        * **Scope:** Design and construction of reinforced concrete structures, materials, mixing, placing, and acceptance criteria.
        * **Characteristic Strength ($f_{cu}$):** Evaluated via 150mm cube crushing tests at 28 days.
        * **Statistical Acceptance:** $f_{cu} \\ge \\max(f_m - k \\cdot s, 0.85 f_m)$.
        * **Durability Limits:** Max W/C ratio 0.45 for high grades ($\ge 30\text{ N/mm}^2$), minimum cement content $300\text{ kg/m}^3$.
        """)

    with tab_hb2:
        st.subheader("Egyptian Code for Soil Mechanics & Foundations (ECP 202)")
        st.markdown("""
        * **Scope:** Subsurface investigation, bearing capacity, shallow and deep foundations, earth retaining structures, and slope stability.
        * **Soil Compaction:** Minimum Proctor compaction density (95% to 98% Modified Proctor for subgrades).
        * **Settlement Control:** Differential and total settlement limits under service loads.
        """)

    with tab_hb3:
        st.subheader("Egyptian Code for Roads and Airfields (ECP 104)")
        st.markdown("""
        * **Scope:** Highway alignment, subgrade preparation, unbound subbase and base courses, bituminous asphalt layers, and concrete pavement joints.
        * **Pavement Layers:** Subgrade CBR testing (ASTM D1883 / AASHTO T193), crushed stone base course compaction, and asphalt Marshall stability (ASTM D6927 / AASHTO T245).
        * **Defect Management:** Pavement cracking, rutting, and subgrade settlement are treated via stabilization, milling, and resurfacing—**never** structural epoxy injection.
        """)

    with tab_hb4:
        st.subheader("International Standards Integration (ASTM, AASHTO, BS, EN, ISO)")
        st.markdown("""
        * **ASTM:** American Society for Testing and Materials (e.g., ASTM C39 for concrete cylinders/cubes, ASTM D1557 for soil compaction).
        * **AASHTO:** American Association of State Highway and Transportation Officials (Highway and pavement design and testing).
        * **BS / EN / ISO:** British Standards, European Norms, and International Organization for Standardization governing quality management, cement testing, and structural safety (e.g., ISO 9001, BS EN 1992 / Eurocode 2).
        """)

else:
    # --- VERIFIER DASHBOARD MODE ---
    st.header("1. Input Cube Crushing Results (N/mm²)")
    input_method = st.radio("Choose Input Method:", ["Manual Entry", "Upload Excel File (.xlsx)"], horizontal=True)

    cubes_7, cubes_14, cubes_28 = [], [], []

    def parse_input(text_str):
        if not text_str.strip():
            return []
        return [float(x.strip()) for x in text_str.split(",") if x.strip() != ""]

    if input_method == "Manual Entry":
        st.info("💡 Enter strength values separated by commas.")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.subheader("7-Day Test")
            input_7 = st.text_area("7-Day Cubes:", value="21.0, 22.5, 20.5", height=100)
        with col_b:
            st.subheader("14-Day Test")
            input_14 = st.text_area("14-Day Cubes:", value="26.0, 27.2, 25.8", height=100)
        with col_c:
            st.subheader("28-Day Test")
            input_28 = st.text_area("28-Day Cubes:", value="32.5, 34.0, 31.0, 35.5, 29.0, 33.0", height=100)

        try:
            cubes_7 = parse_input(input_7)
            cubes_14 = parse_input(input_14)
            cubes_28 = parse_input(input_28)
        except ValueError:
            st.error("⚠️ Please enter valid numerical values separated by commas.")
            st.stop()
    else:
        st.info("💡 Upload an Excel file containing cube crushing test data.")
        uploaded_excel = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"], key="excel_uploader")
        if uploaded_excel is not None:
            try:
                excel_file = pd.ExcelFile(uploaded_excel)
                sheet_selected = st.selectbox("Select Sheet:", excel_file.sheet_names)
                df = pd.read_excel(uploaded_excel, sheet_name=sheet_selected)
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                col_1, col_2, col_3 = st.columns(3)
                with col_1:
                    col_7_name = st.selectbox("7-Day Column:", ["None"] + numeric_cols)
                with col_2:
                    col_14_name = st.selectbox("14-Day Column:", ["None"] + numeric_cols)
                with col_3:
                    col_28_name = st.selectbox("28-Day Column:", ["None"] + numeric_cols)

                if col_7_name != "None": cubes_7 = df[col_7_name].dropna().astype(float).tolist()
                if col_14_name != "None": cubes_14 = df[col_14_name].dropna().astype(float).tolist()
                if col_28_name != "None": cubes_28 = df[col_28_name].dropna().astype(float).tolist()
            except Exception as e:
                st.error(f"⚠️ Error reading file: {e}")
                st.stop()
        else:
            st.warning("👈 Please upload an Excel sheet or switch to Manual Entry to continue.")
            st.stop()

    def analyze_stage(cube_list, age_name, target_ratio):
        if not cube_list or len(cube_list) < 3:
            return None
        n_val = len(cube_list)
        mean_val = float(np.mean(cube_list))
        s_val = float(np.std(cube_list, ddof=1)) if n_val > 1 else 0.0
        k_val = 1.91 if n_val < 30 else 1.64
        fcu_calc_1 = mean_val - (k_val * s_val)
        fcu_calc_2 = 0.85 * mean_val
        fcu_char = max(fcu_calc_1, fcu_calc_2)
        min_val = min(cube_list)
        stage_target_fcu = target_ratio * fcu_spec
        cond1 = fcu_char >= stage_target_fcu
        cond2 = min_val >= (0.85 * stage_target_fcu)
        is_compliant = cond1 and cond2
        return {
            "age_name": age_name, "n": n_val, "mean": mean_val, "s": s_val, "k": k_val,
            "fcu_calc_1": fcu_calc_1, "fcu_calc_2": fcu_calc_2, "fcu_char": fcu_char,
            "min": min_val, "target_ratio": target_ratio, "stage_target_fcu": stage_target_fcu,
            "min_threshold": 0.85 * stage_target_fcu, "cond1": cond1, "cond2": cond2, "is_compliant": is_compliant
        }

    stages_data = {
        "7 Days": analyze_stage(cubes_7, "7-Day Stage", 0.70),
        "14 Days": analyze_stage(cubes_14, "14-Day Stage", 0.85),
        "28 Days": analyze_stage(cubes_28, "28-Day Stage", 1.00),
    }

    st.markdown("---")
    st.header("2. Batch Plant Mix Design Compliance Audit (ECP 203 & ASTM C94)")

    with st.container():
        st.markdown("### 🚚 Batch Plant Mix Design Audit Summary")
        st.dataframe(df_mix_audit, use_container_width=True)
        
        mix_overall_text = "PASS - All site mix parameters comply with ECP 203 / ASTM limits." if mix_overall_pass else "FAIL - One or more parameters exceed allowable limits."
        if mix_overall_pass:
            st.success(f"**Overall Mix Verdict:** {mix_overall_text}")
        else:
            st.error(f"**Overall Mix Verdict:** {mix_overall_text}")

    st.markdown("---")
    st.header("3. Cube Compliance Summaries & Detailed Calculation Sheets")
    tabs = st.tabs(["**7-Day Stage**", "**14-Day Stage**", "**28-Day Stage**", "**📐 Worked Calculation Sheet**"])

    for idx, (stage_label, tab) in enumerate(zip(["7 Days", "14 Days", "28 Days"], tabs[:3])):
        with tab:
            res = stages_data[stage_label]
            if res is None:
                st.info(f"ℹ️ Insufficient data for {stage_label} testing (minimum 3 cubes required).")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Sample Count (n)", f"{res['n']} cubes")
                c2.metric("Mean Strength (f_m)", f"{res['mean']:.2f} N/mm²")
                c3.metric("Std. Deviation (s)", f"{res['s']:.2f} N/mm²")
                
                st.markdown("---")
                st.markdown(f"#### 🔍 Detailed Sample-by-Sample & Statistical Breakdown ({stage_label})")
                
                cube_vals = cubes_7 if stage_label == "7 Days" else (cubes_14 if stage_label == "14 Days" else cubes_28)
                sample_breakdown = []
                for i, val in enumerate(cube_vals):
                    min_lim = res['min_threshold']
                    ind_pass = val >= min_lim
                    sample_breakdown.append({
                        "Sample #": i + 1,
                        "Measured Strength (x_i) N/mm²": val,
                        "Min Individual Limit (N/mm²)": round(min_lim, 2),
                        "Individual Check": "PASS ✅" if ind_pass else "FAIL ❌"
                    })
                df_sb = pd.DataFrame(sample_breakdown)
                st.dataframe(df_sb, use_container_width=True)
                
                if res["is_compliant"]:
                    st.success(f"✅ **STAGE PASS ({stage_label}):** Fully satisfied according to ECP 203 & ASTM standards.")
                else:
                    st.error(f"❌ **STAGE FAIL ({stage_label}):** Non-compliant with standard limits.")

    with tabs[3]:
        st.subheader("📐 Fully Worked Numerical Calculation Sheet (ECP 203 / ASTM / ACI)")
        for stage_name, res in stages_data.items():
            if res is not None:
                st.markdown(f"### 🔹 {stage_name} Evaluation Breakdown")
                cube_vals = cubes_7 if stage_name == "7 Days" else (cubes_14 if stage_name == "14 Days" else cubes_28)
                vals_str = ", ".join([str(v) for v in cube_vals])
                st.markdown(f"• **Input Samples:** `[{vals_str}]` (n = {res['n']})")
                st.markdown(f"• **Mean ($f_m$):** {res['mean']:.2f} N/mm² | **StdDev ($s$):** {res['s']:.2f} N/mm²")
                st.markdown(f"• **Characteristic Strength ($f_{{cu}}$):** {res['fcu_char']:.2f} N/mm²")
                st.markdown("---")

    # Visualizations Section
    st.markdown("---")
    st.header("4. Visual Analytics & Strength Trend Charts")
    chart_col1, chart_col2 = st.columns(2)

    chart_data_list = []
    for i, val in enumerate(cubes_7): chart_data_list.append({"Cube Label": f"7-{i+1} ({val})", "Sample Index": i+1, "Strength": val, "Stage": "7 Days"})
    for i, val in enumerate(cubes_14): chart_data_list.append({"Cube Label": f"14-{i+1} ({val})", "Sample Index": i+1, "Strength": val, "Stage": "14 Days"})
    for i, val in enumerate(cubes_28): chart_data_list.append({"Cube Label": f"28-{i+1} ({val})", "Sample Index": i+1, "Strength": val, "Stage": "28 Days"})

    with chart_col1:
        st.subheader("Individual Cube Strengths")
        if chart_data_list:
            df_chart = pd.DataFrame(chart_data_list)
            fig_bars = px.scatter(df_chart, x="Sample Index", y="Strength", color="Stage", text="Cube Label", template="plotly_dark")
            fig_bars.update_traces(mode="text+markers", textposition="top center", marker=dict(size=12))
            fig_bars.update_layout(plot_bgcolor="#031338", paper_bgcolor="#1B2A4A", font=dict(color="#FFFFFF", size=10))
            st.plotly_chart(fig_bars, use_container_width=True)

    summary_chart_data = []
    for stage_key in ["7 Days", "14 Days", "28 Days"]:
        res = stages_data[stage_key]
        if res:
            summary_chart_data.append({"Stage": stage_key, "Calculated fcu": res["fcu_char"], "Target Requirement": res["stage_target_fcu"]})

    with chart_col2:
        st.subheader("Characteristic $f_{cu}$ vs Target")
        if summary_chart_data:
            df_summary_chart = pd.DataFrame(summary_chart_data)
            fig_lines = go.Figure()
            fig_lines.add_trace(go.Scatter(x=df_summary_chart["Stage"], y=df_summary_chart["Calculated fcu"], mode="lines+markers+text", text=[f"{v:.2f}" for v in df_summary_chart["Calculated fcu"]], name="Calculated fcu", line=dict(color="#00BFFF", width=3)))
            fig_lines.add_trace(go.Scatter(x=df_summary_chart["Stage"], y=df_summary_chart["Target Requirement"], mode="lines+markers+text", text=[f"{v:.2f}" for v in df_summary_chart["Target Requirement"]], name="Target", line=dict(color="#FF8C00", width=3, dash="dash")))
            fig_lines.update_layout(plot_bgcolor="#031338", paper_bgcolor="#1B2A4A", font=dict(color="#FFFFFF", size=10))
            st.plotly_chart(fig_lines, use_container_width=True)

    display_project_name = project_name if project_name.strip() else "Unnamed Project"
    display_engineer_name = engineer_name if engineer_name.strip() else "Not Specified"
    formatted_report_date = report_date.strftime("%Y-%m-%d")
    formatted_casting_date = casting_date.strftime("%Y-%m-%d")

    overview_data = [
        {"Parameter": "Project Name", "Details": display_project_name},
        {"Parameter": "Structural Element / Chainage", "Details": pour_location},
        {"Parameter": "Specified 28-Day Grade ($f_{cu}$)", "Details": f"{fcu_spec} N/mm²"},
        {"Parameter": "Mixer Truck / Equipment ID", "Details": mixer_truck_no},
        {"Parameter": "Batch Ticket / Geo-Log ID", "Details": batch_ticket_id},
        {"Parameter": "Casting Date", "Details": formatted_casting_date},
        {"Parameter": "Cement Content", "Details": f"{cement_content_val} kg/m³"},
        {"Parameter": "Water Content", "Details": f"{water_content_val} kg/m³"},
        {"Parameter": "Water-Cement Ratio (W/C)", "Details": f"{wc_ratio:.2f}"},
        {"Parameter": "Engineer Name", "Details": display_engineer_name},
        {"Parameter": "Report Date", "Details": formatted_report_date},
        {"Parameter": "Governing Standards", "Details": f"Core: ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, ISO | Suppl: {supplementary_code}"},
    ]
    df_overview = pd.DataFrame(overview_data)

    max_len = max(len(cubes_7), len(cubes_14), len(cubes_28), 1)
    raw_matrix = {
        "Cube Sample #": list(range(1, max_len + 1)),
        "7-Day Strength (N/mm²)": cubes_7 + [None] * (max_len - len(cubes_7)),
        "14-Day Strength (N/mm²)": cubes_14 + [None] * (max_len - len(cubes_14)),
        "28-Day Strength (N/mm²)": cubes_28 + [None] * (max_len - len(cubes_28)),
    }
    df_raw_cubes = pd.DataFrame(raw_matrix)

    summary_rows = []
    for stage_key in ["7 Days", "14 Days", "28 Days"]:
        res = stages_data[stage_key]
        if res:
            summary_rows.append({
                "Testing Stage": stage_key, "Sample Count (n)": res["n"], "Target Ratio": f"{int(res['target_ratio']*100)}%",
                "Target Strength (N/mm²)": round(res["stage_target_fcu"], 2), "Mean Strength (N/mm²)": round(res["mean"], 2),
                "Standard Deviation (N/mm²)": round(res["s"], 2), "Margin Factor (k)": res["k"],
                "Calculated fcu (N/mm²)": round(res["fcu_char"], 2), "Min Individual Cube (N/mm²)": round(res["min"], 2),
                "Compliance Verdict": "PASS" if res["is_compliant"] else "FAIL"
            })
    df_summary_table = pd.DataFrame(summary_rows)

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_overview.to_excel(writer, sheet_name="Project Overview & Metadata", index=False)
        df_mix_audit.to_excel(writer, sheet_name="Mix Design Audit", index=False)
        df_summary_table.to_excel(writer, sheet_name="Multi-Stage Results Summary", index=False)
        df_raw_cubes.to_excel(writer, sheet_name="Raw Individual Cubes", index=False)
    excel_buffer.seek(0)

    def generate_pdf_report(logo_bytes=None):
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        section_style = ParagraphStyle("SecTitle", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#1B2A4A"), spaceBefore=12, spaceAfter=4, fontName="Helvetica-Bold")

        build_professional_pdf_header(story, "Multi-Standard Concrete Acceptance & Mix Compliance Report", "Multi-Stage Verification & Statistical Audit", logo_bytes, display_engineer_name, display_project_name, pour_location, formatted_report_date)

        story.append(Paragraph("<b>1. Project Overview & Traceability Metadata</b>", section_style))
        overview_data_list = [["Parameter", "Details"]] + df_overview.values.tolist()
        t_overview = Table(overview_data_list, colWidths=[180, 360])
        t_overview.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>2. Batch Plant Mix Design Compliance Audit</b>", section_style))
        mix_table_rows = [list(df_mix_audit.columns)] + df_mix_audit.values.tolist()
        t_mix = Table(mix_table_rows, colWidths=[180, 120, 120, 120])
        t_mix.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ]))
        story.append(t_mix)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>3. Cube Compliance Results Summary & Statistical Evaluation</b>", section_style))
        summary_headers = ["Stage", "n", "Target", "Req (MPa)", "Mean (MPa)", "StdDev", "fcu (MPa)", "Verdict"]
        summary_table_rows = [summary_headers]
        for r in summary_rows:
            summary_table_rows.append([str(r["Testing Stage"]), str(r["Sample Count (n)"]), str(r["Target Ratio"]), str(r["Target Strength (N/mm²)"]), str(r["Mean Strength (N/mm²)"]), str(r["Standard Deviation (N/mm²)"]), str(r["Calculated fcu (N/mm²)"]), str(r["Compliance Verdict"])])
        t_summary = Table(summary_table_rows, colWidths=[65, 30, 45, 60, 65, 55, 65, 115])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>4. Raw Individual Cube Strengths Matrix & Sample Counts</b>", section_style))
        raw_headers = list(df_raw_cubes.columns)
        raw_table_rows = [raw_headers]
        for idx, row in df_raw_cubes.iterrows():
            raw_table_rows.append([
                str(row["Cube Sample #"]),
                str(row["7-Day Strength (N/mm²)"]) if pd.notna(row["7-Day Strength (N/mm²)"]) else "-",
                str(row["14-Day Strength (N/mm²)"]) if pd.notna(row["14-Day Strength (N/mm²)"]) else "-",
                str(row["28-Day Strength (N/mm²)"]) if pd.notna(row["28-Day Strength (N/mm²)"]) else "-"
            ])
        t_raw = Table(raw_table_rows, colWidths=[100, 146, 146, 148])
        t_raw.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(t_raw)
        story.append(Spacer(1, 6))

        qr_data_content = f"MULTI_CODE_VERIFIED | Project: {display_project_name} | Location: {pour_location} | Ticket: {batch_ticket_id} | Date: {formatted_report_date} | Engineer: {display_engineer_name}"
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(qr_data_content)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        build_professional_pdf_footer_and_signatures(story, qr_buffer)

        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

    pdf_data = generate_pdf_report(company_logo_bytes)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📥 Download Excel Report (.xlsx)",
            data=excel_buffer,
            file_name=f"MultiCode_Report_{display_project_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col_btn2:
        st.download_button(
            label="📄 Download Professional PDF Report (.pdf)",
            data=pdf_data,
            file_name=f"MultiCode_Report_{display_project_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

# --- LUXURY CORPORATE FOOTER SECTION (BIG COMPANY FORMAT) ---
st.markdown("---")
footer_html = """
<div class="corporate-footer">
  <div class="corporate-footer-grid">
    <div class="corporate-footer-col">
      <h4>🏗️ Multi-Standard Engineering QA Portal</h4>
      <p>Automated compliance verification platform across ECP 203, ECP 202, ECP 104, ASTM, AASHTO, BS, EN, and ISO standards.</p>
    </div>
    <div class="corporate-footer-col" style="text-align: right;">
      <h4>Professional Contacts</h4>
      <p>
        LinkedIn: <a href="https://www.linkedin.com/in/mohamed-abd-al-aty-a326a1214/" target="_blank">Mohamed Abd Al Aty</a><br/>
        Email: <a href="mailto:mohamedabdalaty63@gmail.com">mohamedabdalaty63@gmail.com</a><br/>
        <span>Specialized in Geotechnical QA/QC & Civil Engineering Standards.</span>
      </p>
    </div>
  </div>
  <div class="corporate-footer-bottom">
    <div>© 2026 Eng. Mohamed Abd Al Aty. All rights reserved.</div>
    <div>AI-Powered Civil Engineering Assistant</div>
  </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
