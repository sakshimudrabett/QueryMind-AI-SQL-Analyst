"""
groq_sql.py
Converts natural language questions into PostgreSQL-compatible SQL
using Groq's LLaMA 3.3 model.
"""

import re
from groq import Groq


SYSTEM_PROMPT = """You are an expert PostgreSQL query engineer.

Given a user's question in plain English and a database schema, produce one correct,
executable PostgreSQL SQL query.

STRICT RULES:
- Output ONLY the raw SQL. No explanation, no markdown, no code fences, no preamble.
- Use standard PostgreSQL syntax (e.g. ILIKE, DATE_TRUNC, TO_CHAR where appropriate).
- Only reference tables and columns that exist in the provided schema.
- When aggregating, always alias the result column with a readable snake_case name.
- For top-N questions, use ORDER BY ... DESC LIMIT N.
- For time-series / trend questions, use DATE_TRUNC or TO_CHAR to group by period.
- Always use GROUP BY on non-aggregated columns when using aggregate functions.
- Use double-quotes for identifiers with spaces or mixed case if needed.
- Never use DROP, DELETE, INSERT, UPDATE, or any DDL/DML statement.
"""


def generate_sql_with_groq(question: str, schema: str, api_key: str) -> str:
    """
    Call Groq LLaMA 3.3 to convert a natural language question into PostgreSQL SQL.

    Args:
        question : Plain-English question from the user.
        schema   : Text description of the database schema (tables + columns).
        api_key  : Groq API key.

    Returns:
        A clean PostgreSQL SQL string.

    Raises:
        groq.APIError: On API communication failure.
    """
    client = Groq(api_key=api_key)

    user_message = (
        f"Database Schema:\n{schema}\n\n"
        f"Question: {question}\n\n"
        f"SQL:"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.05,
        max_tokens=600,
    )

    raw = response.choices[0].message.content.strip()
    return _clean_sql(raw)


def _clean_sql(raw: str) -> str:
    """Remove markdown fences and stray whitespace from LLM output."""
    raw = re.sub(r"```[\w]*", "", raw)
    raw = raw.replace("```", "")
    lines = raw.strip().splitlines()
    sql_lines = []
    started = False
    for line in lines:
        upper = line.strip().upper()
        if not started and any(upper.startswith(kw) for kw in ("SELECT", "WITH", "(")):
            started = True
        if started:
            sql_lines.append(line)
    result = "\n".join(sql_lines).strip()
    return result if result else raw.strip()