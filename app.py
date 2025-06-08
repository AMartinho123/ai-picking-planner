import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

st.set_page_config(page_title="Simplify", layout="wide")

langs = {
    "pt": {
        "title": "Simplify - Painel Logistico",
        "upload_label": "Carregar arquivo CSV com dados reais",
        "no_file": "Nenhum arquivo carregado. Usando dados simulados.",
        "total_orders": "Total de Pedidos",
        "sla_avg": "Media de SLA Real",
        "prod_title": "Produtividade por operador",
        "reco_title": "Recomendacoes do dia",
        "below_avg": "{op} esta abaixo da media em {val:.1f}%.",
        "above_avg": "{op} esta acima da media em {val:.1f}%.",
        "in_avg": "{op} esta dentro da media.",
        "report_title": "Relatorio de Desempenho - {date}",
        "reco_label": "Recomendacoes:",
        "download_pdf": "Baixar Relatorio em PDF",
        "col_operator": "Operador",
        "col_rate": "Pedidos por Minuto",
        "col_sla": "SLA (%)"
    }
}

lang_code = st.sidebar.selectbox(
    "Idioma / Language",
    options=list(langs.keys()),
    format_func=lambda x: {
        "pt": "Português"
    }[x]
)

l = langs[lang_code]
st.title(l["title"])

uploaded_file = st.file_uploader(l["upload_label"], type=["csv", "xlsx"])

if uploaded_file is None:
    st.info(l["no_file"])
    df = pd.DataFrame({
        "data": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "nome_completo": [
            "Joao Silva", "Maria Santos", "Ana Costa", "Pedro Alves", "Lucas Oliveira",
            "Joao Silva", "Maria Santos", "Ana Costa", "Pedro Alves", "Lucas Oliveira"
        ],
        "pedidos": [30, 45, 40, 50, 35, 42, 38, 55, 44, 47],
        "tempo_min": [60, 60, 55, 70, 50, 60, 58, 72, 65, 67],
        "SLA_real": [98, 95, 96, 97, 94, 95, 96, 93, 97, 94],
        "zona": ["A", "B", "A", "C", "B"] * 2
    })
else:
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = [col.strip().lower() for col in df.columns]
    renomear = {
        "sla_real": "SLA_real",
        "nome_completo": "nome_completo",
        "tempo_min": "tempo_min",
        "produtividade": "produtividade"
    }
    df = df.rename(columns=renomear)
    if "nome_completo" in df.columns:
        df["nome_completo"] = df["nome_completo"].astype(str).str.strip()

if "data" in df.columns:
    df["data"] = pd.to_datetime(df["data"])

with st.expander("🔍 Filtrar dados"):
    col_f1, col_f2, col_f3 = st.columns(3)
    datas_disponiveis = df["data"].dt.date.unique() if "data" in df.columns else []
    nomes_disponiveis = df["nome_completo"].unique() if "nome_completo" in df.columns else []
    zonas_disponiveis = df["zona"].unique() if "zona" in df.columns else []

    data_filtro = col_f1.selectbox(
        "Data",
        options=["Todos"] + sorted(datas_disponiveis),
        format_func=lambda x: x.strftime("%d/%m/%Y") if isinstance(x, datetime.date) else x
    )
    nome_filtro = col_f2.multiselect(
        "Operador",
        options=nomes_disponiveis,
        default=list(nomes_disponiveis)
    )
    zona_filtro = col_f3.multiselect(
        "Zona",
        options=zonas_disponiveis,
        default=list(zonas_disponiveis)
    )

    df_hoje = df.copy()
    if data_filtro != "Todos":
        df_hoje = df_hoje[df_hoje["data"].dt.date == data_filtro]
    if nome_filtro:
        df_hoje = df_hoje[df_hoje["nome_completo"].isin(nome_filtro)]
    if zona_filtro:
        df_hoje = df_hoje[df_hoje["zona"].isin(zona_filtro)]

if "tempo_min" in df_hoje.columns and "pedidos" in df_hoje.columns:
    df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]

total_pedidos = df_hoje["pedidos"].sum() if "pedidos" in df_hoje.columns else 0
sla_medio = df_hoje["SLA_real"].mean() if "SLA_real" in df_hoje.columns else 0

col1, col2 = st.columns(2)
col1.metric(label=l["total_orders"], value=total_pedidos)
col2.metric(label=l["sla_avg"], value=f"{sla_medio:.1f}%")

if not df_hoje.empty and "nome_completo" in df_hoje.columns and "produtividade" in df_hoje.columns:
    fig = px.bar(df_hoje, x="nome_completo", y="produtividade", color="nome_completo", title=l["prod_title"])
    st.plotly_chart(fig, use_container_width=True)

recomendacoes = []
media_prod = df_hoje["produtividade"].mean() if "produtividade" in df_hoje.columns else 0
for _, row in df_hoje.iterrows():
    nome = row.get("nome_completo", "?")
    val = row.get("produtividade", 0) - media_prod
    if val < -0.5:
        recomendacoes.append(l["below_avg"].format(op=nome, val=abs(val)))
    elif val > 0.5:
        recomendacoes.append(l["above_avg"].format(op=nome, val=val))
    else:
        recomendacoes.append(l["in_avg"].format(op=nome))

st.subheader(l["reco_title"])
for rec in recomendacoes:
    st.write("-", rec)

def gerar_relatorio_pdf(df_hoje, recomendacoes, l, data_filtro):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    data_str = data_filtro.strftime('%d/%m/%Y') if hasattr(data_filtro, 'strftime') else "Todos"
    titulo = l["report_title"].format(date=data_str)
    elements.append(Paragraph(titulo, styles['Title']))
    elements.append(Spacer(1, 12))

    data = [[l["col_operator"], l["col_rate"], l["col_sla"]]]
    for _, row in df_hoje.iterrows():
        operador = str(row.get("nome_completo", "-"))
        produtividade = f"{row.get('produtividade', 0):.2f}" if row.get('produtividade') is not None else "-"
        sla = f"{row.get('SLA_real', 0):.1f}%" if row.get('SLA_real') is not None else "-"
        data.append([operador, produtividade, sla])

    tabela = Table(data, colWidths=[60*mm, 60*mm, 40*mm])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(tabela)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph(l["reco_label"], styles['Heading2']))
    for rec in recomendacoes:
        elements.append(Paragraph(rec, styles['Normal']))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_buffer = gerar_relatorio_pdf(df_hoje, recomendacoes, l, data_filtro)

st.download_button(
    label=l["download_pdf"],
    data=pdf_buffer,
    file_name=f"relatorio_{lang_code}_{data_filtro.strftime('%Y-%m-%d') if hasattr(data_filtro, 'strftime') else 'todos'}.pdf",
    mime="application/pdf"
)
