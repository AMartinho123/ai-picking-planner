import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from fpdf import FPDF
import io

# Dados simulados
data = {
    "data": pd.date_range(start="2025-06-01", periods=10).repeat(3),
    "operador": ["Joao", "Ana", "Carlos"] * 10,
    "zona": ["A", "B", "C"] * 10,
    "pedidos": [120, 80, 100] * 10,
    "tempo_min": [300, 220, 250] * 10,
    "SLA_meta": [95] * 30,
    "SLA_real": [92, 96, 94] * 10
}
df = pd.DataFrame(data)

st.set_page_config(page_title="Simplify", layout="wide")
st.title("Simplify - Painel Logistico")

# Filtrar para o ultimo dia
data_hoje = df["data"].max()
df_hoje = df[df["data"] == data_hoje].copy()
df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]

# Metricas
total_pedidos = df_hoje["pedidos"].sum()
sla_medio = df_hoje["SLA_real"].mean()

col1, col2 = st.columns(2)
col1.metric("Total de Pedidos", total_pedidos)
col2.metric("Media de SLA Real", f"{sla_medio:.2f}%")

# Grafico de produtividade
st.subheader("Produtividade por operador")
fig = px.bar(df_hoje, x="operador", y="produtividade", color="zona", text="produtividade")
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Recomendacoes
st.subheader("Recomendacoes do dia")
media_geral = df_hoje["produtividade"].mean()
recomendacoes = []
for _, row in df_hoje.iterrows():
    diff = (row["produtividade"] - media_geral) / media_geral * 100
    if diff < -15:
        msg = f"{row['operador']} esta abaixo da media em {abs(diff):.1f}%."
        st.error(msg)
    elif diff > 15:
        msg = f"{row['operador']} esta acima da media em {diff:.1f}%."
        st.success(msg)
    else:
        msg = f"{row['operador']} esta dentro da media."
        st.info(msg)
    recomendacoes.append(msg)

# Funcao para gerar o PDF sem acentos/emojis

def gerar_relatorio_pdf(df, recomendacoes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, txt="Relatorio de Desempenho", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Operador", 1)
    pdf.cell(60, 10, "Pedidos por Minuto", 1)
    pdf.cell(60, 10, "SLA Real (%)", 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(60, 10, str(row['operador']), 1)
        pdf.cell(60, 10, f"{row['produtividade']:.2f}", 1)
        pdf.cell(60, 10, f"{row['SLA_real']:.2f}", 1)
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Recomendacoes:", ln=True)
    pdf.set_font("Arial", size=12)
    for rec in recomendacoes:
        texto_limpo = rec.encode("ascii", "ignore").decode()
        pdf.multi_cell(0, 10, texto_limpo, align='L')
        pdf.ln(1)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Botao de download
pdf_buffer = gerar_relatorio_pdf(df_hoje, recomendacoes)
st.download_button("Baixar Relatorio em PDF", data=pdf_buffer, file_name="relatorio_simplify.pdf", mime="application/pdf")
