import re
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Email Parser + SQL Search", page_icon="📧", layout="centered")
st.title("📧 Email Parser")
st.write("Enter an email address and I'll split it into **username** and **domain**, save it, and let you **search** the history.")

# ---------- DB setup ----------
@st.cache_resource
def get_conn():
    conn = sqlite3.connect("emails.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT,
            domain TEXT,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn

conn = get_conn()

# helpers
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def parse_email(e: str):
    e = e.strip()
    if not EMAIL_RE.match(e):
        return None, None
    user, domain = e.split("@", 1)
    return user, domain

# ---------- Parse & Save ----------
st.subheader("Parse & Save")
with st.form("parse_form", clear_on_submit=False):
    email = st.text_input("Email address", placeholder="e.g. 24bcs11147@cuchd.in")
    submit = st.form_submit_button("Parse & Save")

if submit:
    username, domain = parse_email(email)
    if not username:
        st.error("Please enter a valid email (must contain one @ and a domain).")
    else:
        st.success(f"Username: **{username}**  |  Domain: **{domain}**")
        # insert with de-duplication
        try:
            conn.execute(
                "INSERT OR IGNORE INTO emails (email, username, domain, parsed_at) VALUES (?, ?, ?, ?)",
                (email.strip(), username, domain, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()
            st.toast("Saved to database ✅", icon="✅")
        except Exception as e:
            st.error(f"DB error: {e}")

# ---------- Search ----------
st.subheader("Search History")

col1, col2 = st.columns(2)
with col1:
    find_domain = st.text_input("🔎 Search by domain", placeholder="e.g. gmail.com / cuchd.in")
with col2:
    find_username = st.text_input("🔎 Search by username", placeholder="e.g. 24bcs11147")

query = "SELECT id, email, username, domain, parsed_at FROM emails"
params = []
where = []

if find_domain:
    where.append("domain LIKE ?")
    params.append(f"%{find_domain.strip()}%")
if find_username:
    where.append("LOWER(username) LIKE LOWER(?)")
    params.append(f"%{find_username.strip()}%")
if where:
    query += " WHERE " + " AND ".join(where)
query += " ORDER BY parsed_at DESC"

df = pd.read_sql_query(query, conn, params=params if params else None)
st.dataframe(df, use_container_width=True)

# optional: quick stats
with st.expander("Quick stats"):
    top_domains = pd.read_sql_query(
        "SELECT domain, COUNT(*) AS total FROM emails GROUP BY domain",
        conn
    )

