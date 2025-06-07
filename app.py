import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="AI Picking Planner", layout="wide")
st.title("📦 AI Picking Planner")

# Upload de CSV
st.sidebar.header("📁 Carregar dados")
uploaded_file = st.sidebar.file_uploader("Selecione seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["data"] = pd.to_datetime(df["data"])
else:
    st.info("Nenhum CSV carregado. Usando dados simulados.")
    # Dados simulados de backup
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

# Último dia da base
data_hoje = df["data"].max()
df_hoje = df[df["data"] == data_hoje]

st.subheader(f"📅 Resumo do dia atual ({data_hoje.date()})")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Pedidos", df_hoje["pedidos"].sum())
with col2:
    st.metric("Média de SLA Real", f"{df_hoje['SLA_real'].mean():.2f}%")

# Previsão para o dia seguinte
st.subheader("🔮 Previsão para o dia seguinte")
df_grouped = df.groupby(["data", "zona"]).agg({"pedidos": "sum"}).reset_index()
df_grouped["dia_semana"] = df_grouped["data"].dt.day_name()
media_por_dia = df_grouped.groupby(["dia_semana", "zona"])["pedidos"].mean().reset_index()
dia_amanha = (data_hoje + datetime.timedelta(days=1)).day_name()
df_prev = media_por_dia[media_por_dia["dia_semana"] == dia_amanha]
st.write(f"Previsão para {dia_amanha}:")
st.dataframe(df_prev.rename(columns={"zona": "Zona", "pedidos": "Pedidos esperados"}), use_container_width=True)

# Produtividade
st.subheader("📊 Produtividade por operador (interativo)")
df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]
fig = px.bar(df_hoje, x="operador", y="produtividade", color="zona", text="produtividade", title="Produtividade (pedidos/min)")
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(yaxis_title="Pedidos por Minuto", xaxis_title="Operador")
st.plotly_chart(fig, use_container_width=True)

# Recomendações automáticas
st.subheader("🧠 Recomendações e resumo do dia")
media_geral = df_hoje["produtividade"].mean()
mais_prod = df_hoje.loc[df_hoje["produtividade"].idxmax()]
menos_prod = df_hoje.loc[df_hoje["produtividade"].idxmin()]

st.markdown(f"""
- 📈 O operador mais produtivo foi **{mais_prod['operador']}** com **{mais_prod['produtividade']:.2f} pedidos/min**.
- 📉 O menos produtivo foi **{menos_prod['operador']}** com **{menos_prod['produtividade']:.2f} pedidos/min**.
- 📊 A produtividade média geral foi de **{media_geral:.2f} pedidos/min**.
""")

for _, row in df_hoje.iterrows():
    diff = (row["produtividade"] - media_geral) / media_geral * 100
    if diff < -15:
        st.error(f"🚨 {row['operador']} está com produtividade {abs(diff):.1f}% abaixo da média.")
    elif diff > 15:
        st.success(f"✅ {row['operador']} está com produtividade {diff:.1f}% acima da média.")
    else:
        st.info(f"ℹ️ {row['operador']} está dentro da média.")
