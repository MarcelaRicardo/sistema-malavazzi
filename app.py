import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página e layout do sistema
st.set_page_config(page_title="SisCL Malavazzi", layout="wide", page_icon="👁️")

# ----------------- 🔒 TELA DE SEGURANÇA E ACESSO -----------------
SENHA_CORRETA = "malavazzi123" 

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.subheader("🔑 SisCL Malavazzi - Controle de Lentes de Contato")
    st.write("Setor de Enfermagem em Oftalmologia")
    senha_digitada = st.text_input("Digite a senha de acesso:", type="password", placeholder="Digite a senha da clínica aqui")
    if st.button("Entrar no Sistema"):
        if senha_digitada == SENHA_CORRETA:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta! Acesso negado por segurança.")
    st.stop()

# ----------------- 📊 BANCO DE DADOS LOCAL EM MEMÓRIA -----------------
if "pacientes" not in st.session_state:
    st.session_state["pacientes"] = pd.DataFrame(columns=['id', 'prontuario', 'nome', 'telefone', 'email', 'endereco', 'medico', 'refracao', 'grau_lente', 'tipo_lente', 'fornecedor', 'periodo_troca', 'data_cadastro'])
if "estoque" not in st.session_state:
    st.session_state["estoque"] = pd.DataFrame(columns=['id', 'item', 'tipo', 'fornecedor', 'qtd', 'qtd_minima', 'validade', 'preco_custo', 'preco_venda', 'nota_fiscal'])
if "agenda" not in st.session_state:
    st.session_state["agenda"] = pd.DataFrame(columns=['id', 'data', 'paciente', 'tipo_procedimento', 'medico', 'status', 'anotacoes'])
if "vendas" not in st.session_state:
    st.session_state["vendas"] = pd.DataFrame(columns=['id', 'paciente_nome', 'item', 'valor', 'forma_pagamento', 'nota_fiscal', 'data_venda', 'proxima_renovacao'])
if "pedidos" not in st.session_state:
    st.session_state["pedidos"] = pd.DataFrame(columns=['id', 'fornecedor', 'tipo_pedido', 'item', 'quantidade', 'status', 'data_pedido'])
if "caixa" not in st.session_state:
    st.session_state["caixa"] = pd.DataFrame(columns=['id', 'tipo', 'descricao', 'valor', 'data'])
if "notas_fiscais" not in st.session_state:
    st.session_state["notas_fiscais"] = pd.DataFrame(columns=['id', 'cnpj', 'categoria', 'valor', 'paciente_vinculo', 'data_emissao'])

def obter_novo_id(df):
    if df.empty:
        return 1
    return int(df['id'].max() + 1)

# --- IDENTIFICAÇÃO NA BARRA LATERAL ---
st.sidebar.image("https://unsplash.com", caption="SisCL Malavazzi")
st.sidebar.title("SisCL Malavazzi v4.1")
st.sidebar.markdown("**Responsável:**\nEnfª Marcela Ricardo\nCOREN/SP 826.079")
st.sidebar.markdown("---")

aba_selecionada = st.sidebar.radio("Navegar pelo Setor:", [
    "🏠 Painel de Alertas",
    "👤 Central de Pacientes",
    "📅 Agenda & Compromissos",
    "📦 Estoque & Notas Fiscais",
    "📋 Pedidos aos Fornecedores",
    "🛍️ Frente de Vendas",
    "💰 Caixa & Fechamento",
    "📖 Manual, POPs & Fluxograma",
    "🧾 Receitas, Termos & Entrega"
])

hoje = datetime.today().date()

# ----------------- 1. PAINEL DE ALERTAS -----------------
if aba_selecionada == "🏠 Painel de Alertas":
    st.title("Painel de Controle e Alertas Inteligentes")
    
    df_p = st.session_state["pacientes"]
    df_e = st.session_state["estoque"]
    df_v = st.session_state["vendas"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pacientes", len(df_p))
    
    df_e['qtd'] = pd.to_numeric(df_e['qtd'], errors='coerce').fillna(0)
    df_e['qtd_minima'] = pd.to_numeric(df_e['qtd_minima'], errors='coerce').fillna(0)
    criticos = len(df_e[df_e['qtd'] <= df_e['qtd_minima']])
    col2.metric("Alertas de Estoque Baixo", criticos)
    col3.metric("Movimentações de Caixa", len(st.session_state["caixa"]))
    
    st.subheader("🔔 Notificações Clínicas Ativas (Ciclo de 6 Meses)")
    if not df_v.empty:
        df_v['proxima_renovacao'] = pd.to_datetime(df_v['proxima_renovacao']).dt.date
        vencidos = df_v[df_v['proxima_renovacao'] <= hoje]
        if not vencidos.empty:
            for _, linha in vencidos.iterrows():
                st.error(f"⚠️ **Paciente {linha['paciente_nome']}**: Completou 6 meses! Necessário renovar lentes e trocar estojo por segurança.")
        else:
            st.success("Nenhum descarte de lente ou troca de estojo pendente para hoje.")
    else:
        st.info("Nenhuma venda registrada para processamento de alertas.")

# ----------------- 2. CENTRAL DE PACIENTES -----------------
elif aba_selecionada == "👤 Central de Pacientes":
    st.title("Prontuário e Cadastro Clínico de Pacientes")
    aba_cadastro, aba_consulta = st.tabs(["Novo Cadastro", "Consultar Prontuário Individual"])
    
    with aba_cadastro:
        with st.form("cadastro_paciente"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo", placeholder="Ex: João da Silva")
            pront = col1.text_input("Número do Prontuário Geral", placeholder="Ex: 14523-X")
            tel = col1.text_input("WhatsApp / Telefone", placeholder="Ex: (11) 99999-1234")
            email = col1.text_input("E-mail", placeholder="Ex: joao.silva@email.com")
            end = col1.text_input("Endereço Residencial", placeholder="Ex: Rua das Flores, 123 - Centro")
            medico = col1.selectbox("Médico Responsável", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
            
            refra = col2.text_area("Refração Médica Atual", placeholder="Ex:\nOD: -2.00 DE / -0.50 DC x 180°\nOE: -2.25 DE")
            grau_l = col2.text_area("Grau da Lente Adaptada", placeholder="Ex:\nOD: -2.00 (Curva: 8.6 / Diâm: 14.2)\nOE: -2.25")
            tipo_l = col2.selectbox("Tipo de Lente", ["Gelatinosa", "Rígida Gás Permeável (RGP)", "Escleral"])
            forn = col2.selectbox("Fornecedor Recomendado", ["CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"])
            periodo = col2.selectbox("Período de Troca", ["Mensal", "Anual", "Descarte Diário"])
            
            if st.form_submit_button("Salvar Prontuário"):
                df = st.session_state["pacientes"]
                n_id = obter_novo_id(df)
                nova_l = {'id': n_id, 'prontuario': pront, 'nome': nome, 'telefone': tel, 'email': email, 'endereco': end, 'medico': medico, 'refracao': refra, 'grau_lente': grau_l, 'tipo_lente': tipo_l, 'fornecedor': forn, 'periodo_troca': periodo, 'data_cadastro': str(hoje)}
                st.session_state["pacientes"] = pd.concat([df, pd.DataFrame([nova_l])], ignore_index=True)
                st.success("Ficha clínica criada e salva com sucesso!")

    with aba_consulta:
        df = st.session_state["pacientes"]
        if not df.empty:
            p_escolhido = st.selectbox("Selecione o Paciente para Visualizar:", df['nome'].tolist())
            linha_paciente = df[df['nome'] == p_escolhido].iloc[0]
            
            st.markdown(f"### 📋 Prontuário Eletrônico: {linha_paciente['nome']}")
            c1, c2 = st.columns(2)
            c1.write(f"**Prontuário Nº:** {linha_paciente['prontuario']} | **Médico:** {linha_paciente['medico']}")
            c1.write(f"**Contato:** {linha_paciente['telefone']} | {linha_paciente['email']}")
            c1.write(f"**Endereço:** {linha_paciente['endereco']}")
            
            c2.write(f"**Refração Óculos:** {linha_paciente['refracao']}")
            c2.write(f"**Grau Adaptado na Lente:** {linha_paciente['grau_lente']}")
            c2.write(f"**Lente Selecionada:** {linha_paciente['tipo_lente']} ({linha_paciente['fornecedor']})")
        else:
            st.warning("Nenhum paciente cadastrado.")

# ----------------- 3. AGENDA & COMPROMISSOS -----------------
elif aba_selecionada == "📅 Agenda & Compromissos":
    st.title("Agenda de Atendimentos do Setor")
    
    with st.form("nova_agenda"):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Data", hoje)
        pac = col1.text_input("Paciente", placeholder="Ex: Maria Oliveira")
        tipo_a = col1.selectbox("Tipo de Compromisso", ["Consulta", "Teste de Lente", "Adaptação", "Entrega", "Retorno", "Pedido"])
        med = col2.selectbox("Médico", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
        status = col2.selectbox("Status", ["Agendado", "Realizado", "Cancelado"])
        obs = col2.text_area("Anotações / Lembretes Importantes", placeholder="Ex: Trazer estojo de teste RGP.")
        
        if st.form_submit_button("Confirmar Agendamento"):
            df = st.session_state["agenda"]
            nova_l = {'id': obter_novo_id(df), 'data': str(dt), 'paciente': pac, 'tipo_procedimento': tipo_a, 'medico': med, 'status': status, 'anotacoes': obs}
            st.session_state["agenda"] = pd.concat([df, pd.DataFrame([nova_l])], ignore_index=True)
            st.success("Compromisso agendado com sucesso!")

    st.markdown("---")
    f_data = st.date_input("Filtrar Agenda do Dia:", hoje)
    df_a = st.session_state["agenda"]
    filtrado = df_a[df_a['data'] == str(f_data)]
    if not filtrado.empty:
        st.dataframe(filtrado[['paciente', 'tipo_procedimento', 'medico', 'status', 'anotacoes']], use_container_width=True)
    else:
        st.info("Nenhum atendimento agendado para a data selecionada.")

# ----------------- 4. ESTOQUE & NOTAS FISCAIS -----------------
elif aba_selecionada == "📦 Estoque & Notas Fiscais":
    st.title("Gerenciamento de Insumos, Lentes e Notas Fiscais")
    t_est, t_nf = st.tabs(["Estoque de Lentes (Caixas e Testes)", "Registro de Notas Fiscais"])
    
    with t_est:
        with st.form("cadastro_estoque"):
            col1, col2 = st.columns(2)
            it = col1.text_input("Nome do Modelo/Insumo", placeholder="Ex: Biofinity Torica -2.00/-0.75x180")
            tp = col1.selectbox("Categoria", ["Lente de Teste (Amostra)", "Caixa Comercial", "Estojo", "Solução de Limpeza", "Sacolas / Insumos"])
