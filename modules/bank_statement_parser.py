import pandas as pd
import re


# Transaction category keywords
CATEGORIES = {
    'Salary': ['salary', 'sal cr', 'sal credit', 'payroll', 'wages'],
    'EMI / Loan': ['emi', 'loan', 'home loan', 'car loan', 'personal loan'],
    'Rent': ['rent', 'house rent', 'rental'],
    'Utilities': ['electricity', 'water', 'gas', 'telephone', 'mobile',
                  'broadband', 'internet', 'bill'],
    'Insurance': ['lic', 'insurance', 'premium', 'policy'],
    'Investment': ['sip', 'mutual fund', 'mf', 'nsc', 'ppf', 'fd',
                   'fixed deposit', 'rd'],
    'Cash Withdrawal': ['atm', 'cash withdrawal', 'cash wd'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'shopping', 'mall'],
    'Food': ['swiggy', 'zomato', 'restaurant', 'food', 'hotel'],
    'Medical': ['medical', 'hospital', 'pharmacy', 'chemist', 'health'],
    'Fuel': ['petrol', 'diesel', 'fuel', 'hp', 'bharat petroleum'],
    'Interest': ['interest credit', 'int cr', 'interest earned'],
    'Transfer In': ['neft cr', 'imps cr', 'rtgs cr', 'upi cr',
                    'transfer in'],
    'Transfer Out': ['neft dr', 'imps dr', 'rtgs dr', 'transfer out'],
    'Grocery': ['grocery', 'supermarket', 'bigbasket', 'blinkit',
                'zepto', 'dmart'],
}


def categorise_transaction(narration):
    narration_lower = str(narration).lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in narration_lower:
                return category
    return 'Others'


def load_bank_statement(filepath):
    if hasattr(filepath, 'name'):
        filename = filepath.name
    else:
        filename = str(filepath)

    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower()

    # Try to find required columns flexibly
    col_map = {}
    for col in df.columns:
        if any(x in col for x in ['date', 'dt', 'txn date']):
            col_map['date'] = col
        elif any(x in col for x in ['narration', 'description',
                                     'particulars', 'details', 'remarks']):
            col_map['narration'] = col
        elif any(x in col for x in ['debit', 'dr', 'withdrawal',
                                     'withdrawl']):
            col_map['debit'] = col
        elif any(x in col for x in ['credit', 'cr', 'deposit']):
            col_map['credit'] = col
        elif any(x in col for x in ['balance', 'bal', 'closing']):
            col_map['balance'] = col

    # Rename to standard names
    df = df.rename(columns={v: k for k, v in col_map.items()})

    # Convert to numeric
    for col in ['debit', 'credit', 'balance']:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', ''),
                errors='coerce').fillna(0)

    # Add category
    if 'narration' in df.columns:
        df['category'] = df['narration'].apply(categorise_transaction)

    return df


def analyse_bank_statement(df):
    total_credits = df['credit'].sum()
    total_debits = df['debit'].sum()
    net_flow = total_credits - total_debits

    # Monthly summary
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce',
                                     dayfirst=True)
        df['month'] = df['date'].dt.to_period('M').astype(str)
        monthly = df.groupby('month').agg(
            Total_Credits=('credit', 'sum'),
            Total_Debits=('debit', 'sum')
        ).reset_index()
        monthly['Net_Flow'] = (monthly['Total_Credits'] -
                               monthly['Total_Debits'])
    else:
        monthly = pd.DataFrame()

    # Category wise spending
    category_summary = df[df['debit'] > 0].groupby('category').agg(
        Total_Spent=('debit', 'sum'),
        Transaction_Count=('debit', 'count')
    ).reset_index().sort_values('Total_Spent', ascending=False)

    # Credit sources
    credit_summary = df[df['credit'] > 0].groupby('category').agg(
        Total_Received=('credit', 'sum'),
        Transaction_Count=('credit', 'count')
    ).reset_index().sort_values('Total_Received', ascending=False)

    # Salary detection
    salary_txns = df[df['category'] == 'Salary']
    avg_salary = salary_txns['credit'].mean() if len(salary_txns) > 0 else 0
    salary_months = len(salary_txns)

    # EMI detection
    emi_txns = df[df['category'] == 'EMI / Loan']
    total_emi = emi_txns['debit'].sum()
    avg_emi = emi_txns['debit'].mean() if len(emi_txns) > 0 else 0

    # Cash withdrawal analysis
    cash_txns = df[df['category'] == 'Cash Withdrawal']
    total_cash = cash_txns['debit'].sum()
    cash_percent = (total_cash / total_debits * 100
                    if total_debits > 0 else 0)

    # Balance stats
    if 'balance' in df.columns:
        avg_balance = df['balance'].mean()
        min_balance = df['balance'].min()
        max_balance = df['balance'].max()
    else:
        avg_balance = min_balance = max_balance = 0

    # DSCR (Debt Service Coverage Ratio)
    monthly_income = avg_salary if avg_salary > 0 else (
        total_credits / max(1, len(
            df['month'].unique()) if 'month' in df.columns else 1))
    dscr = (monthly_income / avg_emi) if avg_emi > 0 else 0

    # Red flags
    red_flags = []
    if cash_percent > 30:
        red_flags.append(
            f"High cash withdrawals — {cash_percent:.1f}% of total debits")
    if min_balance < 0:
        red_flags.append("Account went into negative balance")
    if dscr < 1.5 and avg_emi > 0:
        red_flags.append(
            f"Low DSCR of {dscr:.2f} — loan repayment capacity is weak")
    if salary_months < 3:
        red_flags.append("Less than 3 months of salary credits detected")

    summary = {
        'total_credits': total_credits,
        'total_debits': total_debits,
        'net_flow': net_flow,
        'avg_monthly_salary': avg_salary,
        'salary_months_detected': salary_months,
        'total_emi': total_emi,
        'avg_monthly_emi': avg_emi,
        'total_cash_withdrawal': total_cash,
        'cash_withdrawal_percent': cash_percent,
        'avg_balance': avg_balance,
        'min_balance': min_balance,
        'max_balance': max_balance,
        'dscr': dscr,
        'red_flags': red_flags
    }

    return summary, monthly, category_summary, credit_summary