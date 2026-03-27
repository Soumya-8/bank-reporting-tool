def generate_pl(income, expenses):
    total_income = income['credit'].sum()
    total_expenses = expenses['debit'].sum()
    net_profit = total_income - total_expenses

    print("\n========================================")
    print("         PROFIT & LOSS STATEMENT        ")
    print("========================================")

    print("\n--- Income ---")
    for _, row in income.iterrows():
        print(f"  {row['gl_name']:<35} Rs. {row['credit']:>12,.2f}")
    print(f"\n  {'Total Income':<35} Rs. {total_income:>12,.2f}")

    print("\n--- Expenses ---")
    for _, row in expenses.iterrows():
        print(f"  {row['gl_name']:<35} Rs. {row['debit']:>12,.2f}")
    print(f"\n  {'Total Expenses':<35} Rs. {total_expenses:>12,.2f}")

    print("\n----------------------------------------")
    if net_profit >= 0:
        print(f"  {'Net Profit':<35} Rs. {net_profit:>12,.2f}")
    else:
        print(f"  {'Net Loss':<35} Rs. {abs(net_profit):>12,.2f}")
    print("========================================\n")

    return total_income, total_expenses, net_profit