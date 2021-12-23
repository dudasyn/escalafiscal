import random
import datetime as dt
import pandas as pd


class Fiscal:
    def __init__(self, nome, lista_dias_ferias,lista_dias_escalados = []):
        self.nome = nome
        self.lista_dias_ferias = lista_dias_ferias
        self.lista_dias_escalados = lista_dias_escalados

    def retorna_dias_escalados(self):
        dias = []
        for data in self.lista_dias_escalados:
            dias.append(data.day)
        return(dias)

    
    def retorna_dias_indisponiveis(self):
        
        dias_indisponiveis = []
        for dia in self.lista_dias_ferias:
            dias_indisponiveis.append(dia)

        for dia in self.lista_dias_escalados:
            dias_indisponiveis.append(dia)

        dias = [x for x in dias_indisponiveis]
        if len(dias)==0:
            return []
        return dias

class Escala:
    def __init__(self, start_date, end_date,  fiscais, n_fiscais=2,n_escalas = 1):

        self.start_date = start_date
        self.end_date = end_date
        self.fiscais = fiscais
        self.fiscaisbackup = fiscais.copy()
        self.n_fiscais = n_fiscais
        self.n_escalas = n_escalas

    def retorna_lista_de_feriados(self):
        feriados = [["2022-01-01", "Confraternização Universal"], ["2022-04-21", "Tiradentes"], ["2022-05-01", "Dia do trabalhador"], ["2022-09-07", "Independência"], ["2022-10-12", "Padroeira do Brasil"], ["2022-11-02", "Finados"], ["2022-11-15", "Proclamação da República"], ["2022-12-25", "Natal"] ]
        lista = []
        for feriado in feriados:
            date = dt.datetime.strptime(feriado[0], "%Y-%m-%d").date()
            lista.append(date)
        return(lista)
    
    def retorna_lista_dias_escalados(self):
        dias = []

        for fiscal in self.fiscaisbackup:
            dias.append(fiscal.retorna_dias_escalados())

        return dias

    def retorna_nome_dos_fiscais_escalados(self):
        # Retorna string
        fiscais = []
        for fiscal in self.fiscaisbackup:
            fiscais.append(fiscal.nome)
        return fiscais

    def gera_resumo_fiscais(self):
    
        fiscais_escalados = self.retorna_nome_dos_fiscais_escalados()

        dias_escalados = self.retorna_lista_dias_escalados()
        print(dias_escalados)
        lista_total_dias_escalados = [len(x) for x in dias_escalados]

        z = list(zip(fiscais_escalados, dias_escalados,lista_total_dias_escalados))
        df = pd.DataFrame(z, columns=['Fiscal','Dias Escalados','Total de Dias'])

        def foo(lista):
    
            string = ''
            for item in lista:
                string+= str(item)+ ', '
            return string
        df['Dias Escalados'] = df['Dias Escalados'].apply(foo)
        return df

    def converte_escala_em_dataframe(self,dic_escala,tipo):

        df = pd.DataFrame.from_dict(dic_escala, orient="index").reset_index()
        df = df.rename(columns={'index': 'Dia', 0:'fiscal 1',1:'fiscal 2'})
        df['fiscal 1'] = df['fiscal 1'].apply([lambda fobj: fobj.nome])
        df['fiscal 2'] = df['fiscal 2'].apply([lambda fobj: fobj.nome])
        df[tipo] = df['fiscal 1'] + ' e ' + df['fiscal 2']
        df = df.drop(['fiscal 1','fiscal 2'], 1)
        return df

    def gera_df_escalas(self, escalas):

        retorno = pd.DataFrame()

        df_fazenda = self.converte_escala_em_dataframe(escalas[0],"Plantão Fazenda")
        if(len(escalas) == 1):
            retorno = df_fazenda
    
        if (len(escalas) == 2):
            df_manha = self.converte_escala_em_dataframe(escalas[1],"Plantão Chat Manhã")
            df_manha.drop('Dia', axis=1, inplace=True)      
            retorno = pd.concat([df_fazenda,df_manha], axis = 1)
        
        if(len(escalas) == 3):

            df_manha = self.converte_escala_em_dataframe(escalas[1],"Plantão Chat Manhã")
            df_manha.drop('Dia', axis=1, inplace=True)  
            df_tarde = self.converte_escala_em_dataframe(escalas[2],"Plantão Chat Tarde")
            df_tarde.drop('Dia', axis=1, inplace=True) 
            df = pd.concat([df_tarde,df_manha], axis = 1)
            retorno = pd.concat([df_fazenda,df], axis =1)

        return retorno

    def esta_sendo_explorado(self, fiscal,lista_fiscais):

        lista_size_todos = [len(x.lista_dias_escalados) for x in lista_fiscais]
        meu_tamanho = len(fiscal.lista_dias_escalados)
        if meu_tamanho > min(lista_size_todos):
            return True       
             
        return False

    def magic_test(self, data):

        fiscais = self.fiscais.copy()
        fiscais_disponiveis = []
        demais_fiscais = []
        fiscais_de_ferias = []

        for fiscal in fiscais:
            if len(fiscal.lista_dias_ferias)==0:
                demais_fiscais.append(fiscal)
            else:
                fiscais_de_ferias.append(fiscal)

        # 1º Teste, tenta alocar um fiscal de férias
        for fiscal in fiscais:
            if self.esta_sendo_explorado(fiscal, fiscais_de_ferias) or (data in fiscal.lista_dias_ferias) or (data in fiscal.lista_dias_escalados):
                print(f'Fiscal {fiscal.nome} não esta disponivel no dia {data.day} - geral')
            else:
                fiscais_disponiveis.append(fiscal)
        # 2º Teste, se não conseguir alocar um fiscal de férias tenta os demais fiscais fazendo checagem do dia e se esta sendo explorado
        if len(fiscais_disponiveis) == 0:
            for fiscal in demais_fiscais:
                if self.esta_sendo_explorado(fiscal, demais_fiscais) or (data in fiscal.lista_dias_escalados):
                    print(f'Fiscal {fiscal.nome} não esta disponivel no dia {data.day} - demais fiscais')
                else:
                    fiscais_disponiveis.append(fiscal)
        # 3º teste, se mesmo assim não conseguir vai escolher um que está sendo explorado mesmo

        if len(fiscais_disponiveis) == 0:
            for fiscal in demais_fiscais:
                if (data in fiscal.lista_dias_escalados):
                    print(f'Fiscal {fiscal.nome} não esta disponivel no dia {data.day} - demais fiscais')
                else:
                    fiscais_disponiveis.append(fiscal)
        return fiscais_disponiveis

    def retorna_fiscal_disponivel(self,dia):
        fiscais_disponiveis = self.magic_test(dia)
        return random.choice(fiscais_disponiveis)
        
    def gera_escala(self):
        delta = dt.timedelta(days=1)
        data = self.start_date
        escalas = []
        feriados = self.retorna_lista_de_feriados()
        for i in range(self.n_escalas):
            escala = {}
            while self.start_date <= self.end_date:
                fiscais=[]
                weekno = self.start_date.weekday()
                if (weekno < 5) and not(self.start_date in feriados):
                    for i in range(self.n_fiscais):
                        fiscal = self.retorna_fiscal_disponivel(self.start_date)
                        fiscal.lista_dias_escalados.append(self.start_date)
                        fiscais.append(fiscal)
                    escala.update({self.start_date:fiscais})
                self.start_date += delta
            print(self.gera_resumo_fiscais())
            escalas.append(escala)
            self.start_date = data
            df = self.gera_df_escalas(escalas)
        return df