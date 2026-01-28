import streamlit as st
from src.genai_sql import generate_sql
from src.sql_executor import run_query
from src.insight_generator import generate_insights

st.set_page_config(
    page_title="AI Data Analyst Assistant",
    layout="centered"
)

st.title("📊 AI-Powered Data Analyst Assistant")
st.write(
    "Select a business question from the list below. "
    "The system generates SQL, executes it, and provides insights."
)

st.divider()

# -------------------------------
# Question Suggestions (ONLY)
# -------------------------------
st.subheader("💡 Select a business question")

SUGGESTED_QUESTIONS = [
    "Which region has the highest revenue?",
    "Revenue by region",
    "Show top 5 products by revenue",
    "Revenue by customer segment",
    "Revenue by product category",
    "Show monthly revenue trend",
    "Monthly sales performance"
]

question = st.selectbox(
    "Choose a question:",
    [""] + SUGGESTED_QUESTIONS
)

# -------------------------------
# Run analysis
# -------------------------------
if question:
    sql = generate_sql(question)

    st.subheader("🧠 Generated SQL")
    st.code(sql, language="sql")

    result = run_query(sql)

    st.subheader("📄 Query Result")
    st.dataframe(result, use_container_width=True)

    insights = generate_insights(result, question)

    st.subheader("📌 Business Insights")
    for line in insights.split("\n"):
        st.write("•", line)
