import streamlit as st
import pandas as pd
import numpy as np
import os

# =========================================================================
# ⚙️ CONFIGURAÇÕES, GABARITOS E ESTADO DA SESSÃO
# =========================================================================
st.set_page_config(page_title="Dashboard de Gabaritos", layout="wide")

CSV_FILE = "resultados.csv"

# 🇬🇧/🇪🇸 GABARITOS DE LINGUAGENS (Separados pelas 5 primeiras questões)
GABARITO_ING_5            = "ceeca" # 5 primeiras questões de Inglês
GABARITO_ESP_5            = "addac" # 5 primeiras questões de Espanhol
GABARITO_LINGUAGENS_RESTO = "baadbcdebbeaedbbadeaecbebaeceacceebeceab" # Questões 6 a 45 (40 caracteres)

# 🎯 OUTRAS ÁREAS (45 caracteres cada)
GABARITO_HUMANAS    = "cceceaadcbcaecdddddaecaabbacecdbcacdcbdedadbd"

GABARITO_NATUREZA   = "caecbdbbcedbcbcbaedcbacabcdbdccececcbdaaecbcb"

GABARITO_MATEMATICA = "abcaebbdcadccabeaeddbddbccccaeedceccabbcecacd"

if "privado_desbloqueado" not in st.session_state:
    st.session_state["privado_desbloqueado"] = False

def validar_senha():
    SENHA_CORRETA = "suasenha123"
    if st.session_state["senha_digitada"] == SENHA_CORRETA:
        st.session_state["privado_desbloqueado"] = True
    else:
        st.error("Senha incorreta! ❌ Tente novamente.")

def carregar_dados():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")
            return None
    return None

# =========================================================================
# 📊 PÁGINA 1: PÚBLICA (Gráficos por Questão com Filtro de Idioma)
# =========================================================================

def pagina_graficos_publicos():
    st.title("📊 Análise Dinâmica de Acertos por Questão")
    st.subheader("Comparação dinâmica com o gabarito oficial")
    
    df = carregar_dados()
    if df is None:
        st.warning("⚠️ O arquivo `resultados.csv` não foi localizado ou está vazio.")
        return

    # Filtros por colunas existentes
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        opcoes_serie = ["Geral"] + list(df['Série:'].dropna().unique()) if 'Série:' in df.columns else ["Geral"]
        serie = st.selectbox("Selecione a Série:", opcoes_serie)
    with col_f2:
        area_selecionada = st.selectbox("Selecione a Área para ver o Gráfico:", ["Linguagens", "Humanas", "Natureza", "Matematica"])

    # Filtragem por Série
    df_filtrado = df.copy()
    if serie != "Geral" and 'Série:' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Série:'] == serie]

    if area_selecionada not in df_filtrado.columns:
        st.error(f"A coluna '{area_selecionada}' não foi encontrada no CSV.")
        return

    st.markdown("---")
    st.markdown(f"### 📈 Estatísticas de Acertos: **{area_selecionada}**")

    questoes_labels = []
    lista_acertos = []
    lista_erros = []
    lista_brancos = []

    # --- FLUXO ESPECIAL PARA A ÁREA DE LINGUAGENS ---
    if area_selecionada == "Linguagens":
        
        # 1. Processa as 5 primeiras questões duplicando por Idioma (ING e ESP separados)
        for i in range(5):
            num_questao = i + 1
            
            # --- SUB-PASSO A: INGLÊS ---
            letra_ing = GABARITO_ING_5.lower()[i]
            acertos_ing, erros_ing, brancos_ing = 0, 0, 0
            
            # --- SUB-PASSO B: ESPANHOL ---
            letra_esp = GABARITO_ESP_5.lower()[i]
            acertos_esp, erros_esp, brancos_esp = 0, 0, 0

            for idx, row in df_filtrado.iterrows():
                if pd.isna(row[area_selecionada]):
                    continue
                    
                resposta_aluno = str(row[area_selecionada]).strip().lower()
                idioma_aluno = str(row.get('Idioma', 'ing')).strip().lower()
                
                if len(resposta_aluno) > i:
                    letra_marcada = resposta_aluno[i]
                    
                    # 🚨 NOVA REGRA: Se a resposta for 'x', ignora completamente e pula o aluno
                    if letra_marcada == 'x':
                        continue
                    
                    if idioma_aluno == "esp":
                        if letra_marcada == letra_esp:
                            acertos_esp += 1
                        elif letra_marcada in ['', ' ']:
                            brancos_esp += 1
                        else:
                            erros_esp += 1
                    else:  # Caso seja 'ing' ou indefinido
                        if letra_marcada == letra_ing:
                            acertos_ing += 1
                        elif letra_marcada in ['', ' ']:
                            brancos_ing += 1
                        else:
                            erros_ing += 1

            # Adiciona os dados de Inglês
            questoes_labels.append(f"Q{num_questao:02d}-ING ({letra_ing.upper()})")
            lista_acertos.append(acertos_ing)
            lista_erros.append(erros_ing)
            lista_brancos.append(brancos_ing)
            
            # Adiciona os dados de Espanhol
            questoes_labels.append(f"Q{num_questao:02d}-ESP ({letra_esp.upper()})")
            lista_acertos.append(acertos_esp)
            lista_erros.append(erros_esp)
            lista_brancos.append(brancos_esp)

        # 2. Processa as questões de 6 a 45 unificando todos os alunos
        for i in range(5, 45):
            num_questao = i + 1
            letra_correta = GABARITO_LINGUAGENS_RESTO.lower()[i - 5]
            
            acertos, erros, brancos = 0, 0, 0
            
            for idx, row in df_filtrado.iterrows():
                if pd.isna(row[area_selecionada]):
                    brancos += 1
                    continue
                    
                resposta_aluno = str(row[area_selecionada]).strip().lower()
                
                if len(resposta_aluno) > i:
                    letra_marcada = resposta_aluno[i]
                    
                    # 🚨 NOVA REGRA: Se a resposta for 'x', ignora completamente e pula o aluno
                    if letra_marcada == 'x':
                        continue
                        
                    if letra_marcada == letra_correta:
                        acertos += 1
                    elif letra_marcada in ['', ' ']:
                        brancos += 1
                    else:
                        erros += 1
                else:
                    brancos += 1

            questoes_labels.append(f"Q{num_questao:02d} ({letra_correta.upper()})")
            lista_acertos.append(acertos)
            lista_erros.append(erros)
            lista_brancos.append(brancos)

    # --- FLUXO PADRÃO PARA AS OUTRAS ÁREAS (HUMANAS, NATUREZA, MATEMÁTICA) ---
    else:
        mapa_outros = {"Humanas": GABARITO_HUMANAS, "Natureza": GABARITO_NATUREZA, "Matematica": GABARITO_MATEMATICA}
        gabarito_oficial = mapa_outros[area_selecionada].lower()

        for i in range(45):
            num_questao = i + 1
            letra_correta = gabarito_oficial[i]
            
            acertos, erros, brancos = 0, 0, 0
            
            for idx, row in df_filtrado.iterrows():
                if pd.isna(row[area_selecionada]):
                    brancos += 1
                    continue
                    
                resposta_aluno = str(row[area_selecionada]).strip().lower()
                
                if len(resposta_aluno) > i:
                    letra_marcada = resposta_aluno[i]
                    
                    # 🚨 NOVA REGRA: Se a resposta for 'x', ignora completamente e pula o aluno
                    if letra_marcada == 'x':
                        continue
                        
                    if letra_marcada == letra_correta:
                        acertos += 1
                    elif letra_marcada in ['', ' ']:
                        brancos += 1
                    else:
                        erros += 1
                else:
                    brancos += 1

            questoes_labels.append(f"Q{num_questao:02d} ({letra_correta.upper()})")
            lista_acertos.append(acertos)
            lista_erros.append(erros)
            lista_brancos.append(brancos)

    # --- MONTAGEM DO DATAFRAME E EXIBIÇÃO DO GRÁFICO INTERATIVO ---
    df_grafico = pd.DataFrame({
        "Acertos": lista_acertos,
        "Brancos": lista_brancos,
        "Erros": lista_erros
    }, index=questoes_labels)

    # Renderiza o gráfico interativo atualizado
    st.bar_chart(df_grafico, height=450)
    st.info("💡 Observação: Alunos marcados com 'x' em uma determinada questão foram completamente removidos da base de cálculo dela, reduzindo proporcionalmente o tamanho da sua barra correspondente.")


# =========================================================================
# 🔒 PÁGINA 2: PRIVADA (Quantidade de Acertos Inteligente por Aluno)
# =========================================================================

def pagina_administracao_privada():
    st.title("🔒 Área Administrativa Restrita")

    if not st.session_state["privado_desbloqueado"]:
        st.warning("Esta página contém dados sensíveis. Por favor, identifique-se.")
        st.text_input("Digite a senha de acesso:", type="password", key="senha_digitada", on_change=validar_senha)
        st.stop() 

    st.success("🔓 Acesso concedido com sucesso!")
    
    st.markdown("---")
    st.subheader("📋 Classificação de Alunos por Área")
    
    df = carregar_dados()
    if df is not None:
        col_nome = 'Nome Completo' if 'Nome Completo' in df.columns else df.columns[0]
        lista_resultados_finais = []
        
        # Loop linha por linha avaliando cada aluno individualmente
        for idx, row in df.iterrows():
            nome_aluno = row[col_nome]
            serie_aluno = row.get('Série:', 'N/A')
            idioma_aluno = str(row.get('Idioma', 'ing')).strip().lower() # Padrão inglês caso falte
            
            acertos_por_area = {
                "Nome": nome_aluno,
                "Série": serie_aluno,
                "Idioma": idioma_aluno.upper(),
                "Acertos Linguagens": 0,
                "Acertos Humanas": 0,
                "Acertos Natureza": 0,
                "Acertos Matematica": 0
            }
            
            for area in ["Linguagens", "Humanas", "Natureza", "Matematica"]:
                if area in df.columns and pd.notna(row[area]):
                    resposta_aluno = str(row[area]).strip().lower()
                    
                    # Definição dinâmica do gabarito para a matéria de Linguagens baseada no idioma do aluno
                    if area == "Linguagens":
                        if idioma_aluno == "esp":
                            gabarito_oficial = (GABARITO_ESP_5 + GABARITO_LINGUAGENS_RESTO).lower()
                        else:
                            gabarito_oficial = (GABARITO_ING_5 + GABARITO_LINGUAGENS_RESTO).lower()
                    else:
                        mapa_gabaritos = {"Humanas": GABARITO_HUMANAS, "Natureza": GABARITO_NATUREZA, "Matematica": GABARITO_MATEMATICA}
                        gabarito_oficial = mapa_gabaritos[area].lower()
                    
                    contagem_acertos = 0
                    for i in range(min(len(resposta_aluno), 45)):
                        if resposta_aluno[i] == 'x':  # Ignora se o aluno marcou X
                            continue
                        if resposta_aluno[i] == gabarito_oficial[i]:
                            contagem_acertos += 1
                            
                    acertos_por_area[f"Acertos {area}"] = contagem_acertos
            
            lista_resultados_finais.append(acertos_por_area)
            
        df_notas = pd.DataFrame(lista_resultados_finais)
        
        # --- FILTRO DE ORDENAÇÃO (RANKING POR ÁREA) ---
        ordenar_por = st.selectbox(
            "🏆 Classificar ranking por:",
            ["Acertos Linguagens", "Acertos Humanas", "Acertos Natureza", "Acertos Matematica", "Nome"]
        )
        
        # Se for por área, ordena do maior para o menor (False). Se for por nome, ordem alfabética (True).
        ordem_ascendente = True if ordenar_por == "Nome" else False
        df_notas = df_notas.sort_values(by=ordenar_por, ascending=ordem_ascendente).reset_index(drop=True)
        
        # Adiciona uma coluna visual de posição no ranking se estiver ordenando por notas
        if ordenar_por != "Nome":
            df_notas.index = df_notas.index + 1
            df_notas.index.name = "Posição"
            
        # Exibe a planilha formatada
        st.dataframe(df_notas, use_container_width=True)
        
        # Botão de Download das notas ordenadas
        csv_notas = df_notas.to_csv(index=True).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Notas Consolidadas", data=csv_notas, file_name="ranking_alunos_enem.csv", mime="text/csv")
    else:
        st.info("Nenhum dado cadastrado até o momento.")

    if st.button("Bloquear Página novamente (Sair)"):
        st.session_state["privado_desbloqueado"] = False
        st.rerun()
# =========================================================================
# 🗺️ ROTEADOR DE NAVEGAÇÃO MULTIPÁGINAS
# =========================================================================
pg = st.navigation([
    st.Page(pagina_graficos_publicos, title="Gráficos Públicos", icon="📊"),
    st.Page(pagina_administracao_privada, title="Área Privada", icon="🔒")
])

pg.run()