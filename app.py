import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("💰 Personal Finance Assistant (MVP)")

uploaded_file = st.file_uploader("Upload your bank transaction history (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Transaction Data Preview")
    st.dataframe(df.head())

    inflow = df[df['Type'] == 'Inflow']['Amount'].sum()
    outflow = df[df['Type'] == 'Outflow']['Amount'].sum()
    savings = inflow - outflow

    st.subheader("💵 Summary")
    st.write(f"Total Inflow: ₹{inflow:,.2f}")
    st.write(f"Total Outflow: ₹{outflow:,.2f}")
    st.write(f"Net Savings: ₹{savings:,.2f}")

    st.subheader("📈 Inflow vs Outflow")
    fig, ax = plt.subplots()
    ax.pie([inflow, outflow], labels=["Inflow", "Outflow"], autopct='%1.1f%%')
    st.pyplot(fig)

    st.subheader("🤖 AI Recommendation")
    if savings > 0:
        st.success(f"Great job! Consider investing ₹{round(savings*0.3)} into SIPs.")
    else:
        st.warning("Your expenses exceed income. Try cutting discretionary spendings.")
