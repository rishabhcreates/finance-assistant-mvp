import streamlit as st
import pandas as pd
import requests

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Finance Assistant", layout="wide")

st.title("💰 Personal Finance Assistant")
st.markdown("Upload your transactions and get **AI-powered insights** into your spending habits.")

# -----------------------
# File Uploader
# -----------------------
uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type=["csv"])

# -----------------------
# Helper - AI Call
# -----------------------
def get_ai_suggestions(goal, transactions):
    """Send goal + transaction summary to Perplexity API"""
    api_key = st.secrets["PERPLEXITY_API_KEY"]
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Summarize transactions for context
    tx_summary = (
        transactions.groupby("category")["amount"].sum().reset_index().to_dict(orient="records")
        if "category" in transactions.columns else []
    )

    payload = {
        "model": "llama-3.1-sonar-small-128k-online",  # small + online for MVP
        "messages": [
            {
                "role": "system",
                "content": "You are a financial advisor. Provide practical, concise suggestions."
            },
            {
                "role": "user",
                "content": f"My goal is: {goal}. Based on my spending summary: {tx_summary}, suggest 3 actionable measures."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ API Error: {response.text}"

# -----------------------
# If File Uploaded
# -----------------------
if uploaded_file is not None:
    try:
        transactions = pd.read_csv(uploaded_file)

        # Normalize column names
        transactions.columns = [col.strip().lower() for col in transactions.columns]

        if "amount" not in transactions.columns:
            st.error("CSV must include an `amount` column.")
        else:
            st.success("✅ Transactions loaded successfully!")

            # Preview
            st.subheader("📊 Transactions Preview")
            st.dataframe(transactions.head(10), use_container_width=True)

            # Summary
            st.subheader("📈 Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Transactions", len(transactions))
            with col2:
                st.metric("Total Spent", f"${transactions['amount'].sum():,.2f}")

            # Category breakdown
            if "category" in transactions.columns:
                st.subheader("📌 Spending by Category")
                category_summary = (
                    transactions.groupby("category")["amount"].sum()
                    .reset_index().sort_values(by="amount", ascending=False)
                )
                st.bar_chart(category_summary.set_index("category"))
            else:
                st.info("No `category` column found. Add one to see breakdown.")

            # Goal + AI
            st.subheader("🎯 Set a Goal & Get AI Suggestions")
            goal = st.text_input("Enter your financial goal (e.g., 'Save 10,000 for emergency fund')")

            if goal:
                with st.spinner("💡 Getting AI suggestions..."):
                    suggestions = get_ai_suggestions(goal, transactions)
                st.markdown("### 🤖 AI Recommendations")
                st.write(suggestions)

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("👆 Please upload a CSV file to get started.")
