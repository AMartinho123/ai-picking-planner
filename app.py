import streamlit as st
import pandas as pd

st.title("Teste de Upload e Visualização de Dados")

uploaded_file = st.file_uploader("Carregar ficheiro CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dados carregados:")
    st.dataframe(df.head())

    if 'data' in df.columns and 'pedidos' in df.columns:
        df['data'] = pd.to_datetime(df['data'])
        df_pedidos_dia = df.groupby(df['data'].dt.date)['pedidos'].sum().reset_index()
        df_pedidos_dia.columns = ['data', 'total_pedidos']
        st.line_chart(df_pedidos_dia.set_index('data')['total_pedidos'])
else:
    st.info("Por favor, carregue um ficheiro CSV para começar.")
