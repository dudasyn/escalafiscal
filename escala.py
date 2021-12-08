import random
import datetime as dt
import pandas as pd

class Fiscal:
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

    def resumo(self):
        retorno = '' 
        retorno = f'Fiscal - {self.nome}\n'
        for dias in self.lista_dias_escalados:
            retorno += retorno + f' - {dias}'

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

    def checa_fiscal_ja_escalado_no_dia(self,fiscal, dia):
        if dia in fiscal.lista_dias_escalados:
            return True
        else:
            return False

    def checa_fiscal_ferias(self, fiscal, dia):
        lista_de_ferias = fiscal.checa_ferias()
        if dia.day in lista_de_ferias:
            return True
        else:
            return False

    def fiscal_super_alocado(self,f):
        # ou seja é maior que os outros
        meu_tamanho = len(f.lista_dias_escalados)
        lista_size_todos = []
        for fiscal in self.fiscais:

            lista_size_todos.append(len(fiscal.lista_dias_escalados))

        if (meu_tamanho == min(lista_size_todos)):
            self.fiscais.remove(f)
            return False
        else:
            return True
        
    def checa_fiscal_disponivel(self, fiscal, dia):
        # Pro fiscal estar disponivel para seleção ele não pode estar de férias
        # não pode estar escalado no dia
        # e se tiver fiscal escalado para um numero menor de dias que ele, ele também não estará disponivel (falta implementar)
        #self.fiscal_escalado_menos_dias(fiscal)
        if (self.checa_fiscal_ja_escalado_no_dia(fiscal, dia) == True) or (self.checa_fiscal_ferias(fiscal,dia) == True) or (self.fiscal_super_alocado(fiscal) == True):
            # Escolhe outro
            return False
        else:
            return True

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
        z = list(zip(fiscais_escalados, dias_escalados))
        df = pd.DataFrame(z, columns=['Fiscal','Dias Escalados'])

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
    
    def retorna_fiscal_disponivel(self, data):

        fiscalrandom = random.choice(self.fiscais)

        while (self.checa_fiscal_disponivel(fiscalrandom, data) == False):
            self.fiscais.remove(fiscalrandom)
            if (len(self.fiscais) == 0):
                self.fiscais = self.fiscaisbackup.copy()
            fiscalrandom = random.choice(self.fiscais)

        return fiscalrandom

    def retorna_lista_de_feriados(self):
        feriados = [["2022-01-01", "Confraternização Universal"], ["2022-04-21", "Tiradentes"], ["2022-05-01", "Dia do trabalhador"], ["2022-09-07", "Independência"], ["2022-10-12", "Padroeira do Brasil"], ["2022-11-02", "Finados"], ["2022-11-15", "Proclamação da República"], ["2022-12-25", "Natal"] ]
        lista = []
        for feriado in feriados:
            date = dt.datetime.strptime(feriado[0], "%Y-%m-%d").date()
            lista.append(date)
        return(lista)
    
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
                        if (len(self.fiscais) == 0):
                            self.fiscais = self.fiscaisbackup.copy()
                        fiscal = self.retorna_fiscal_disponivel(self.start_date)
                        fiscal.lista_dias_escalados.append(self.start_date)
                        fiscais.append(fiscal)
                        
                    escala.update({self.start_date:fiscais})
                self.start_date += delta
            escalas.append(escala)
            self.start_date = data
            df = self.gera_df_escalas(escalas)
        return df