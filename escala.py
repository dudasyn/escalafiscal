import random
import datetime as dt
import pandas as pd

class Fiscal:
    dias_na_escala = 0
    def __init__(self, nome, inicio_ferias, dias_de_ferias, lista_dias_escalados=[]):
        self.nome = nome
        self.inicio_ferias = inicio_ferias
        self.dias_de_ferias = dias_de_ferias
        self.lista_dias_escalados = list(lista_dias_escalados)


    def retorna_dias_escalados(self):
        dias = []
        for data in self.lista_dias_escalados:
            dias.append(data.day)

        return(dias)

    def checa_ferias(self):
        if pd.isnull(self.dias_de_ferias):
            self.dias_de_ferias = 0
            return []
        
        date_list = [x.day for x in [self.inicio_ferias + dt.timedelta(days=x) for x in range(int(self.dias_de_ferias))]]
        return date_list
        
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

            df_manha = self.converte_escala_em_dataframe(escalas[1],"Plantão Manhã")
            df_manha.drop('Dia', axis=1, inplace=True)  
            df_tarde = self.converte_escala_em_dataframe(escalas[2],"Plantão Tarde")
            df_tarde.drop('Dia', axis=1, inplace=True) 
            df = pd.concat([df_tarde,df_manha], axis = 1)
            retorno = pd.concat([df_fazenda,df], axis =1)

        return retorno
    
    def checa_fiscal_disponivel(self, fiscal, dia):
        # Primeiro verifico se o fiscal está de férias se ele estiver de férias não adianta nem verificar outra coisa pq ele nao vai estar disponivel
        lista_de_ferias = fiscal.checa_ferias()
        if dia.day in lista_de_ferias:
            return False
        else:
            # Agora que eu sei que ele não esta de ferias, posso aloca-lo, mas tenho que ver se ele já foi alocado no dia
            if dia in fiscal.lista_dias_escalados:
                return False
            else:
                # agora que sei que ele nao esta de ferias nem foi alocado neste dia posso escala-lo mas
                # tenho que verificar se ele é candidato na lista
                meu_tamanho = len(fiscal.lista_dias_escalados)

                lista_size_todos = []

                for fiscal in self.fiscaisbackup:
                    lista_size_todos.append(len(fiscal.lista_dias_escalados))

                if (meu_tamanho == min(lista_size_todos)):
                    #self.fiscais.remove(fiscal)
                    return True
                else:
                    # Se ele não for candidato nesta lista eu tenho que remover ele e restaurar a lista pra começar de novo
                    if (len(self.fiscais) == 0):
                        self.fiscais = self.fiscaisbackup.copy()
                    return False


    def retorna_fiscal_disponivel(self, data):

        random.shuffle(self.fiscais)
        fiscalrandom = self.fiscais.pop()

        if (len(self.fiscais) == 0):
            self.fiscais = self.fiscaisbackup.copy()

        while (self.checa_fiscal_disponivel(fiscalrandom, data) == False):
            random.shuffle(self.fiscais)
            fiscalrandom = self.fiscais.pop()
            if (len(self.fiscais) == 0):
                self.fiscais = self.fiscaisbackup.copy()

        return fiscalrandom


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