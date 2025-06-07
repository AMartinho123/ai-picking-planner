import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from fpdf import FPDF
import io

st.set_page_config(page_title="Simplify", layout="wide")

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



lang_code = st.sidebar.selectbox(
    "Idioma / Language",
    options=list(langs.keys()),
    format_func=lambda x: {
        "pt": "Português",
        "en": "English",
        "fr": "Français",
        "nl": "Nederlands",
        "de": "Deutsch",
        "es": "Español"
    }[x]
)

l = langs[lang_code]
st.title(l["title"])

uploaded_file = st.file_uploader(l["upload_label"], type=["csv", "xlsx"])

if uploaded_file is None:
    st.info(l["no_file"])
    df = pd.DataFrame({
        "data": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "operador": ["Joao", "Maria", "Ana", "Pedro", "Lucas"] * 2,
        "pedidos": [30, 45, 40, 50, 35, 42, 38, 55, 44, 47],
        "tempo_min": [60, 60, 55, 70, 50, 60, 58, 72, 65, 67],
        "SLA_real": [98, 95, 96, 97, 94, 95, 96, 93, 97, 94],
        "zona": ["A", "B", "A", "C", "B"] * 2
    })
else:
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "csv":
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip().lower() for col in df.columns]
        if "operador" in df.columns:
            df["operador"] = df["operador"].astype(str).str.strip()
    else:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip().lower() for col in df.columns]
        if "operador" in df.columns:
            df["operador"] = df["operador"].astype(str).str.strip()

if "data" in df.columns:
    df["data"] = pd.to_datetime(df["data"])

# Filtros interativos
with st.expander("🔍 Filtrar dados"):
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

    if "pedidos" in df_hoje.columns and "tempo_min" in df_hoje.columns:
        df_hoje["produtividade"] = df_hoje["pedidos"] / df_hoje["tempo_min"]
    else:
        df_hoje["produtividade"] = 0

# Tradução das colunas para exibição
colunas_traduzidas = {
    "operador": l.get("col_operator", "Operador"),
    "produtividade": l.get("col_rate", "Pedidos por Minuto"),
    "SLA_real": l.get("col_sla", "SLA (%)"),
    "zona": "Zona",
    "data": "Data",
    "pedidos": "Pedidos",
    "tempo_min": "Tempo (min)"
}
df_exibicao = df_hoje.rename(columns={col: colunas_traduzidas.get(col, col) for col in df_hoje.columns})

if df_hoje.empty:
    st.warning("Nenhum dado disponível com os filtros selecionados.")
else:
    st.dataframe(df_exibicao)

# Métricas principais
col1, col2 = st.columns(2)
with col1:
    total = df_hoje["pedidos"].sum() if "pedidos" in df_hoje.columns else 0
    st.metric(label=l["total_orders"], value=int(total))
with col2:
    sla = df_hoje["SLA_real"].mean() if "SLA_real" in df_hoje.columns else 0
    st.metric(label=l["sla_avg"], value=f"{sla:.1f}%")

# Gráfico de produtividade
if not df_hoje.empty:
    st.subheader(l["prod_title"])
    fig = px.bar(df_hoje, x="operador", y="produtividade", color="operador",
                 labels={"produtividade": l["col_rate"], "operador": l["col_operator"]})
    st.plotly_chart(fig, use_container_width=True)

# Recomendações
if not df_hoje.empty:
    st.subheader(l["reco_title"])
    media = df_hoje["produtividade"].mean()
    recomendacoes = []
    for _, row in df_hoje.iterrows():
        dif = ((row["produtividade"] - media) / media) * 100 if media > 0 else 0
        if dif < -10:
            texto = l["below_avg"].format(op=row["operador"], val=abs(dif))
        elif dif > 10:
            texto = l["above_avg"].format(op=row["operador"], val=dif)
        else:
            texto = l["in_avg"].format(op=row["operador"])
        st.write(texto)
        recomendacoes.append(texto)

    def gerar_relatorio_pdf(df, recomendacoes):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        data_hoje = datetime.datetime.now()
        pdf.cell(0, 10, txt=l["report_title"].format(date=data_hoje.strftime('%d/%m/%Y')), ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 10, l["col_operator"])
        pdf.cell(50, 10, l["col_rate"])
        pdf.cell(40, 10, l["col_sla"])
        pdf.ln()
        pdf.set_font("Arial", '', 10)
        for _, row in df.iterrows():
            op = row.get("operador", "")
            pdf.cell(40, 10, str(op))
            prod = row.get("produtividade", 0)
            prod_text = f"{prod:.2f}" if isinstance(prod, (int, float)) else ""
            pdf.cell(50, 10, prod_text)
            sla = row.get("SLA_real", "")
            sla_text = f"{sla:.1f}%" if isinstance(sla, (int, float)) else ""
            pdf.cell(40, 10, sla_text)
            pdf.ln()
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, l["reco_label"], ln=True)
        pdf.set_font("Arial", '', 10)
        import unicodedata
        for rec in recomendacoes:
            texto_limpo = unicodedata.normalize('NFKD', rec).encode('ASCII', 'ignore').decode('ASCII')
            pdf.multi_cell(0, 10, texto_limpo)

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer

    pdf_buffer = gerar_relatorio_pdf(df_hoje, recomendacoes)
    file_name = f"relatorio_{lang_code}_{data_filtro.strftime('%Y-%m-%d')}.pdf"
    st.download_button(label=l["download_pdf"], data=pdf_buffer, file_name=file_name, mime="application/pdf")
