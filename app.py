import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import math

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Finance Assistant MVP",
    page_icon="💰",
    layout="wide"
)

# Secrets
PERP_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", None)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)

PERP_CHAT_ENDPOINT = "https://api.perplexity.ai/chat/completions"  # check docs

# ----------------------------
# DATA LOADING
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("transactions.csv")

transactions = load_data()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.title("⚙️ Settings")
goal = st.sidebar.text_input("🎯 Enter your savings goal", placeholder="e.g., Save ₹50,000 in 6 months")

st.sidebar.markdown("---")
st.sidebar.info("Upload your own CSV in the future version!")

# ----------------------------
# UI HEADER
# ----------------------------
st.title("💰 Smart Finance Assistant")
st.markdown("Analyze your transactions, set savings goals, and get **AI-powered insights**.")

# ----------------------------
# TRANSACTIONS CAROUSEL
# ----------------------------
st.subheader("📑 Transactions")

page_size = 5
total_pages = math.ceil(len(transactions) / page_size)
page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

start = (page - 1) * page_size
end = start + page_size
st.dataframe(transactions.iloc[start:end], use_container_width=True)

# ----------------------------
# INFLOW / OUTFLOW CHART
# ----------------------------
inflow = transactions[transactions["Type"] == "Credit"]["Amount"].sum()
outflow = transactions[transactions["Type"] == "Debit"]["Amount"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Inflow", f"₹{inflow:,.0f}")
    st.metric("Total Outflow", f"₹{outflow:,.0f}")

with col2:
    fig, ax = plt.subplots()
    ax.pie(
        [max(inflow, 0), max(outflow, 0)],
        labels=["Inflow", "Outflow"],
        autopct='%1.1f%%',
        startangle=90,
        colors=["#4CAF50", "#F44336"]
    )
    ax.axis("equal")
    st.pyplot(fig)

# ----------------------------
# AI HELPERS
# ----------------------------
def call_perplexity(prompt):
    if not PERP_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {PERP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-medium-chat",  # adjust based on docs
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post(PERP_CHAT_ENDPOINT, headers=headers, json=payload)
        if resp.status_code == 200:
            j = resp.json()
            return j["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Perplexity error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"⚠️ Perplexity call failed: {e}"


def analyze_transactions(transactions, goal=None):
    trans_text = transactions.to_string(index=False)
    prompt = f"""
    You are a personal finance assistant.
    Here is the transaction history:
    {trans_text}

    1. Summarize inflow & outflow.
    2. Highlight unusual or big expenses.
    3. Suggest 2-3 budgeting strategies.
    """

    if goal:
        prompt += f"\nAlso, suggest strategies to achieve this goal: {goal}"

    return call_perplexity(prompt)


def query_transactions(transactions, user_query):
    trans_text = transactions.to_string(index=False)
    prompt = f"""
    You are a finance AI. Answer user queries from this transaction history:
    {trans_text}

    Question: {user_query}
    """
    return call_perplexity(prompt)

# ----------------------------
# AI INSIGHTS
# ----------------------------
if st.button("🔍 Get AI Insights"):
    report = analyze_transactions(transactions, goal)
    st.subheader("📊 AI Insights")
    st.write(report)

# ----------------------------
# Q&A
# ----------------------------
st.subheader("💬 Ask AI About Your Finances")
user_query = st.text_input("Type your question", placeholder="e.g., How much did I spend on food?")
if user_query:
    answer = query_transactions(transactions, user_query)
    st.success(answer)
