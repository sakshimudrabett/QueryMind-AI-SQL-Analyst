"""
insight_generator.py
Produces concise business insights from a query result using Groq LLaMA 3.
"""

import pandas as pd
from groq import Groq


SYSTEM_PROMPT = """You are a senior business analyst reviewing a data table.

Given a table and the question that produced it, write 3–5 sharp, specific insights.

Rules:
- Reference actual numbers, names, or percentages from the data.
- Each insight is exactly one standalone sentence on its own line.
- No bullet points, no numbering, no headers.
- Do not re-state the question or say "the data shows".
- Focus on what's remarkable: outliers, growth, gaps, risks, opportunities.
"""


def generate_insights_with_groq(df: pd.DataFrame, question: str, api_key: str) -> str:
    """
    Generate business insights from a query result DataFrame.

    Args:
        df       : Query result (max 25 rows sent to LLM).
        question : The original natural language question.
        api_key  : Groq API key.

    Returns:
        A newline-separated string of insight sentences.
    """
    client = Groq(api_key=api_key)

    # Keep prompt small: send at most 25 rows as a markdown table
    table_md = df.head(25).to_markdown(index=False)

    prompt = (
        f"Question: {question}\n\n"
        f"Data:\n{table_md}\n\n"
        f"Insights:"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.35,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()