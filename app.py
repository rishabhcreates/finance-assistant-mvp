import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Finance Assistant", page_icon="💰", layout="wide")

st.title("💰 Personal Finance Assistant (MVP)")

uploaded_file = st.file_uploader("📂 Upload your bank transaction history (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Transaction Data Preview")

    # Pagination (5 transactions per page)
    items_per_page = 5
    total_pages = (len(df) - 1) // items_per_page + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

    start = (page - 1) * items_per_page
    end = start + items_per_page
    st.dataframe(df.iloc[start:end], use_container_width=True)

    # Calculate inflow/outflow
    inflow = df[df['Type'] == 'Inflow']['Amount'].sum()
    outflow = df[df['Type'] == 'Outflow']['Amount'].sum()

    # Ensure positive for pie chart
    inflow = abs(inflow)
    outflow = abs(outflow)
    savings = inflow - outflow

    st.subheader("💵 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Inflow", f"₹{inflow:,.2f}")
    col2.metric("Outflow", f"₹{outflow:,.2f}")
    col3.metric("Net Savings", f"₹{savings:,.2f}")

    # Pie chart
    st.subheader("📈 Inflow vs Outflow")
    fig, ax = plt.subplots()
    ax.pie([inflow, outflow], labels=["Inflow", "Outflow"], autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Dummy AI insights
    st.subheader("🤖 AI Recommendation")
    if savings > 0:
        st.success(f"Great job! You're saving money. Consider investing ₹{round(savings*0.3)} into SIPs.")
    else:
        st.warning("Your expenses exceed income. Try reducing discretionary spendings like dining out or subscriptions.")

else:
    st.info("Please upload a CSV file to begin.")
