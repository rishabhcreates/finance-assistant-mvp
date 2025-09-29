import streamlit as st
import pandas as pd

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(page_title="Finance Assistant", layout="wide")

st.title("💰 Personal Finance Assistant")
st.markdown("Upload your transactions and get instant insights into your spending habits.")

# -----------------------
# File Uploader
# -----------------------
uploaded_file = st.file_uploader("📂 Upload your transactions CSV", type=["csv"])

# -----------------------
# If File Uploaded
# -----------------------
if uploaded_file is not None:
    try:
        transactions = pd.read_csv(uploaded_file)

        # Clean column names (in case of spaces/case sensitivity)
        transactions.columns = [col.strip().lower() for col in transactions.columns]

        # ✅ Check if required columns exist
        if "amount" not in transactions.columns:
            st.error("CSV must include an `amount` column.")
        else:
            st.success("✅ Transactions loaded successfully!")

            # -----------------------
            # Show Preview
            # -----------------------
            st.subheader("📊 Transactions Preview")
            st.dataframe(transactions.head(10), use_container_width=True)

            # -----------------------
            # Summary Stats
            # -----------------------
            st.subheader("📈 Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Transactions", len(transactions))
            with col2:
                st.metric("Total Spent", f"${transactions['amount'].sum():,.2f}")

            # -----------------------
            # Spending by Category
            # -----------------------
            if "category" in transactions.columns:
                st.subheader("📌 Spending by Category")
                category_summary = (
                    transactions.groupby("category")["amount"]
                    .sum()
                    .reset_index()
                    .sort_values(by="amount", ascending=False)
                )
                st.bar_chart(category_summary.set_index("category"))
            else:
                st.info("No `category` column found. Add one to see category breakdown.")

            # -----------------------
            # Goal Input
            # -----------------------
            st.subheader("🎯 Set a Goal")
            goal = st.text_input("Enter your financial goal (e.g., 'Save 10,000 for emergency fund')")

            if goal:
                st.success(f"Your Goal: {goal}")
                st.markdown(
                    "👉 AI suggestions for achieving this goal will be added here (Perplexity API integration)."
                )

    except Exception as e:
        st.error(f"Error reading file: {e}")

# -----------------------
# If No File Uploaded
# -----------------------
else:
    st.info("👆 Please upload a CSV file to get started.")
    st.markdown(
        """
        **Sample CSV format:**
        ```
        date,amount,category,description
        2025-01-01,50,Food,Lunch
        2025-01-03,120,Transport,Taxi
        2025-01-05,300,Shopping,Clothes
        ```
        """
    )
