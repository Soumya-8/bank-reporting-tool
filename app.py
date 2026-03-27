from modules.ingestion import load_trial_balance, categorise
from modules.pl_engine import generate_pl
from modules.balance_sheet import generate_balance_sheet

df = load_trial_balance("data/trial_balance.csv")
assets, liabilities, income, expenses = categorise(df)
total_income, total_expenses, net_profit = generate_pl(income, expenses)
generate_balance_sheet(assets, liabilities, net_profit)