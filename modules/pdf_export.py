from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import datetime

def generate_pdf(assets, liabilities, income, expenses, net_profit, filepath="outputs/financial_report.pdf"):

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#1a3c5e'),
                                  alignment=TA_CENTER, spaceAfter=6)
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
                                     fontSize=10, textColor=colors.grey,
                                     alignment=TA_CENTER, spaceAfter=20)
    section_style = ParagraphStyle('section', parent=styles['Heading2'],
                                    fontSize=13, textColor=colors.HexColor('#1a3c5e'),
                                    spaceBefore=16, spaceAfter=8)

    today = datetime.date.today().strftime("%d %B %Y")
    elements.append(Paragraph("Bank Financial Report", title_style))
    elements.append(Paragraph(f"Generated on {today}", subtitle_style))

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
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor('#f0f4f8'), colors.white]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4edda')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(pl_table)
    elements.append(Spacer(1, 0.2*inch))

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
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor('#f0f4f8'), colors.white]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d4edda')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(bs_table)

    doc.build(elements)
    return filepath