import streamlit as st
import pandas as pd
from google import genai
import os
import json
from utils.helpers import init_db, load_data
from profiler.schema_profiler import SchemaProfiler
from profiler.content_profiler import ContentProfiler
from sql_generator.sql_builder import generate_repair_sql

st.set_page_config(layout="wide", page_title="Data Quality & Repair Studio")

st.title("🛠️ Data Quality & SQL Repair Studio")
st.markdown("Automated profiling and repair for ingested datasets")

conn = init_db()

# Load data paths
RAW_PATH = "data/customers_raw.csv"
REF_PATH = "data/customers_reference.csv"

try:
    raw_df, ref_df = load_data(conn, RAW_PATH, REF_PATH)
except FileNotFoundError:
    st.error("Data files not found. Ensure customers_raw.csv and customers_reference.csv are in their respective data folders")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Raw Dataset")
    st.dataframe(raw_df.head(10))
with col2:
    st.subheader("Reference Dataset")
    st.dataframe(ref_df.head(10))

st.divider()

# Profiling
st.header("📊 Data Profiling Report")

schema_prof = SchemaProfiler(conn)
schema_report = schema_prof.profile()

content_prof = ContentProfiler(conn)
content_report = content_prof.profile()

tab1, tab2 = st.tabs(["Schema Issues", "Content Issues"])

with tab1:
    st.markdown(f"**Status:** {schema_report['status']}")
    for issue in schema_report['issues']:
        st.error(issue)

with tab2:
    for item in content_report:
        if item["Violations"] > 0:
            st.warning(f"**{item['Rule']}**: {item['Violations']} violations found. ({item['Description']})")
        else:
            st.success(f"**{item['Rule']}**: Passed")

st.divider()

# SQL Generation
st.header("⚙️ Auto-Generated Repair SQL")

# Get active rules (rules that have implementations)
active_rules = [item["Rule_Obj"] for item in content_report]

generated_sql = generate_repair_sql(schema_report["ref_columns"], active_rules)

st.code(generated_sql, language="sql")

if st.button("▶️ Test Execute SQL"):
    try:
        result_df = conn.execute(generated_sql).fetchdf()
        st.success("SQL executed successfully! Showing clean data preview:")
        st.dataframe(result_df)
    except Exception as e:
        st.error(f"SQL Execution Failed: {e}")

st.divider()

st.header("📄 Auto-Generate Extensive Report")
st.markdown("Use Gemini 2.5 Flash-Lite to generate a comprehensive text report of the profiling results and fixes.")

def get_ai_summary_report(schema_rep, content_rep, sql):
    """
    Retrieves the extensive report. Pulls from a local text file if available 
    to avoid generating dynamically every time, otherwise calls Gemini.
    """
    local_file_path = "report_summary.txt"
    
    # Extract from local text file if it already exists
    if os.path.exists(local_file_path):
        with open(local_file_path, "r", encoding="utf-8") as f:
            return f.read()

    # If no local file, generate dynamically via Gemini 2.5 Flash-Lite
    # Ensure you have GEMINI_API_KEY set in your environment variables
    client = genai.Client() 
    
    # Prepare the context payload
    prompt = f"""
    You are a Data Engineering Assistant. Analyze the following data quality profiling results and the generated SQL fixes.
    Create a highly detailed, professional text report summarizing the issues found and the exact SQL transformations applied to fix them.
    Format the output cleanly so it is easy to read in a standard text editor.
    Do not bold anything so it looks clean in plain text format.

    Schema Report:
    {json.dumps(schema_rep, indent=2)}
    
    Content Report Violations:
    {json.dumps([{ 'Rule': r['Rule'], 'Violations': r['Violations'], 'Description': r['Description'] } for r in content_rep], indent=2)}
    
    Generated SQL Fixes:
    {sql}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
    )
    
    report_text = response.text
    
    # Cache to local text file for future extraction
    with open(local_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    return report_text

# UI for Generation and Download
if st.button("✨ Generate AI Report"):
    try:
        with st.spinner("Calling Gemini 2.5 Flash-Lite..."):
            report_content = get_ai_summary_report(schema_report, content_report, generated_sql)
            st.session_state['report_content'] = report_content
            st.success("Report generated and cached successfully!")
    except Exception as e:
        st.error(f"Failed to generate report: {e}\n\nMake sure GEMINI_API_KEY is set in your environment variables.")

# Show download button only if the report is in session state
if 'report_content' in st.session_state:
    st.download_button(
        label="⬇️ Download Extensive Report (TXT)",
        data=st.session_state['report_content'],
        file_name="Data_Quality_Extensive_Report.txt",
        mime="text/plain"
    )