import streamlit as st
import pandas as pd
import os
import re
from dotenv import load_dotenv

from src.groq_sql import generate_sql_with_groq
from src.pg_executor import run_query, get_schema, upload_dataframe
from src.insight_generator import generate_insights_with_groq
from src.history import load_history, save_to_history, clear_history

load_dotenv()

st.set_page_config(
    page_title="QueryMind — AI SQL Analyst",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@300;400;500&family=Geist:wght@300;400;500;600;700&display=swap');

:root {
    --bg:          #06080d;
    --bg2:         #0d1117;
    --bg3:         #111820;
    --bg4:         #151d28;
    --border:      rgba(255,255,255,0.06);
    --border2:     rgba(255,255,255,0.12);
    --accent:      #00c8ff;
    --accent-dim:  rgba(0,200,255,0.07);
    --accent2:     #00e5a0;
    --accent2-dim: rgba(0,229,160,0.07);
    --purple:      #a78bfa;
    --purple-dim:  rgba(167,139,250,0.07);
    --text:        #e2e8f0;
    --text2:       #8b9ab0;
    --text3:       #4a5568;
    --success:     #34d399;
    --danger:      #f87171;
    --warn:        #fbbf24;
}

* { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1100px; }

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }
[data-testid="stSidebar"] * { color: var(--text) !important; font-family: 'Geist', sans-serif !important; }
[data-testid="stSidebar"] .stExpander {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}

textarea, input[type="text"], input[type="password"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
    border-radius: 10px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea:focus, input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,200,255,0.1) !important;
}

[data-testid="stFileUploader"] {
    background: var(--bg3) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00c8ff18, #00e5a010) !important;
    color: var(--accent) !important;
    font-weight: 500 !important;
    font-family: 'Geist', sans-serif !important;
    border: 1px solid rgba(0,200,255,0.25) !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00c8ff28, #00e5a018) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 18px rgba(0,200,255,0.15) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

.stCode, pre { background: var(--bg2) !important; border: 1px solid var(--border2) !important; border-radius: 12px !important; border-left: 3px solid var(--accent) !important; }
code { font-family: 'Geist Mono', monospace !important; color: var(--accent2) !important; font-size: 0.82rem !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border2) !important; border-radius: 12px !important; overflow: hidden !important; }
[data-testid="stDataFrame"] * { font-family: 'Geist Mono', monospace !important; }
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }
details { background: var(--bg3) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
summary { color: var(--text2) !important; padding: 10px 14px !important; font-size: 0.85rem !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

.hero { padding: 2rem 0 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.hero-eyebrow { font-family:'Geist Mono',monospace; font-size:0.68rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--accent); margin-bottom:10px; display:flex; align-items:center; gap:8px; }
.hero-eyebrow::before { content:''; display:inline-block; width:18px; height:1px; background:var(--accent); }
.hero-title { font-size:2.8rem; font-weight:700; line-height:1.1; letter-spacing:-0.03em; margin-bottom:10px; }
.hero-title .static { background:linear-gradient(135deg,#e2e8f0,#94a3b8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.hero-title .dynamic { background:linear-gradient(135deg,#00c8ff,#00e5a0); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.hero-sub { font-size:0.95rem; color:var(--text2); font-weight:300; line-height:1.6; }
.tag-row { display:flex; gap:8px; margin-top:14px; flex-wrap:wrap; }
.tag { font-family:'Geist Mono',monospace; font-size:0.68rem; color:var(--text3); background:var(--bg3); border:1px solid var(--border2); border-radius:20px; padding:3px 11px; }

.section-label { font-family:'Geist Mono',monospace; font-size:0.62rem; letter-spacing:0.16em; text-transform:uppercase; color:var(--text3); margin-bottom:10px; display:flex; align-items:center; gap:10px; }
.section-label::after { content:''; flex:1; height:1px; background:var(--border); }

.upload-success { background:var(--accent2-dim); border:1px solid rgba(0,229,160,0.2); border-radius:12px; padding:16px 20px; margin-top:12px; }
.upload-success-title { font-size:0.85rem; color:var(--accent2); font-weight:500; margin-bottom:8px; }
.upload-meta { display:flex; gap:20px; font-family:'Geist Mono',monospace; font-size:0.78rem; color:var(--text2); flex-wrap:wrap; }
.upload-meta span { color:var(--accent); }
.col-pills { display:flex; flex-wrap:wrap; gap:5px; margin-top:10px; }
.col-pill { background:var(--bg4); border:1px solid var(--border2); border-radius:6px; padding:3px 9px; font-family:'Geist Mono',monospace; font-size:0.7rem; color:var(--accent); }

.insight-card { background:var(--bg3); border:1px solid var(--border); border-left:3px solid var(--accent2); border-radius:0 12px 12px 0; padding:13px 18px; margin-bottom:9px; font-size:0.88rem; color:var(--text); line-height:1.65; transition:background 0.15s; }
.insight-card:hover { background:var(--accent2-dim); }
.insight-num { display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; background:var(--accent2); border-radius:50%; font-size:9px; font-weight:700; color:#06080d; margin-right:8px; vertical-align:middle; flex-shrink:0; }

.stat-pill { display:inline-flex; align-items:center; gap:5px; background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:6px 14px; font-family:'Geist Mono',monospace; font-size:0.8rem; }
.stat-pill .val { color:var(--accent); font-weight:500; }
.stat-pill .lbl { color:var(--text3); font-size:0.7rem; }

.conn-row { display:flex; align-items:center; gap:6px; font-family:'Geist Mono',monospace; font-size:0.72rem; margin-bottom:5px; }
.dot-ok   { width:6px; height:6px; border-radius:50%; background:var(--success); box-shadow:0 0 5px var(--success); flex-shrink:0; }
.dot-fail { width:6px; height:6px; border-radius:50%; background:var(--danger); flex-shrink:0; }
.conn-ok-text   { color:var(--success); }
.conn-fail-text { color:var(--danger); }

.sidebar-title { font-family:'Geist Mono',monospace; font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--text3); margin:1.2rem 0 0.5rem; }
.schema-pill { display:inline-block; background:var(--bg4); border:1px solid var(--border); border-radius:4px; padding:2px 7px; font-family:'Geist Mono',monospace; font-size:0.68rem; color:var(--accent); margin:2px; }

.empty-state { text-align:center; padding:2.5rem 2rem; color:var(--text3); }
.empty-state .icon { font-size:2rem; margin-bottom:10px; opacity:0.35; }
.empty-state strong { display:block; color:var(--text2); font-size:0.95rem; margin-bottom:5px; }
.empty-state p { font-size:0.82rem; line-height:1.6; margin:0; }

.delete-btn button { background:transparent !important; border:1px solid rgba(248,113,113,0.2) !important; color:var(--danger) !important; font-size:0.72rem !important; padding:4px 10px !important; border-radius:6px !important; }
.delete-btn button:hover { background:rgba(248,113,113,0.08) !important; border-color:var(--danger) !important; box-shadow:none !important; transform:none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
defaults = {
    "question":        "",
    "active_table":    None,
    "active_columns":  [],
    "suggestions":     [],
    "uploaded_tables": {},
    "query_count":     0,
    "last_rows":       0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
pg_url       = os.getenv("DATABASE_URL", "").strip()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def make_suggestions(table: str, columns: list) -> list:
    numeric_hints  = ["revenue","sales","profit","amount","price","cost","quantity","total","count","value","score","salary","budget","spend","qty"]
    date_hints     = ["date","time","month","year","day","created","updated","period","week","quarter"]
    category_hints = ["category","region","segment","type","status","city","country","product","name","department","group","brand","channel","gender","state"]

    num_col  = next((c for c in columns if any(h in c.lower() for h in numeric_hints)), None)
    date_col = next((c for c in columns if any(h in c.lower() for h in date_hints)), None)
    cat_col  = next((c for c in columns if any(h in c.lower() for h in category_hints)), None)

    s = []
    if cat_col and num_col:
        s.append(f"Which {cat_col} has the highest total {num_col}?")
        s.append(f"Show top 5 {cat_col}s ranked by {num_col}")
        s.append(f"What is the average {num_col} grouped by {cat_col}?")
    if date_col and num_col:
        s.append(f"Show the {num_col} trend over {date_col}")
        s.append(f"What is the monthly breakdown of {num_col}?")
    if cat_col:
        s.append(f"How many records are there per {cat_col}?")
    if num_col:
        s.append(f"Show top 10 rows sorted by {num_col} descending")
    s.append(f"Show me the first 20 rows of {table}")
    return s[:6]


def csv_to_table_name(filename: str) -> str:
    raw  = filename.replace(".csv", "").lower()
    name = re.sub(r"[^a-z0-9_]", "_", raw)
    return re.sub(r"_+", "_", name).strip("_")[:50]


def drop_table(table_name: str, database_url: str):
    import psycopg2
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    conn.cursor().execute(f'DROP TABLE IF EXISTS "{table_name}";')
    conn.close()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Geist Mono',monospace;font-size:1.05rem;font-weight:500;color:#e2e8f0;margin-bottom:2px;">◈ QueryMind</div>
    <div style="font-size:0.68rem;color:#4a5568;font-family:'Geist Mono',monospace;margin-bottom:1.4rem;">AI SQL Analyst</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">Status</div>', unsafe_allow_html=True)
    g_ok = bool(groq_api_key)
    p_ok = bool(pg_url)
    st.markdown(f"""
    <div class="conn-row"><span class="{"dot-ok" if g_ok else "dot-fail"}"></span>
    <span class="{"conn-ok-text" if g_ok else "conn-fail-text"}">{"Groq API ready" if g_ok else "GROQ_API_KEY missing"}</span></div>
    <div class="conn-row"><span class="{"dot-ok" if p_ok else "dot-fail"}"></span>
    <span class="{"conn-ok-text" if p_ok else "conn-fail-text"}">{"PostgreSQL ready" if p_ok else "DATABASE_URL missing"}</span></div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.uploaded_tables:
        st.markdown('<div class="sidebar-title">Uploaded tables</div>', unsafe_allow_html=True)
        for tname, meta in list(st.session_state.uploaded_tables.items()):
            is_active = tname == st.session_state.active_table
            star = "★ " if is_active else "⬡ "
            with st.expander(f"{star}{tname}", expanded=is_active):
                st.markdown(f"""
                <div style="font-family:'Geist Mono',monospace;font-size:0.7rem;color:var(--text3);margin-bottom:6px;">
                    {meta['rows']:,} rows · {meta['cols']} cols · {meta['filename']}
                </div>
                """, unsafe_allow_html=True)
                pills = "".join(f'<span class="schema-pill">{c}</span>' for c in meta['columns'][:8])
                more  = f'<span class="schema-pill">+{len(meta["columns"])-8}</span>' if len(meta['columns']) > 8 else ""
                st.markdown(f'<div style="line-height:2.2">{pills}{more}</div>', unsafe_allow_html=True)

                col_sel, col_del = st.columns([1, 1])
                with col_sel:
                    if not is_active:
                        if st.button("Use this", key=f"use_{tname}", use_container_width=True):
                            st.session_state.active_table   = tname
                            st.session_state.active_columns = meta['columns']
                            st.session_state.suggestions    = make_suggestions(tname, meta['columns'])
                            st.session_state.question       = ""
                            st.rerun()
                with col_del:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("Delete", key=f"del_{tname}", use_container_width=True):
                        try:
                            drop_table(tname, pg_url)
                        except Exception:
                            pass
                        del st.session_state.uploaded_tables[tname]
                        if st.session_state.active_table == tname:
                            remaining = list(st.session_state.uploaded_tables.keys())
                            if remaining:
                                nt = remaining[-1]
                                st.session_state.active_table   = nt
                                st.session_state.active_columns = st.session_state.uploaded_tables[nt]['columns']
                                st.session_state.suggestions    = make_suggestions(nt, st.session_state.uploaded_tables[nt]['columns'])
                            else:
                                st.session_state.active_table   = None
                                st.session_state.active_columns = []
                                st.session_state.suggestions    = []
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    st.markdown('<div class="sidebar-title">Session</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <div class="stat-pill"><span class="val">{st.session_state.query_count}</span><span class="lbl">&nbsp;queries</span></div>
        <div class="stat-pill"><span class="val">{st.session_state.last_rows:,}</span><span class="lbl">&nbsp;last rows</span></div>
        <div class="stat-pill"><span class="val">{len(st.session_state.uploaded_tables)}</span><span class="lbl">&nbsp;tables</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-title">History</div>', unsafe_allow_html=True)
    history = load_history()
    if history:
        for i, item in enumerate(reversed(history[-8:])):
            short = item["question"][:40] + ("…" if len(item["question"]) > 40 else "")
            if st.button(f"↩  {short}", key=f"h_{i}", use_container_width=True):
                st.session_state.question = item["question"]
                st.rerun()
        if st.button("Clear history", use_container_width=True):
            clear_history()
            st.rerun()
    else:
        st.caption("No history yet.")


# ─────────────────────────────────────────────
# MAIN — Hero
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <span style="font-family:'Geist Mono',monospace; font-size:1.5rem; color:#00c8ff; font-weight:600; letter-spacing:-0.03em;">◈ QueryMind</span>
        <span style="font-family:'Geist Mono',monospace; font-size:0.68rem; color:#4a5568; background:#111820; border:1px solid rgba(255,255,255,0.08); border-radius:20px; padding:3px 10px; letter-spacing:0.06em;">AI SQL ANALYST</span>
    </div>
    <div class="hero-eyebrow">Natural Language → SQL Engine</div>
    <div class="hero-title">
        <span class="static">Upload your data.<br>Ask </span><span class="dynamic">anything.</span>
    </div>
    <div class="hero-sub">Drop any CSV · pick which table to query · get SQL, results &amp; AI insights</div>
    <div class="tag-row">
        <span class="tag">Groq LLaMA 3.3</span>
        <span class="tag">PostgreSQL</span>
        <span class="tag">Multiple datasets</span>
        <span class="tag">Smart suggestions</span>
        <span class="tag">AI insights</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 1 — Upload CSV
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">01 &nbsp; Upload a CSV dataset</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop CSV here",
    type=["csv"],
    label_visibility="collapsed",
    help="Upload multiple CSVs — each becomes its own table. Old tables are kept.",
)

if uploaded_file is not None:
    table_name     = csv_to_table_name(uploaded_file.name)
    already_loaded = table_name in st.session_state.uploaded_tables

    if not already_loaded:
        with st.spinner(f"Loading `{uploaded_file.name}` into PostgreSQL…"):
            try:
                df_upload = pd.read_csv(uploaded_file)
                upload_dataframe(df_upload, table_name, pg_url)
                rows, cols_n = df_upload.shape
                col_names = list(df_upload.columns)

                st.session_state.uploaded_tables[table_name] = {
                    "filename": uploaded_file.name,
                    "rows": rows, "cols": cols_n, "columns": col_names,
                }
                st.session_state.active_table   = table_name
                st.session_state.active_columns = col_names
                st.session_state.suggestions    = make_suggestions(table_name, col_names)
                st.session_state.question       = ""

                col_list = "".join(f'<span class="col-pill">{c}</span>' for c in col_names[:12])
                more = f'<span class="col-pill">+{len(col_names)-12} more</span>' if len(col_names) > 12 else ""
                st.markdown(f"""
                <div class="upload-success">
                    <div class="upload-success-title">✓ &nbsp; Loaded & active</div>
                    <div class="upload-meta">
                        <div>Table &nbsp;<span>{table_name}</span></div>
                        <div><span>{rows:,}</span> rows</div>
                        <div><span>{cols_n}</span> columns</div>
                    </div>
                    <div class="col-pills" style="margin-top:10px">{col_list}{more}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Upload failed: {e}")
    else:
        meta = st.session_state.uploaded_tables[table_name]
        st.info(f"`{table_name}` already loaded ({meta['rows']:,} rows). Switching to it.")
        st.session_state.active_table   = table_name
        st.session_state.active_columns = meta['columns']
        st.session_state.suggestions    = make_suggestions(table_name, meta['columns'])

    if st.session_state.active_table:
        with st.expander("Preview — first 5 rows", expanded=False):
            try:
                st.dataframe(run_query(f'SELECT * FROM "{st.session_state.active_table}" LIMIT 5', pg_url), use_container_width=True)
            except Exception:
                pass

elif not st.session_state.uploaded_tables:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">⬆</div>
        <strong>No datasets yet</strong>
        <p>Drop a CSV above. Upload multiple files to keep<br>
        all tables available and switch between them anytime.</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 2 — Table picker (if multiple)
# ─────────────────────────────────────────────
if len(st.session_state.uploaded_tables) > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">02 &nbsp; Select which table to query</div>', unsafe_allow_html=True)

    options     = list(st.session_state.uploaded_tables.keys())
    current_idx = options.index(st.session_state.active_table) if st.session_state.active_table in options else 0
    selected    = st.selectbox(
        "Active table",
        options=options,
        index=current_idx,
        format_func=lambda t: f"{t}  ({st.session_state.uploaded_tables[t]['rows']:,} rows · {st.session_state.uploaded_tables[t]['filename']})",
        label_visibility="collapsed",
    )
    if selected != st.session_state.active_table:
        st.session_state.active_table   = selected
        st.session_state.active_columns = st.session_state.uploaded_tables[selected]['columns']
        st.session_state.suggestions    = make_suggestions(selected, st.session_state.uploaded_tables[selected]['columns'])
        st.session_state.question       = ""
        st.rerun()


# ─────────────────────────────────────────────
# STEP 3 — Ask question
# ─────────────────────────────────────────────
if st.session_state.active_table:
    st.markdown("<br>", unsafe_allow_html=True)
    step_num = "03" if len(st.session_state.uploaded_tables) > 1 else "02"
    st.markdown(
        f'<div class="section-label">{step_num} &nbsp; Ask a question about '
        f'<span style="color:var(--accent);font-family:\'Geist Mono\',monospace">'
        f'{st.session_state.active_table}</span></div>',
        unsafe_allow_html=True
    )

    if st.session_state.suggestions:
        icons = ["◎", "◈", "▷", "◉", "◆", "◇"]
        cols  = st.columns(2)
        for i, sug in enumerate(st.session_state.suggestions):
            with cols[i % 2]:
                if st.button(f"{icons[i % len(icons)]}  {sug}", key=f"sug_{i}", use_container_width=True):
                    st.session_state.question = sug
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    question = st.text_area(
        "Question",
        value=st.session_state.question,
        placeholder=(
            "e.g.  Which category has the highest total revenue?\n"
            "       Show the top 10 rows sorted by sales.\n"
            "       What is the trend over time?"
        ),
        height=100,
        label_visibility="collapsed",
    )

    col_run, col_clear, _ = st.columns([1.3, 1, 5])
    with col_run:
        run_btn = st.button("▶  Analyze", use_container_width=True)
    with col_clear:
        if st.button("✕  Clear", use_container_width=True):
            st.session_state.question = ""
            st.rerun()

    # ─────────────────────────────────────────
    # PIPELINE
    # ─────────────────────────────────────────
    if run_btn:
        question = question.strip()

        if not question:
            st.warning("Please enter a question or pick a suggestion.")
            st.stop()
        if not groq_api_key:
            st.error("GROQ_API_KEY missing from .env")
            st.stop()
        if not pg_url:
            st.error("DATABASE_URL missing from .env")
            st.stop()

        try:
            schema = get_schema(pg_url)
            schema_str = "\n".join(
                f'Table "{t}" — columns: {", ".join(c for c, _ in cols)}'
                for t, cols in schema.items()
            )
            schema_str = f'[Query this table: "{st.session_state.active_table}"]\n\n' + schema_str
        except Exception as e:
            st.error(f"Could not load schema: {e}")
            st.stop()

        st.markdown("<br>", unsafe_allow_html=True)

        step_sql = "04" if len(st.session_state.uploaded_tables) > 1 else "03"
        st.markdown(f'<div class="section-label">{step_sql} &nbsp; Generated SQL</div>', unsafe_allow_html=True)
        with st.spinner("Generating SQL with LLaMA 3.3…"):
            try:
                sql = generate_sql_with_groq(question, schema_str, groq_api_key)
                st.session_state.question = ""
            except Exception as e:
                st.error(f"SQL generation failed: {e}")
                st.stop()

        st.code(sql, language="sql")
        edited_sql = st.text_area("✏️ Edit SQL before running (optional)", value=sql, height=80, key="edit_sql")

        step_res = "05" if len(st.session_state.uploaded_tables) > 1 else "04"
        st.markdown(f'<div class="section-label">{step_res} &nbsp; Query results</div>', unsafe_allow_html=True)
        with st.spinner("Running on PostgreSQL…"):
            try:
                result = run_query(edited_sql, pg_url)
            except Exception as e:
                st.error(f"Query failed: {e}")
                st.stop()

        if result is None or result.empty:
            st.info("No rows returned. Try rephrasing your question.")
            st.stop()

        n_rows, n_cols = result.shape
        st.markdown(f"""
        <div style="display:flex;gap:8px;margin-bottom:12px;">
            <div class="stat-pill"><span class="val">{n_rows:,}</span><span class="lbl">&nbsp;rows</span></div>
            <div class="stat-pill"><span class="val">{n_cols}</span><span class="lbl">&nbsp;columns</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(result, use_container_width=True, height=340)
        st.download_button("⬇  Download result as CSV", result.to_csv(index=False).encode(), "result.csv", "text/csv")

        st.session_state.last_rows    = n_rows
        st.session_state.query_count += 1

        step_ins = "06" if len(st.session_state.uploaded_tables) > 1 else "05"
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-label">{step_ins} &nbsp; AI business insights</div>', unsafe_allow_html=True)
        with st.spinner("Generating insights…"):
            try:
                insights = generate_insights_with_groq(result, question, groq_api_key)
            except Exception as e:
                insights = f"Could not generate insights: {e}"

        for i, line in enumerate(insights.strip().split("\n")):
            line = line.strip().lstrip("-•–—*123456789. ")
            if line:
                st.markdown(
                    f'<div class="insight-card"><span class="insight-num">{i+1}</span>{line}</div>',
                    unsafe_allow_html=True,
                )

        save_to_history(question, edited_sql)