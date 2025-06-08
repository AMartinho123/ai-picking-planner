import streamlit as st
from fpdf import FPDF
import io
import unicodedata
import re

# Dados simulados para teste
recomendacoes = [
    "Operador A está abaixo da média.",
    "Operador B está dentro da média.",
    "Operador C está acima da média."
]

st.title("Teste PDF")

def limpar_texto(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_ascii = texto_normalizado.encode('ASCII', 'ignore').decode('ASCII')
    texto_limpo = ''.join(ch for ch in texto_ascii if ch.isprintable())
    texto_limpo = re.sub(r'(\S{30})(?=\S)', r'\1 ', texto_limpo)  # insere espaços em palavras muito longas
    return texto_limpo

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Relatório de Teste", ln=True, align="C")

pdf = PDF()
pdf.add_page()

pdf.set_font("Helvetica", "", 10)

for rec in recomendacoes:
    texto_limpo = limpar_texto(str(rec))
    pdf.multi_cell(0, 10, texto_limpo, align='L')

pdf_buffer = io.BytesIO()
pdf.output(pdf_buffer)
pdf_buffer.seek(0)

st.download_button(
    label="Baixar PDF de Teste",
    data=pdf_buffer,
    file_name="teste_relatorio.pdf",
    mime="application/pdf"
)
