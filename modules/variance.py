import pandas as pd

def calculate_variance(df1, df2):
    df1 = df1[['gl_code', 'gl_name', 'debit', 'credit']].copy()
    df2 = df2[['gl_code', 'gl_name', 'debit', 'credit']].copy()

    merged = pd.merge(df1, df2, on=['gl_code', 'gl_name'],
                      suffixes=('_m1', '_m2'), how='outer').fillna(0)

    merged['debit_change'] = merged['debit_m2'] - merged['debit_m1']
    merged['credit_change'] = merged['credit_m2'] - merged['credit_m1']

    merged['debit_change_%'] = merged.apply(
        lambda r: round((r['debit_change'] / r['debit_m1']) * 100, 1)
        if r['debit_m1'] != 0 else 0, axis=1)

    merged['credit_change_%'] = merged.apply(
        lambda r: round((r['credit_change'] / r['credit_m1']) * 100, 1)
        if r['credit_m1'] != 0 else 0, axis=1)

    result = merged[['gl_code', 'gl_name',
                      'debit_m1', 'debit_m2', 'debit_change', 'debit_change_%',
                      'credit_m1', 'credit_m2', 'credit_change', 'credit_change_%']]

    result.columns = ['GL Code', 'GL Name',
                       'Debit M1', 'Debit M2', 'Debit Change', 'Debit Change %',
                       'Credit M1', 'Credit M2', 'Credit Change', 'Credit Change %']
    return result