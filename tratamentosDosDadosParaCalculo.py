import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as op
from LacsLalur.lacsLalurAntesInoTributarias import LacsLalurCSLL




class FiltrandoDadosParaCalculo(LacsLalurCSLL):
    _widget_counter = 0


    @st.cache_data(ttl='1d', show_spinner=False)
    def load_excel_file(file_path):
        return pd.read_excel(file_path)
    
    st.cache_data(ttl='1d')
    def __init__(self, data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file):
        self.data = None 
        super().__init__(data, lacs_file, lalur_file, ecf670_file, ec630_file)
        self.reservEstatuaria = 0.0
        self.resContingencia = 0.0
        self.reserExp = 0.0
        self.outrasResLuc = 0.0
        self.lucroAcumulado = 0.0
        self.reservLucro = 0.0
        


        #---Inviolavel Seguranca
        # self.l100 = pd.read_excel(r'C:\Users\lauro.loyola\Desktop\JPC\Inviolavel Seguranca\Declarações Federais - ECF - L - Lucro Real - Lucro Líquido - L030, L100 - Balanço Patrimonial - Lucro Real.xlsx')
        # self.l300 = pd.read_excel(r'C:\Users\lauro.loyola\Desktop\JPC\Inviolavel Seguranca\Declarações Federais - ECF - L - Lucro Real - Lucro Líquido - L030, L300 - Demonstração do Resultado do Exercício - Lucro Real.xlsx')


        #---ORBENK
        self.l100 = FiltrandoDadosParaCalculo.load_excel_file(l100_file)
        self.l300 = FiltrandoDadosParaCalculo.load_excel_file(l300_file)


        self.resultsCalcJcp = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"]) 
        self.lucro_periodo_value = 0

    def nomeDasEmpresas():
        l100 = self.l100
        tabelaEmpresas = pd.DataFrame(columns=['CNPJ','Nome da Empresa'])
        
        self.nomeEmpresa = ''
        if l100['CNPJ'] == '82513490000194':
            self.nomeEmpresa = 'PROFISER SERVIÇOS PROFISSIONAIS LTDA'

        elif l100['CNPJ'] == '10332516000197':    
            self.nomeEmpresa = 'ORBENK TERCEIRIZAÇÃO E SERVIÇOS LTDA'

        elif l100['CNPJ'] == '04048628000118':
            self.nomeEmpresa = 'INVIOLAVEL SEGURANÇA ELETRONICA LTDA'
        else:
            self.nomeEmpresa = 'Empresa não encontrada'              



    st.cache_data(ttl='1d')
    def set_date(self, data):
        self.data = data         
    
    st.cache_data(ttl='1d')
    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&(
            l100['Descrição Conta Referencial']=='Capital Subscrito de Domiciliados e Residentes no País')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capSocial = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Social", "Value": self.capSocial}])], ignore_index=True)

    st.cache_data(ttl='1d')
    def capitalIntegralizador(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.01.01.21')&(
            l100['Conta Referencial']=='2.03.01.02.10')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capitalIntegra = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    
    st.cache_data(ttl='1d')
    def ReservasDeCapital(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.01.99')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.reservaCapital = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Capital", "Value": self.reservaCapital}])], ignore_index=True)

    st.cache_data(ttl='1d')        
    def ajustesAvalPatrimonial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Descrição Conta Referencial']=='Reavaliação de Ativos Próprios')]
        self.ajusteAvaPatrimonial = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Avaliação Patrimonial", "Value": self.ajusteAvaPatrimonial}])], ignore_index=True)

    st.cache_data(ttl='1d')                
    def lucrosAcumulados(self):

        l100 = self.l100
        l300 = self.l300

        lucroperio = l300[(l300['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (l300['Data Inicial'].str.contains(self.data))&(
            l300['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        lucroperio = lucroperio['Vlr Saldo Final'].sum()

        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.01')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        
        self.lucroAcumulado = np.where(l100['Vlr Saldo Final'].sum()-lucroperio<0,0,l100['Vlr Saldo Final'].sum()-lucroperio)

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
      
    st.cache_data(ttl='1d')
    def ajustesExerAnteriores(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.10')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.ajustExercAnt = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Exercícios Anteriores", "Value": self.ajustExercAnt}])], ignore_index=True)

    st.cache_data(ttl='1d')
    def lucroPeriodo(self):
        l100 = self.l300
        l100 = l100[(l100['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.lucro_periodo_value = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)

    st.cache_data(ttl='1d')
    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservaCapital,self.lucroAcumulado,self.reservLucro))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    


    # def ReservaLegal(self):
    #     key = f'reservaLegal{self.data}'
        

    #     if key not in st.session_state:
    #         st.session_state[key] = 0.0

    #     st.session_state[key] = st.session_state[key]
    #     self.reservLegal = st.number_input('Digite o valor da Reserva Legal', key=key, value=st.session_state[key])
    #     self.reservLucro = self.reservLegal
    #     self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)
    def update_totalfinsparaJPC(self):
        self.totalJSPC = self.capSocial + self.reservaCapital + self.lucroAcumulado + self.reservLucro
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    
    def update_reservas(self):
        self.reservLucro = self.reservLegal + self.reservEstatuaria + self.resContingencia + self.reserExp + self.outrasResLuc
        self.resultsTabelaFinal.loc[self.resultsTabelaFinal['Operation'] == 'Reservas de Lucros', 'Value'] = self.reservLucro

    def ReservaLegal(self):
        key = f'reservaLegal{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.reservLegal = st.number_input('Digite o valor da Reserva Legal', key=key, value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)
        self.update_totalfinsparaJPC()  # <--- Call the new method here



    def ReservaEstatutária(self):
        key = f'reservaEsta{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]

        self.reservEstatuaria =  st.number_input('Digite o valor da Reserva Estatuaria',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva Estatutária", "Value": self.reservEstatuaria}])], ignore_index=True)
    

    def ReservaContingencias(self):
        key = f'reservaCont{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]

        self.resContingencia =  st.number_input('Digite o valor da Reserva Reserva de contingências',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva para Contingências", "Value": self.resContingencia}])], ignore_index=True)
    

    def ReservaExpansao(self):
        key = f'reservaExpans{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.reserExp =  st.number_input('Digite o valor da Reserva de Expansão',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation":"Reserva de Lucros para Expansão", "Value": self.reserExp}])], ignore_index=True)
    

    def OutrasReservasLucros(self):
        key = f'reservaOutras{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.outrasResLuc = st.number_input('Digite o valor Outras reservas de lucros',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Outras Reservas de Lucros", "Value": self.outrasResLuc}])], ignore_index=True)

    st.cache_data(ttl='1d')
    def ReservasLucros(self):
        self.reservLucro = self.reservLegal + self.reservEstatuaria + self.resContingencia + self.reserExp + self.outrasResLuc
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Lucros", "Value": self.reservLucro}])], ignore_index=True)
    
    st.cache_data(ttl='1d')
    def acoesTesouraria(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.12')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.acosTesouraria = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)
    
    st.cache_data(ttl='1d')
    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    st.cache_data(ttl='1d')
    def PrejuizoPeriodo(self):

  
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Exercícios Anteriores", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    st.cache_data(ttl='1d')    
    def prejuizosAcumulados(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízos Acumulados", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    st.cache_data(ttl='1d')
    def runPipe(self):

        self.capitalSocial()
        self.capitalIntegralizador()
        self.ReservasDeCapital()
        self.ajustesAvalPatrimonial()

        self.ReservaLegal()
        self.ReservaEstatutária()
        self.ReservaContingencias()
        self.ReservaExpansao()
        self.OutrasReservasLucros()
        self.ReservasLucros()

        self.acoesTesouraria()
        self.contPatrimonioNaoClass()
        #self.PrejuizoPeriodo()
        self.prejuizosAcumulados()

        self.acoesTesouraria()
        self.lucrosAcumulados()
        self.ajustesExerAnteriores()
        self.lucroPeriodo()
        self.TotalFinsCalcJSPC()
        

        self.resultsCalcJcp['Value'] = self.resultsCalcJcp['Value'].apply(lambda x: "{:,.2f}".format(x))
        st.dataframe(self.resultsCalcJcp)

    st.cache_data(ttl='1d')
    def runPipeFinalTable(self):

        self.lucrosAcumulados()
        self.lucroPeriodo()
        self.exclusoes()
        self.adicoes()
        self.lucroAntesCSLL()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()   
        self.LucroLiquidoAntesIRPJ()
        self.baseCSLL()

        self.resultsTabelaFinal['Value'] = self.resultsTabelaFinal['Value'].apply(lambda x: "{:,.2f}".format(x))
        st.dataframe(self.resultsTabelaFinal)

# if __name__=='__main__':

#     jcp = FiltrandoDadosParaCalculo() 

#     jcp.runPipeFinalTable()
#     #jcp.runPipeFinalTabelLacsLalur()
#     st.subheader('Calculo JCP')
#     jcp.runPipe()
#     st.subheader('Lacs e Lalur ')
#     jcp.runPipeLacsLalurIRPJ()
#     jcp.runPipeLacsLalurCSLL()

