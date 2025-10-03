import json, re, io
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="Ghost Cleaner", layout="centered")
st.title("Ghost → Clean JSON")

uploaded = st.file_uploader("Upload your Ghost export JSON", type=["json"])
download_name = st.text_input("Output filename", value="almost_clean.json")

def extract_body(post):
    if post.get("plaintext"):
        return post["plaintext"].strip()
    html = post.get("html")
    if not html:
        return None
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+\n|\n\s+|\s{2,}", " ", text).strip()
    return text or None

def clean_post(p):
    body = extract_body(p)
    if not body:
        return None
    return {
        "date": p.get("published_at"),
        "title": p.get("title"),
        "content": body,
    }

if uploaded:
    data = json.load(uploaded)
    posts = data.get("db", [{}])[0].get("data", {}).get("posts", [])
    st.write(f"Detected **{len(posts)}** posts in export.")
    if st.button("Clean now"):
        cleaned = [c for c in (clean_post(p) for p in posts) if c]
        buf = io.BytesIO()
        buf.write(json.dumps(cleaned, ensure_ascii=False, indent=2).encode("utf-8"))
        buf.seek(0)
        st.success(f"Cleaned {len(cleaned)} posts.")
        st.download_button("Download cleaned JSON", buf, file_name=download_name, mime="application/json")
