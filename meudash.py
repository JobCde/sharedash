#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px

# Carregar os dados
file_path = 'C:\\teste_python\\PROJETO_EY_VALE\\SERRA_NORTE_DADOS.xlsx'
df = pd.read_excel(file_path)
#%%
mapeamento_respostas = {
    'R_11j8hQsi6cjWXGP': {'função': 'Gerente_PM', 'área': 'Planejamento de Mina'},
    'R_5X6So1KaWVhaSU9': {'função': 'Gerente_OP', 'área': 'Operação'},
    'R_7ltAL3jBQ8LT0Nl': {'função': 'Operador(a), engenheiro(a), técnico(a), Geólogo(a), Instrutor(a)', 'área': 'COI'},
    'R_8168XV6kNeqnYf4': {'função': 'Coordenador_COI', 'área': 'COI'},
    'R_2oI4AeBzoFKIDiK': {'função': 'Coordenador_COI2', 'área': 'COI'},
    'R_3nVKNV9pYTuXGAn': {'função': 'Operador(a), engenheiro(a), técnico(a), Geólogo(a), Instrutor(a)', 'área': 'Planejamento de Mina'},
    'R_7PdrjLfqYFDsYex': {'função': 'Coordenador_OP', 'área': 'Operação'},
    'R_6ULGnkOrIjIr06l': {'função': 'Coordenador_PM', 'área': 'Planejamento de Mina'},
    'R_1N3pB730iIBSPG3': {'função': 'Geólogo', 'área': 'Geociência'},
    'R_3IZaW7ejNEtYpwW': {'função': 'Coordenador_OP2', 'área': 'Operação'},
    'R_7mOxbfeluKROnYX': {'função': 'Técnico', 'área': 'Perfuração e Desmonte'},
    'R_7gLAyYbbzABCJk5': {'função': 'Coordenador_Geo', 'área': 'Geociência'}
}

# Criar DataFrame auxiliar para associações de áreas e funções
associacoes = pd.DataFrame.from_dict(mapeamento_respostas, orient='index')
associacoes['codigo'] = associacoes.index

# Filtros
st.sidebar.title("Filtros")

# Filtro por Área de Atuação
area_selecionada = st.sidebar.selectbox("Selecione a Área de Atuação:", associacoes['área'].unique())

# Filtrar as funções disponíveis para a área selecionada
funcoes_disponiveis = associacoes[associacoes['área'] == area_selecionada]['função'].unique()
funcao_selecionada = st.sidebar.selectbox("Selecione a Função Atual:", funcoes_disponiveis)

# Obter os códigos dos respondentes que correspondem à área e função selecionadas
codigos_selecionados = associacoes[
    (associacoes['área'] == area_selecionada) &
    (associacoes['função'] == funcao_selecionada)
]['codigo'].values

# Filtrar o DataFrame original para exibir as respostas dos códigos selecionados
df_filtrado = df[['sku_questao', 'questao'] + list(codigos_selecionados)]
localidade_selecionada = "Serra Norte"

#%%
# Exibir o quadro de resumo para a função selecionada
st.write(f"**Função:** {funcao_selecionada}\n\n**Área**: {area_selecionada}")  # Linha 62

# Localidade e tempo na função
tempo_na_funcao = df_filtrado.iloc[2][codigos_selecionados[0]]  # Linha 63 (C4:N4)
tempo_no_iqm = df_filtrado.iloc[4][codigos_selecionados[0]]  # Linha 64 (C6:N6)

# Função para analisar o sentimento de todas as respostas combinadas
def analisar_sentimento_global(respostas):  # Linha 65
    palavras_positivas = ['bom', 'ótimo', 'excelente', 'positivo', 'melhor']
    palavras_neutras = ['adequado', 'neutro', 'ok', 'suficiente', 'parcialmente']
    palavras_canal_amarelo = ['preocupante', 'canal amarelo', 'precaução', 'alerta', 'Discordo']
    
    respostas_combinadas = ' '.join(str(resposta) for resposta in respostas).lower()  # Linha 66
    if any(palavra in respostas_combinadas for palavra in palavras_positivas):
        return "Positivo"
    elif any(palavra in respostas_combinadas for palavra in palavras_neutras):
        return "Neutro"
    elif any(palavra in respostas_combinadas for palavra in palavras_canal_amarelo):
        return "Canal Amarelo"
    else:
        return "Indefinido"

#%%
# Combinar todas as respostas do funcionário para análise
respostas_combinadas = [row[codigos_selecionados[0]] for index, row in df_filtrado.iterrows() if not pd.isna(row[codigos_selecionados[0]])]  # Linha 66
sentimento_global = analisar_sentimento_global(respostas_combinadas)  # Linha 67

# Exibir o quadro de resumo com destaque no dashboard
st.markdown(
    f"""
    <div style='border:2px solid #4CAF50; padding: 10px; background-color: #f9f9f9;'>
        <h3>Resumo da Função</h3>
        <p><strong>Localidade:</strong> {localidade_selecionada}</p>
        <p><strong>Tempo na Função:</strong> {tempo_na_funcao}</p>
        <p><strong>Tempo no Programa IQM:</strong> {tempo_no_iqm}</p>
        <p><strong>Sentimento Global:</strong> {sentimento_global}</p>
    </div>
    """, unsafe_allow_html=True
)
#%%
termo_busca = st.sidebar.text_input("Digite um termo para buscar nas perguntas:", "")

# Filtrar perguntas com base no termo de busca
if termo_busca:
    perguntas_filtradas = df_filtrado[df_filtrado['questao'].str.contains(termo_busca, case=False, na=False)]
else:
    perguntas_filtradas = df_filtrado

# Remover linhas com respostas "null"
perguntas_filtradas = perguntas_filtradas.dropna(subset=[codigos_selecionados[0]])
perguntas_filtradas = perguntas_filtradas[perguntas_filtradas[codigos_selecionados[0]] != "null"]

# Remover duplicatas
perguntas_filtradas = perguntas_filtradas.drop_duplicates(subset=['questao', codigos_selecionados[0]])

# Permitir seleção múltipla das perguntas filtradas
perguntas_selecionadas = st.sidebar.multiselect("Selecione as perguntas que deseja visualizar:", perguntas_filtradas['questao'].unique())

# Exibir as perguntas e respostas selecionadas ou todas se nada for selecionado
st.write("**Perguntas Selecionadas e Respostas**")
if perguntas_selecionadas:
     df_exibicao = perguntas_filtradas[perguntas_filtradas['questao'].isin(perguntas_selecionadas)]
else:
    df_exibicao = perguntas_filtradas

# Exibir as perguntas e respostas no formulário
for index, row in df_exibicao.iterrows():
    st.write(f"**{row['questao']}**")
    resposta = row[codigos_selecionados[0]]
    st.write(resposta)