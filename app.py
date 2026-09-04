# Generate Rich Structured Excel Report
display_project_name = project_name if project_name.strip() else "Unnamed Project"

# --- FIXED: Define display_engineer_name here so it is available for Excel and PDF ---
display_engineer_name = (
    engineer_name if engineer_name.strip() else "Not Specified"
display_project_name = project_name if project_name.strip() else "Unnamed Project"

# --- FIXED: Define display_engineer_name here so it is available for Excel and PDF ---
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
