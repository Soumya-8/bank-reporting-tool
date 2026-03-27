import pandas as pd

def calculate_variance(df1, df2):
    merged = pd.merge(
        df1, df2,
        on='gl_code',
        suffixes=('_m1', '_m2'),
        how='outer'
    ).fillna(0)

    merged['variance'] = merged['credit_m2'] - merged['credit_m1']
    merged['percent_change'] = merged.apply(
        lambda x: (x['variance'] / x['credit_m1'] * 100)
        if x['credit_m1'] != 0 else 0,
        axis=1
    )

    return merged[['gl_code', 'gl_name_m1', 'credit_m1', 'credit_m2', 'variance', 'percent_change']]