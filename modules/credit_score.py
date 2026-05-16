def calculate_credit_score(summary):
    score = 0
    breakdown = {}

    # 1. Income stability (max 25 points)
    salary_months = summary.get('salary_months_detected', 0)
    if salary_months >= 6:
        pts = 25
    elif salary_months >= 3:
        pts = 15
    else:
        pts = 5
    score += pts
    breakdown['Income Stability'] = {
        'score': pts, 'max': 25,
        'detail': f"{salary_months} months of regular salary detected"}

    # 2. DSCR (max 25 points)
    dscr = summary.get('dscr', 0)
    if dscr >= 2.5:
        pts = 25
    elif dscr >= 2.0:
        pts = 20
    elif dscr >= 1.5:
        pts = 15
    elif dscr >= 1.0:
        pts = 8
    else:
        pts = 0
    score += pts
    breakdown['Debt Service Coverage'] = {
        'score': pts, 'max': 25,
        'detail': f"DSCR of {dscr:.2f} (ideal is above 1.5)"}

    # 3. Cash flow (max 20 points)
    net_flow = summary.get('net_flow', 0)
    if net_flow > 0:
        pts = 20
    elif net_flow > -10000:
        pts = 10
    else:
        pts = 0
    score += pts
    breakdown['Cash Flow'] = {
        'score': pts, 'max': 20,
        'detail': f"Net flow: Rs. {net_flow:,.2f}"}

    # 4. Cash withdrawal behaviour (max 15 points)
    cash_pct = summary.get('cash_withdrawal_percent', 0)
    if cash_pct < 10:
        pts = 15
    elif cash_pct < 20:
        pts = 10
    elif cash_pct < 30:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown['Cash Withdrawal Behaviour'] = {
        'score': pts, 'max': 15,
        'detail': f"{cash_pct:.1f}% of debits are cash withdrawals"}

    # 5. Minimum balance (max 15 points)
    min_bal = summary.get('min_balance', 0)
    if min_bal >= 10000:
        pts = 15
    elif min_bal >= 5000:
        pts = 10
    elif min_bal >= 0:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown['Balance Maintenance'] = {
        'score': pts, 'max': 15,
        'detail': f"Minimum balance: Rs. {min_bal:,.2f}"}

    # Rating
    if score >= 85:
        rating = "EXCELLENT"
        color = "green"
        recommendation = "Strong candidate. Loan may be approved."
    elif score >= 70:
        rating = "GOOD"
        color = "blue"
        recommendation = "Good candidate. Approve with standard terms."
    elif score >= 55:
        rating = "AVERAGE"
        color = "orange"
        recommendation = "Average profile. Approve with caution and collateral."
    elif score >= 40:
        rating = "WEAK"
        color = "red"
        recommendation = "Weak profile. Detailed scrutiny required."
    else:
        rating = "POOR"
        color = "darkred"
        recommendation = "High risk. Not recommended for approval."

    return score, rating, color, recommendation, breakdown