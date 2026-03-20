# ◈ QueryMind — AI SQL Analyst

> Upload any CSV · ask questions in plain English · get SQL, results & AI insights instantly.


## What is QueryMind?

QueryMind is a natural language SQL analyst that lets anyone — technical or not — query their data just by asking a question in plain English.

You upload a CSV, type something like *"Which category had the highest revenue last month?"* and the app generates the correct PostgreSQL query, runs it against your data, and returns results with AI-generated business insights.

No SQL knowledge required.

---

## Live Demo

> Deployed on Render — [querymind.onrender.com](https://querymind.onrender.com)

---

## Features

- **Natural language → SQL** using Groq LLaMA 3.3 (70B)
- **Upload any CSV** — auto-cleans column names and loads into PostgreSQL
- **Multiple datasets** — upload as many CSVs as you want, switch between them anytime
- **Auto-generated question suggestions** based on your column names
- **AI business insights** on every query result
- **Query history** — revisit and re-run past questions
- **Editable SQL** — tweak the generated query before running
- **CSV export** — download any result table
- **Schema explorer** in sidebar — browse all uploaded tables and columns
- **Session stats** — tracks queries run and rows returned

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + custom CSS (Geist font, dark theme) |
| AI / LLM | Groq API — LLaMA 3.3 70B |
| Database | PostgreSQL via Supabase |
| ORM / Driver | psycopg2 + SQLAlchemy |
| Language | Python 3.11 |
| Deployment | Render |

---

## Project Structure

```
QueryMind/
│
├── app.py                    # Main Streamlit UI
├── render.yaml               # Render deployment config
├── requirements.txt
├── .env.example              # Credential template
├── .gitignore
│
└── src/
    ├── groq_sql.py           # NL → PostgreSQL via Groq LLaMA 3.3
    ├── pg_executor.py        # Query runner + schema introspection + CSV uploader
    ├── insight_generator.py  # AI business insights from query results
    └── history.py            # JSON-based query history
```

---

## How It Works

```
User types a question in plain English
            ↓
Schema of the uploaded CSV is injected into the LLM prompt
            ↓
Groq LLaMA 3.3 generates a PostgreSQL query
            ↓
Query runs against PostgreSQL (Supabase)
            ↓
Results displayed as a table + AI insights generated
```

The schema is always injected into the prompt so the LLM never guesses column names — it works with your real data every time.

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/QueryMind.git
cd QueryMind
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up credentials

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
GROQ_API_KEY=gsk_your_groq_key_here
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

- Get a free Groq API key at [console.groq.com](https://console.groq.com)
- Get a free PostgreSQL database at [supabase.com](https://supabase.com)

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Deployment (Render)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect your repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
5. Add environment variables: `GROQ_API_KEY` and `DATABASE_URL`
6. Deploy

---

## Security

- Only `SELECT` queries are allowed — a guard blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and all other DDL/DML before anything reaches the database
- Credentials are read from environment variables only — never hardcoded or logged
- API keys live in `.env` locally and in Render's secret environment variables in production

---

## Example Questions

Once you upload a CSV, try asking:

```
Which category has the highest total revenue?
Show the top 10 rows sorted by sales descending
What is the monthly trend over time?
How many records are there per region?
What is the average order value by customer segment?
Show all orders where quantity is greater than 50
```

---

## Author

**Sakshi Mudrabett**

