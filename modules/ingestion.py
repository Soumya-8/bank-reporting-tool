import pandas as pd

def load_trial_balance(filepath):
    df = pd.read_csv(filepath)
    print("File loaded successfully!")
    print(f"Total GL entries found: {len(df)}")
    print("\nFirst few rows:")
    print(df.head())
    return df

def categorise(df):
    assets = df[df['gl_code'].between(1000, 3999)]
    liabilities = df[df['gl_code'].between(4000, 4999)]
    income = df[df['gl_code'].between(5000, 5999)]
    expenses = df[df['gl_code'].between(6000, 6999)]

    print("\n--- Categorisation Summary ---")
    print(f"Asset entries:     {len(assets)}")
    print(f"Liability entries: {len(liabilities)}")
    print(f"Income entries:    {len(income)}")
    print(f"Expense entries:   {len(expenses)}")

    return assets, liabilities, income, expenses