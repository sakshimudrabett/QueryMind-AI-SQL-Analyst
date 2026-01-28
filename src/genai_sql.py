"""
Intent-based NL → SQL Generator
Order matters: specific intents MUST come before generic ones.
"""

def generate_sql(user_question):
    q = user_question.lower()

    # 1️⃣ Customer segment revenue (VERY specific)
    if "customer segment" in q or ("segment" in q and "customer" in q):
        return """
        SELECT customer_segment, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY customer_segment
        ORDER BY total_revenue DESC;
        """

    # 2️⃣ Product category revenue
    if "category" in q:
        return """
        SELECT category, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY category
        ORDER BY total_revenue DESC;
        """

    # 3️⃣ Top products by revenue
    if "top" in q and "product" in q:
        return """
        SELECT product, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY product
        ORDER BY total_revenue DESC
        LIMIT 5;
        """

    # 4️⃣ Monthly revenue trend
    if "month" in q or "monthly" in q or "trend" in q:
        return """
        SELECT strftime('%Y-%m', order_date) AS month,
               SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY month
        ORDER BY month;
        """

    # 5️⃣ Region-wise highest revenue (MORE generic → comes later)
    if "region" in q and ("highest" in q or "most" in q):
        return """
        SELECT region, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
        LIMIT 1;
        """

    # 6️⃣ Region-wise revenue (generic)
    if "region" in q:
        return """
        SELECT region, SUM(revenue) AS total_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC;
        """

    # 7️⃣ Safe fallback
    return "SELECT * FROM sales LIMIT 5;"
