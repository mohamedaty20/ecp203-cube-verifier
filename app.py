import io
import datetime
import os
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

# Google GenAI for AI Auditor
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

# FPDF for AI Lab Report Audit PDF exports (aliased to avoid collision with ReportLab Image)
from fpdf import FPDF

# --- 1. PAGE CONFIGURATION (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="ECP 203 Concrete Cube & Mix Verifier",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- AI AUDITOR PDF CLASS ---
class AuditPDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'ECP 203 Lab Report Audit & Cube Verification', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def run_ai_auditor_module():
    st.subheader("🤖 AI Lab Report & ECP 203 Auditor")
    st.write("Upload a PDF lab report. Python will instantly extract the text locally and audit it against ECP 203 standards.")

    # File Uploader focused on PDFs for local text extraction
    uploaded_file = st.file_uploader("Upload Lab Report (PDF)", type=["pdf"])

    if uploaded_file is not None:
        st.info(f"Uploaded Document: {uploaded_file.name}")

        if st.button("Run Fast ECP 203 Audit"):
            with st.spinner("Extracting text and running audit..."):
                try:
                    # 1. Locally extract text from the PDF using Python (Super fast, zero API lag)
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"

                    if not extracted_text.strip():
                        st.error("⚠️ Could not extract text from this PDF. It might be scanned as an image. Please ensure it's a text-based PDF.")
                        return

                    # 2. Initialize Gemini Client using Streamlit secrets or environment variables
                    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                    if not api_key:
                        st.error("⚠️ GEMINI_API_KEY is not configured in your Streamlit secrets or environment variables.")
                        return

                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    You are an expert civil quality control engineer specialized in the Egyptian Code of Practice (ECP 203) for reinforced concrete structures.
                    Analyze the following extracted text from a concrete cube test report or data sheet:
                    
                    {extracted_text}
                    
                    Verify the following:
                    1. Check if characteristic compressive strength (fcu) meets the specified design grade.
                    2. Check testing ages (7-day and 28-day strength criteria and progression).
                    3. Identify any non-conformances (NCR), outliers, or failures to meet ECP 203 compliance tolerances.
                    Provide a detailed, professional audit report with clear headings, findings, and recommendations.
                    """

                    # 3. Send text with thinking_level set to LOW for instant generation on 3.7-flash
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
                        )
                    )
                    
                    audit_result = response.text
                    st.success("Audit Completed Instantly!")
                    st.markdown("### 📋 Audit Findings")
                    st.markdown(audit_result)

                    # PDF Report Generation for Audit
                    pdf = AuditPDFReport()
                    pdf.add_page()
                    pdf.set_font("helvetica", size=10)
                    
                    clean_text = audit_result.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, clean_text)
                    
                    pdf_output_path = "ecp203_audit_report.pdf"
                    pdf.output(pdf_output_path)

                    with open(pdf_output_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Audit Report (PDF)",
                            data=pdf_file,
                            file_name="ECP203_Lab_Audit_Report.pdf",
                            mime="application/pdf"
                        )

                except Exception as e:
                    st.error(f"An error occurred during AI processing: {e}")

# --- 2. CUSTOM STYLING ---
dark_style = """
<style>
.stApp {
    background-color: #031338 !important;
    color: #121417 !important;
}
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}
[data-testid="stImage"] {
    width: 100vw !important;
    position: relative !important;
    left: 50% !important;
    right: 50% !important;
    margin-left: -50vw !important;
    margin-right: -50vw !important;
    margin-bottom: 2rem !important;
}
[data-testid="stImage"] img {
    width: 100% !important;
    object-fit: cover;
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
button[aria-label="Close sidebar"], 
button[aria-label="Open sidebar"] {
    color: #FFFFFF !important;
    background-color: #1B2A4A !important;
}
.author-credit {
    color: #FFFFFF !important;
    font-size: 1rem;
    font-weight: bold;
    margin-top: -15px;
    margin-bottom: 15px;
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
.stDownloadButton>button {
    background-color: #020461 !important;
    color: #FFFFFF !important;
    border: none;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}
.stDownloadButton>button:hover {
    background-color: #8f010b !important;
    color: #FFFFFF !important;
}
hr {
    border-color: #262730 !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"], div[data-baseweb="card"] {
    background-color: #1B2A4A !important;
}
div[data-testid="stDataFrame"] > div {
    background-color: #1B2A4A !important;
}
.dataframe {
    background-color: #1B2A4A !important;
    color: #FFFFFF !important;
}
.footer-container {
    background: linear-gradient(135deg, #1B2A4A 0%, #031338 100%);
    border: 1px solid #FF8C00;
    border-radius: 10px;
    padding: 25px;
    margin-top: 4rem;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
}
</style>
"""
st.markdown(dark_style, unsafe_allow_html=True)

# --- 3. TOP BANNER / COVER PHOTO ---
if os.path.exists("logo.png"):
    st.image("logo.png")

ticker_html = """
<div style="overflow: hidden; white-space: nowrap; background-color: #FF8C00; color: #031338; padding: 8px 0; font-weight: bold; font-size: 15px; margin-bottom: 20px; border-radius: 4px;">
  <div style="display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite;">
    🚀 ECP 203 Concrete Quality Control Active &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; ⚠️ Ensure all cube crushing results and batch tickets are verified daily &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; 🏗️ Current Project Inspection in Progress
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

st.title("ECP 203 Concrete Acceptance & Mix Compliance Verifier")
st.markdown(
    '<p class="author-credit">Made by Eng. Mohamed Abd Al Aty</p>',
    unsafe_allow_html=True,
)

# --- APP SCREEN NAVIGATION SELECTOR (Including AI Auditor) ---
app_mode = st.radio(
    "📱 App Screen Navigation:",
    [
        "📊 Verifier Dashboard",
        "🤖 AI Lab Report Auditor",
        "📖 ECP 203 Official Formulas & Site Instructions Handbook",
    ],
    horizontal=True,
)
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("PROJECT & BATCH DETAILS")
project_name = st.sidebar.text_input("Project Name", value="", placeholder="Enter project name")
pour_location = st.sidebar.text_input("Structural Element / Pour Location", "Slab Axis A1-C5")
fcu_spec = st.sidebar.number_input("Specified 28-Day Grade fcu (N/mm²)", min_value=10.0, max_value=100.0, value=30.0, step=5.0)

st.sidebar.subheader("🚚 Batch Plant & Site Logs")
mixer_truck_no = st.sidebar.text_input("Mixer Truck No.", value="TRK-104")
batch_ticket_id = st.sidebar.text_input("Batch Ticket ID", value="BT-99482")
casting_date = st.sidebar.date_input("Casting Date", value=datetime.date.today() - datetime.timedelta(days=7))

st.sidebar.subheader("⚖️ Mix Design Specifications")
cement_content = st.sidebar.number_input("Cement Content (kg/m³)", min_value=200.0, max_value=600.0, value=350.0, step=10.0)
water_content = st.sidebar.number_input("Free Water Content (kg/m³)", min_value=100.0, max_value=300.0, value=150.0, step=5.0)
wc_ratio = water_content / cement_content if cement_content > 0 else 0.0
st.sidebar.write(f"• **Calculated W/C Ratio:** `{wc_ratio:.2f}`")

slump_value = st.sidebar.number_input("Slump Test Value (mm)", min_value=0.0, max_value=300.0, value=150.0, step=5.0)
concrete_temp = st.sidebar.number_input("Concrete Temp (°C)", min_value=0.0, max_value=60.0, value=28.5, step=0.5)

engineer_name = st.sidebar.text_input("Engineer Name", value="", placeholder="Enter your name")
report_date = st.sidebar.date_input("Report Date", value=datetime.date.today())

st.sidebar.markdown("---")
st.sidebar.header("COMPANY BRANDING")
company_logo_file = st.sidebar.file_uploader("Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
company_logo_bytes = company_logo_file.read() if company_logo_file else None

# --- BATCH PLANT MIX DESIGN ECP 203 AUDIT LOGIC ---
max_allowed_wc = 0.45 if fcu_spec >= 30 else 0.50
min_allowed_cement = 300.0
max_allowed_temp = 35.0

wc_compliant = wc_ratio <= max_allowed_wc
cement_compliant = cement_content >= min_allowed_cement
temp_compliant = concrete_temp <= max_allowed_temp
mix_overall_pass = wc_compliant and cement_compliant and temp_compliant

mix_audit_rows = [
    {
        "Mix Parameter": "Water-Cement Ratio (W/C)",
        "Actual Value": f"{wc_ratio:.2f}",
        "ECP 203 Limit": f"≤ {max_allowed_wc:.2f}",
        "Status": "PASS" if wc_compliant else "FAIL"
    },
    {
        "Mix Parameter": "Minimum Cement Content",
        "Actual Value": f"{cement_content} kg/m³",
        "ECP 203 Limit": f"≥ {min_allowed_cement} kg/m³",
        "Status": "PASS" if cement_compliant else "FAIL"
    },
    {
        "Mix Parameter": "Fresh Concrete Temperature",
        "Actual Value": f"{concrete_temp} °C",
        "ECP 203 Limit": f"≤ {max_allowed_temp} °C",
        "Status": "PASS" if temp_compliant else "FAIL"
    }
]
df_mix_audit = pd.DataFrame(mix_audit_rows)

# Input Mode Selector for Cubes
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

if not (cubes_7 or cubes_14 or cubes_28):
  st.warning("⚠️ Please provide cube strength data for at least one testing age.")
  st.stop()

# Statistical analysis function
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

# --- CONDITIONAL DISPLAY BASED ON SELECTED APP MODE ---
if app_mode == "📖 ECP 203 Official Formulas & Site Instructions Handbook":
  st.markdown("---")
  st.header("📖 Egyptian Code of Practice (ECP 203) - Technical Reference Handbook")
  st.markdown("Professional guidance notes, acceptance criteria formulas, and site quality control protocols.")

  tab_hb1, tab_hb2, tab_hb3 = st.tabs(["🏗️ 1. Characteristic Strength Formulas", "⚖️ 2. Mix Proportioning & Limits", "📋 3. Site Inspection Instructions"])

  with tab_hb1:
    st.subheader("Statistical Acceptance Criteria & Formulas (ECP 203)")
    st.markdown("""
    According to the Egyptian Code for Design and Construction of Reinforced Concrete Structures (**ECP 203**), structural concrete acceptance is evaluated based on standard cube crushing tests (150mm cubes tested at 28 days unless specified otherwise).

    * **1. Arithmetic Mean Strength ($f_m$):**
      $$f_m = \\frac{\\sum_{i=1}^{n} x_i}{n}$$
    * **2. Standard Deviation ($s$):**
      $$s = \\sqrt{\\frac{\\sum_{i=1}^{n} (x_i - f_m)^2}{n - 1}}$$
    * **3. Characteristic Compressive Strength ($f_{cu}$):**
      $$f_{cu} = \\max\\left(f_m - k \\cdot s,\\; 0.85 \\cdot f_m\\right)$$
      *(Note: Factor $k = 1.91$ for $n < 30$, and $1.64$ for $n \\ge 30$)*
    """)

  with tab_hb2:
    st.subheader("Mix Design Limits & Compliance Thresholds (ECP 203)")
    st.markdown("""
    * **Water-Cement Ratio (W/C):** Max 0.45 for grade $\\ge 30\\text{ N/mm}^2$; Max 0.50 for lower grades.
    * **Minimum Cement Content:** At least $300\\text{ kg/m}^3$ for durability.
    * **Fresh Concrete Temperature:** Must not exceed $35\\text{ °C}$ during placement.
    """)

  with tab_hb3:
    st.subheader("Site Quality Control Guidelines")
    st.markdown("""
    1. **Sampling Frequency:** At least one set of 6 cubes per $100\\text{ m}^3$ or structural pour per shift.
    2. **Curing:** Immediate water curing at $20 \\pm 2\\text{ °C}$ until testing age.
    """)

elif app_mode == "🤖 AI Lab Report Auditor":
  st.markdown("---")
  run_ai_auditor_module()

else:
  # --- VERIFIER DASHBOARD MODE ---
  st.markdown("---")
  st.header("2. Batch Plant Mix Design ECP 203 Compliance Audit")

  with st.container():
    st.markdown("### 🚚 Batch Plant Mix Design Audit Summary")
    st.dataframe(df_mix_audit, use_container_width=True)
    
    mix_overall_text = "PASS - All site mix parameters comply with ECP 203 limits." if mix_overall_pass else "FAIL - One or more parameters exceed ECP 203 allowable limits."
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
        
        st.markdown(
            f"* **Arithmetic Mean ($f_m$):** {res['mean']:.2f} N/mm²\n"
            f"* **Standard Deviation ($s$):** {res['s']:.2f} N/mm²\n"
            f"* **Factor ($k$):** {res['k']} (for $n = {res['n']}$)\n"
            f"* **Characteristic Strength ($f_{{cu}}$):** **{res['fcu_char']:.2f} N/mm²**\n"
            f"* **Target Required Strength ($f_{{cu,\\text{{target}}}}$):** {res['stage_target_fcu']:.2f} N/mm²\n"
            f"* **Minimum Individual Cube Limit ($0.85 \\cdot f_{{cu,\\text{{target}}}}$):** {res['min_threshold']:.2f} N/mm²"
        )
        
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
          st.success(f"✅ **STAGE PASS ({stage_label}):** Fully satisfied according to ECP 203.")
        else:
          st.error(f"❌ **STAGE FAIL ({stage_label}):** Non-compliant with ECP 203 limits.")

  with tabs[3]:
    st.subheader("📐 Fully Worked Numerical Calculation Sheet (ECP 203)")
    for stage_name, res in stages_data.items():
      if res is not None:
        st.markdown(f"### 🔹 {stage_name} Evaluation Breakdown")
        cube_vals = cubes_7 if stage_name == "7 Days" else (cubes_14 if stage_name == "14 Days" else cubes_28)
        vals_str = ", ".join([str(v) for v in cube_vals])
        
        st.markdown(f"""
        * **Input Samples ($x_i$):** `[{vals_str}]` ($n = {res['n']}$)
        * **Arithmetic Mean ($f_m$):** {res['mean']:.2f} N/mm²
        * **Standard Deviation ($s$):** {res['s']:.2f} N/mm²
        * **Characteristic Strength ($f_{{cu}}$):** {res['fcu_char']:.2f} N/mm²
        """)
        st.markdown("---")
      else:
        st.markdown(f"### 🔹 {stage_name} Evaluation Breakdown")
        st.info(f"No data available for {stage_name}.")
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
    st.subheader("Characteristic fcu vs Target")
    if summary_chart_data:
      df_summary_chart = pd.DataFrame(summary_chart_data)
      fig_lines = go.Figure()
      fig_lines.add_trace(go.Scatter(x=df_summary_chart["Stage"], y=df_summary_chart["Calculated fcu"], mode="lines+markers+text", text=[f"{v:.2f}" for v in df_summary_chart["Calculated fcu"]], name="Calculated fcu", line=dict(color="#00BFFF", width=3)))
      fig_lines.add_trace(go.Scatter(x=df_summary_chart["Stage"], y=df_summary_chart["Target Requirement"], mode="lines+markers+text", text=[f"{v:.2f}" for v in df_summary_chart["Target Requirement"]], name="Target", line=dict(color="#FF8C00", width=3, dash="dash")))
      fig_lines.update_layout(plot_bgcolor="#031338", paper_bgcolor="#1B2A4A", font=dict(color="#FFFFFF", size=10))
      st.plotly_chart(fig_lines, use_container_width=True)

# DataFrames for Export
display_project_name = project_name if project_name.strip() else "Unnamed Project"
display_engineer_name = engineer_name if engineer_name.strip() else "Not Specified"
formatted_report_date = report_date.strftime("%Y-%m-%d")
formatted_casting_date = casting_date.strftime("%Y-%m-%d")

overview_data = [
    {"Parameter": "Project Name", "Details": display_project_name},
    {"Parameter": "Structural Element / Pour Location", "Details": pour_location},
    {"Parameter": "Specified 28-Day Grade (fcu)", "Details": f"{fcu_spec} N/mm²"},
    {"Parameter": "Mixer Truck Number", "Details": mixer_truck_no},
    {"Parameter": "Batch Ticket ID", "Details": batch_ticket_id},
    {"Parameter": "Casting Date", "Details": formatted_casting_date},
    {"Parameter": "Cement Content", "Details": f"{cement_content} kg/m³"},
    {"Parameter": "Water Content", "Details": f"{water_content} kg/m³"},
    {"Parameter": "Water-Cement Ratio (W/C)", "Details": f"{wc_ratio:.2f}"},
    {"Parameter": "Fresh Concrete Slump", "Details": f"{slump_value} mm"},
    {"Parameter": "Fresh Concrete Temperature", "Details": f"{concrete_temp} °C"},
    {"Parameter": "Engineer Name", "Details": display_engineer_name},
    {"Parameter": "Report Date", "Details": formatted_report_date},
    {"Parameter": "Standard Specification", "Details": "Egyptian Code of Practice (ECP 203)"},
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

# Excel Export Buffer
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_overview.to_excel(writer, sheet_name="Project Overview & Metadata", index=False)
  df_mix_audit.to_excel(writer, sheet_name="Mix Design Audit", index=False)
  df_summary_table.to_excel(writer, sheet_name="Multi-Stage Results Summary", index=False)
  df_raw_cubes.to_excel(writer, sheet_name="Raw Individual Cubes", index=False)
excel_buffer.seek(0)

# PDF Report Generation Function
def generate_pdf_report(logo_bytes=None):
  pdf_buffer = io.BytesIO()
  doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
  story = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#1B2A4A"), spaceAfter=4, alignment=1)
  subtitle_style = ParagraphStyle("DocSub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#000000"), spaceAfter=15, alignment=1)
  section_style = ParagraphStyle("SecTitle", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#000000"), spaceBefore=8, spaceAfter=3)
  body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#333333"), spaceAfter=3)

  if logo_bytes:
    try:
      story.append(ReportLabImage(io.BytesIO(logo_bytes), width=120, height=45))
      story.append(Spacer(1, 4))
    except Exception:
      pass

  story.append(Paragraph("ECP 203 Concrete Acceptance & Mix Compliance Report", title_style))
  story.append(Paragraph(f"Multi-Stage Verification & Mix Audit | Report Date: {formatted_report_date}", subtitle_style))
  story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1B2A4A"), spaceAfter=6))

  # Overview Table
  story.append(Paragraph("<b>1. Project Overview & Traceability Metadata</b>", section_style))
  overview_data_list = [["Parameter", "Details"]] + df_overview.values.tolist()
  t_overview = Table(overview_data_list, colWidths=[180, 360])
  t_overview.setStyle(TableStyle([
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
      ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
      ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
      ("FONTSIZE", (0, 0), (-1, -1), 8),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
      ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
  ]))
  story.append(t_overview)
  story.append(Spacer(1, 4))

  # Mix Audit Table
  story.append(Paragraph("<b>2. Batch Plant Mix Design ECP 203 Compliance Audit</b>", section_style))
  mix_table_rows = [list(df_mix_audit.columns)] + df_mix_audit.values.tolist()
  t_mix = Table(mix_table_rows, colWidths=[180, 120, 120, 120])
  t_mix.setStyle(TableStyle([
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
      ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
      ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
      ("FONTSIZE", (0, 0), (-1, -1), 8),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
  ]))
  story.append(t_mix)
  story.append(Spacer(1, 4))

  # Summary Table
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
      ("FONTSIZE", (0, 0), (-1, -1), 8),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
  ]))
  story.append(t_summary)
  story.append(Spacer(1, 4))

  # Raw Cubes Matrix
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
      ("FONTSIZE", (0, 0), (-1, -1), 8),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
      ("ALIGN", (0, 0), (-1, -1), "CENTER"),
  ]))
  story.append(t_raw)
  story.append(Spacer(1, 4))

  # QR Code Generation
  qr_data_content = f"ECP203_VERIFIED | Project: {display_project_name} | Location: {pour_location} | Ticket: {batch_ticket_id} | Date: {formatted_report_date} | Engineer: {display_engineer_name}"
  qr = qrcode.QRCode(version=1, box_size=5, border=1)
  qr.add_data(qr_data_content)
  qr.make(fit=True)
  qr_img = qr.make_image(fill_color="black", back_color="white")
  
  qr_buffer = io.BytesIO()
  qr_img.save(qr_buffer, format="PNG")
  qr_buffer.seek(0)
  reportlab_qr_image = ReportLabImage(qr_buffer, width=65, height=65)

  # Sign-Off Block
  story.append(Paragraph("<b>5. Engineering Sign-Off & Approvals & Digital Verification</b>", section_style))
  sign_cell_1 = Paragraph(f"<b>Prepared By:</b><br/>{display_engineer_name}<br/>Sign: _________", body_style)
  sign_cell_2 = Paragraph("<b>Checked By (QA/QC):</b><br/>Name: _________<br/>Sign: _________", body_style)
  sign_cell_3 = Paragraph("<b>Approved (Consultant):</b><br/>Name: _________<br/>Sign: _________", body_style)
  qr_cell = [Paragraph("<b>Scan to Verify:</b>", body_style), reportlab_qr_image]
  
  t_sign = Table([[sign_cell_1, sign_cell_2, sign_cell_3, qr_cell]], colWidths=[140, 140, 140, 100])
  t_sign.setStyle(TableStyle([
      ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9F9F9")),
      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
      ("TOPPADDING", (0, 0), (-1, -1), 4),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
      ("ALIGN", (3, 0), (3, 0), "CENTER"),
  ]))
  story.append(t_sign)

  doc.build(story)
  pdf_buffer.seek(0)
  return pdf_buffer

pdf_data = generate_pdf_report(company_logo_bytes)

# Download Buttons Section
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
  st.download_button(
      label="📥 Download Excel Report (.xlsx)",
      data=excel_buffer,
      file_name=f"ECP203_Report_{display_project_name.replace(' ', '_')}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
with col_btn2:
  st.download_button(
      label="📄 Download Professional PDF Report (.pdf)",
      data=pdf_data,
      file_name=f"ECP203_Report_{display_project_name.replace(' ', '_')}.pdf",
      mime="application/pdf",
  )

# --- LUXURY CORPORATE FOOTER SECTION ---
st.markdown("---")
st.markdown(
    """
    <div class="footer-container">
      <div style="display: flex; justify-content: space-between; flex-wrap: wrap; align-items: center;">
        <div style="flex: 1; min-width: 250px; margin-bottom: 15px;">
          <h4 style="color: #FF8C00; margin-bottom: 5px; font-size: 1.1rem;">🏗️ ECP 203 Quality Assurance Portal</h4>
          <p style="color: #CCCCCC; font-size: 0.85rem; margin: 0;">Automated statistical compliance verification and rigorous structural mix design auditing platform built for elite civil engineering teams.</p>
        </div>
        <div style="flex: 1; min-width: 200px; text-align: right; margin-bottom: 15px;">
          <p style="color: #FFFFFF; font-size: 0.9rem; margin-bottom: 5px;"><b>Official Direct Contacts:</b></p>
          <p style="margin: 0; font-size: 0.85rem;">
            Linkedin: <a href='https://www.linkedin.com/in/mohamed-abd-al-aty-a326a1214/' target='_blank' style='color: #00BFFF; text-decoration: none;'>Mohamed Abd Al Aty</a><br>
            Gmail: <a href='mailto:mohamedabdalaty63@gmail.com' style='color: #00BFFF; text-decoration: none;'>mohamedabdalaty63@gmail.com</a>
          </p>
        </div>
      </div>
      <hr style="border-color: rgba(255,140,0,0.3); margin: 15px 0;">
      <div style="text-align: center;">
        <p style="color: #888888; font-size: 0.8rem; margin: 0;">© 2026 Eng. Mohamed Abd Al Aty. All rights reserved. Designed to Egyptian Code of Practice (ECP 203) standards.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
