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
st.subheader("Official Compliance Checking according to Egyptian Code of Practice (ECP 203)")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("📋 Project Details")
project_name = st.sidebar.text_input("Project Name", "New Capital Site Alpha")
pour_location = st.sidebar.text_input("Structural Element / Pour Location", "Slab Axis A1-C5")
fcu_spec = st.sidebar.number_input("Specified Grade fcu (N/mm²)", min_value=10.0, max_value=100.0, value=30.0, step=5.0)

# Input Mode Selector (Manual Text or Excel Sheet)
st.header("1. Input 28-Day Cube Crushing Results (N/mm²)")
input_method = st.radio("Choose Input Method:", ["Manual Entry", "Upload Excel File (.xlsx)"], horizontal=True)

cube_values = []

if input_method == "Manual Entry":
    st.info("💡 Enter individual cube strengths separated by commas.")
    default_cubes = "32.5, 34.0, 31.0, 35.5, 29.0, 33.0"
    cubes_input = st.text_area("Cube Crushing Strengths:", value=default_cubes)
    
    try:
        cube_values = [float(x.strip()) for x in cubes_input.split(",") if x.strip() != ""]
    except ValueError:
        st.error("⚠️ Please enter valid numerical values separated by commas.")
        st.stop()

else:
    st.info("💡 Upload an Excel file containing a column with cube strength values.")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("📊 **Preview of Uploaded File:**", df.head())
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                st.error("⚠️ No numeric columns found in the uploaded file.")
                st.stop()
                
            selected_col = st.selectbox("Select Column Containing Cube Results:", numeric_cols)
            cube_values = df[selected_col].dropna().astype(float).tolist()
        except Exception as e:
            st.error(f"⚠️ Error reading Excel file: {e}")
            st.stop()
    else:
        st.warning("👈 Please upload an Excel sheet to continue.")
        st.stop()

# Validate Sample Size
if len(cube_values) < 3:
    st.warning("⚠️ ECP 203 requires at least 3 cube results for statistical verification.")
    st.stop()

# Statistical Calculations (ECP 203 Logic)
n = len(cube_values)
mean_fcu = float(np.mean(cube_values))
s = float(np.std(cube_values, ddof=1))  # Sample standard deviation (n - 1)

# Statistical factor k according to sample size n
k = 1.91 if n < 30 else 1.64

# Characteristic Strength Calculations
fcu_calc_1 = mean_fcu - (k * s)
fcu_calc_2 = 0.85 * mean_fcu
fcu_char = max(fcu_calc_1, fcu_calc_2)
min_cube = min(cube_values)

# Pass / Fail Compliance Logic
cond1 = fcu_char >= fcu_spec
cond2 = min_cube >= (0.85 * fcu_spec)
is_compliant = cond1 and cond2

# Results Display
st.markdown("---")
st.header("2. Compliance Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Sample Count (n)", f"{n} cubes")
col2.metric("Mean Strength (f_m)", f"{mean_fcu:.2f} N/mm²")
col3.metric("Std. Deviation (s)", f"{s:.2f} N/mm²")

st.write("")
status_text = "PASS" if is_compliant else "FAIL"

if is_compliant:
    st.success(f"✅ **PASS:** Concrete batch complies with specified grade {fcu_spec:.1f} N/mm² per ECP 203.")
else:
    st.error(f"❌ **FAIL:** Concrete batch DOES NOT comply with specified grade {fcu_spec:.1f} N/mm² per ECP 203.")

# Export Results to Excel
summary_data = {
    "Parameter": [
        "Project Name",
        "Pour Location / Element",
        "Engineer in Charge",
        "Specified Grade fcu (N/mm²)",
        "Sample Size (n)",
        "Mean Strength f_m (N/mm²)",
        "Standard Deviation s (N/mm²)",
        "Margin Factor (k)",
        "Calculated fcu (N/mm²)",
        "Minimum Individual Cube (N/mm²)",
        "Min. Individual Threshold (0.85*fcu)",
        "Overall Compliance Status"
    ],
    "Value": [
        project_name,
        pour_location,
        "Eng. Mohamed Abd Al Aty",
        fcu_spec,
        n,
        round(mean_fcu, 2),
        round(s, 2),
        k,
        round(fcu_char, 2),
        round(min_cube, 2),
        round(0.85 * fcu_spec, 2),
        status_text
    ]
}

cubes_df = pd.DataFrame({"Cube No.": range(1, n + 1), "Crushing Strength (N/mm²)": cube_values})
summary_df = pd.DataFrame(summary_data)

# Generate Excel buffer in memory
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Compliance Summary", index=False)
    cubes_df.to_excel(writer, sheet_name="Cube Results", index=False)

buffer.seek(0)

# Download Button
st.download_button(
    label="📥 Download Excel Compliance Report (.xlsx)",
    data=buffer,
    file_name=f"ECP203_Report_{project_name.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Educational / Step-by-Step Calculation Breakdown
with st.expander("🔍 Show Step-by-Step ECP 203 Calculation Formulas"):
    st.markdown("### **ECP 203 Compliance Evaluation Method**")
    
    st.markdown("""
    According to **ECP 203 (Section 2-6)**, the characteristic compressive strength ($f_{cu}$) and individual strength requirements are calculated as follows:
    """)
    
    st.latex(r"\text{Mean Strength: } f_m = \frac{\sum f_i}{n}")
    st.write(f"👉 **Mean ($f_m$)** = `{mean_fcu:.2f}` N/mm²")
    
    st.latex(r"\text{Standard Deviation: } s = \sqrt{\frac{\sum (f_i - f_m)^2}{n - 1}}")
    st.write(f"👉 **Std. Dev. ($s$)** = `{s:.2f}` N/mm²")
    
    st.markdown("**Statistical Margin Factor ($k$):**")
    st.write(f"• For $n < 30$: $k = 1.91$ | For $n \\ge 30$: $k = 1.64$")
    st.write(f"👉 Applied factor: **$k = {k}$** (because sample count $n = {n}$)")
    
    st.markdown("---")
    st.markdown("### **1. Characteristic Strength Check ($f_{cu}$)**")
    
    st.latex(r"f_{cu,1} = f_m - (k \times s)")
    st.latex(rf"f_{{cu,1}} = {mean_fcu:.2f} - ({k} \times {s:.2f}) = {fcu_calc_1:.2f} \text{{ N/mm}}^2")
    
    st.latex(r"f_{cu,2} = 0.85 \times f_m")
    st.latex(rf"f_{{cu,2}} = 0.85 \times {mean_fcu:.2f} = {fcu_calc_2:.2f} \text{{ N/mm}}^2")
    
    st.latex(r"f_{cu} = \max(f_{cu,1}, f_{cu,2})")
    st.write(f"👉 **Calculated $f_{{cu}}$** = `{fcu_char:.2f}` N/mm² | **Required Spec:** `{fcu_spec:.1f}` N/mm²")
    
    if cond1:
        st.markdown("✔️ **Condition 1 Met:** $f_{cu} \\ge f_{cu,\\text{spec}}$")
    else:
        st.markdown("❌ **Condition 1 Failed:** $f_{cu} < f_{cu,\\text{spec}}$")

    st.markdown("---")
    st.markdown("### **2. Individual Cube Minimum Check**")
    st.latex(r"f_{\text{cube, min}} \ge 0.85 \times f_{cu,\text{spec}}")
    st.write(f"• Minimum allowed individual cube limit ($0.85 \\times f_{{cu,\\text{{spec}}}}$): **`{0.85 * fcu_spec:.2f}` N/mm²**")
    st.write(f"• Lowest recorded cube result in sample: **`{min_cube:.2f}` N/mm²**")
    
    if cond2:
        st.markdown("✔️ **Condition 2 Met:** Lowest individual cube strength meets the requirement.")
    else:
        st.markdown("❌ **Condition 2 Failed:** Lowest individual cube strength is below the minimum allowable limit.")
