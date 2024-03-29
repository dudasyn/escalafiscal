
import pandas as pd
import datetime as dt
import streamlit as st
from escala import *
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

st.title('Gerador de Escala - Auditores Fiscais do Município de Duque de Caxias')
st.header('Aplicativo web para gerar escalas (Fazenda e Chat)')

st.write('Não considera Sábados, domingos e a lista de feriados nacionais constantes neste link: https://www.cnnbrasil.com.br/nacional/veja-quais-sao-as-datas-e-feriados-nacionais-de-2022/')
st.write("O modelo do arquivo excel pode ser baixado no link: https://github.com/dudasyn/escalafiscal/blob/main/Fiscais.xlsx")
st.write('Não considera os dias de férias constantes na planilha.')


uploaded_file = st.file_uploader('Faça o upload do arquivo com a relação de fiscais...')
if uploaded_file is not None:

    fiscal_tables=pd.read_excel(uploaded_file)
    fiscal_tables = fiscal_tables.sample(len(fiscal_tables))
    fiscais = []
    date_list = []
    n_fiscais = 2
    n_escalas = 3
    for i in range(len(fiscal_tables.inicio_ferias)):
        data_inicio_ferias = fiscal_tables.inicio_ferias[i]
        dias_de_ferias = fiscal_tables.dias_de_ferias[i]
        if pd.isnull(dias_de_ferias):
            dias_de_ferias = 0
        date_list = [x for x in [data_inicio_ferias + dt.timedelta(days=x) for x in range(int(dias_de_ferias))]]
        fiscais.append(Fiscal(fiscal_tables.Nome[i],date_list,[]))


    st.subheader('Selecione o período da escala')
    start_date = st.date_input("Dia inicial", dt.date(2022, 1, 1))
    end_date = st.date_input("Dia Final", dt.date(2022, 1, 31))
    escala = Escala(start_date, end_date, fiscais,n_fiscais,n_escalas)

    fazenda = pd.DataFrame()
    resumo = pd.DataFrame()
    if st.button('Gerar Escala'):
        fazenda = escala.gera_escala()
        st.write(fazenda)
        st.subheader('Relação dos Fiscais e dias escalados')
        resumo = escala.gera_resumo_fiscais()
        st.write(resumo)

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format': '0.00'}) 
            worksheet.set_column('A:A', None, format1)  
            writer.save()
            processed_data = output.getvalue()
            return processed_data
        df_fazenda_excel = to_excel(fazenda)
        #df_resumo_excel = to_excel(resumo)

        st.download_button(label='📥 Download da Escala', data=df_fazenda_excel ,file_name= 'Escala.xlsx')

else:
    st.warning('Você precisa fazer upload do arquivo de fiscais')
