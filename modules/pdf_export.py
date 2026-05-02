import io
import os
import datetime
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def make_bar_chart(total_income, total_expenses):
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(['Income', 'Expenses'],
           [total_income, total_expenses],
           color=['#1a3c5e', '#e74c3c'],
           width=0.5, edgecolor='white')
    ax.set_title('Income vs Expenses', fontweight='bold',
                 color='#1a3c5e', fontsize=10)
    ax.set_ylabel('Amount (Rs.)', fontsize=8)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}M'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf


def make_pie_chart(expenses):
    fig, ax = plt.subplots(figsize=(4, 2.5))
    wedge_colors = ['#1a3c5e', '#2e6da4', '#4a90d9',
                    '#7eb8e8', '#b8d4f0']
    wedges, texts = ax.pie(
        expenses['debit'],
        labels=None,
        startangle=90,
        colors=wedge_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax.legend(
        wedges,
        [f"{row['gl_name']} "
         f"({row['debit']/expenses['debit'].sum()*100:.1f}%)"
         for _, row in expenses.iterrows()],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.45),
        fontsize=6,
        frameon=False)
    ax.set_title('Expense Breakdown', fontweight='bold',
                 color='#1a3c5e', fontsize=10, pad=8)
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf


def table_style():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3c5e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2),
         [colors.HexColor('#f0f4f8'), colors.white]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4edda')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])


def generate_pdf(assets, liabilities, income, expenses,
                 net_profit, ratios=None):

    # Always use memory buffer — works on both laptop and cloud
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'title', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#1a3c5e'),
        alignment=TA_CENTER, spaceAfter=6)
    subtitle_style = ParagraphStyle(
        'subtitle', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey,
        alignment=TA_CENTER, spaceAfter=20)
    section_style = ParagraphStyle(
        'section', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#1a3c5e'),
        spaceBefore=16, spaceAfter=8)

    today = datetime.date.today().strftime("%d %B %Y")
    elements.append(Paragraph("VyaparScore — Bank Financial Report",
                               title_style))
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
    pl_table.setStyle(table_style())
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
    bs_table.setStyle(table_style())
    elements.append(bs_table)
    elements.append(Spacer(1, 0.2*inch))

    # --- Ratios Table ---
    if ratios:
        elements.append(Paragraph("Key Financial Ratios", section_style))
        ratio_data = [["Ratio", "Value"]]
        for name, value in ratios.items():
            ratio_data.append([name, f"{value}%"])
        ratio_table = Table(ratio_data, colWidths=[4*inch, 2.5*inch])
        ratio_table.setStyle(table_style())
        elements.append(ratio_table)
        elements.append(Spacer(1, 0.2*inch))

    # --- Charts ---
    elements.append(Paragraph("Financial Charts", section_style))
    bar_buf = make_bar_chart(
        income['credit'].sum(), expenses['debit'].sum())
    pie_buf = make_pie_chart(expenses)
    chart_table = Table([[
        Image(bar_buf, width=3*inch, height=2*inch),
        Image(pie_buf, width=3*inch, height=2*inch)
    ]], colWidths=[3.5*inch, 3.5*inch])
    elements.append(chart_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer