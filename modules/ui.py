import streamlit as st
from modules.ingestion import load_trial_balance, categorise
from modules.pl_engine import generate_pl
from modules.balance_sheet import generate_balance_sheet

def run_app():
    st.title("Bank Financial Reporting Tool")
    st.markdown("Automated P&L and Balance Sheet generator for banks")

    uploaded_file = st.file_uploader("Upload Trial Balance CSV", type="csv")

    if uploaded_file is not None:
        df = load_trial_balance(uploaded_file)
        assets, liabilities, income, expenses = categorise(df)
        total_income, total_expenses, net_profit = generate_pl(income, expenses)

        st.success(f"File loaded! {len(df)} GL entries found.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rs. {total_income:,.0f}")
        col2.metric("Total Expenses", f"Rs. {total_expenses:,.0f}")
        col3.metric("Net Profit", f"Rs. {net_profit:,.0f}")

        st.subheader("Profit & Loss Statement")
        st.dataframe(income[['gl_name','credit']].rename(
            columns={'gl_name':'Income Head','credit':'Amount (Rs.)'}))
        st.dataframe(expenses[['gl_name','debit']].rename(
            columns={'gl_name':'Expense Head','debit':'Amount (Rs.)'}))

        st.subheader("Balance Sheet")
        st.dataframe(assets[['gl_name','debit']].rename(
            columns={'gl_name':'Asset','debit':'Amount (Rs.)'}))
        st.dataframe(liabilities[['gl_name','credit']].rename(
            columns={'gl_name':'Liability / Capital','credit':'Amount (Rs.)'}))