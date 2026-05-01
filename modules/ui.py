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
    # Simple Header
    st.markdown("""
        <div style="background-color:#1a3c5e;padding:15px;border-radius:10px;margin-bottom:25px;">
            <h1 style="color:white;margin:0;">BankReport AI v1.0</h1>
            <p style="color:#b8d4f0;margin:0;">Automated Financial Analysis</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        st.info("Upload your Trial Balance to begin analysis.")
        st.markdown("---")
        st.write("**Supported Columns:**")
        st.code("gl_code, gl_name, debit, credit")

    # 1. Upload Section
    st.subheader("📁 1. Upload Trial Balance")
    uploaded_file = st.file_uploader("Choose Trial Balance CSV", type="csv")

    if uploaded_file:
        df = load_trial_balance(uploaded_file)
        assets, liabilities, income, expenses = categorise(df)
        total_income, total_expenses, net_profit = generate_pl(income, expenses)

        st.success(f"Successfully loaded {len(df)} GL entries.")

        # 2. Key Metrics
        st.subheader("📈 2. Financial Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Income", f"₹{total_income:,.2f}")
        m2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
        m3.metric("Net Profit", f"₹{net_profit:,.2f}")

        # 3. Statements
        st.markdown("---")
        t1, t2 = st.tabs(["Profit & Loss Statement", "Balance Sheet"])
        
        with t1:
            col_a, col_b = st.columns(2)
            col_a.write("**Income Items**")
            st.dataframe(income[['gl_name', 'credit']].rename(columns={'gl_name':'Name', 'credit':'Credit'}), use_container_width=True)
            col_b.write("**Expense Items**")
            st.dataframe(expenses[['gl_name', 'debit']].rename(columns={'gl_name':'Name', 'debit':'Debit'}), use_container_width=True)

        with t2:
            col_c, col_d = st.columns(2)
            col_c.write("**Assets**")
            st.dataframe(assets[['gl_name', 'debit']], use_container_width=True)
            col_d.write("**Liabilities & Capital**")
            st.dataframe(liabilities[['gl_name', 'credit']], use_container_width=True)

        # 4. Ratios & Charts
        st.markdown("---")
        st.subheader("📊 3. Analysis & Insights")
        ratios = calculate_ratios(total_income, total_expenses, net_profit, assets, liabilities)
        insights = interpret_ratios(ratios)

        r_cols = st.columns(4)
        for i, (name, val) in enumerate(ratios.items()):
            r_cols[i].metric(name, f"{val}%")

        for insight in insights:
            if any(x in insight.lower() for x in ["low", "high", "not healthy", "exceeds"]):
                st.warning(insight)
            else:
                st.success(insight)

        # Charts
        c1, c2 = st.columns(2)
        with c1:
            fig1, ax1 = plt.subplots()
            ax1.bar(["Income", "Expenses"], [total_income, total_expenses], color=['#1a3c5e', '#e74c3c'])
            st.pyplot(fig1)
        with c2:
            fig2, ax2 = plt.subplots()
            ax2.pie(expenses['debit'], labels=expenses['gl_name'], autopct='%1.1f%%')
            st.pyplot(fig2)

        # 5. Export
        st.markdown("---")
        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf(assets, liabilities, income, expenses, net_profit, ratios)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, "Bank_Report.pdf", "application/pdf")

        # 6. Advanced Modules
        st.markdown("---")
        st.subheader("🔍 4. Specialized Modules")
        
        with st.expander("Variance Analysis (Month-on-Month)"):
            v_col1, v_col2 = st.columns(2)
            f1 = v_col1.file_uploader("Month 1 CSV", type="csv")
            f2 = v_col2.file_uploader("Month 2 CSV", type="csv")
            if f1 and f2:
                v_df = calculate_variance(load_trial_balance(f1), load_trial_balance(f2))
                st.dataframe(v_df, use_container_width=True)

        with st.expander("NPA Classification (RBI Rules)"):
            loan_file = st.file_uploader("Upload Loan Data", type="csv", key="npa_loan")
            if loan_file:
                l_df = pd.read_csv(loan_file)
                npa_res = classify_npa(l_df)
                st.dataframe(npa_res, use_container_width=True)
                st.metric("Total Provision Required", f"₹{npa_res['provision_required'].sum():,.2f}")