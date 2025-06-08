import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

st.set_page_config(page_title="Simplify", layout="wide")

# Dados simulados para teste
recomendacoes = [
    "Operador A está abaixo da média.",
    "Operador B está dentro da média.",
    "Operador C está acima da média."
]

st.title("Teste PDF com ReportLab")

def gerar_pdf_buffer(recomendacoes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    title_style = styles['Title']
    elements.append(Paragraph("Relatório de Teste", title_style))
    elements.append(Spacer(1, 12))

    # Tabela de recomendações
    data = [["Recomendações"]]
    for rec in recomendacoes:
        data.append([rec])

    table = Table(data, colWidths=[160*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_buffer = gerar_pdf_buffer(recomendacoes)

st.download_button(
    label="Baixar PDF de Teste",
    data=pdf_buffer,
    file_name="teste_relatorio_reportlab.pdf",
    mime="application/pdf"
)
