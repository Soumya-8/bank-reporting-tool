import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.ingestion import load_trial_balance, categorise
from modules.pl_engine import generate_pl
from modules.balance_sheet import generate_balance_sheet
from modules.ratios import calculate_ratios, interpret_ratios
from modules.pdf_export import generate_pdf
from modules.variance import calculate_variance
from modules.npa import classify_npa

def run_app():
    st.title("Bank Financial Reporting Tool")
    st.markdown("Automated P&L, Balance Sheet, Ratios, Charts, Variance and NPA Analysis")

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
        st.dataframe(income[['gl_name', 'credit']].rename(
            columns={'gl_name': 'Income Head', 'credit': 'Amount (Rs.)'}))
        st.dataframe(expenses[['gl_name', 'debit']].rename(
            columns={'gl_name': 'Expense Head', 'debit': 'Amount (Rs.)'}))

        st.subheader("Balance Sheet")
        st.dataframe(assets[['gl_name', 'debit']].rename(
            columns={'gl_name': 'Asset', 'debit': 'Amount (Rs.)'}))
        st.dataframe(liabilities[['gl_name', 'credit']].rename(
            columns={'gl_name': 'Liability / Capital', 'credit': 'Amount (Rs.)'}))

        st.subheader("Key Financial Ratios")
        ratios = calculate_ratios(
            total_income, total_expenses, net_profit, assets, liabilities)
        insights = interpret_ratios(ratios)

        col1, col2 = st.columns(2)
        ratio_items = list(ratios.items())
        for i, (name, value) in enumerate(ratio_items):
            if i % 2 == 0:
                col1.metric(name, f"{value}%")
            else:
                col2.metric(name, f"{value}%")

        st.subheader("CA Insights")
        for insight in insights:
            if "not" in insight or "high" in insight or "exceeds" in insight or "low" in insight:
                st.warning(insight)
            else:
                st.success(insight)

        st.subheader("Financial Charts")
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            ax.bar(['Income', 'Expenses'], [total_income, total_expenses],
                   color=['#1a3c5e', '#e74c3c'])
            ax.set_title('Income vs Expenses')
            ax.set_ylabel('Amount (Rs.)')
            st.pyplot(fig)

        with col2:
            fig2, ax2 = plt.subplots()
            ax2.pie(expenses['debit'], labels=expenses['gl_name'],
                    autopct='%1.1f%%', startangle=90)
            ax2.set_title('Expense Breakdown')
            st.pyplot(fig2)

        st.subheader("Download Report")
        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf(
                assets, liabilities, income, expenses, net_profit)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Click here to download PDF",
                    data=f,
                    file_name="bank_financial_report.pdf",
                    mime="application/pdf")
            st.success("PDF generated successfully!")

        st.subheader("Variance Analysis (Month Comparison)")
        st.markdown("Upload two months of trial balance to compare changes")
        file1 = st.file_uploader("Upload Month 1 CSV", type="csv", key="m1")
        file2 = st.file_uploader("Upload Month 2 CSV", type="csv", key="m2")
        if file1 and file2:
            df1 = load_trial_balance(file1)
            df2 = load_trial_balance(file2)
            variance_df = calculate_variance(df1, df2)
            st.dataframe(variance_df)

        st.subheader("NPA Classification")
        st.markdown("Upload loan data CSV with columns: loan_id, borrower_name, loan_amount, days_overdue")
        loan_file = st.file_uploader("Upload Loan Data CSV", type="csv", key="loan")
        if loan_file:
            loans_df = pd.read_csv(loan_file)
            result = classify_npa(loans_df)
            st.dataframe(result)
            npa_count = len(result[result['status'] != 'Standard'])
            total_provision = result['provision_required'].sum()
            col1, col2 = st.columns(2)
            col1.metric("Total NPAs detected", npa_count)
            col2.metric("Total Provision Required", f"Rs. {total_provision:,.0f}")