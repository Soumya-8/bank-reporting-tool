import pandas as pd
import re
import io

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


def clean_amount(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    val_str = re.sub(r'[,\s₹Rs]', '', val_str)
    val_str = val_str.replace('(', '-').replace(')', '')
    try:
        return float(val_str)
    except Exception:
        return 0.0


def find_column(columns, keywords):
    columns_lower = [c.lower().strip() for c in columns]
    for keyword in keywords:
        for i, col in enumerate(columns_lower):
            if keyword in col:
                return columns[i]
    return None


def parse_pdf_statement(filepath):
    try:
        import pdfplumber
        all_rows = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 1:
                        for row in table:
                            if row and any(cell for cell in row):
                                all_rows.append(row)

        if not all_rows:
            return None

        # Use first row as header
        headers = [str(h).strip() if h else f'col_{i}'
                   for i, h in enumerate(all_rows[0])]
        data = all_rows[1:]
        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        raise ValueError(f"Could not read PDF: {str(e)}")


def load_bank_statement(filepath):
    if hasattr(filepath, 'name'):
        filename = filepath.name
    else:
        filename = str(filepath)

    filename_lower = filename.lower()

    # Load based on file type
    if filename_lower.endswith('.pdf'):
        df = parse_pdf_statement(filepath)
        if df is None:
            raise ValueError(
                "Could not extract tables from PDF. "
                "Please try converting to Excel or CSV.")
    elif filename_lower.endswith('.xlsx') or filename_lower.endswith('.xls'):
        # Try different header rows
        df = None
        for header_row in [0, 1, 2, 3, 4]:
            try:
                temp = pd.read_excel(filepath, header=header_row)
                # Check if this looks like a bank statement
                cols_lower = [str(c).lower() for c in temp.columns]
                has_date = any(x in ' '.join(cols_lower)
                               for x in ['date', 'dt', 'txn'])
                has_amount = any(x in ' '.join(cols_lower)
                                 for x in ['debit', 'credit', 'amount',
                                           'withdrawal', 'deposit', 'dr',
                                           'cr'])
                if has_date and has_amount:
                    df = temp
                    break
            except Exception:
                continue
        if df is None:
            df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    # Remove completely empty rows
    df = df.dropna(how='all')

    # Find columns flexibly
    cols = list(df.columns)

    date_col = find_column(cols,
        ['date', 'dt', 'txn date', 'value date', 'trans date'])
    narration_col = find_column(cols,
        ['narration', 'description', 'particulars', 'details',
         'remarks', 'transaction', 'detail', 'ref'])
    debit_col = find_column(cols,
        ['debit', 'dr', 'withdrawal', 'withdrawl', 'debit amount',
         'dr amount', 'withdrawal amount'])
    credit_col = find_column(cols,
        ['credit', 'cr', 'deposit', 'credit amount', 'cr amount',
         'deposit amount'])
    balance_col = find_column(cols,
        ['balance', 'bal', 'closing', 'closing balance', 'running'])

    # If debit/credit not found separately, look for single amount column
    amount_col = None
    if not debit_col and not credit_col:
        amount_col = find_column(cols,
            ['amount', 'amt', 'transaction amount'])

    # Build standardised dataframe
    result = pd.DataFrame()

    if date_col:
        result['date'] = pd.to_datetime(
            df[date_col], errors='coerce', dayfirst=True)
    else:
        result['date'] = pd.NaT

    if narration_col:
        result['narration'] = df[narration_col].astype(str)
    else:
        # Try to find any text column
        for col in cols:
            if df[col].dtype == object and col not in [date_col]:
                result['narration'] = df[col].astype(str)
                break
        else:
            result['narration'] = 'Unknown'

    if debit_col:
        result['debit'] = df[debit_col].apply(clean_amount)
    elif amount_col:
        result['debit'] = df[amount_col].apply(
            lambda x: clean_amount(x) if clean_amount(x) < 0 else 0)
    else:
        result['debit'] = 0.0

    if credit_col:
        result['credit'] = df[credit_col].apply(clean_amount)
    elif amount_col:
        result['credit'] = df[amount_col].apply(
            lambda x: clean_amount(x) if clean_amount(x) > 0 else 0)
    else:
        result['credit'] = 0.0

    if balance_col:
        result['balance'] = df[balance_col].apply(clean_amount)
    else:
        result['balance'] = 0.0

    # Remove rows where both debit and credit are 0
    result = result[
        (result['debit'] != 0) | (result['credit'] != 0)].copy()

    # Add category
    result['category'] = result['narration'].apply(
        categorise_transaction)

    result = result.reset_index(drop=True)
    return result


def analyse_bank_statement(df):
    # Safety check
    if 'credit' not in df.columns:
        df['credit'] = 0.0
    if 'debit' not in df.columns:
        df['debit'] = 0.0
    if 'balance' not in df.columns:
        df['balance'] = 0.0
    if 'category' not in df.columns:
        df['category'] = 'Others'

    total_credits = df['credit'].sum()
    total_debits = df['debit'].sum()
    net_flow = total_credits - total_debits

    # Monthly summary
    if 'date' in df.columns and df['date'].notna().any():
        df['month'] = df['date'].dt.to_period('M').astype(str)
        monthly = df.groupby('month').agg(
            Total_Credits=('credit', 'sum'),
            Total_Debits=('debit', 'sum')
        ).reset_index()
        monthly['Net_Flow'] = (monthly['Total_Credits'] -
                               monthly['Total_Debits'])
        num_months = max(1, len(monthly))
    else:
        monthly = pd.DataFrame()
        num_months = 1

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
    avg_salary = (salary_txns['credit'].mean()
                  if len(salary_txns) > 0 else 0)
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
    avg_balance = df['balance'].mean() if df['balance'].sum() > 0 else 0
    min_balance = df['balance'].min() if df['balance'].sum() > 0 else 0
    max_balance = df['balance'].max() if df['balance'].sum() > 0 else 0

    # Monthly income estimate
    monthly_income = (avg_salary if avg_salary > 0
                      else total_credits / num_months)
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
            f"Low DSCR of {dscr:.2f} — repayment capacity is weak")
    if salary_months < 3 and avg_salary > 0:
        red_flags.append(
            "Less than 3 months of salary credits detected")
    if total_credits == 0:
        red_flags.append(
            "No credit transactions detected — check file format")

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