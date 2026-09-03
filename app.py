import streamlit as st
import numpy as np
import pandas as pd
import io

st.set_page_config(
    page_title="ECP 203 Concrete Cube Evaluator",
    page_icon="🏗️",
    layout="wide"
)

# App Title & Header
st.title("🏗️ :orange[ECP 203 Concrete Cube Acceptance Verifier]")
st.subheader("Official Compliance Checking according to Egyptian Code of Practice (ECP 203)")
st.markdown("---")

# Sidebar - Project Metadata Inputs
st.sidebar.header("📋 Project Details")
project_name = st.sidebar.text_input("Project Name", "New Capital Site Alpha")
pour_location = st.sidebar.text_input("Structural Element / Pour Location", "Slab Axis A1-C5")
fcu_specified = st.sidebar.number_input("Specified Grade fcu (N/mm²)", min_value=15.0, max_value=80.0, value=30.0, step=5.0)

# Main Section - Cube Results Input
st.header("1. Input 28-Day Cube Crushing Results (N/mm²)")
st.info("💡 ECP 203 evaluates compliance based on group statistical distribution and minimum individual cube strength.")

default_cubes = "32.5, 34.0, 31.0, 35.5, 29.0, 33.0"
user_input = st.text_area("Enter cube results separated by commas:", value=default_cubes, height=100)

# Execution Logic
if st.button("🔍 Run ECP 203 Verification", type="primary"):
    try:
        # Parse inputs
        cube_results = [float(x.strip()) for x in user_input.split(",") if x.strip() != ""]
        n = len(cube_results)

        if n < 3:
            st.error("⚠️ ECP 203 requires at least 3 cube test results for statistical evaluation.")
        else:
            # Mathematical Calculations (NumPy Engine)
            f_m = float(np.mean(cube_results))
            s = float(np.std(cube_results, ddof=1)) if n > 1 else 0.0
            f_min = float(np.min(cube_results))
            
            # ECP 203 Statistical Margin Factor (k)
            k = 1.64 if n >= 30 else 1.91
            f_cu_calc = f_m - (k * s)
            
            # Acceptance Conditions
            group_pass = f_cu_calc >= fcu_specified
            min_individual_target = fcu_specified - 3.0
            individual_pass = f_min >= min_individual_target
            
            overall_pass = group_pass and individual_pass

            # Display Key Metrics
            st.markdown("### 2. Statistical Analysis Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sample Count (n)", f"{n} cubes")
            col2.metric("Mean Strength (f_m)", f"{f_m:.2f} N/mm²")
            col3.metric("Standard Dev (s)", f"{s:.2f} N/mm²")
            col4.metric("Characteristic Strength (f_cu)", f"{f_cu_calc:.2f} N/mm²")

            # Output Verification Verdict
            st.markdown("### 3. ECP 203 Compliance Verdict")
            if overall_pass:
                st.success(f"✅ **ACCEPTED**: The batch complies with ECP 203 requirements for Grade {fcu_specified:.0f} N/mm².")
            else:
                st.error(f"❌ **REJECTED**: Concrete batch fails ECP 203 criteria.")

            # Detailed Compliance Table
            check_data = [
                {
                    "ECP 203 Rule": "Group Mean Check (f_m - k·s)",
                    "Required Limit": f"≥ {fcu_specified:.1f} N/mm²",
                    "Calculated Value": f"{f_cu_calc:.2f} N/mm²",
                    "Status": "PASS" if group_pass else "FAIL"
                },
                {
                    "ECP 203 Rule": "Minimum Individual Cube Check",
                    "Required Limit": f"≥ {min_individual_target:.1f} N/mm²",
                    "Calculated Value": f"{f_min:.2f} N/mm²",
                    "Status": "PASS" if individual_pass else "FAIL"
                }
            ]
            
            df_checks = pd.DataFrame(check_data)
            st.table(df_checks)

            # Excel Download Generator
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                report_df = pd.DataFrame([{
                    "Project": project_name,
                    "Location": pour_location,
                    "Specified fcu": fcu_specified,
                    "Mean Strength": round(f_m, 2),
                    "Std Deviation": round(s, 2),
                    "Calculated fcu": round(f_cu_calc, 2),
                    "Verdict": "ACCEPTED" if overall_pass else "REJECTED"
                }])
                report_df.to_excel(writer, index=False, sheet_name="ECP203_Report")
            
            st.download_button(
                label="📥 Download Official Excel Report (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"ECP203_Cube_Report_{project_name.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except ValueError:
        st.error("❌ Invalid input format! Please enter numeric values separated by commas.")
