import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Finance Assistant", layout="wide")
st.title("💰 Personal Finance Assistant")
st.markdown("Upload your transactions and get AI-powered insights into your finances.")

# -----------------------
# File Uploader
# -----------------------
uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type=["csv"])

# -----------------------
# Helper - AI Call
# -----------------------
def get_ai_suggestions(goal, inflow, outflow, breakdown):
    api_key = st.secrets.get("PERPLEXITY_API_KEY", None)
    if not api_key:
        st.error("⚠️ PERPLEXITY_API_KEY not set in secrets.")
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    content = (
        f"My financial goal is: {goal}.\n"
        f"Summary:\n- Total inflow: ₹{inflow}\n- Total outflow: ₹{outflow}\n"
        f"- Breakdown by category: {breakdown}\n"
        "Provide 3 specific, actionable steps with numbers for saving, investing, or SIPs."
    )

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content": content}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "⚠️ Unexpected response format from API."
    else:
        return f"⚠️ API Error: {response.text}"

# -----------------------
# If File Uploaded
# -----------------------
if uploaded_file is not None:
    try:
        transactions = pd.read_csv(uploaded_file)
        transactions.columns = [c.strip().lower() for c in transactions.columns]

        if "amount" not in transactions.columns:
            st.error("CSV must include an `amount` column.")
        else:
            st.success("✅ Transactions loaded successfully!")

            # -----------------------
            # Inflow & Outflow
            # -----------------------
            if "type" in transactions.columns:
                inflow = transactions.loc[transactions["type"].str.lower() == "inflow", "amount"].sum()
                outflow = transactions.loc[transactions["type"].str.lower() == "outflow", "amount"].sum()
            else:
                inflow = transactions[transactions["amount"] > 0]["amount"].sum()
                outflow = -transactions[transactions["amount"] < 0]["amount"].sum()  # make positive
            
            st.subheader("📈 Inflow vs Outflow")
            col1, col2 = st.columns(2)
            col1.metric("Total Inflow", f"₹{inflow:,.2f}")
            col2.metric("Total Outflow", f"₹{outflow:,.2f}")
            
            # Pie chart
            fig, ax = plt.subplots()
            ax.pie([inflow, outflow], labels=["Inflow", "Outflow"], autopct="%1.1f%%", startangle=90, colors=["#4CAF50", "#F44336"])
            ax.set_title("Inflow vs Outflow")
            st.pyplot(fig)


            # -----------------------
            # Transactions Preview
            # -----------------------
            st.subheader("📊 Transactions Preview")
            st.dataframe(transactions.head(10), use_container_width=True)

            # Category Breakdown
            if "category" in transactions.columns:
                st.subheader("📌 Spending/Investments by Category")
                breakdown = transactions.groupby("category")["amount"].sum().reset_index()
                st.bar_chart(breakdown.set_index("category"))
            else:
                st.info("No `category` column found. Add one for breakdown.")
                breakdown = []

        
            # AI Suggestions
            breakdown_dict = breakdown.to_dict(orient="records") if len(breakdown) > 0 else []


            # -----------------------
            # Goal + AI Suggestions
            # -----------------------
            st.subheader("🎯 Set a Goal & Get AI Suggestions")
            goal = st.text_input("Enter your financial goal (e.g., 'Save ₹50,000 in 6 months')")

            if goal:
                with st.spinner("💡 Generating AI suggestions..."):
                    breakdown_dict = breakdown.to_dict(orient="records") if len(breakdown) > 0 else []
                    suggestions = get_ai_suggestions(goal, inflow, outflow, breakdown_dict)
                st.markdown("### 🤖 AI Recommendations")
                st.write(suggestions)

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👆 Please upload a CSV file to get started.")
