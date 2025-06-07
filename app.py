import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
# 🌐 Seletor de idioma
st.sidebar.markdown("🌐 **Idioma / Language**")
lang = st.sidebar.selectbox("Escolha / Choose / Kies", options=["pt", "en", "nl"], index=0)
t = idiomas[lang]

# 🌐 Traduções
idiomas = {
    "pt": {
        "resumo": "📅 Resumo do dia atual",
        "total_pedidos": "Total de Pedidos",
        "sla_medio": "Média de SLA Real",
        "previsao": "🔮 Previsão para o dia seguinte",
        "produtividade": "📊 Produtividade por operador (interativo)",
        "recomendacoes": "🧠 Recomendações e resumo do dia",
        "upload_csv": "📁 Carregar dados",
        "nenhum_csv": "Nenhum CSV carregado. Usando dados simulados.",
        "selecionar_csv": "Selecione seu arquivo CSV"
    },
    "en": {
        "resumo": "📅 Daily Summary",
        "total_pedidos": "Total Orders",
        "sla_medio": "Average SLA",
        "previsao": "🔮 Forecast for Tomorrow",
        "produtividade": "📊 Operator Productivity (interactive)",
        "recomendacoes": "🧠 Insights and Summary",
        "upload_csv": "📁 Upload Data",
        "nenhum_csv": "No CSV uploaded. Using simulated data.",
        "selecionar_csv": "Upload your CSV file"
    },
    "nl": {
        "resumo": "📅 Dagoverzicht",
        "total_pedidos": "Totaal Aantal Orders",
        "sla_medio": "Gemiddelde SLA",
        "previsao": "🔮 Prognose voor Morgen",
        "produtividade": "📊 Productiviteit per Operator (interactief)",
        "recomendacoes": "🧠 Aanbevelingen en Samenvatting",
        "upload_csv": "📁 Gegevens Uploaden",
        "nenhum_csv": "Geen CSV geüpload. Gesimuleerde gegevens worden gebruikt.",
        "selecionar_csv": "Selecteer uw CSV-bestand"
    }
}

st.set_page_config(page_title="AI Picking Planner", layout="wide")
st.title("📦 AI Picking Planner")

# 🌐 Seletor de idioma
st.sidebar.markdown("🌐 **Idioma / Language**")
lang = st.sidebar.selectbox("Escolha / Choose / Kies", options=["pt", "en", "nl"], index=0)
t = idiomas[lang]

# 📁 Upload de CSV
st.sidebar.header(t["upload_csv"])
uploaded_file = st.sidebar.file_uploader(t["selecionar_csv"], type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["data"] = pd.to_datetime(df["data"])
else:
    st.info(t["nenhum_csv"])
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

# 📅 Último dia
data_hoje = df["data"].max()
df_hoje = df[df["data"] == data_hoje]

st.subheader(f"{t['resumo']} ({data_hoje.date()})")
col1, col2 = st.columns(2)
with col1:
    st.metric(t["total_pedidos"], df_hoje["pedidos"].sum())
with col2:
    st.metric(t["sla_medio"], f"{df_hoje['SLA_real'].mean():.2f}%")

# 🔮 Previsão
st.subheader(t["previsao"])
df_grouped = df.groupby(["data", "zona"]).agg({"pedidos": "sum"}).reset_index()
df_grouped["dia_semana"] = df_grouped["data"].dt.day_name()
media_por_dia = df_grouped.groupby(["dia_semana", "zona"])["pedidos"].mean().reset_index()
dia_amanha = (data_hoje + datetime.timedelta(days=1)).day_name()
df_prev = media_por_dia[media_por_dia["dia_semana"] == dia_amanha]
st.dataframe(df_prev.rename(columns={"zona": "Zona", "pedidos": "Pedidos esperados"}), use_container_width=True)

# 📊 Produtividade
st.subheader(t["produtividade"])
df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]
fig = px.bar(df_hoje, x="operador", y="produtividade", color="zona", text="produtividade", title=None)
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(yaxis_title="Pedidos/Minuto", xaxis_title="Operador")
st.plotly_chart(fig, use_container_width=True)

# 🧠 Recomendações
st.subheader(t["recomendacoes"])
media_geral = df_hoje["produtividade"].mean()
mais_prod = df_hoje.loc[df_hoje["produtividade"].idxmax()]
menos_prod = df_hoje.loc[df_hoje["produtividade"].idxmin()]

st.markdown(f"""
- 📈 {mais_prod['operador']} teve a maior produtividade: **{mais_prod['produtividade']:.2f} pedidos/min**  
- 📉 {menos_prod['operador']} teve a menor: **{menos_prod['produtividade']:.2f} pedidos/min**  
- 🧮 Média geral: **{media_geral:.2f} pedidos/min**
""")

for _, row in df_hoje.iterrows():
    diff = (row["produtividade"] - media_geral) / media_geral * 100
    if diff < -15:
        st.error(f"🚨 {row['operador']} está {abs(diff):.1f}% abaixo da média.")
    elif diff > 15:
        st.success(f"✅ {row['operador']} está {diff:.1f}% acima da média.")
    else:
        st.info(f"ℹ️ {row['operador']} está dentro da média.")
