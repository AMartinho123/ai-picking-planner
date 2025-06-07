import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="AI Picking Planner", layout="wide")
st.title("📦 AI Picking Planner")

# Gerar dados simulados direto no app (sem CSV)
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

# Último dia
data_hoje = df["data"].max()
df_hoje = df[df["data"] == data_hoje]

st.subheader(f"📅 Resumo do dia atual ({data_hoje.date()})")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Pedidos", df_hoje["pedidos"].sum())
with col2:
    st.metric("Média de SLA Real", f"{df_hoje['SLA_real'].mean():.2f}%")

# Previsão
st.subheader("🔮 Previsão para o dia seguinte")
df_grouped = df.groupby(["data", "zona"]).agg({"pedidos": "sum"}).reset_index()
df_grouped["dia_semana"] = df_grouped["data"].dt.day_name()
media_por_dia = df_grouped.groupby(["dia_semana", "zona"])["pedidos"].mean().reset_index()
dia_amanha = (data_hoje + datetime.timedelta(days=1)).day_name()
df_prev = media_por_dia[media_por_dia["dia_semana"] == dia_amanha]

st.write(f"Previsão para {dia_amanha}:")
st.dataframe(df_prev.rename(columns={"zona": "Zona", "pedidos": "Pedidos esperados"}), use_container_width=True)

