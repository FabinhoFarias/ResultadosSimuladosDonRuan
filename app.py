import streamlit as st
import pandas as pd
import numpy as np

# =========================================================================
# ⚙️ CONFIGURAÇÕES E ESTADO DA SESSÃO
# =========================================================================
st.set_page_config(page_title="Dashboard de Gabaritos", layout="wide")

# Inicializa a variável que controla se a página privada foi liberada
if "privado_desbloqueado" not in st.session_state:
    st.session_state["privado_desbloqueado"] = False

# Função simples que valida a senha
def validar_senha():
    SENHA_CORRETA = "suasenha123" # 🔑 Defina a sua senha simples aqui
    
    if st.session_state["senha_digitada"] == SENHA_CORRETA:
        st.session_state["privado_desbloqueado"] = True
    else:
        st.error("Senha incorreta! ❌ Tente novamente.")

# =========================================================================
# 📊 PÁGINA 1: PÚBLICA (Gráficos Dinâmicos abertos para a Web)
# =========================================================================
def pagina_graficos_publicos():
    st.title("📊 Análise Dinâmica de Gabaritos")
    st.subheader("Dados públicos acessíveis para qualquer usuário")
    st.write("Utilize os filtros abaixo para explorar os resultados corrigidos.")

    # Exemplo de filtros dinâmicos
    col1, col2 = st.columns(2)
    with col1:
        turma = st.selectbox("Selecione a Turma:", ["Geral", "Turma A", "Turma B"])
    with col2:
        materia = st.selectbox("Selecione a Matéria:", ["Matemática", "Português", "Geral"])

    # Simulação de dados dinâmicos dos seus gabaritos
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Acertos', 'Erros', 'Brancos']
    )

    # Plotando os gráficos dinâmicos
    st.bar_chart(chart_data)
    
    st.info("💡 Dica: Passe o mouse sobre as barras para ver os dados exatos.")

# =========================================================================
# 🔒 PÁGINA 2: PRIVADA (Exige apenas uma senha simples)
# =========================================================================
def pagina_administracao_privada():
    st.title("🔒 Área Administrativa Restrita")

    # --- A BARREIRA DE SEGURANÇA ---
    # Se o usuário NÃO digitou a senha correta ainda, mostra o input e TRAVA o app
    if not st.session_state["privado_desbloqueado"]:
        st.warning("Esta página contém dados sensíveis. Por favor, identifique-se.")
        
        st.text_input(
            "Digite a senha de acesso:", 
            type="password", 
            key="senha_digitada", 
            on_change=validar_senha
        )
        
        # O st.stop() é o segredo: ele corta a execução aqui. 
        # Ninguém consegue ver o que está escrito abaixo desta linha sem a senha.
        st.stop() 

    # --- CONTEÚDO PRIVADO (Só roda se passar pelo st.stop() acima) ---
    st.success("🔓 Acesso concedido com sucesso!")
    st.subheader("Painel de Controle e Dados Brutos")
    
    st.write("Aqui você pode colocar tabelas de alunos, logs de correção ou botões de exclusão.")
    
    # Exemplo de tabela privada
    dados_privados = pd.DataFrame({
        'Aluno': ['João Silva', 'Maria Santos', 'Pedro Souza'],
        'Nota': [8.5, 9.0, 6.5],
        'JSON Gerado': ['respostas_1.json', 'respostas_2.json', 'respostas_3.json']
    })
    st.dataframe(dados_privados, use_container_width=True)

    # Botão opcional para o administrador "deslogar"/bloquear a página de novo
    if st.button("Bloquear Página novamente (Sair)"):
        st.session_state["privado_desbloqueado"] = False
        st.rerun()

# =========================================================================
# 🗺️ ROTEADOR DE NAVEGAÇÃO MULTIPÁGINAS
# =========================================================================
# O st.navigation cria o menu lateral automaticamente na mesma URL
pg = st.navigation([
    st.Page(pagina_graficos_publicos, title="Gráficos Públicos", icon="📊"),
    st.Page(pagina_administracao_privada, title="Área Privada", icon="🔒")
])

# Executa a página selecionada pelo usuário no menu lateral
pg.run()