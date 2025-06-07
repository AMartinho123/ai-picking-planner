import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from fpdf import FPDF
import io

# Dados simulados ou upload de CSV
data = {
    "data": pd.date_range(start="2025-06-01", periods=10).repeat(3),
    "operador": ["João", "Ana", "Carlos"] * 10,
    "zona": ["A", "B", "C"] * 10,
    "pedidos": [120, 80, 100] * 10,
    "tempo_min": [300, 220, 250] * 10,
    "SLA_meta": [95] * 30,
    "SLA_real": [92, 96, 94] * 10
}
df = pd.DataFrame(data)

# Processamento
st.set_page_config(page_title="Simplify", layout="wide")
st.title("📦 Simplify - Painel Logístico")

data_hoje = df["data"].max()
df_hoje = df[df["data"] == data_hoje].copy()
df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]

# Seção de resumo
total_pedidos = df_hoje["pedidos"].sum()
sla_medio = df_hoje["SLA_real"].mean()

col1, col2 = st.columns(2)
col1.metric("Total de Pedidos", total_pedidos)
col2.metric("Média de SLA Real", f"{sla_medio:.2f}%")

# Gráfico de produtividade
st.subheader("📊 Produtividade por operador")
fig = px.bar(df_hoje, x="operador", y="produtividade", color="zona", text="produtividade")
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Recomendações automáticas
st.subheader("🧠 Recomendações do dia")
media_geral = df_hoje["produtividade"].mean()
recomendacoes = []
for _, row in df_hoje.iterrows():
    diff = (row["produtividade"] - media_geral) / media_geral * 100
    if diff < -15:
        msg = f"⚠️ {row['operador']} está abaixo da média em {abs(diff):.1f}%."
        st.error(msg)
    elif diff > 15:
        msg = f"✅ {row['operador']} está acima da média em {diff:.1f}%."
        st.success(msg)
    else:
        msg = f"ℹ️ {row['operador']} está dentro da média."
        st.info(msg)
    recomendacoes.append(msg)

# Função para gerar PDF
def gerar_relatorio_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Desempenho", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Operador", 1)
    pdf.cell(60, 10, "Pedidos/Minuto", 1)
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
    pdf.cell(200, 10, txt="Recomendações:", ln=True)
    pdf.set_font("Arial", size=12)
    for rec in recomendacoes:
        pdf.multi_cell(0, 10, rec)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Botão de download
pdf_buffer = gerar_relatorio_pdf(df_hoje)
st.download_button("📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="relatorio_simplify.pdf", mime="application/pdf")
