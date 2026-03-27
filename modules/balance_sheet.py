def generate_balance_sheet(assets, liabilities, net_profit):
    total_assets = assets['debit'].sum()
    total_liabilities = liabilities['credit'].sum() + net_profit

    print("\n========================================")
    print("           BALANCE SHEET                ")
    print("========================================")

    print("\n--- Assets ---")
    for _, row in assets.iterrows():
        print(f"  {row['gl_name']:<35} Rs. {row['debit']:>12,.2f}")
    print(f"\n  {'Total Assets':<35} Rs. {total_assets:>12,.2f}")

    print("\n--- Liabilities & Capital ---")
    for _, row in liabilities.iterrows():
        print(f"  {row['gl_name']:<35} Rs. {row['credit']:>12,.2f}")
    print(f"  {'Net Profit (current year)':<35} Rs. {net_profit:>12,.2f}")
    print(f"\n  {'Total Liabilities & Capital':<35} Rs. {total_liabilities:>12,.2f}")

    print("\n----------------------------------------")
    if round(total_assets) == round(total_liabilities):
        print("  Balance sheet BALANCES correctly!")
    else:
        difference = total_assets - total_liabilities
        print(f"  WARNING: Difference of Rs. {difference:,.2f} found!")
    print("========================================\n")

    return total_assets, total_liabilities