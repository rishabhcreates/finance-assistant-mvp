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
# Helper - AI Call
# -----------------------
def get_ai_suggestions(goal, inflow, outflow, breakdown):
    api_key = st.secrets.get("PERPLEXITY_API_KEY")
    if not api_key:
        return "⚠️ API key missing in Streamlit secrets."

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    content = (
        f"My financial goal is: {goal}.\n"
        f"Summary:\n- Total inflow: ₹{inflow:,.2f}\n- Total outflow: ₹{outflow:,.2f}\n"
        f"- Breakdown by category: {breakdown}\n\n"
        "1. Provide 3 specific, actionable steps with numbers for saving, investing, or SIPs.\n"
        "2. Also provide 3 practical savings tips based on this data."
    )

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a certified financial advisor."},
            {"role": "user", "content": content}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                return "⚠️ Unexpected response format from API."
        else:
            return f"⚠️ API Error: {response.text}"
    except Exception as e:
        return f"⚠️ Request failed: {e}"

# -----------------------
# File Uploader
# -----------------------
uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().capitalize() for c in df.columns]  # normalize headers

        required_cols = {"Date", "Amount", "Type", "Category"}
        if not required_cols.issubset(df.columns):
            st.error(f"CSV must include the following columns: {required_cols}")
        else:
            st.success("✅ Transactions loaded successfully!")

            # Convert types
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df = df.dropna(subset=["Amount"])

            # -----------------------
            # Inflow & Outflow
            # -----------------------
            inflow = df[df["Type"].str.lower() == "inflow"]["Amount"].sum()
            outflow = abs(df[df["Type"].str.lower() == "outflow"]["Amount"].sum())
            savings = inflow - outflow if inflow > outflow else 0

            st.subheader("📈 Financial Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Inflow", f"₹{inflow:,.2f}")
            c2.metric("Total Outflow", f"₹{outflow:,.2f}")
            c3.metric("Estimated Savings", f"₹{savings:,.2f}")

            # -----------------------
            # Pie Chart: Expenses + Savings
            # -----------------------
            st.subheader("🧩 Expense Breakdown")

            expense_df = df[df["Type"].str.lower() == "outflow"]
            category_expense = expense_df.groupby("Category")["Amount"].sum().abs().to_dict()

            if savings > 0:
                category_expense["Savings"] = savings

            labels = list(category_expense.keys())
            sizes = list(category_expense.values())

            colors = [
                "#F44336" if lbl != "Savings" else "#4CAF50"  # Red for expenses, Green for savings
                for lbl in labels
            ]

            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                colors=colors
            )
            ax.set_title("Inflow Distribution")
            ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            st.pyplot(fig)

            # -----------------------
            # Transactions Preview
            # -----------------------
            st.subheader("📋 Recent Transactions")
            st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)

            # -----------------------
            # AI Suggestions
            # -----------------------
            st.subheader("🎯 Set a Financial Goal")
            goal = st.text_input("Enter your goal (e.g., 'Save ₹50,000 in 6 months')")

            if goal:
                with st.spinner("💡 Analyzing and generating insights..."):
                    suggestions = get_ai_suggestions(goal, inflow, outflow, category_expense)
                st.markdown("### 🤖 AI Recommendations")
                st.write(suggestions)

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👆 Please upload a CSV file to get started.")
