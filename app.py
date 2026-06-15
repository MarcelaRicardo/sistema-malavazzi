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
    senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Entrar no Sistema"):
        if senha_digitada == SENHA_CORRETA:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta! Acesso negado por segurança.")
    st.stop()

# ----------------- 📊 BANCO DE DADOS LOCAL SIMPLIFICADO -----------------
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
st.sidebar.title("SisCL Malavazzi v3.0")
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
    opcao = st.tabs(["Novo Cadastro", "Consultar Prontuário Individual"])
    
    with opcao[0]:
        with st.form("cadastro_paciente"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            pront = col1.text_input("Número do Prontuário Geral")
            tel = col1.text_input("WhatsApp / Telefone")
            email = col1.text_input("E-mail")
            end = col1.text_input("Endereço Residencial")
            medico = col1.selectbox("Médico Responsável", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
            
            refra = col2.text_area("Refração Médica Atual")
            grau_l = col2.text_area("Grau da Lente Adaptada")
            tipo_l = col2.selectbox("Tipo de Lente", ["Gelatinosa", "Rígida Gás Permeável (RGP)", "Escleral"])
            forn = col2.selectbox("Fornecedor Recomendado", ["CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"])
            periodo = col2.selectbox("Período de Troca", ["Mensal", "Anual", "Descarte Diário"])
            
            if st.form_submit_button("Salvar Prontuário"):
                df = st.session_state["pacientes"]
                n_id = obter_novo_id(df)
                nova_l = {'id': n_id, 'prontuario': pront, 'nome': nome, 'telefone': tel, 'email': email, 'endereco': end, 'medico': medico, 'refracao': refra, 'grau_lente': grau_l, 'tipo_lente': tipo_l, 'fornecedor': forn, 'periodo_troca': periodo, 'data_cadastro': str(hoje)}
                st.session_state["pacientes"] = pd.concat([df, pd.DataFrame([nova_l])], ignore_index=True)
                st.success("Ficha clínica criada e salva com sucesso!")

    with opcao[1]:
        df = st.session_state["pacientes"]
        if not df.empty:
            p_escolhido = st.selectbox("Selecione o Paciente:", df['nome'].tolist())
            ficha = df[df['nome'] == p_escolhido].iloc[0]
            
            st.markdown(f"### 📋 Prontuário Eletrônico: {ficha['nome']}")
            c1, c2 = st.columns(2)
            c1.write(f"**Prontuário Nº:** {ficha['prontuario']} | **Médico:** {ficha['medico']}")
            c1.write(f"**Contato:** {ficha['telefone']} | {ficha['email']}")
            c1.write(f"**Endereço:** {ficha['endereco']}")
            
            c2.write(f"**Refração Óculos:** {ficha['refracao']}")
            c2.write(f"**Grau Adaptado na Lente:** {ficha['grau_lente']}")
            c2.write(f"**Lente Selecionada:** {ficha['tipo_lente']} ({ficha['fornecedor']})")
        else:
            st.warning("Nenhum paciente cadastrado.")

# ----------------- 3. AGENDA & COMPROMISSOS -----------------
elif aba_selecionada == "📅 Agenda & Compromissos":
    st.title("Agenda de Atendimentos do Setor")
    
    with st.form("nova_agenda"):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Data", hoje)
        pac = col1.text_input("Paciente")
        tipo_a = col1.selectbox("Tipo de Compromisso", ["Consulta", "Teste de Lente", "Adaptação", "Entrega", "Retorno", "Pedido"])
        med = col2.selectbox("Médico", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
        status = col2.selectbox("Status", ["Agendado", "Realizado", "Cancelado"])
        obs = col2.text_area("Anotações / Lembretes Importantes")
        
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
    t_est = st.tabs(["Estoque de Lentes (Caixas e Testes)", "Registro de Notas Fiscais"])
    
    with t_est[0]:
        with st.form("cadastro_estoque"):
            col1, col2 = st.columns(2)
            it = col1.text_input("Nome do Modelo/Insumo")
            tp = col1.selectbox("Categoria", ["Lente de Teste (Amostra)", "Caixa Comercial", "Estojo", "Solução de Limpeza"])
            fn = col1.selectbox("Fabricante", ["CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"])
            qt = col1.number_input("Quantidade Inicial", min_value=0, value=10)
            
            qm = col2.number_input("Estoque Mínimo", min_value=0, value=2)
            val = col2.date_input("Validade", hoje + timedelta(days=365))
            pc = col2.number_input("Preço de Custo (R$)", min_value=0.0, value=0.0)
            pv = col2.number_input("Preço de Venda (R$)", min_value=0.0, value=0.0)
            nf_vinculo = col2.text_input("Número da Nota Fiscal de Entrada")
            if st.form_submit_button("Registrar Entrada no Estoque"):
df = st.session_state["estoque"]
nova_l = {'id': obter_novo_id(df), 'item': it, 'tipo': tp, 'fornecedor': fn, 'qtd': qt, 'qtd_minima': qm, 'validade': str(val), 'preco_custo': pc, 'preco_venda': pv, 'nota_fiscal': nf_vinculo}
st.session_state["estoque"] = pd.concat([df, pd.DataFrame([nova_l])], ignore_index=True)
st.success("Item adicionado ao estoque físico.")
st.markdown("---")
st.subheader("Inventário Geral Atualizado")
st.dataframe(st.session_state["estoque"], use_container_width=True)
with t_est[1]:
st.subheader("Lançamento de Notas Fiscais Recebidas")
with st.form("form_nf"):
cnpj = st.text_input("CNPJ do Fornecedor")
cat = st.selectbox("Categoria do Gasto", ["Lentes Comerciais", "Lentes de Teste", "Acessórios/Estojos", "Materiais de Escritório/Sacolas"])
v_nf = st.number_input("Valor Total da NF (R$)", min_value=0.0)
p_vinc = st.text_input("Vincular Paciente (Opcional)")
if st.form_submit_button("Salvar Nota Fiscal"):
df_nf = st.session_state["notas_fiscais"]
nova_l = {'id': obter_novo_id(df_nf), 'cnpj': cnpj, 'categoria': cat, 'valor': v_nf, 'paciente_vinculo': p_vinc, 'data_emissao': str(hoje)}
st.session_state["notas_fiscais"] = pd.concat([df_nf, pd.DataFrame([nova_l])], ignore_index=True)
st.success("Nota Fiscal registrada com sucesso!")
----------------- 5. PEDIDOS AOS FORNECECORES -----------------
elif aba_selecionada == "📋 Pedidos aos Fornecedores":
st.title("Rastreabilidade de Pedidos de Lentes")
with st.form("novo_pedido"):
col1, col2 = st.columns(2)
f_ped = col1.selectbox("Fornecedor", ["CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"])
t_ped = col1.selectbox("Tipo de Solicitação", ["Pedido de Caixa Comercial", "Pedido de Teste / Amostra Grátis", "Compra de Estojos/Sacolas"])
it_ped = col1.text_input("Especificações Técnicas do Item")
qtd_ped = col2.number_input("Quantidade", min_value=1, value=1)
st_ped = col2.selectbox("Status do Pedido", ["Realizado", "Pendente", "Recebido"])
if st.form_submit_button("Registrar Pedido de Compra"):
df = st.session_state["pedidos"]
nova_l = {'id': obter_novo_id(df), 'fornecedor': f_ped, 'tipo_pedido': t_ped, 'item': it_ped, 'quantidade': qtd_ped, 'status': st_ped, 'data_pedido': str(hoje)}
st.session_state["pedidos"] = pd.concat([df, pd.DataFrame([nova_l])], ignore_index=True)
st.success("Pedido enviado para a lista de monitoramento.")
st.markdown("---")
st.subheader("Lista de Compras e Pedidos Ativos")
st.dataframe(st.session_state["pedidos"], use_container_width=True)
----------------- 6. FRENTE DE VENDAS -----------------
elif aba_selecionada == "🛍️ Frente de Vendas":
st.title("Registro de Saída Comercial e Agendamento de Renovação")
df_p = st.session_state["pacientes"]
df_e = st.session_state["estoque"]
if not df_p.empty and not df_e.empty:
with st.form("venda_rapida"):
p_venda = st.selectbox("Selecione o Paciente Comprador:", df_p['nome'].tolist())
i_venda = st.selectbox("Item do Estoque:", df_e['item'].tolist())
f_pag = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
n_fiscal = st.text_input("Número da Nota Fiscal emitida")
valor_item = float(df_e[df_e['item'] == i_venda]['preco_venda'].iloc[0])
st.info(f"Valor do Item Selecionado: R$ {valor_item:.2f}")
if st.form_submit_button("Efetivar Venda Comercial"):
prox_renov = hoje + timedelta(days=180)
df_v = st.session_state["vendas"]
nova_v = {'id': obter_novo_id(df_v), 'paciente_nome': p_venda, 'item': i_venda, 'valor': valor_item, 'forma_pagamento': f_pag, 'nota_fiscal': n_fiscal, 'data_venda': str(hoje), 'proxima_renovacao': str(prox_renov)}
st.session_state["vendas"] = pd.concat([df_v, pd.DataFrame([nova_v])], ignore_index=True)
df_c = st.session_state["caixa"]
nova_c = {'id': obter_novo_id(df_c), 'tipo': "Entrada", 'descricao': f"Venda de LC para {p_venda}", 'valor': valor_item, 'data': str(hoje)}
st.session_state["caixa"] = pd.concat([df_c, pd.DataFrame([nova_c])], ignore_index=True)
st.success(f"Venda concluída! Alerta de retorno gerado para: {prox_renov.strftime('%d/%m/%Y')}")
else:
st.warning("É preciso ter pacientes e itens no estoque para realizar uma venda.")
----------------- 7. CAIXA & FECHAMENTO -----------------
elif aba_selecionada == "💰 Caixa & Fechamento":
st.title("Fluxo de Caixa e Relatórios de Produtividade Médica")
df_c = st.session_state["caixa"]
if not df_c.empty:
df_c['valor'] = pd.to_numeric(df_c['valor'], errors='coerce').fillna(0)
entradas = df_c[df_c['tipo'] == 'Entrada']['valor'].sum()
saidas = df_c[df_c['tipo'] == 'Saída']['valor'].sum()
else:
entradas, saidas = 0.0, 0.0
saldo_real = entradas - saidas
c1, c2, c3 = st.columns(3)
c1.metric("Total Entradas", f"R$ {entradas:.2f}")
c2.metric("Total Saídas", f"R$ {saidas:.2f}")
c3.metric("Saldo do Caixa", f"R$ {saldo_real:.2f}")
st.markdown("---")
st.subheader("📊 Faturamento Diário, Mensal e Anual Separado por Médico")
df_v = st.session_state["vendas"]
df_p = st.session_state["pacientes"]
if not df_v.empty and not df_p.empty:
df_v['valor'] = pd.to_numeric(df_v['valor'], errors='coerce').fillna(0)
df_m = df_v.merge(df_p[['nome', 'medico']], left_on='paciente_nome', right_on='nome', how='left')
col1, col2, col3 = st.columns(3)
col1.metric("Dr. Edmar", f"R$ {df_m[df_m['medico'] == 'Dr. Edmar']['valor'].sum():.2f}")
col2.metric("Dr. Gustavo", f"R$ {df_m[df_m['medico'] == 'Dr. Gustavo']['valor'].sum():.2f}")
col3.metric("Amparo", f"R$ {df_m[df_m['medico'] == 'Amparo']['valor'].sum():.2f}")
st.subheader("Detalhamento Geral de Vendas")
st.dataframe(df_v, use_container_width=True)
else:
st.info("Nenhuma venda faturada cadastrada no sistema.")
----------------- 8. MANUAL, POPS & FLUXOGRAMA -----------------
elif aba_selecionada == "📖 Manual, POPs & Fluxograma":
st.title("Qualidade e Segurança: Manuais, POPs de Enfermagem e Protocolos")
opcao_m = st.selectbox("Selecione o Documento Normativo:", ["Manual de Boas Práticas e Segurança", "Protocolos de Adaptação", "Procedimentos Operacionais Padrão (POPs)", "Fluxograma de Atendimento do Setor"])
if opcao_m == "Manual de Boas Práticas e Segurança":
st.markdown("### Manual de Funcionamento do Setor de Lentes de Contato - Clínica Malavazzi\nObjetivo Geral: Garantir a excelência técnica na adaptação de lentes alinhada ao Núcleo de Segurança do Paciente.\n\n#### Metas Internas de Segurança Aplicadas:\n1. Identificação Correta: Cruzamento compulsório do nome e prontuário geral.\n2. Higienização: Uso obrigatório de sabonete líquido antisséptico e álcool a 70%.\n3. Prevenção de Infecções: Esterilização química rigorosa das lentes rígidas.")
elif opcao_m == "Protocolos de Adaptação":
st.markdown("### Protocolo de Adaptação Técnica (Gelatinosas vs RGP)\n* Lentes Gelatinosas: Avaliação de centralização e movimentação ao piscar (0.5 a 1.0mm).\n* Lentes Rígidas (RGP): Avaliação estrita do padrão de fluoresceína sob lâmpada de fenda.")
elif opcao_m == "Procedimentos Operacionais Padrão (POPs)":
st.markdown("### POP - Limpeza do Setor e Manutenção de Caixas de Lente Rígida\n* Código: POP-ENF-LC-001 | Versão: 1.0\n* Responsável Técnico: Enfª Marcela Ricardo.\n* Passo a Passo: Fricção linear com solução multiuso, enxágue com soro fisiológico 0.9% e armazenamento em solução conservante específica. Cronograma: Troca das soluções a cada 3 meses.")
elif opcao_m == "Fluxograma de Atendimento do Setor":
st.markdown("1. Consulta Médica ➡️ 2. Indicação de Lente ➡️ 3. Pedido de Lente de Teste ➡️ 4. Chegada do Teste e Adaptação ➡️ 5. Avaliação Clínica ➡️ 6. Se Aprovado: Pedido de Caixa Comercial para 6 meses.")
----------------- 9. RECEITAS, TERMOS & ENTREGA -----------------
elif aba_selecionada == "🧾 Receitas, Termos & Entrega":
st.title("Documentos de Entrega, Receitas e Termo de Consentimento")
df_p = st.session_state["pacientes"]
if not df_p.empty:
p_doc = st.selectbox("Escolha o Paciente para gerar os impressos:", df_p['nome'].tolist())
st.markdown("---")
st.subheader("📄 1. Receita Personalizada de Colírio Lubrificante")
st.text_area("Texto para Impressão:", value=f"RECEITUÁRIO OFICIAL - CLINICA MALAVAZZI\n\nNome do Paciente: {p_doc}\nMedicamento: Systane Ultra Sem Conservantes\nApresentação: Frasco de 10 mL\n\nPosologia: Instilar 1 a 2 gotas em cada olho, de 3 a 5 vezes ao dia, enquanto estiver usando as lentes de contato.\n\nProfissional: Enfª Marcela Ricardo - COREN/SP 826.079\nData: {hoje.strftime('%d/%m/%Y')}", height=180)
st.markdown("---")
st.subheader("📝 2. Termo de Consentimento e Treinamento")
st.text_area("Declaração de Ciência do Paciente:", value=f"TERMO DE RESPONSABILIDADE\n\nEu declaro que recebi o treinamento prático ministrado pela Enfermeira Marcela Ricardo sobre:\n1. Higienização das mãos antes do manuseio.\n2. Substituição do estojo a cada 6 meses e limpeza a cada 3 meses.\n3. Proibição de dormir com as lentes.\n\nNome do Paciente: {p_doc}\nAssinatura: _____________________________________ Data: {hoje.strftime('%d/%m/%Y')}", height=180)
else:
st.warning("Cadastre um paciente primeiro para gerar seus impressos correspondentes.")
