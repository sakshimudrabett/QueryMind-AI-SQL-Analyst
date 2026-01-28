# AI-Powered Data Analyst Assistant

## 📌 Project Overview
This project is an AI-inspired data analytics assistant that allows users to select common business questions and automatically generates SQL queries, executes them on a structured dataset, and produces business insights.

The goal of this project is to demonstrate how Generative AI concepts can be applied responsibly in a data analytics workflow, focusing on accuracy, interpretability, and business relevance.

---

## 🎯 Key Features
- Converts business questions into SQL queries using an intent-based GenAI-style logic
- Executes SQL queries on a structured sales dataset (SQLite)
- Generates clear business insights and recommendations
- Interactive Streamlit-based web interface
- Designed with a pluggable LLM architecture (can integrate real LLM APIs)

---

## 🧠 Supported Business Questions
The system currently supports the following analytical questions:

- Which region has the highest revenue?
- Revenue by region
- Show top 5 products by revenue
- Revenue by customer segment
- Revenue by product category
- Show monthly revenue trend
- Monthly sales performance

The application intentionally uses guided questions to ensure accuracy and avoid ambiguity, similar to enterprise BI tools.

---

## 🏗️ Project Architecture
GenAI_Data_Analyst/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│ └── sales_data.csv
│
└── src/
├── genai_sql.py
├── sql_executor.py
├── insight_generator.py
└── load_data.py


---

## ⚙️ How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone <repository-url>
cd GenAI_Data_Analyst

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Load data into SQLite
python src/load_data.py

4️⃣ Run the Streamlit application
streamlit run app.py

📊 Dataset

The project uses a sample sales dataset containing:

Order details

Customer segments

Product categories

Regions

Revenue and quantity information

The dataset is stored as a CSV file and loaded into SQLite for analysis.

🧠 GenAI Design Note

During development, a deterministic intent-based logic is used to simulate GenAI behavior for converting natural language questions into SQL. This avoids API dependency while preserving a production-ready architecture that can integrate LLMs such as Hugging Face, Gemini, or OpenAI in future iterations.

🚀 Future Enhancements

Integration with real LLM APIs for dynamic question handling

Additional analytical dimensions (profit, growth rate, forecasting)

Interactive visualizations and dashboards

User-defined custom filters

👩‍💻 Author

Sakshi Mudrabett