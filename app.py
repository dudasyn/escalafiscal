
import pandas as pd
import datetime as dt
import streamlit as st
from escala import *

st.title('Gerador de Escala - Auditores Fiscais do Município de Duque de Caxias')
st.header('Software randomico para gerar escalas (Fazenda e Chat)')


uploaded_file = st.file_uploader('Faça o upload do arquivo com a relação de fiscais...')
if uploaded_file is not None:
    df1=pd.read_excel(uploaded_file)
    
    fiscais = []
    #fiscal_tables = pd.read_excel("./Fiscais.xlsx")
    fiscal_tables = df1
    fiscal_tables = fiscal_tables.sample(len(fiscal_tables))
    ##st.write('Relação dos fiscais:', fiscal_tables)

    for i in range(len(fiscal_tables)):
        fiscais.append(Fiscal(fiscal_tables.Nome[i],fiscal_tables.inicio_ferias[i],fiscal_tables.dias_de_ferias[i]))

    #st.write('Relação dos fiscais:', fiscais)
    st.subheader('Selecione o período da escala')
    start_date = st.date_input("Dia inicial",dt.date(2022, 1, 1))
    end_date = st.date_input("Dia Final",dt.date(2022, 1, 31))
    option = st.selectbox('O que deseja gerar?',('Fazenda', 'Fazenda e Plantão Chat (manhã e tarde)'))
    st.write('Você selecionou:', option)
    if option == 'Fazenda':
        n_escalas = 1
    else:
        n_escalas = 3

    escala = Escala(start_date, end_date, fiscais,2,n_escalas)
    fazenda = pd.DataFrame()
    if st.button('Gerar Escala'):
        fazenda = escala.gera_escala()
        st.write(fazenda)
        st.subheader('Relação dos Fiscais e dias escalados')
        st.write(escala.gera_resumo_fiscais())


else:
    st.warning('Você precisa fazer upload do arquivo de fiscais')
