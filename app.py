import io
import streamlit as st
import numpy as np
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="ECP 203 Concrete Cube Verifier",
    page_icon="🏗️",
    layout="centered"
)

# Custom CSS to hide default Streamlit header and footer
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Main Title & Subtitle
st.title("🏗️ ECP 203 Concrete Cube Acceptance Verifier")
st.caption("Made by Eng. Mohamed Abd Al Aty")
st.subheader("Multi-Stage (7, 14, & 28-Day) Compliance Checking according to ECP 203")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("📋 Project Details")
project_name = st.sidebar.text_input("Project Name", "New Capital Site Alpha")
pour_location = st.sidebar.text_input("Structural Element / Pour Location", "Slab Axis A1-C5")
fcu_spec = st.sidebar.number_input("Specified 28-Day Grade fcu (N/mm²)", min_value=10.0, max_value=100.0, value=30.0, step=5.0)

# Input Mode Selector
st.header("1. Input Cube Crushing Results (N/mm²)")
input_method = st.radio("Choose Input Method:", ["Manual Entry", "Upload Excel File (.xlsx)"], horizontal=True)

cubes_7 = []
cubes_14 = []
cubes_28 = []

def parse_input(text_str):
    if not text_str.strip():
        return []
    return [float(x.strip()) for x in text_str.split(",") if x.strip() != ""]

if input_method == "Manual Entry":
    st.info("💡 Enter strength values separated by commas. (28-Day results are required for official ECP 203 compliance).")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.subheader("7-Day Test")
        input_7 = st.text_area("7-Day Cubes (Optional):", value="21.0, 22.5, 20.5", height=100)
    with col_b:
        st.subheader("14-Day Test")
        input_14 = st.text_area("14-Day Cubes (Optional):", value="26.0, 27.2, 25.8", height=100)
    with col_c:
        st.subheader("28-Day Test")
        input_28 = st.text_area("28-Day Cubes (Required):", value="32.5, 34.0, 31.0, 35.5, 29.0, 33.0", height=100)
        
    try:
        cubes_7 = parse_input(input_7)
        cubes_14 = parse_input(input_14)
        cubes_28 = parse_input(input_28)
    except ValueError:
        st.error("⚠️ Please enter valid numerical values separated by commas.")
        st.stop()

else:
    st.info("💡 Upload an Excel file. You can select columns for each testing age from your file.")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
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
                col_7_name = st.selectbox("7-Day Column (Optional):", ["None"] + numeric_cols)
            with col_2:
                col_14_name = st.selectbox("14-Day Column (Optional):", ["None"] + numeric_cols)
            with col_3:
                col_28_name = st.selectbox("28-Day Column (Required):", numeric_cols)
                
            if col_7_name != "None":
                cubes_7 = df[col_7_name].dropna().astype(float).tolist()
            if col_14_name != "None":
                cubes_14 = df[col_14_name].dropna().astype(float).tolist()
            if col_28_name:
                cubes_28 = df[col_28_name].dropna().astype(float).tolist()
                
        except Exception as e:
            st.error(f"⚠️ Error reading Excel file: {e}")
            st.stop()
    else:
        st.warning("👈 Please upload an Excel sheet to continue.")
        st.stop()

# Validate 28-Day Sample Size
if len(cubes_28) < 3:
    st.warning("⚠️ ECP 203 requires at least 3 valid 28-day cube results for compliance verification.")
    st.stop()

# Helper function for statistical analysis
def analyze_stage(cube_list):
    if not cube_list:
        return None
    n_val = len(cube_list)
    mean_val = float(np.mean(cube_list))
    s_val = float(np.std(cube_list, ddof=1)) if n_val > 1 else 0.0
    k_val = 1.91 if n_val < 30 else 1.64
    fcu_calc_1 = mean_val - (k_val * s_val)
    fcu_calc_2 = 0.85 * mean_val
    fcu_char = max(fcu_calc_1, fcu_calc_2)
    min_val = min(cube_list)
    return {
        "n": n_val,
        "mean": mean_val,
        "s": s_val,
        "k": k_val,
        "fcu_calc_1": fcu_calc_1,
        "fcu_calc_2": fcu_calc_2,
        "fcu_char": fcu_char,
        "min": min_val
    }

stats_7 = analyze_stage(cubes_7)
stats_14 = analyze_stage(cubes_14)
stats_28 = analyze_stage(cubes_28)

# Compliance Logic for 28-Day Results
cond1 = stats_28["fcu_char"] >= fcu_spec
cond2 = stats_28["min"] >= (0.85 * fcu_spec)
is_compliant = cond1 and cond2

# Results Display
st.markdown("---")
st.header("2. Compliance Summary (28-Day Target)")

col1, col2, col3 = st.columns(3)
col1.metric("28-Day Count (n)", f"{stats_28['n']} cubes")
col2.metric("Mean Strength (f_m)", f"{stats_28['mean']:.2f} N/mm²")
col3.metric("Std. Deviation (s)", f"{stats_28['s']:.2f} N/mm²")

st.write("")
status_text = "PASS" if is_compliant else "FAIL"

if is_compliant:
    st.success(f"✅ **PASS:** Concrete batch complies with specified grade {fcu_spec:.1f} N/mm² per ECP 203.")
else:
    st.error(f"❌ **FAIL:** Concrete batch DOES NOT comply with specified grade {fcu_spec:.1f} N/mm² per ECP 203.")

# Display Early Stage Comparisons
if stats_7 or stats_14:
    st.subheader("📈 Multi-Stage Strength Progression")
    stage_cols = st.columns(3)
    
    with stage_cols[0]:
        st.markdown("**7-Day Results**")
        if stats_7:
            st.write(f"• Count: `{stats_7['n']}` cubes")
            st.write(f"• Mean: `{stats_7['mean']:.2f}` N/mm²")
            st.write(f"• % of Spec: `{ (stats_7['mean']/fcu_spec)*100:.1f}%`")
        else:
            st.write("No data provided.")
            
    with stage_cols[1]:
        st.markdown("**14-Day Results**")
        if stats_14:
            st.write(f"• Count: `{stats_14['n']}` cubes")
            st.write(f"• Mean: `{stats_14['mean']:.2f}` N/mm²")
            st.write(f"• % of Spec: `{ (stats_14['mean']/fcu_spec)*100:.1f}%`")
        else:
            st.write("No data provided.")
            
    with stage_cols[2]:
        st.markdown("**28-Day Results**")
        st.write(f"• Count: `{stats_28['n']}` cubes")
        st.write(f"• Mean: `{stats_28['mean']:.2f}` N/mm²")
        st.write(f"• % of Spec: `{ (stats_28['mean']/fcu_spec)*100:.1f}%`")

# Generate Professional Excel File
summary_rows = [
    {"Metric / Field": "Project Name", "Value": project_name},
    {"Metric / Field": "Pour Location / Element", "Value": pour_location},
    {"Metric / Field": "Engineer in Charge", "Value": "Eng. Mohamed Abd Al Aty"},
    {"Metric / Field": "Specified 28-Day Grade fcu (N/mm²)", "Value": fcu_spec},
    {"Metric / Field": "28-Day Overall Compliance Status", "Value": status_text},
    {"Metric / Field": "---", "Value": "---"},
    {"Metric / Field": "7-Day Sample Count (n)", "Value": stats_7['n'] if stats_7 else "N/A"},
    {"Metric / Field": "7-Day Mean Strength f_m (N/mm²)", "Value": round(stats_7['mean'], 2) if stats_7 else "N/A"},
    {"Metric / Field": "7-Day Characteristic fcu (N/mm²)", "Value": round(stats_7['fcu_char'], 2) if stats_7 else "N/A"},
    {"Metric / Field": "---", "Value": "---"},
    {"Metric / Field": "14-Day Sample Count (n)", "Value": stats_14['n'] if stats_14 else "N/A"},
    {"Metric / Field": "14-Day Mean Strength f_m (N/mm²)", "Value": round(stats_14['mean'], 2) if stats_14 else "N/A"},
    {"Metric / Field": "14-Day Characteristic fcu (N/mm²)", "Value": round(stats_14['fcu_char'], 2) if stats_14 else "N/A"},
    {"Metric / Field": "---", "Value": "---"},
    {"Metric / Field": "28-Day Sample Count (n)", "Value": stats_28['n']},
    {"Metric / Field": "28-Day Mean Strength f_m (N/mm²)", "Value": round(stats_28['mean'], 2)},
    {"Metric / Field": "28-Day Standard Deviation s (N/mm²)", "Value": round(stats_28['s'], 2)},
    {"Metric / Field": "28-Day Margin Factor (k)", "Value": stats_28['k']},
    {"Metric / Field": "28-Day Characteristic fcu (N/mm²)", "Value": round(stats_28['fcu_char'], 2)},
    {"Metric / Field": "28-Day Minimum Individual Cube (N/mm²)", "Value": round(stats_28['min'], 2)},
    {"Metric / Field": "28-Day Individual Minimum Threshold (0.85*fcu)", "Value": round(0.85 * fcu_spec, 2)},
]

summary_df = pd.DataFrame(summary_rows)

# Create alignment for raw cube results across 7, 14, and 28 days
max_len = max(len(cubes_7), len(cubes_14), len(cubes_28))
cubes_matrix = {
    "Cube #": list(range(1, max_len + 1)),
    "7-Day Strength (N/mm²)": cubes_7 + [None] * (max_len - len(cubes_7)),
    "14-Day Strength (N/mm²)": cubes_14 + [None] * (max_len - len(cubes_14)),
    "28-Day Strength (N/mm²)": cubes_28 + [None] * (max_len - len(cubes_28)),
}
raw_cubes_df = pd.DataFrame(cubes_matrix)

# Technical notes calculation sheet
calculation_notes = [
    {"Section": "1. Standard Reference", "Details": "Egyptian Code of Practice for Concrete Structures (ECP 203 - Section 2-6)."},
    {"Section": "2. Mean Strength (f_m)", "Details": "Calculated as the arithmetic mean: f_m = Sum(f_i) / n, where f_i is the cube crushing strength."},
    {"Section": "3. Standard Deviation (s)", "Details": "Calculated as sample standard deviation using degrees of freedom (n - 1): s = sqrt(Sum(f_i - f_m)^2 / (n - 1))."},
    {"Section": "4. Statistical Factor (k)", "Details": "If sample size n < 30, k = 1.91. If sample size n >= 30, k = 1.64."},
    {"Section": "5. Characteristic Strength (f_cu)", "Details": "Evaluated as the maximum of two conditions: f_cu,1 = f_m - (k * s) and f_cu,2 = 0.85 * f_m. f_cu = max(f_cu,1, f_cu,2)."},
    {"Section": "6. Acceptance Criteria 1", "Details": "The characteristic strength f_cu must be greater than or equal to specified strength f_cu,spec."},
    {"Section": "7. Acceptance Criteria 2", "Details": "Every individual cube result must be >= 0.85 * f_cu,spec."},
    {"Section": "8. Multi-Stage Evaluation", "Details": "7-Day and 14-Day tests provide early quality assurance metrics. Official compliance acceptance is evaluated on 28-day results."}
]
notes_df = pd.DataFrame(calculation_notes)

# Excel File Stream
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Executive Summary", index=False)
    raw_cubes_df.to_excel(writer, sheet_name="Raw Cube Data", index=False)
    notes_df.to_excel(writer, sheet_name="ECP 203 Calculation Notes", index=False)

buffer.seek(0)

# Download Button
st.download_button(
    label="📥 Download Complete Multi-Stage Excel Report (.xlsx)",
    data=buffer,
    file_name=f"ECP203_MultiStage_Report_{project_name.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Expandable Step-by-Step ECP 203 Formulas
with st.expander("🔍 Show Step-by-Step ECP 203 Calculation Formulas"):
    st.markdown("### **ECP 203 Compliance Evaluation Method (28-Day Test)**")
    
    st.latex(r"\text{Mean Strength: } f_m = \frac{\sum f_i}{n}")
    st.write(f"👉 **Mean ($f_m$)** = `{stats_28['mean']:.2f}` N/mm²")
    
    st.latex(r"\text{Standard Deviation: } s = \sqrt{\frac{\sum (f_i - f_m)^2}{n - 1}}")
    st.write(f"👉 **Std. Dev. ($s$)** = `{stats_28['s']:.2f}` N/mm²")
    
    st.markdown("**Statistical Margin Factor ($k$):**")
    st.write(f"• For $n < 30$: $k = 1.91$ | For $n \\ge 30$: $k = 1.64$")
    st.write(f"👉 Applied factor: **$k = {stats_28['k']}$** (because sample count $n = {stats_28['n']}$)")
    
    st.markdown("---")
    st.markdown("### **1. Characteristic Strength Check ($f_{cu}$)**")
    
    st.latex(r"f_{cu,1} = f_m - (k \times s)")
    st.latex(rf"f_{{cu,1}} = {stats_28['mean']:.2f} - ({stats_28['k']} \times {stats_28['s']:.2f}) = {stats_28['fcu_calc_1']:.2f} \text{{ N/mm}}^2")
    
    st.latex(r"f_{cu,2} = 0.85 \times f_m")
    st.latex(rf"f_{{cu,2}} = 0.85 \times {stats_28['mean']:.2f} = {stats_28['fcu_calc_2']:.2f} \text{{ N/mm}}^2")
    
    st.latex(r"f_{cu} = \max(f_{cu,1}, f_{cu,2})")
    st.write(f"👉 **Calculated $f_{{cu}}$** = `{stats_28['fcu_char']:.2f}` N/mm² | **Required Spec:** `{fcu_spec:.1f}` N/mm²")
    
    if cond1:
        st.markdown("✔️ **Condition 1 Met:** $f_{cu} \\ge f_{cu,\\text{spec}}$")
    else:
        st.markdown("❌ **Condition 1 Failed:** $f_{cu} < f_{cu,\\text{spec}}$")

    st.markdown("---")
    st.markdown("### **2. Individual Cube Minimum Check**")
    st.latex(r"f_{\text{cube, min}} \ge 0.85 \times f_{cu,\text{spec}}")
    st.write(f"• Minimum allowed individual cube limit ($0.85 \\times f_{{cu,\\text{{spec}}}}$): **`{0.85 * fcu_spec:.2f}` N/mm²**")
    st.write(f"• Lowest recorded cube result in sample: **`{stats_28['min']:.2f}` N/mm²**")
    
    if cond2:
        st.markdown("✔️ **Condition 2 Met:** Lowest individual cube strength meets the requirement.")
    else:
        st.markdown("❌ **Condition 2 Failed:** Lowest individual cube strength is below the minimum allowable limit.")
