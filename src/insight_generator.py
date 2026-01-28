def generate_insights(df, question):
    """
    Converts SQL query results into business insights.
    Handles numeric values safely.
    """

    if df.empty:
        return "No data available to generate insights."

    insights = []

    # Identify dimension and metric columns
    dimension = df.columns[0]
    metric = df.columns[1]

    top_row = df.iloc[0]

    # Safely convert metric to float
    try:
        metric_value = float(top_row[metric])
    except ValueError:
        metric_value = 0.0

    # Revenue-related insights
    if "revenue" in question.lower():
        insights.append(
            f"The highest contributor is '{top_row[dimension]}' with total revenue of {metric_value:,.0f}."
        )

        insights.append(
            "This indicates a strong concentration of revenue in the top-performing segment."
        )

        insights.append(
            "The business may consider strengthening underperforming segments to reduce dependency."
        )

    # Trend-related insights
    if "month" in question.lower() or "trend" in question.lower():
        insights.append(
            "Revenue shows variation across months, indicating possible seasonality."
        )
        insights.append(
            "Further analysis can help align inventory and marketing strategies."
        )

    return "\n".join(insights)
