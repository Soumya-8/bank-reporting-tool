import pandas as pd

def classify_npa(loans_df):
    required = ['loan_id', 'borrower_name', 'loan_amount', 'days_overdue']
    for col in required:
        if col not in loans_df.columns:
            raise ValueError(f"Missing column in loan data: {col}")

    def get_status(days):
        if days < 90:
            return 'Standard'
        elif days < 180:
            return 'Sub-Standard'
        elif days < 360:
            return 'Doubtful'
        else:
            return 'Loss'

    def get_provision(row):
        if row['status'] == 'Standard':
            return round(row['loan_amount'] * 0.0025, 2)
        elif row['status'] == 'Sub-Standard':
            return round(row['loan_amount'] * 0.10, 2)
        elif row['status'] == 'Doubtful':
            return round(row['loan_amount'] * 0.50, 2)
        else:
            return round(row['loan_amount'] * 1.00, 2)

    loans_df = loans_df.copy()
    loans_df['status'] = loans_df['days_overdue'].apply(get_status)
    loans_df['npa'] = loans_df['status'] != 'Standard'
    loans_df['provision_required'] = loans_df.apply(get_provision, axis=1)

    return loans_df