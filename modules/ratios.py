def calculate_ratios(total_income, total_expenses, net_profit, assets, liabilities):

    total_assets = assets['debit'].sum()

    deposits = liabilities[liabilities['gl_name'].str.contains('Deposit', case=False)]
    total_deposits = deposits['credit'].sum()

    loans = assets[assets['gl_name'].str.contains('Loans', case=False)]
    total_loans = loans['debit'].sum()

    interest_income = total_income
    interest_expense = total_expenses

    roa = (net_profit / total_assets) * 100 if total_assets else 0
    cost_to_income = (total_expenses / total_income) * 100 if total_income else 0
    credit_to_deposit = (total_loans / total_deposits) * 100 if total_deposits else 0
    nim = ((interest_income - interest_expense) / total_assets) * 100 if total_assets else 0

    ratios = {
        "Return on Assets (ROA) %": round(roa, 2),
        "Cost to Income Ratio %": round(cost_to_income, 2),
        "Credit to Deposit Ratio %": round(credit_to_deposit, 2),
        "Net Interest Margin (NIM) %": round(nim, 2),
    }

    return ratios


def interpret_ratios(ratios):
    insights = []

    if ratios["Return on Assets (ROA) %"] < 1:
        insights.append("ROA is below 1% — bank is not generating enough profit from its assets.")
    else:
        insights.append("ROA is healthy — bank is generating good profit from its assets.")

    if ratios["Cost to Income Ratio %"] > 60:
        insights.append("Cost to Income is high — expenses are eating too much of the income.")
    else:
        insights.append("Cost to Income is under control — bank is operating efficiently.")

    if ratios["Credit to Deposit Ratio %"] > 75:
        insights.append("Credit to Deposit ratio exceeds RBI's recommended 75% limit.")
    else:
        insights.append("Credit to Deposit ratio is within RBI recommended limits.")

    if ratios["Net Interest Margin (NIM) %"] < 2:
        insights.append("NIM is low — bank needs to improve its lending vs deposit rate spread.")
    else:
        insights.append("NIM is healthy — good spread between lending and deposit rates.")

    return insights