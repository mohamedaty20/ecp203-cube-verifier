import io
import numpy as np
import pandas as pd
import streamlit as st

# 1. Page Configuration (MUST be first Streamlit command)
st.set_page_config(
    page_title="ECP 203 Concrete Cube Verifier",
    page_icon="◮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom Styling (Navy Blue Sidebar & Padded Main Layout)
dark_style = """
<style>
/* Force dark background on the entire app */
.stApp {
    background-color: #0E1117 !important;
    color: #FFFFFF !important;
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

/* Subtitles and Section Headers (Orange) */
h2, h3, .stSubheader {
    color: #FF8C00 !important;
    font-weight: 600;
}

/* Metric Cards */
[data-testid="stMetricValue"] {
    color: #00BFFF !important;
}

/* Text Inputs and Area Formatting */
textarea, input {
    background-color: #1E222D !important;
    color: #FFFFFF !important;
    border: 1px solid #FF8C00 !important;
}

/* Download Button Styling */
.stDownloadButton>button {
    background-color: #FF8C00 !important;
    color: #FFFFFF !important;
    border: none;
    font-weight: bold;
}
.stDownloadButton>button:hover {
    background-color: #E07B00 !important;
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
st.sidebar.caption("Please enter your project name here")
project_name = st.sidebar.text_input("Project Name", "New Capital Site Alpha")
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
  st.info(" Enter strength values separated by commas.")

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
      " Upload an Excel file. Select columns for each testing age from your"
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
      st.write(" **Preview of Uploaded Data:**", df.head())

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
    st.warning(" Please upload an Excel sheet to continue.")
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

# Generate Excel File Stream
summary_rows = [
    {"Metric / Field": "Project Name", "Value": project_name},
    {"Metric / Field": "Pour Location / Element", "Value": pour_location},
    {"Metric / Field": "Engineer in Charge", "Value": "Eng. Mohamed Abd Al Aty"},
    {"Metric / Field": "Specified 28-Day Grade fcu (N/mm²)", "Value": fcu_spec},
]

for stage_key in ["7 Days", "14 Days", "28 Days"]:
  res = stages_data[stage_key]
  summary_rows.append(
      {"Metric / Field": f"--- {stage_key} Evaluation ---", "Value": "---"}
  )
  if res:
    summary_rows.extend([
        {"Metric / Field": f"{stage_key} Sample Count (n)", "Value": res["n"]},
        {
            "Metric / Field": f"{stage_key} Target Strength (N/mm²)",
            "Value": round(res["stage_target_fcu"], 2),
        },
        {
            "Metric / Field": f"{stage_key} Mean Strength f_m (N/mm²)",
            "Value": round(res["mean"], 2),
        },
        {
            "Metric / Field": f"{stage_key} Standard Deviation s (N/mm²)",
            "Value": round(res["s"], 2),
        },
        {"Metric / Field": f"{stage_key} Margin Factor (k)", "Value": res["k"]},
        {
            "Metric / Field": f"{stage_key} Calculated fcu (N/mm²)",
            "Value": round(res["fcu_char"], 2),
        },
        {
            "Metric / Field": f"{stage_key} Minimum Individual Cube (N/mm²)",
            "Value": round(res["min"], 2),
        },
        {
            "Metric / Field": f"{stage_key} Compliance Verdict",
            "Value": "PASS" if res["is_compliant"] else "FAIL",
        },
    ])
  else:
    summary_rows.append({
        "Metric / Field": f"{stage_key} Data Status",
        "Value": "No valid data provided",
    })

summary_df = pd.DataFrame(summary_rows)

max_len = max(len(cubes_7), len(cubes_14), len(cubes_28), 1)
cubes_matrix = {
    "Cube #": list(range(1, max_len + 1)),
    "7-Day Strength (N/mm²)": cubes_7 + [None] * (max_len - len(cubes_7)),
    "14-Day Strength (N/mm²)": cubes_14 + [None] * (max_len - len(cubes_14)),
    "28-Day Strength (N/mm²)": cubes_28 + [None] * (max_len - len(cubes_28)),
}
raw_cubes_df = pd.DataFrame(cubes_matrix)

calculation_notes = [
    {
        "Section": "1. Standard Reference",
        "Details": (
            "Egyptian Code of Practice for Concrete Structures (ECP 203 -"
            " Section 2-6)."
        ),
    },
    {
        "Section": "2. Multi-Stage Testing Framework",
        "Details": (
            "Evaluations are conducted for 7-Day (~70% target fcu), 14-Day"
            " (~85% target fcu), and 28-Day (100% full specified fcu)."
        ),
    },
    {
        "Section": "3. Mean Strength (f_m)",
        "Details": (
            "Calculated as the arithmetic mean per stage: f_m = Sum(f_i) / n."
        ),
    },
    {
        "Section": "4. Standard Deviation (s)",
        "Details": (
            "Calculated using sample degrees of freedom: s = sqrt(Sum(f_i -"
            " f_m)^2 / (n - 1))."
        ),
    },
    {
        "Section": "5. Margin Factor (k)",
        "Details": (
            "If sample size n < 30, k = 1.91. If sample size n >= 30, k = 1.64."
        ),
    },
    {
        "Section": "6. Characteristic Strength (f_cu)",
        "Details": (
            "Evaluated per stage as: f_cu,1 = f_m - (k * s) and f_cu,2 = 0.85 *"
            " f_m. f_cu = max(f_cu,1, f_cu,2)."
        ),
    },
    {
        "Section": "7. Acceptance Condition 1",
        "Details": (
            "The calculated characteristic strength f_cu must meet or exceed"
            " the target stage strength."
        ),
    },
    {
        "Section": "8. Acceptance Condition 2",
        "Details": (
            "Every individual cube result must be >= 0.85 * (target stage"
            " strength)."
        ),
    },
]
notes_df = pd.DataFrame(calculation_notes)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
  summary_df.to_excel(writer, sheet_name="Multi-Stage Compliance", index=False)
  raw_cubes_df.to_excel(writer, sheet_name="Raw Cube Data", index=False)
  notes_df.to_excel(
      writer, sheet_name="ECP 203 Calculation Notes", index=False
  )

buffer.seek(0)

st.download_button(
    label="📥 Download Complete Multi-Stage Excel Report (.xlsx)",
    data=buffer,
    file_name=f"ECP203_All_Stages_Report_{project_name.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# Step-by-Step Breakdown
with st.expander(
    "🔍 Show Step-by-Step ECP 203 Calculation Formulas (All Stages)"
):
  for stage_key in ["7 Days", "14 Days", "28 Days"]:
    res = stages_data[stage_key]
    st.markdown(f"### ** {stage_key} Stage ECP 203 Evaluation**")
    if res is None:
      st.write(f"No sufficient data provided for {stage_key} stage.")
      st.markdown("---")
      continue

    st.latex(r"\text{Mean Strength: } f_m = \frac{\sum f_i}{n}")
    st.write(f" **Mean ($f_m$)** = `{res['mean']:.2f}` N/mm²")

    st.latex(
        r"\text{Standard Deviation: } s = \sqrt{\frac{\sum (f_i - f_m)^2}{n -"
        r" 1}}"
    )
    st.write(
        f" **Std. Dev. ($s$)** = `{res['s']:.2f}` N/mm² | **Factor $k$** ="
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
        f" **Calculated Stage $f_{{cu}}$** = `{res['fcu_char']:.2f}` N/mm² |"
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
              # Footer Copyright Notice (Centered & Light Grey)
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 0.85rem;"
    " margin-top: 3rem;'>© 2026 Eng. Mohamed Abd Al Aty. All rights reserved."
    " Unauthorized commercial use, reproduction, or distribution is strictly"
    " prohibited.</p>",
    unsafe_allow_html=True,
)
