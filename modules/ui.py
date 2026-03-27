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


def apply_styles():
    st.markdown("""
    <style>
    .stApp { background-color: #eef2f7; }
    html, body, [class*="css"] { color: #1a2b3c !important; }

    .main-header {
        background: linear-gradient(90deg, #1a3c5e, #2e6da4);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p { color: #b8d4f0; font-size: 0.9rem; margin: 0; }

    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #c0cfe0;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    div[data-testid="metric-container"] label {
        color: #2a4a6a !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1a3c5e !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }

    h2, h3 { color: #1a3c5e !important; border-bottom: 2px solid #2e6da4; padding-bottom: 0.3rem; }
    p, label, span, div { color: #1a2b3c; }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #e8f0f8 !important;
        border: 2px dashed #2e6da4 !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: #1a3c5e !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #1a3c5e !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] svg { fill: #2e6da4 !important; }

    .stButton > button {
        background: linear-gradient(90deg, #1a3c5e, #2e6da4);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .stButton > button:hover { opacity: 0.85; color: white !important; }

    .stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid #c0cfe0; }
    [data-testid="stDataFrameResizable"] {
        background: #f0f4f8 !important;
        border-radius: 8px;
        border: 1px solid #c0cfe0 !important;
    }

    section[data-testid="stSidebar"] { background: #1a3c5e !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] code {
        background: #2e6da4 !important;
        color: white !important;
        border-radius: 4px;
        padding: 2px 6px;
    }

    hr { border-color: #c0cfe0; }
    .footer {
        text-align: center;
        color: #4a6a8a;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #c0cfe0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="main-header">
        <div>
            <h1>BankReport AI</h1>
            <p>Automated Financial Reporting for Banks</p>
        </div>
        <div style="color:#b8d4f0; font-size:0.85rem; text-align:right;">
            Powered by Python<br>
            <span style="color:#7ec8e3;">v1.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## Navigation")
        st.markdown("---")
        st.markdown("**Modules**")
        st.markdown("- Financial Statements")
        st.markdown("- Key Ratios")
        st.markdown("- Charts")
        st.markdown("- PDF Export")
        st.markdown("- Variance Analysis")
        st.markdown("- NPA Classification")
        st.markdown("---")
        st.markdown("**How to use**")
        st.markdown("1. Upload trial balance CSV")
        st.markdown("2. View auto-generated reports")
        st.markdown("3. Download PDF")
        st.markdown("---")
        st.markdown("**Supported format**")
        st.code("gl_code, gl_name,\ndebit, credit")


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


def run_app():
    apply_styles()
    render_header()
    render_sidebar()

    st.subheader("Upload Trial Balance")
    uploaded_file = st.file_uploader(
        "Upload your bank's trial balance CSV file", type="csv")

    if uploaded_file is not None:
        df = load_trial_balance(uploaded_file)
        assets, liabilities, income, expenses = categorise(df)
        total_income, total_expenses, net_profit = generate_pl(
            income, expenses)

        st.success(f"File loaded successfully — {len(df)} GL entries found.")

        st.markdown("---")
        st.subheader("Financial Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rs. {total_income:,.0f}")
        col2.metric("Total Expenses", f"Rs. {total_expenses:,.0f}")
        col3.metric("Net Profit", f"Rs. {net_profit:,.0f}",
                    delta=f"{((net_profit/total_income)*100):.1f}% margin")

        st.markdown("---")
        st.subheader("Profit & Loss Statement")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Income**")
            st.dataframe(
                styled_df(income[['gl_name', 'credit']],
                          {'gl_name': 'Income Head', 'credit': 'Amount (Rs.)'}),
                use_container_width=True)
        with col2:
            st.markdown("**Expenses**")
            st.dataframe(
                styled_df(expenses[['gl_name', 'debit']],
                          {'gl_name': 'Expense Head', 'debit': 'Amount (Rs.)'}),
                use_container_width=True)

        st.markdown("---")
        st.subheader("Balance Sheet")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Assets**")
            st.dataframe(
                styled_df(assets[['gl_name', 'debit']],
                          {'gl_name': 'Asset', 'debit': 'Amount (Rs.)'}),
                use_container_width=True)
        with col2:
            st.markdown("**Liabilities & Capital**")
            st.dataframe(
                styled_df(liabilities[['gl_name', 'credit']],
                          {'gl_name': 'Liability / Capital',
                           'credit': 'Amount (Rs.)'}),
                use_container_width=True)

        st.markdown("---")
        st.subheader("Key Financial Ratios")
        ratios = calculate_ratios(
            total_income, total_expenses, net_profit, assets, liabilities)
        insights = interpret_ratios(ratios)

        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        for i, (name, value) in enumerate(ratios.items()):
            cols[i].metric(name, f"{value}%")

        st.markdown("**CA Insights**")
        for insight in insights:
            if any(w in insight for w in ["not", "high", "exceeds", "low"]):
                st.warning(insight)
            else:
                st.success(insight)

        st.markdown("---")
        st.subheader("Financial Charts")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(['Income', 'Expenses'],
                   [total_income, total_expenses],
                   color=['#1a3c5e', '#e74c3c'],
                   width=0.5, edgecolor='white')
            ax.set_title('Income vs Expenses',
                         fontweight='bold', color='#1a3c5e')
            ax.set_ylabel('Amount (Rs.)')
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}M'))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.patch.set_facecolor('white')
            st.pyplot(fig)

        with col2:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            wedge_colors = ['#1a3c5e', '#2e6da4', '#4a90d9',
                            '#7eb8e8', '#b8d4f0']
            wedges, texts = ax2.pie(
                expenses['debit'],
                labels=None,
                startangle=90,
                colors=wedge_colors,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            ax2.legend(
                wedges,
                [f"{row['gl_name']} "
                 f"({row['debit']/expenses['debit'].sum()*100:.1f}%)"
                 for _, row in expenses.iterrows()],
                loc='lower center',
                bbox_to_anchor=(0.5, -0.35),
                fontsize=8,
                frameon=False)
            ax2.set_title('Expense Breakdown',
                          fontweight='bold', color='#1a3c5e', pad=10)
            fig2.patch.set_facecolor('white')
            plt.tight_layout()
            st.pyplot(fig2)

        st.markdown("---")
        st.subheader("Download Report")
        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf(
                assets, liabilities, income,
                expenses, net_profit, ratios)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Click here to download PDF",
                    data=f,
                    file_name="bank_financial_report.pdf",
                    mime="application/pdf")
            st.success("PDF generated successfully!")

        st.markdown("---")
        st.subheader("Variance Analysis")
        st.markdown(
            "Upload two months of trial balance to compare changes")
        col1, col2 = st.columns(2)
        with col1:
            file1 = st.file_uploader(
                "Month 1 CSV", type="csv", key="m1")
        with col2:
            file2 = st.file_uploader(
                "Month 2 CSV", type="csv", key="m2")
        if file1 and file2:
            df1 = load_trial_balance(file1)
            df2 = load_trial_balance(file2)
            variance_df = calculate_variance(df1, df2)
            st.dataframe(variance_df, use_container_width=True)

        st.markdown("---")
        st.subheader("NPA Classification")
        st.markdown(
            "Upload loan data CSV with columns: "
            "loan_id, borrower_name, loan_amount, days_overdue")
        loan_file = st.file_uploader(
            "Upload Loan Data CSV", type="csv", key="loan")
        if loan_file:
            loans_df = pd.read_csv(loan_file)
            result = classify_npa(loans_df)
            st.dataframe(result, use_container_width=True)
            col1, col2 = st.columns(2)
            npa_count = len(result[result['status'] != 'Standard'])
            total_provision = result['provision_required'].sum()
            col1.metric("Total NPAs detected", npa_count)
            col2.metric("Total Provision Required",
                        f"Rs. {total_provision:,.0f}")

        st.markdown("""
        <div class="footer">
            BankReport AI v1.0 — Built for cooperative and urban banks in India<br>
            For support contact: your@email.com
        </div>
        """, unsafe_allow_html=True)