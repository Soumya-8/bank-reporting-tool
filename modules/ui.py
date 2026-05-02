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


def styled_df(df, col_rename):
    return df.rename(columns=col_rename).style.set_properties(**{
        'background-color': '#f0f4f8',
        'color': '#1a2b3c',
        'border': '1px solid #c0cfe0',
        'font-size': '13px'
    }).set_table_styles([{
        'selector': 'thead th',
        'props': [
            ('background-color', '#1a3c5e'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('font-size', '13px')
        ]
    }])


def highlight_npa(row):
    if row['status'] == 'Loss':
        return ['background-color: #fde8e8; color: #7a0000'] * len(row)
    elif row['status'] == 'Doubtful':
        return ['background-color: #fff3cd; color: #5a3e00'] * len(row)
    elif row['status'] == 'Sub-Standard':
        return ['background-color: #fff8e1; color: #4a3800'] * len(row)
    else:
        return ['background-color: #e8f5e9; color: #1a3c1a'] * len(row)


def highlight_variance(row):
    debit_change = row.get('Debit Change', 0)
    credit_change = row.get('Credit Change', 0)
    if debit_change > 0 or credit_change > 0:
        return ['background-color: #e8f5e9; color: #1a3c1a'] * len(row)
    elif debit_change < 0 or credit_change < 0:
        return ['background-color: #fde8e8; color: #7a0000'] * len(row)
    else:
        return ['background-color: #f0f4f8; color: #1a2b3c'] * len(row)


def run_app():
    # Header
    st.markdown("""
        <div style="background-color:#1a3c5e;padding:15px;
                    border-radius:10px;margin-bottom:25px;">
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

    # 1. Upload
    st.subheader("📁 1. Upload Trial Balance")
    uploaded_file = st.file_uploader("Choose Trial Balance CSV", type="csv")

    if uploaded_file:
        df = load_trial_balance(uploaded_file)
        assets, liabilities, income, expenses = categorise(df)
        total_income, total_expenses, net_profit = generate_pl(
            income, expenses)

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
            st.markdown("**Income Items**")
            st.dataframe(
                styled_df(
                    income[['gl_name', 'credit']],
                    {'gl_name': 'Name', 'credit': 'Amount (Rs.)'}),
                use_container_width=True)
            st.markdown("**Expense Items**")
            st.dataframe(
                styled_df(
                    expenses[['gl_name', 'debit']],
                    {'gl_name': 'Name', 'debit': 'Amount (Rs.)'}),
                use_container_width=True)

        with t2:
            st.markdown("**Assets**")
            st.dataframe(
                styled_df(
                    assets[['gl_name', 'debit']],
                    {'gl_name': 'Name', 'debit': 'Amount (Rs.)'}),
                use_container_width=True)
            st.markdown("**Liabilities & Capital**")
            st.dataframe(
                styled_df(
                    liabilities[['gl_name', 'credit']],
                    {'gl_name': 'Name', 'credit': 'Amount (Rs.)'}),
                use_container_width=True)

        # 4. Ratios & Insights
        st.markdown("---")
        st.subheader("📊 3. Analysis & Insights")
        ratios = calculate_ratios(
            total_income, total_expenses, net_profit, assets, liabilities)
        insights = interpret_ratios(ratios)

        r_cols = st.columns(4)
        for i, (name, val) in enumerate(ratios.items()):
            r_cols[i].metric(name, f"{val}%")

        for insight in insights:
            if any(x in insight.lower() for x in
                   ["low", "high", "not healthy", "exceeds", "not"]):
                st.warning(insight)
            else:
                st.success(insight)

        # Charts
        st.markdown("---")
        st.subheader("📉 4. Financial Charts")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)

        # Bar chart
        ax1.bar(["Income", "Expenses"],
                [total_income, total_expenses],
                color=['#1a3c5e', '#e74c3c'],
                width=0.4, edgecolor='white')
        ax1.set_title('Income vs Expenses',
                      fontweight='bold', color='#1a3c5e',
                      fontsize=11, pad=10)
        ax1.set_ylabel('Amount (Rs.)', fontsize=9)
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(
                lambda x, _: f'{x/1_000_000:.1f}M'))
        ax1.tick_params(labelsize=9)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_facecolor('#f9fbfd')

        # Pie chart
        wedge_colors = ['#1a3c5e', '#2e6da4', '#4a90d9',
                        '#7eb8e8', '#b8d4f0']
        wedges, texts = ax2.pie(
            expenses['debit'],
            labels=None,
            startangle=90,
            colors=wedge_colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            radius=0.75)
        ax2.legend(
            wedges,
            [f"{row['gl_name']} "
             f"({row['debit']/expenses['debit'].sum()*100:.1f}%)"
             for _, row in expenses.iterrows()],
            loc='lower center',
            bbox_to_anchor=(0.5, -0.22),
            fontsize=8,
            frameon=False)
        ax2.set_title('Expense Breakdown',
                      fontweight='bold', color='#1a3c5e',
                      fontsize=11, pad=10)

        fig.patch.set_facecolor('white')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        # 5. PDF Export
        st.markdown("---")
        st.subheader("📄 5. Download Report")
        if st.button("Generate PDF Report"):
            pdf_buffer = generate_pdf(
                assets, liabilities, income,
                expenses, net_profit, ratios)
            st.download_button(
                "Download PDF",
                pdf_buffer,
                "Bank_Report.pdf",
                "application/pdf")

        # 6. Variance Analysis
        st.markdown("---")
        st.subheader("🔍 6. Specialized Modules")

        with st.expander("Variance Analysis (Month-on-Month)"):
            v_col1, v_col2 = st.columns(2)
            f1 = v_col1.file_uploader(
                "Month 1 CSV", type="csv", key="var1")
            f2 = v_col2.file_uploader(
                "Month 2 CSV", type="csv", key="var2")
            if f1 and f2:
                v_df = calculate_variance(
                    load_trial_balance(f1),
                    load_trial_balance(f2))
                styled_variance = v_df.style\
                    .apply(highlight_variance, axis=1)\
                    .set_table_styles([{
                        'selector': 'thead th',
                        'props': [
                            ('background-color', '#1a3c5e'),
                            ('color', 'white'),
                            ('font-weight', 'bold'),
                            ('font-size', '13px')
                        ]
                    }])
                st.dataframe(styled_variance, use_container_width=True)
                st.info("Green = increased. Red = decreased.")

        with st.expander("NPA Classification (RBI Rules)"):
            loan_file = st.file_uploader(
                "Upload Loan Data CSV", type="csv", key="npa_loan")
            if loan_file:
                l_df = pd.read_csv(loan_file)
                npa_res = classify_npa(l_df)
                styled_npa = npa_res.style\
                    .apply(highlight_npa, axis=1)\
                    .set_table_styles([{
                        'selector': 'thead th',
                        'props': [
                            ('background-color', '#1a3c5e'),
                            ('color', 'white'),
                            ('font-weight', 'bold'),
                            ('font-size', '13px')
                        ]
                    }])
                st.dataframe(styled_npa, use_container_width=True)
                col1, col2 = st.columns(2)
                npa_count = len(
                    npa_res[npa_res['status'] != 'Standard'])
                total_provision = npa_res['provision_required'].sum()
                col1.metric("Total NPAs Detected", npa_count)
                col2.metric("Total Provision Required",
                            f"₹{total_provision:,.2f}")
                st.markdown("**NPA Summary by Category**")
                summary = npa_res.groupby('status').agg(
                    Count=('loan_id', 'count'),
                    Total_Amount=('loan_amount', 'sum'),
                    Total_Provision=('provision_required', 'sum')
                ).reset_index()
                st.dataframe(
                    styled_df(summary, {
                        'status': 'Status',
                        'Count': 'Count',
                        'Total_Amount': 'Total Amount (Rs.)',
                        'Total_Provision': 'Provision Required (Rs.)'
                    }),
                    use_container_width=True)

        st.markdown("""
        <div style="text-align:center; color:#4a6a8a; font-size:0.8rem;
                    margin-top:2rem; padding-top:1rem;
                    border-top:1px solid #c0cfe0;">
            BankReport AI v1.0 — VyaparScore |
            Built for cooperative and urban banks in India
        </div>
        """, unsafe_allow_html=True)