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


    def calcula_desvio(self,data):
        lista_desvios = []
        
        for dia_escalado in self.lista_dias_escalados:
            lista_desvios.append(abs(dia_escalado.day - data.day))

        if(len(lista_desvios)==0):
            return 0
        return min(lista_desvios)            

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
        feriados = [["2023-01-01", "Confraternização Universal"], ["2023-04-21", "Tiradentes"], ["2023-02-28","Carnaval - Ponto Facultativo"],["2023-03-01","Carnaval - Ponto Facultativo"],["2023-04-15","Paixão de Cristo"],["2023-04-21","Tiradentes"], ["2023-03-01","Carnaval - Ponto Facultativo"],["2023-05-01", "Dia do trabalhador"], ["2023-09-07", "Independência"], ["2023-06-16","Corpus Chisti"],["2023-10-12", "Padroeira do Brasil"], ["2023-11-02", "Finados"], ["2023-11-15", "Proclamação da República"], ["2023-12-25", "Natal"]]
                    #28 de outubro, Dia do Servidor Público – art. 236 da Lei nº 8.112, de 11 de dezembro de 1990, (ponto facultativo);       
        # ["2023-03-02","Carnaval - Quarta de Cinzas"] - tirei a quarta de cinzas
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

    def retorna_fiscal_com_maximo_desvio(self, fiscais_disponiveis, data):
    
        maior_desvio = 0
        print(f'Lista de fiscais disponiveis pro dia {data}')
        for fiscal in fiscais_disponiveis:
            desvio = fiscal.calcula_desvio(data)

            print(f'Fiscal {fiscal.nome} e seu desvio é {desvio}')
            
            if (desvio > maior_desvio):
                maior_desvio = desvio
                
        if (maior_desvio == 0):
            return random.choice(fiscais_disponiveis)
        else:
            random.shuffle(fiscais_disponiveis)
            for fiscal in fiscais_disponiveis:
                if fiscal.calcula_desvio(data) == maior_desvio:
                    print(f'Fiscal com maior desvio é o {fiscal.nome} que tem o desvio de {maior_desvio}')
                    print('')
                    return fiscal

    def esta_sendo_explorado(self, fiscal,lista_fiscais):

        lista_size_todos = [len(x.lista_dias_escalados) for x in lista_fiscais]
        meu_tamanho = len(fiscal.lista_dias_escalados)
        if meu_tamanho > min(lista_size_todos):
            return True       
             
        return False
    def retorna_fiscal_disponivel(self, data):

        fiscais = self.fiscais.copy()
        fiscais_disponiveis = []
        demais_fiscais = []
        fiscais_de_ferias = []
        
        # Depois trocar por filter ou list comprehension se der
        for fiscal in fiscais:
            if len(fiscal.lista_dias_ferias)==0:
                demais_fiscais.append(fiscal)
            else:
                fiscais_de_ferias.append(fiscal)

        # 1º Teste, tento alocar todos os fiscais desde que não estejam sendo explorados, não estejam de férias ou não tenham sido escalados no dia
        random.shuffle(fiscais)
        for fiscal in fiscais:
            fiscal_indisponivel = self.esta_sendo_explorado(fiscal, demais_fiscais) or (data in fiscal.lista_dias_ferias) or (data in fiscal.lista_dias_escalados) 
            if (fiscal_indisponivel == False):
                fiscais_disponiveis.append(fiscal)

        if (len(fiscais_disponiveis) == 0):
            random.shuffle(demais_fiscais)
            for fiscal in demais_fiscais:
                fiscal_indisponivel = (data in fiscal.lista_dias_escalados) 
                if (fiscal_indisponivel == False):
                    fiscais_disponiveis.append(fiscal)

        return self.retorna_fiscal_com_maximo_desvio(fiscais_disponiveis, data)
       
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
