import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from fpdf import FPDF
import io

# Suporte multilíngue
langs = {
    "fr": {
        "title": "Simplify - Tableau Logistique",
        "upload_label": "Téléverser un fichier CSV de données réelles",
        "no_file": "Aucun fichier téléversé. Données simulées utilisées.",
        "total_orders": "Total des Commandes",
        "sla_avg": "SLA Moyen (%)",
        "prod_title": "Productivité par opérateur",
        "reco_title": "Recommandations du jour",
        "below_avg": "{op} est en dessous de la moyenne de {val:.1f}%.",
        "above_avg": "{op} est au-dessus de la moyenne de {val:.1f}%.",
        "in_avg": "{op} est dans la moyenne.",
        "report_title": "Rapport de Performance - {date}",
        "reco_label": "Recommandations:",
        "download_pdf": "Télécharger le rapport PDF",
        "col_operator": "Opérateur",
        "col_rate": "Commandes par minute",
        "col_sla": "SLA (%)"
    },
    "nl": {
        "title": "Simplify - Logistiek Dashboard",
        "upload_label": "Upload een CSV-bestand met echte gegevens",
        "no_file": "Geen bestand geüpload. Gesimuleerde gegevens worden gebruikt.",
        "total_orders": "Totaal Bestellingen",
        "sla_avg": "Gemiddelde SLA (%)",
        "prod_title": "Productiviteit per operator",
        "reco_title": "Aanbevelingen van vandaag",
        "below_avg": "{op} ligt {val:.1f}% onder het gemiddelde.",
        "above_avg": "{op} ligt {val:.1f}% boven het gemiddelde.",
        "in_avg": "{op} zit binnen het gemiddelde.",
        "report_title": "Prestatieverslag - {date}",
        "reco_label": "Aanbevelingen:",
        "download_pdf": "Download PDF Rapport",
        "col_operator": "Operator",
        "col_rate": "Bestellingen per minuut",
        "col_sla": "SLA (%)"
    },
    "de": {
        "title": "Simplify - Logistik-Dashboard",
        "upload_label": "CSV-Datei mit echten Daten hochladen",
        "no_file": "Keine Datei hochgeladen. Simulierte Daten werden verwendet.",
        "total_orders": "Gesamtaufträge",
        "sla_avg": "Durchschnittlicher SLA (%)",
        "prod_title": "Produktivität nach Bediener",
        "reco_title": "Empfehlungen des Tages",
        "below_avg": "{op} liegt {val:.1f}% unter dem Durchschnitt.",
        "above_avg": "{op} liegt {val:.1f}% über dem Durchschnitt.",
        "in_avg": "{op} liegt im Durchschnitt.",
        "report_title": "Leistungsbericht - {date}",
        "reco_label": "Empfehlungen:",
        "download_pdf": "PDF-Bericht herunterladen",
        "col_operator": "Bediener",
        "col_rate": "Bestellungen pro Minute",
        "col_sla": "SLA (%)"
    },
    "es": {
        "title": "Simplify - Panel Logístico",
        "upload_label": "Cargar archivo CSV con datos reales",
        "no_file": "No se cargó ningún archivo. Se usan datos simulados.",
        "total_orders": "Total de Pedidos",
        "sla_avg": "SLA Promedio (%)",
        "prod_title": "Productividad por operador",
        "reco_title": "Recomendaciones del día",
        "below_avg": "{op} está por debajo del promedio en {val:.1f}%.",
        "above_avg": "{op} está por encima del promedio en {val:.1f}%.",
        "in_avg": "{op} está dentro del promedio.",
        "report_title": "Informe de Rendimiento - {date}",
        "reco_label": "Recomendaciones:",
        "download_pdf": "Descargar informe en PDF",
        "col_operator": "Operador",
        "col_rate": "Pedidos por Minuto",
        "col_sla": "SLA (%)"
    },
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
    },
    "en": {
        "title": "Simplify - Logistics Dashboard",
        "upload_label": "Upload real data CSV file",
        "no_file": "No file uploaded. Using simulated data.",
        "total_orders": "Total Orders",
        "sla_avg": "Average SLA (%)",
        "prod_title": "Productivity by Operator",
        "reco_title": "Today's Recommendations",
        "below_avg": "{op} is below average by {val:.1f}%.",
        "above_avg": "{op} is above average by {val:.1f}%.",
        "in_avg": "{op} is within average.",
        "report_title": "Performance Report - {date}",
        "reco_label": "Recommendations:",
        "download_pdf": "Download PDF Report",
        "col_operator": "Operator",
        "col_rate": "Orders per Minute",
        "col_sla": "SLA (%)"
    }
}

lang_code = st.sidebar.selectbox("Idioma / Language", options=list(langs.keys()), format_func=lambda x: {"pt": "Português", "en": "English", "fr": "Français", "nl": "Nederlands", "de": "Deutsch", "es": "Español"}[x])
l = langs[lang_code]

# Upload de dados reais
st.set_page_config(page_title="Simplify", layout="wide")
st.title(l["title"])

uploaded_file = st.file_uploader(l["upload_label"], type=["csv", "xlsx"])
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    st.info(l["no_file"])
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

# Filtrar para o ultimo dia
if "data" in df.columns:
    df["data"] = pd.to_datetime(df["data"])
    data_hoje = df["data"].max()
    df_hoje = df[df["data"] == data_hoje].copy()
else:
    df_hoje = df.copy()
    data_hoje = datetime.date.today()

if "pedidos" in df_hoje.columns and "tempo_min" in df_hoje.columns:
    df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]
else:
    df_hoje["produtividade"] = 0

# Histórico comparativo
st.subheader("📊 Comparativo entre dias")
if "data" in df.columns and "operador" in df.columns and "produtividade" in df.columns:
    df_hist = df.copy()
    df_hist_grouped = df_hist.groupby([df_hist["data"].dt.date, "operador"]).agg({
        "produtividade": "mean",
        "SLA_real": "mean"
    }).reset_index()

    aba1, aba2 = st.tabs(["📈 Produtividade", "📉 SLA (%)"])

    with aba1:
        fig_prod = px.line(df_hist_grouped, x="data", y="produtividade", color="operador", markers=True, title="Produtividade ao longo do tempo")
        st.plotly_chart(fig_prod, use_container_width=True)

    with aba2:
        fig_sla = px.line(df_hist_grouped, x="data", y="SLA_real", color="operador", markers=True, title="SLA (%) ao longo do tempo")
        st.plotly_chart(fig_sla, use_container_width=True)

# Metricas
total_pedidos = df_hoje["pedidos"].sum() if "pedidos" in df_hoje.columns else 0
sla_medio = df_hoje["SLA_real"].mean() if "SLA_real" in df_hoje.columns else 0

col1, col2 = st.columns(2)
col1.metric(l["total_orders"], total_pedidos)
col2.metric(l["sla_avg"], f"{sla_medio:.2f}%")

# Grafico de produtividade
st.subheader(l["prod_title"])
if "operador" in df_hoje.columns and "produtividade" in df_hoje.columns:
    fig = px.bar(df_hoje, x="operador", y="produtividade", color="zona" if "zona" in df_hoje.columns else None, text="produtividade")
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# Tradução das colunas para exibição (sem afetar o DataFrame original)
colunas_traduzidas = {
    "operador": l.get("col_operator", "Operador"),
    "produtividade": l.get("col_rate", "Pedidos por Minuto"),
    "SLA_real": l.get("col_sla", "SLA (%)"),
    "zona": "Zona",
    "data": "Data",
    "pedidos": "Pedidos",
    "tempo_min": "Tempo (min)",
}
df_exibicao = df_hoje.rename(columns={col: colunas_traduzidas.get(col, col) for col in df_hoje.columns})

# Filtros interativos
with st.expander("🔍 Filtrar dados"):
    col_f4, col_f5 = st.columns(2)
    col_f1, col_f2, col_f3 = st.columns(3)
    datas_disponiveis = df["data"].dt.date.unique() if "data" in df.columns else []
    operadores_disponiveis = df["operador"].unique() if "operador" in df.columns else []
    zonas_disponiveis = df["zona"].unique() if "zona" in df.columns else []

    data_filtro = col_f1.selectbox("Data", options=sorted(datas_disponiveis), format_func=lambda x: x.strftime('%d/%m/%Y') if isinstance(x, datetime.date) else x)
    operador_filtro = col_f2.multiselect("Operador", options=operadores_disponiveis, default=operadores_disponiveis)
    zona_filtro = col_f3.multiselect("Zona", options=zonas_disponiveis, default=zonas_disponiveis)

    df_hoje = df.copy()
    df_hoje = df_hoje[df_hoje["data"].dt.date == data_filtro]
    df_hoje = df_hoje[df_hoje["operador"].isin(operador_filtro)]
    df_hoje = df_hoje[df_hoje["zona"].isin(zona_filtro)]

    # Filtros adicionais de SLA e produtividade
    sla_min, sla_max = col_f4.slider("SLA (%)", min_value=0, max_value=100, value=(0, 100))
    prod_min, prod_max = col_f5.slider("Produtividade", min_value=0.0, max_value=2.0, value=(0.0, 2.0), step=0.01)
    df_hoje = df_hoje[(df_hoje["SLA_real"] >= sla_min) & (df_hoje["SLA_real"] <= sla_max)]
    df_hoje = df_hoje[(df_hoje["produtividade"] >= prod_min) & (df_hoje["produtividade"] <= prod_max)]

    if "pedidos" in df_hoje.columns and "tempo_min" in df_hoje.columns:
        df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]
    else:
        df_hoje["produtividade"] = 0

# Exibir tabela com colunas traduzidas
st.dataframe(df_exibicao)

# Recomendacoes
st.subheader(l["reco_title"])
recomendacoes = []
if "produtividade" in df_hoje.columns:
    media_geral = df_hoje["produtividade"].mean()
    for _, row in df_hoje.iterrows():
        if "operador" in row:
            diff = (row["produtividade"] - media_geral) / media_geral * 100 if media_geral else 0
            if diff < -15:
                msg = l["below_avg"].format(op=row['operador'], val=abs(diff))
                st.error(msg)
            elif diff > 15:
                msg = l["above_avg"].format(op=row['operador'], val=diff)
                st.success(msg)
            else:
                msg = l["in_avg"].format(op=row['operador'])
                st.info(msg)
            recomendacoes.append(msg)

# Funcao para gerar o PDF com logotipo e sem acentos/emojis

def gerar_relatorio_pdf(df, recomendacoes):
    import os
    logo_path = "logo.png"  # Substitua por um arquivo que você adicione ao repositório

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
        pdf.ln(20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=l["report_title"].format(date=data_hoje.strftime('%d/%m/%Y')), ln=True, align='C')), ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, l.get("col_operator", "Operador"), 1)
    pdf.cell(60, 10, l.get("col_rate", "Pedidos por Minuto"), 1)
    pdf.cell(60, 10, l.get("col_sla", "SLA (%)"), 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(60, 10, str(row.get('operador', '')), 1)
        pdf.cell(60, 10, f"{row.get('produtividade', 0):.2f}", 1)
        pdf.cell(60, 10, f"{row.get('SLA_real', 0):.2f}", 1)
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=l["reco_label"], ln=True)
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
st.download_button(l["download_pdf"], data=pdf_buffer, file_name="relatorio_simplify.pdf", mime="application/pdf")
