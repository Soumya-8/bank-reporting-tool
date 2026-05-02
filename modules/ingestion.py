import pandas as pd

def load_trial_balance(filepath):
    if hasattr(filepath, 'name'):
        filename = filepath.name
    else:
        filename = str(filepath)

    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    df.columns = df.columns.str.strip().str.lower()

    required = ['gl_code', 'gl_name', 'debit', 'credit']
    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Missing column: '{col}'. "
                f"Required columns: gl_code, gl_name, debit, credit")

    df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
    df['gl_code'] = pd.to_numeric(df['gl_code'], errors='coerce').fillna(0)

    return df


def categorise(df):
    assets = df[df['gl_code'].between(1000, 3999)].copy()
    liabilities = df[df['gl_code'].between(4000, 4999)].copy()
    income = df[df['gl_code'].between(5000, 5999)].copy()
    expenses = df[df['gl_code'].between(6000, 6999)].copy()
    return assets, liabilities, income, expenses