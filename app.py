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
        renomear = {
            "sla_real": "SLA_real",
            "operador": "operador",
            "tempo_min": "tempo_min",
            "produtividade": "produtividade"
        }
        df = df.rename(columns=renomear)
        if "operador" in df.columns:
            df["operador"] = df["operador"].astype(str).str.strip()
    else:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip().lower() for col in df.columns]
        renomear = {
            "sla_real": "SLA_real",
            "operador": "operador",
            "tempo_min": "tempo_min",
            "produtividade": "produtividade"
        }
        df = df.rename(columns=renomear)
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

    data_filtro = col_f1.selectbox(
        "Data",
        options=["Todos"] + sorted(datas_disponiveis),
        format_func=lambda x: x.strftime("%d/%m/%Y") if isinstance(x, datetime.date) else x
    )
