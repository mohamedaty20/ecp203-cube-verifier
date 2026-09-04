import io
import numpy as np
import pandas as pd
import streamlit as st
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

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
)

# 1. Page Configuration (MUST be first Streamlit command)
st.set_page_config(
    page_title="ECP 203 Concrete Cube Verifier",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom Styling (Navy Blue Sidebar & Padded Main Layout)
dark_style = """
<style>
/* Force dark background on the entire app */
.stApp {
    background-color: #031338 !important;
    color: #121417 !important;
}

/* Give the main container proper padding so text never touches the sidebar */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}

/* Break the top banner image out of the padding to span 100% edge-to-edge */
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

/* Hide Streamlit default menu/footer but keep sidebar toggle visible */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

/* Navy Blue Sidebar Styling */
[data-testid="stSidebar"], 
section[data-testid="stSidebar"] > div {
    background-color: #1B2A4A !important;
}

/* Bold White Text in Sidebar */
[data-testid="stSidebar"] *, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-weight: bold !important;
}

/* Sidebar Arrow Toggle Button Styling */
button[aria-label="Close sidebar"], 
button[aria-label="Open sidebar"] {
    color: #FFFFFF !important;
    background-color: #1B2A4A !important;
}

/* Author Credit Subtitle Styling */
.author-credit {
    color: #FFFFFF !important;
    font-size: 1rem;
    font-weight: bold;
    margin-top: -15px;
    margin-bottom: 15px;
}

/* General Text Formatting */
p, span, label, div {
    color: #FFFFFF !important;
}

/* Main Headings (Blue) */
h1 {
    color: #00BFFF !important;
    font-weight: 700;
}

/* Subtitles and Section Headers (Red) */
h2, h3, .stSubheader {
    color: #FF8C00 !important;
    font-weight: 600;
}

/* Metric Cards */
[data-testid="stMetricValue"] {
    color: #7e8385 !important;
}

/* Text Inputs and Area Formatting */
textarea, input {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
    border: 1px solid #FF8C00 !important;
}

/* Download Button Styling with Custom Font */
.stDownloadButton>button {
    background-color: #020461 !important;
    color: #FFFFFF !important;
    border: none;
    font-family: 'Segoe UI', Arial, sans-serif !important; /* Change your font style here */
    font-size: 15px !important;
    font-weight: 600 !important;
    font-style: normal !important; /* Can be 'italic' if you want it italicized */
}

.stDownloadButton>button:hover {
    background-color: #8f010b !important;
    color: #FFFFFF !important;
}

/* Section Separator Lines */
hr {
    border-color: #262730 !important;
}
</style>
"""
st.markdown(dark_style, unsafe_allow_html=True)

# 3. Top Banner / Cover Photo (Automatically stretches edge-to-edge via CSS)
st.image("logo.png")

# Main Title & Subtitle
st.title("ECP 203 Concrete Cube Acceptance Verifier")
st.markdown(
    '<p class="author-credit">Made by Eng. Mohamed Abd Al Aty</p>',
    unsafe_allow_html=True,
)
st.subheader(
    "Multi-Stage (7, 14, & 28-Day) Compliance Checking according to ECP 203"
)
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("PROJECT DETAILS")
project_name = st.sidebar.text_input(
    "Project Name",
    value="",
    placeholder="Please enter your project name here",
)
pour_location = st.sidebar.text_input(
    "Structural Element / Pour Location", "Slab Axis A1-C5"
)
fcu_spec = st.sidebar.number_input(
    "Specified 28-Day Grade fcu (N/mm²)",
    min_value=10.0,
    max_value=100.0,
    value=30.0,
    step=5.0,
)
engineer_name = st.sidebar.text_input(
    "Engineer Name",
    value="",
    placeholder="Enter your name here",
)
# Sidebar Divider & Professional Disclaimer Note
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #CCCCCC; font-size: 0.85rem; line-height: 1.4;"
    " text-align: justify;'><i><b>Note to Engineers:</b> All outputs and"
    " compliance calculations follow the Egyptian Code of Practice (ECP 203)."
    " Please independently verify these results for your structural elements."
    " If you notice any missing data or have feedback, feel free to reach out"
    " to refine it. Thank you for your cooperation!</i></p>",
    unsafe_allow_html=True,
)
# Input Mode Selector
st.header("1. Input Cube Crushing Results (N/mm²)")
input_method = st.radio(
    "Choose Input Method:",
    ["Manual Entry", "Upload Excel File (.xlsx)"],
    horizontal=True,
)

cubes_7 = []
cubes_14 = []
cubes_28 = []


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
    input_14 = st.text_area(
        "14-Day Cubes:", value="26.0, 27.2, 25.8", height=100
    )
  with col_c:
    st.subheader("28-Day Test")
    input_28 = st.text_area(
        "28-Day Cubes:", value="32.5, 34.0, 31.0, 35.5, 29.0, 33.0", height=100
    )

  try:
    cubes_7 = parse_input(input_7)
    cubes_14 = parse_input(input_14)
    cubes_28 = parse_input(input_28)
  except ValueError:
    st.error("⚠️ Please enter valid numerical values separated by commas.")
    st.stop()

else:
  st.info(
      "💡 Upload an Excel file. Select columns for each testing age from your"
      " file."
  )
  uploaded_file = st.file_uploader(
      "Choose an Excel file", type=["xlsx", "xls"]
  )

  if uploaded_file is not None:
    try:
      excel_file = pd.ExcelFile(uploaded_file)
      sheet_selected = st.selectbox("Select Sheet:", excel_file.sheet_names)
      df = pd.read_excel(uploaded_file, sheet_name=sheet_selected)
      st.write("📊 **Preview of Uploaded Data:**", df.head())

      numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
      if not numeric_cols:
        st.error("⚠️ No numeric columns found in the uploaded file.")
        st.stop()

      col_1, col_2, col_3 = st.columns(3)
      with col_1:
        col_7_name = st.selectbox("7-Day Column:", ["None"] + numeric_cols)
      with col_2:
        col_14_name = st.selectbox("14-Day Column:", ["None"] + numeric_cols)
      with col_3:
        col_28_name = st.selectbox("28-Day Column:", ["None"] + numeric_cols)

      if col_7_name != "None":
        cubes_7 = df[col_7_name].dropna().astype(float).tolist()
      if col_14_name != "None":
        cubes_14 = df[col_14_name].dropna().astype(float).tolist()
      if col_28_name != "None":
        cubes_28 = df[col_28_name].dropna().astype(float).tolist()

    except Exception as e:
      st.error(f"⚠️ Error reading Excel file: {e}")
      st.stop()
  else:
    st.warning("👈 Please upload an Excel sheet to continue.")
    st.stop()

if not (cubes_7 or cubes_14 or cubes_28):
  st.warning(
      "⚠️ Please provide cube strength data for at least one testing age (7,"
      " 14, or 28 days)."
  )
  st.stop()


# Helper function for statistical analysis & multi-stage ECP 203 verification
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
      "age_name": age_name,
      "n": n_val,
      "mean": mean_val,
      "s": s_val,
      "k": k_val,
      "fcu_calc_1": fcu_calc_1,
      "fcu_calc_2": fcu_calc_2,
      "fcu_char": fcu_char,
      "min": min_val,
      "target_ratio": target_ratio,
      "stage_target_fcu": stage_target_fcu,
      "min_threshold": 0.85 * stage_target_fcu,
      "cond1": cond1,
      "cond2": cond2,
      "is_compliant": is_compliant,
  }


# Analyze all three stages
stages_data = {
    "7 Days": analyze_stage(cubes_7, "7-Day Stage", 0.70),
    "14 Days": analyze_stage(cubes_14, "14-Day Stage", 0.85),
    "28 Days": analyze_stage(cubes_28, "28-Day Stage", 1.00),
}

# Results Display
st.markdown("---")
st.header("2. Compliance Summaries (7, 14 & 28 Days)")

# Tabs with bolded titles
tabs = st.tabs([
    "**7-Day Stage Compliance**",
    "**14-Day Stage Compliance**",
    "**28-Day Stage Compliance**",
])

for idx, (stage_label, tab) in enumerate(
    zip(["7 Days", "14 Days", "28 Days"], tabs)
):
  with tab:
    res = stages_data[stage_label]
    if res is None:
      st.info(
          f"ℹ️ Insufficient or missing data for {stage_label} testing"
          " (minimum 3 cubes required)."
      )
    else:
      c1, c2, c3 = st.columns(3)
      c1.metric("Sample Count (n)", f"{res['n']} cubes")
      c2.metric("Mean Strength (f_m)", f"{res['mean']:.2f} N/mm²")
      c3.metric("Std. Deviation (s)", f"{res['s']:.2f} N/mm²")

      st.write("")
      st.write(
          f"• **Target Strength Threshold ({int(res['target_ratio']*100)}% of"
          f" Spec):** `{res['stage_target_fcu']:.2f}` N/mm²"
      )
      st.write(
          "• **Calculated Characteristic Strength (f_cu):**"
          f" `{res['fcu_char']:.2f}` N/mm²"
      )
      st.write(
          f"• **Minimum Individual Cube:** `{res['min']:.2f}` N/mm² (Min Limit:"
          f" `{res['min_threshold']:.2f}` N/mm²)"
      )

      st.write("")
      if res["is_compliant"]:
        st.success(
            f"✅ **PASS ({stage_label}):** Complies with the target requirements"
            f" of ECP 203 for {stage_label}."
        )
      else:
        st.error(
            f"❌ **FAIL ({stage_label}):** DOES NOT comply with the target"
            f" requirements of ECP 203 for {stage_label}."
        )

# Generate Rich Structured Excel & PDF Data Structures
display_project_name = project_name if project_name.strip() else "Unnamed Project"
display_engineer_name = (
    engineer_name if engineer_name.strip() else "Not Specified"
)

overview_data = [
    {"Parameter": "Project Name", "Details": display_project_name},
    {"Parameter": "Structural Element / Pour Location", "Details": pour_location},
    {"Parameter": "Specified 28-Day Grade (fcu)", "Details": f"{fcu_spec} N/mm²"},
    {"Parameter": "Engineer Name", "Details": display_engineer_name},
    {
        "Parameter": "Standard Specification",
        "Details": "Egyptian Code of Practice (ECP 203)",
    },
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
        "Testing Stage": stage_key,
        "Sample Count (n)": res["n"],
        "Target Ratio": f"{int(res['target_ratio']*100)}%",
        "Target Strength (N/mm²)": round(res["stage_target_fcu"], 2),
        "Mean Strength (N/mm²)": round(res["mean"], 2),
        "Standard Deviation (N/mm²)": round(res["s"], 2),
        "Margin Factor (k)": res["k"],
        "Calculated fcu (N/mm²)": round(res["fcu_char"], 2),
        "Min Individual Cube (N/mm²)": round(res["min"], 2),
        "Min Allowable Limit (N/mm²)": round(res["min_threshold"], 2),
        "Compliance Verdict": "PASS" if res["is_compliant"] else "FAIL",
    })
  else:
    summary_rows.append({
        "Testing Stage": stage_key,
        "Sample Count (n)": "N/A",
        "Target Ratio": "N/A",
        "Target Strength (N/mm²)": "N/A",
        "Mean Strength (N/mm²)": "N/A",
        "Standard Deviation (N/mm²)": "N/A",
        "Margin Factor (k)": "N/A",
        "Calculated fcu (N/mm²)": "N/A",
        "Min Individual Cube (N/mm²)": "N/A",
        "Min Allowable Limit (N/mm²)": "N/A",
        "Compliance Verdict": "No Data Provided",
    })
df_summary_table = pd.DataFrame(summary_rows)

calc_methods = [
    {
        "Step / Parameter": "1. Standard Reference",
        "Mathematical Definition / Description": (
            "Egyptian Code of Practice for Concrete Structures (ECP 203 -"
            " Section 2-6)."
        ),
    },
    {
        "Step / Parameter": "2. Multi-Stage Testing Framework",
        "Mathematical Definition / Description": (
            "Evaluations are conducted for 7-Day (~70% target fcu), 14-Day"
            " (~85% target fcu), and 28-Day (100% full specified fcu)."
        ),
    },
    {
        "Step / Parameter": "3. Mean Strength",
        "Mathematical Definition / Description": (
            "Calculated as the arithmetic mean per stage: Sum of all cube"
            " strengths divided by the total sample count (n)."
        ),
    },
    {
        "Step / Parameter": "4. Standard Deviation",
        "Mathematical Definition / Description": (
            "Calculated using sample degrees of freedom (n - 1) to measure data"
            " dispersion around the mean."
        ),
    },
    {
        "Step / Parameter": "5. Statistical Margin Factor (k)",
        "Mathematical Definition / Description": (
            "If sample size n is less than 30, factor k is 1.91. If sample size"
            " n is 30 or greater, factor k is 1.64."
        ),
    },
    {
        "Step / Parameter": "6. Characteristic Strength Evaluation",
        "Mathematical Definition / Description": (
            "Evaluated per stage using two criteria: (1) Mean strength minus"
            " product of factor k and standard deviation, and (2) 85 percent of"
            " the mean strength. The final characteristic strength is the"
            " maximum of these two values."
        ),
    },
    {
        "Step / Parameter": "7. Acceptance Condition 1",
        "Mathematical Definition / Description": (
            "The calculated characteristic strength must be greater than or"
            " equal to the specified target strength for that stage."
        ),
    },
    {
        "Step / Parameter": "8. Acceptance Condition 2",
        "Mathematical Definition / Description": (
            "Every individual cube result within the sample must be greater"
            " than or equal to 85 percent of the target stage strength limit."
        ),
    },
]
df_methods = pd.DataFrame(calc_methods)

# Excel Export Buffer
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_overview.to_excel(
      writer, sheet_name="Project Overview & Info", index=False
  )
  df_summary_table.to_excel(
      writer, sheet_name="Multi-Stage Results Summary", index=False
  )
  df_raw_cubes.to_excel(writer, sheet_name="Raw Individual Cubes", index=False)
  df_methods.to_excel(
      writer, sheet_name="Calculation Methodology", index=False
  )
excel_buffer.seek(0)


# PDF Export Buffer Generation Function
def generate_pdf_report():
  pdf_buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      pdf_buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=36,
      bottomMargin=36,
  )
  story = []
  styles = getSampleStyleSheet()

  # Custom Styles
  title_style = ParagraphStyle(
      "DocTitle",
      parent=styles["Heading1"],
      fontSize=18,
      textColor=colors.HexColor("#1B2A4A"),
      spaceAfter=4,
      alignment=1,
  )
  subtitle_style = ParagraphStyle(
      "DocSub",
      parent=styles["Normal"],
      fontSize=10,
      textColor=colors.HexColor("#555555"),
      spaceAfter=15,
      alignment=1,
  )
  section_style = ParagraphStyle(
      "SecTitle",
      parent=styles["Heading2"],
      fontSize=13,
      textColor=colors.HexColor("#FF8C00"),
      spaceBefore=12,
      spaceAfter=6,
  )
  body_style = ParagraphStyle(
      "Body",
      parent=styles["Normal"],
      fontSize=9,
      textColor=colors.HexColor("#333333"),
      spaceAfter=4,
  )

  story.append(Paragraph("ECP 203 Concrete Cube Acceptance Report", title_style))
  story.append(
      Paragraph(
          "Multi-Stage Compliance Verification (7, 14, & 28 Days)",
          subtitle_style,
      )
  )
  story.append(
      HRFlowable(
          width="100%",
          thickness=1.5,
          color=colors.HexColor("#1B2A4A"),
          spaceAfter=10,
      )
  )

  # Overview Table
  story.append(Paragraph("<b>1. Project Overview & Metadata</b>", section_style))
  overview_data_list = [["Parameter", "Details"]] + df_overview.values.tolist()
  t_overview = Table(overview_data_list, colWidths=[180, 360])
  t_overview.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 9),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
          ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
      ])
  )
  story.append(t_overview)
  story.append(Spacer(1, 10))

  # Summary Results Table
  story.append(Paragraph("<b>2. Compliance Results Summary</b>", section_style))
  summary_headers = [
      "Stage",
      "n",
      "Target",
      "Req. (MPa)",
      "Mean (MPa)",
      "StdDev",
      "fcu (MPa)",
      "Verdict",
  ]
  summary_table_rows = [summary_headers]
  for r in summary_rows:
    summary_table_rows.append([
        str(r["Testing Stage"]),
        str(r["Sample Count (n)"]),
        str(r["Target Ratio"]),
        str(r["Target Strength (N/mm²)"]),
        str(r["Mean Strength (N/mm²)"]),
        str(r["Standard Deviation (N/mm²)"]),
        str(r["Calculated fcu (N/mm²)"]),
        str(r["Compliance Verdict"]),
    ])
  t_summary = Table(
      summary_table_rows, colWidths=[65, 30, 45, 60, 65, 55, 65, 115]
  )
  t_summary.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 8),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
      ])
  )
  story.append(t_summary)
  story.append(Spacer(1, 10))

  # Raw Individual Cubes Table
  story.append(
      Paragraph("<b>3. Raw Individual Cube Crushing Values</b>", section_style)
  )
  raw_headers = list(df_raw_cubes.columns)
  raw_rows_data = [raw_headers] + [
      [str(val) if val is not None else "-" for val in row]
      for row in df_raw_cubes.values
  ]
  t_raw = Table(raw_rows_data, colWidths=[90, 150, 150, 150])
  t_raw.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 8),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
      ])
  )
  story.append(t_raw)
  story.append(Spacer(1, 10))

  # Calculation Methodology Section (Symbol-free format)
  story.append(
      Paragraph(
          "<b>4. Calculation Methodology & Standards (ECP 203)</b>",
          section_style,
      )
  )
  for item in calc_methods:
    p_text = f"<b>{item['Step / Parameter']}:</b> {item['Mathematical Definition / Description']}"
    story.append(Paragraph(p_text, body_style))

  doc.build(story)
  pdf_buffer.seek(0)
  return pdf_buffer


pdf_data = generate_pdf_report()

# Download Buttons Layout
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
  st.download_button(
      label="📥 Download Excel Report (.xlsx)",
      data=excel_buffer,
      file_name=f"ECP203_Report_{display_project_name.replace(' ', '_')}.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
with col_btn2:
  st.download_button(
      label="📄 Download Professional PDF Report (.pdf)",
      data=pdf_data,
      file_name=f"ECP203_Report_{display_project_name.replace(' ', '_')}.pdf",
      mime="application/pdf",
  )

# Step-by-Step Breakdown Expander
with st.expander(
    "🔍 Show Step-by-Step ECP 203 Calculation Formulas (All Stages)"
):
  for stage_key in ["7 Days", "14 Days", "28 Days"]:
    res = stages_data[stage_key]
    st.markdown(f"### **📌 {stage_key} Stage ECP 203 Evaluation**")
    if res is None:
      st.write(f"No sufficient data provided for {stage_key} stage.")
      st.markdown("---")
      continue

    st.latex(r"\text{Mean Strength: } f_m = \frac{\sum f_i}{n}")
    st.write(f"👉 **Mean ($f_m$)** = `{res['mean']:.2f}` N/mm²")

    st.latex(
        r"\text{Standard Deviation: } s = \sqrt{\frac{\sum (f_i - f_m)^2}{n -"
        r" 1}}"
    )
    st.write(
        f"👉 **Std. Dev. ($s$)** = `{res['s']:.2f}` N/mm² | **Factor $k$** ="
        f" `{res['k']}` (Sample $n = {res['n']}$)"
    )

    st.latex(
        r"f_{cu,1} = f_m - (k \times s) \quad | \quad f_{cu,2} = 0.85 \times f_m"
    )
    st.write(
        f"• $f_{{cu,1}} = {res['mean']:.2f} - ({res['k']} \\times"
        f" {res['s']:.2f}) =$ **`{res['fcu_calc_1']:.2f}` N/mm²**"
    )
    st.write(
        f"• $f_{{cu,2}} = 0.85 \\times {res['mean']:.2f} =$"
        f" **`{res['fcu_calc_2']:.2f}` N/mm²**"
    )
    st.write(
        f"👉 **Calculated Stage $f_{{cu}}$** = `{res['fcu_char']:.2f}` N/mm² |"
        f" **Stage Target:** `{res['stage_target_fcu']:.2f}` N/mm²"
    )

    if res["cond1"]:
      st.markdown("✔️ **Condition 1 Met:** Stage $f_{cu} \\ge$ Target Strength.")
    else:
      st.markdown("❌ **Condition 1 Failed:** Stage $f_{cu} <$ Target Strength.")

    st.latex(r"f_{\text{cube, min}} \ge 0.85 \times f_{cu,\text{target}}")
    st.write(
        f"• Min Individual Limit: **`{res['min_threshold']:.2f}` N/mm²** | Lowest"
        f" Cube: **`{res['min']:.2f}` N/mm²**"
    )

    if res["cond2"]:
      st.markdown("✔️ **Condition 2 Met:** Lowest cube meets the minimum limit.")
    else:
      st.markdown(
          "❌ **Condition 2 Failed:** Lowest cube is below the minimum limit."
      )

    st.markdown("---")

# Contact Information & Footer Copyright Notice
st.markdown(
    "<p style='text-align: center; color: #FFFFFF; font-size: 0.95rem;"
    " margin-top: 3rem;'><b>Contact me at:</b><br>Linkedin: <a"
    " href='https://www.linkedin.com/in/mohamed-abd-al-aty-a326a1214/'"
    " target='_blank' style='color: #00BFFF;'>Mohamed Abd Al Aty</a><br>Gmail:"
    " <a href='mailto:mohamedabdalaty63@gmail.com' style='color:"
    " #00BFFF;'>mohamedabdalaty63@gmail.com</a></p>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 0.85rem;"
    " margin-top: 1.5rem;'>© 2026 Eng. Mohamed Abd Al Aty. All rights reserved."
    " Unauthorized commercial use, reproduction, or distribution is strictly"
    " prohibited.</p>",
    unsafe_allow_html=True,
)
