from modules.ingestion import load_trial_balance, categorise
from modules.pl_engine import generate_pl

df = load_trial_balance("data/trial_balance.csv")
assets, liabilities, income, expenses = categorise(df)
generate_pl(income, expenses)