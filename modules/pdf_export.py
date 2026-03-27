from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import matplotlib.pyplot as plt
import datetime
import io

def make_bar_chart(total_income, total_expenses):
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(['Income', 'Expenses'], [total_income, total_expenses],
           color=['#1a3c5e', '#e74c3c'])
    ax.set_title('Income vs Expenses')
    ax.set_ylabel('Amount (Rs.)')
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}M'))
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf

def make_pie_chart(expenses):
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.pie(expenses['debit'], labels=expenses['gl_name'],
           autopct='%1.1f%%', startangle=90)
    ax.set_title('Expense Breakdown')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf

def generate_pdf(assets, liabilities, income, expenses,
                 net_profit, ratios=None,
                 filepath="outputs/financial_report.pdf"):

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  fontSize=18,
                                  textColor=colors.HexColor('#1a3c5e'),
                                  alignment=TA_CENTER, spaceAfter=6)
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
                                     fontSize=10, textColor=colors.grey,
                                     alignment=TA_CENTER, spaceAfter=20)
    section_style = ParagraphStyle('section', parent=styles['Heading2'],
                                    fontSize=13,
                                    textColor=colors.HexColor('#1a3c5e'),
                                    spaceBefore=16, spaceAfter=8)

    today = datetime.date.today().strftime("%d %B %Y")
    elements.append(Paragraph("Bank Financial Report", title_style))
    elements.append(Paragraph(f"Generated on {today}", subtitle_style))

    # --- P&L Table ---
    elements.append(Paragraph("Profit & Loss Statement", section_style))
    pl_data = [["GL Name", "Amount (Rs.)"]]
    for _, row in income.iterrows():
        pl_data.append([row['gl_name'], f"{row['credit']:,.2f}"])
    pl_data.append(["", ""])
    for _, row in expenses.iterrows():
        pl_data.append([row['gl_name'], f"{row['debit']:,.2f}"])
    pl_data.append(["Net Profit", f"{net_profit:,.2f}"])

    pl_table = Table(pl_data, colWidths=[4*inch, 2.5*inch])
    pl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3c5e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2),
         [colors.HexColor('#f0f4f8'), colors.white]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4edda')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(pl_table)
    elements.append(Spacer(1, 0.2*inch))

    # --- Balance Sheet Table ---
    elements.append(Paragraph("Balance Sheet", section_style))
    bs_data = [["GL Name", "Amount (Rs.)"]]
    bs_data.append(["ASSETS", ""])
    for _, row in assets.iterrows():
        bs_data.append([row['gl_name'], f"{row['debit']:,.2f}"])
    bs_data.append(["LIABILITIES & CAPITAL", ""])
    for _, row in liabilities.iterrows():
        bs_data.append([row['gl_name'], f"{row['credit']:,.2f}"])
    bs_data.append(["Net Profit (current year)", f"{net_profit:,.2f}"])

    bs_table = Table(bs_data, colWidths=[4*inch, 2.5*inch])
    bs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3c5e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2),
         [colors.HexColor('#f0f4f8'), colors.white]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4edda')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(bs_table)
    elements.append(Spacer(1, 0.2*inch))

    # --- Ratios Table ---
    if ratios:
        elements.append(Paragraph("Key Financial Ratios", section_style))
        ratio_data = [["Ratio", "Value"]]
        for name, value in ratios.items():
            ratio_data.append([name, f"{value}%"])
        ratio_table = Table(ratio_data, colWidths=[4*inch, 2.5*inch])
        ratio_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3c5e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#f0f4f8'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(ratio_table)
        elements.append(Spacer(1, 0.2*inch))

    # --- Charts ---
    elements.append(Paragraph("Financial Charts", section_style))
    bar_buf = make_bar_chart(income['credit'].sum(), expenses['debit'].sum())
    pie_buf = make_pie_chart(expenses)
    chart_table = Table([
        [Image(bar_buf, width=3*inch, height=2*inch),
         Image(pie_buf, width=3*inch, height=2*inch)]
    ], colWidths=[3.5*inch, 3.5*inch])
    elements.append(chart_table)

    doc.build(elements)
    return filepath