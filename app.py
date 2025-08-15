import streamlit as st

st.set_page_config(page_title="Email Parser", page_icon="📧", layout="centered")

st.title("📧 Email Parser")
st.write("Enter an email address and I’ll split it into **username** and **domain**.")

email = st.text_input("Email address", placeholder="e.g. name@example.com")

if email:
    email = email.strip()
    if "@" in email and email.count("@") == 1:
        username, domain = email.split("@", 1)
        st.success(f"**Username:** {username}")
        st.info(f"**Domain:** {domain}")
    else:
        st.error("Invalid email address! Please include exactly one '@'.")
