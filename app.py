import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuração da Página do Streamlit
st.set_page_config(page_title="SisCL Malavazzi - Lentes de Contato", layout="wide", page_icon="👁️")

# --- SISTEMA DE ARMAZENAMENTO SEGURO E PERSISTENTE (CSV LOCAL) ---
# Cria os arquivos de dados caso eles não existam no servidor para evitar perdas
def inicializar_dados():
    arquivos = {
        'pacientes.csv': ['id', 'prontuario', 'nome', 'telefone', 'email', 'medico', 'refracao', 'k1_k2', 'grau_lente', 'tipo_lente', 'fornecedor', 'data_cadastro'],
        'estoque.csv': ['id', 'item', 'tipo', 'fornecedor', 'qtd', 'qtd_minima', 'validade', 'preco_custo', 'preco_venda'],
        'agenda.csv': ['id', 'data', 'paciente', 'tipo_procedimento', 'medico', 'status', 'anotacoes'],
        'vendas.csv': ['id', 'paciente_id', 'paciente_nome', 'item', 'valor', 'forma_pagamento', 'nota_fiscal', 'data_venda', 'proxima_renovacao'],
        'caixa.csv': ['id', 'tipo', 'descricao', 'valor', 'data']
    }
    for arquivo, colunas in arquivos.items():
        if not os.path.exists(arquivo):
            pd.DataFrame(columns=colunas).to_csv(arquivo, index=False, encoding='utf-8')

inicializar_dados()

def carregar_dados(arquivo):
    return pd.read_csv(arquivo, encoding='utf-8')

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False, encoding='utf-8')

def gerar_id(df):
    if df.empty:
        return 1
    return int(df['id'].max() + 1)

# --- BARRA LATERAL (SIDEBAR) COM LOGO E IDENTIFICAÇÃO ---
st.sidebar.image("https://unsplash.com", caption="SisCL Malavazzi")
st.sidebar.title("Controle de Lentes de Contato")
st.sidebar.write("**Resp. Técnica:** Enfª Marcela Ricardo")
st.sidebar.write("COREN/SP 826.079")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navegação do Sistema", [
    "🏠 Início (Dashboard)", 
    "👤 Pacientes e Prontuário", 
    "📅 Agenda do Setor", 
    "📦 Controle de Estoque", 
    "🛍️ Registrar Venda", 
    "💰 Fluxo de Caixa e Relatórios"
])

hoje = datetime.today().date()

# ----------------- 1. DASHBOARD DE INÍCIO -----------------
if menu == "🏠 Início (Dashboard)":
    st.title("Painel de Controle - Setor de Lentes de Contato")
    
    df_p = carregar_dados('pacientes.csv')
    df_e = carregar_dados('estoque.csv')
    df_a = carregar_dados('agenda.csv')
    df_c = carregar_dados('caixa.csv')
    df_v = carregar_dados('vendas.csv')
    
    # Processamento de dados para os indicadores
    total_pacientes = len(df_p)
    
    df_e['qtd'] = pd.to_numeric(df_e['qtd'], errors='coerce').fillna(0)
    df_e['qtd_minima'] = pd.to_numeric(df_e['qtd_minima'], errors='coerce').fillna(0)
    estoque_baixo = len(df_e[df_e['qtd'] <= df_e['qtd_minima']])
    
    agendamentos_hoje = len(df_a[df_a['data'] == str(hoje)])
    
    df_c['valor'] = pd.to_numeric(df_c['valor'], errors='coerce').fillna(0)
    receitas = df_c[df_c['tipo'] == 'Entrada']['valor'].sum()
    despesas = df_c[df_c['tipo'] == 'Saída']['valor'].sum()
    saldo = receitas - despesas
    
    # Exibição dos Cartões Métricos
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pacientes Cadastrados", total_pacientes)
    col2.metric("Agendamentos Hoje", agendamentos_hoje)
    col3.metric("Alertas de Estoque Baixo", estoque_baixo, delta="- Atenção" if estoque_baixo > 0 else "OK")
    col4.metric("Saldo Geral do Caixa", f"R$ {saldo:,.2f}")
    
    st.markdown("---")
    
    # Alertas de Renovação Automática (6 meses)
    st.subheader("🔔 Alertas de Renovação Próxima (Ciclo de 6 Meses)")
    if not df_v.empty:
        df_v['proxima_renovacao'] = pd.to_datetime(df_v['proxima_renovacao']).dt.date
        vencendo = df_v[df_v['proxima_renovacao'] <= hoje]
        
        if not vencendo.empty:
            for idx, linha in vencendo.iterrows():
                st.error(f"⚠️ **{linha['paciente_name']}** precisa realizar a troca e compra de novas lentes/estojo. (Venceu em: {linha['proxima_renovacao']})")
        else:
            st.success("Nenhum paciente com vencimento de descarte ou renovação de lente para hoje.")
    else:
        st.info("Nenhuma venda registrada para processamento de alertas.")

# ----------------- 2. PACIENTES E PRONTUÁRIO -----------------
elif menu == "👤 Pacientes e Prontuário":
    st.title("Gerenciamento de Pacientes e Histórico Clínico")
    aba1, aba2 = st.tabs(["📑 Cadastrar Novo Paciente", "📖 Prontuário Eletrônico"])
    
    with aba1:
        with st.form("form_cadastro_paciente"):
            col1, col2 = st.columns(2)
            prontuario = col1.text_input("Número do Prontuário Geral")
            nome = col1.text_input("Nome Completo do Paciente")
            tel = col1.text_input("Telefone de Contato (WhatsApp)")
            email = col1.text_input("E-mail")
            
            medico = col2.selectbox("Médico Responsável", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
            refracao = col2.text_area("Refração Médica (Grau do Óculos)")
            k1_k2 = col2.text_input("Ceratometria / Topografia (K1 e K2)")
            grau_lente = col2.text_area("Grau da Lente de Contato Adaptada")
            
            tipo_lente = col2.selectbox("Tipo de Lente", ["Gelatinosa Monofocal", "Gelatinosa Tórica", "Gelatinosa Multifocal", "Rígida Gás Permeável (RGP)", "Escleral"])
            fornecedor = col2.selectbox("Fornecedor Principal", ["CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"])
            
            if st.form_submit_button("Salvar Registro Clínico"):
                df_p = carregar_dados('pacientes.csv')
                novo_id = gerar_id(df_p)
                nova_linha = {
                    'id': novo_id, 'prontuario': prontuario, 'nome': nome, 'telefone': tel, 'email': email,
                    'medico': medico, 'refracao': refracao, 'k1_k2': k1_k2, 'grau_lente': grau_lente,
                    'tipo_lente': tipo_lente, 'fornecedor': fornecedor, 'data_cadastro': str(hoje)
                }
                df_p = pd.concat([df_p, pd.DataFrame([nova_linha])], ignore_index=True)
                salvar_dados(df_p, 'pacientes.csv')
                st.success(f"Paciente {nome} cadastrado com sucesso no SisCL!")
                st.rerun()

    with aba2:
        df_p = carregar_dados('pacientes.csv')
        if not df_p.empty:
            opcao_paciente = st.selectbox(
                "Selecione o Paciente para abrir a ficha:", 
                df_p.values.tolist(), 
                format_func=lambda x: f"Pront: {x[1]} - {x[2]}"
            )
            
            if opcao_paciente:
                st.markdown(f"## 📋 Ficha do Paciente: {opcao_paciente[2]}")
                col1, col2 = st.columns(2)
                col1.markdown(f"**Prontuário:** {opcao_paciente[1]} | **Cadastro:** {opcao_paciente[11]}")
                col1.markdown(f"**Telefone:** {opcao_paciente[3]} | **E-mail:** {opcao_paciente[4]}")
                col1.markdown(f"**Médico Assistente:** {opcao_paciente[5]}")
                
                col2.markdown(f"**Refração Óculos:** {opcao_paciente[6]}")
                col2.markdown(f"**Curvatura Corneana (K1/K2):** {opcao_paciente[7]}")
                col2.markdown(f"**Grau Definido da LC:** {opcao_paciente[8]}")
                col2.markdown(f"**Lente:** {opcao_paciente[9]} ({opcao_paciente[10]})")
                
                st.markdown("---")
                st.subheader("🛍️ Histórico Comercial e de Compras")
                df_v = carregar_dados('vendas.csv')
                compras_paciente = df_v[df_v['paciente_id'] == int(opcao_paciente[0])]
                if not compras_paciente.empty:
                    st.dataframe(compras_paciente[['data_venda', 'item', 'valor', 'forma_pagamento', 'nota_fiscal', 'proxima_renovacao']])
                else:
                    st.info("Nenhuma aquisição comercial registrada para este paciente.")
        else:
            st.info("Nenhum paciente cadastrado no sistema ainda.")

# ----------------- 3. AGENDA DO SETOR -----------------
elif menu == "📅 Agenda do Setor":
    st.title("Agenda Especializada de Atendimentos")
    
    with st.form("form_agenda"):
        col1, col2 = st.columns(2)
        data_ag = col1.date_input("Data do Atendimento", hoje)
        paciente_ag = col1.text_input("Nome Completo do Paciente")
        tipo_proc = col1.selectbox("Tipo de Procedimento", ["Consulta Geral", "Teste de Lente", "Adaptação Técnica", "Entrega de Caixas", "Retorno Clínico", "Pedido Técnico"])
        
        medico_ag = col2.selectbox("Médico Vinculado", ["Dr. Edmar", "Dr. Gustavo", "Amparo"])
        status_ag = col2.selectbox("Status Inicial", ["Agendado", "Confirmado", "Realizado", "Cancelado"])
        anotacoes_ag = col2.text_area("Notas Importantes / Alertas Clínicos")
        
        if st.form_submit_button("Agendar Procedimento"):
            df_a = carregar_dados('agenda.csv')
            novo_id = gerar_id(df_a)
            nova_linha = {
                'id': novo_id, 'data': str(data_ag), 'paciente': paciente_ag, 
                'tipo_procedimento': tipo_proc, 'medico': medico_ag, 'status': status_ag, 'anotacoes': anotacoes_ag
            }
            df_a = pd.concat([df_a, pd.DataFrame([nova_linha])], ignore_index=True)
            salvar_dados(df_a, 'agenda.csv')
            st.success("Consulta agendada no setor com sucesso!")
            st.rerun()
            
    st.markdown("---")
    filtro_data = st.date_input("Visualizar Consultas por Data:", hoje)
    df_a = carregar_dados('agenda.csv')
    consultas_filtradas = df_a[df_a['data'] == str(filtro_data)]
    
    if not consultas_filtradas.empty:
        st.subheader(f"📅 Compromissos do Dia {filtro_data.strftime('%d/%m/%Y')}")
        st.dataframe(consultas_filtradas[['paciente', 'tipo_procedimento', 'medico', 'status', 'anotacoes']], use_container_width=True)
    else:
Use o código com cuidado.st.info("Nenhum atendimento agendado para a data selecionada.")----------------- 4. CONTROLE DE ESTOQUE -----------------elif menu == "📦 Controle de Estoque":st.title("Gerenciamento de Estoque de Venda e Amostras de Teste")with st.form("form_estoque"):col1, col2 = st.columns(2)item = col1.text_input("Modelo da Lente / Insumo (Ex: Biofinity Esférica)")tipo_item = col1.selectbox("Categoria do Produto", ("Lente de Teste (Amostra)", "Caixa Comercial", "Estojo", "Solução de Limpeza", "Sacolas / Insumos"))forn = col1.selectbox("Fabricante/Fornecedor", ("CooperVision", "Central Oftálmica", "Solótica", "Johnson & Johnson"))qtd = col1.number_input("Quantidade em Unidades", min_value=1, value=1)qtd_min = col2.number_input("Estoque Mínimo (Alerta de Reposição)", min_value=1, value=5)validade = col2.date_input("Data de Validade Técnica", hoje + timedelta(days=365))custo = col2.number_input("Preço Unitário de Custo (R$)", min_value=0.0, value=0.0)venda = col2.number_input("Preço de Venda Praticado (R$)", min_value=0.0, value=0.0)if st.form_submit_button("Lançar Entrada no Estoque"):df_e = carregar_dados('estoque.csv')novo_id = gerar_id(df_e)nova_linha = {'id': novo_id, 'item': item, 'tipo': tipo_item, 'fornecedor': forn,'qtd': qtd, 'qtd_minima': qtd_min, 'validade': str(validade), 'preco_custo': custo, 'preco_venda': venda}df_e = pd.concat([df_e, pd.DataFrame((nova_linha, )), ignore_index=True)salvar_dados(df_e, 'estoque.csv')st.success(f"Item '{item}' adicionado ao inventário da clínica.")st.rerun()st.markdown("---")st.subheader("📋 Inventário Geral Atualizado")df_e = carregar_dados('estoque.csv')if not df_e.empty:st.dataframe(df_e[('id', 'item', 'tipo', 'fornecedor', 'qtd', 'qtd_minima', 'validade', 'preco_venda'), use_container_width=True)else:st.info("Inventário vazio. Cadastre insumos ou caixas comerciais acima.")----------------- 5. REGISTRO DE VENDAS -----------------elif menu == "🛍️ Registrar Venda":st.title("Lançamento Comercial e Cálculo de Renovação")df_p = carregar_dados('pacientes.csv')df_e = carregar_dados('estoque.csv')# Filtra apenas itens que possuem unidades disponíveis no estoquedf_e('qtd') = pd.to_numeric(df_e('qtd'), errors='coerce').fillna(0)itens_disponiveis = df_e[df_e('qtd', > 0)if not df_p.empty and not itens_disponiveis.empty:with st.form("form_venda"):lista_pacientes = df_p.values.tolist()paciente_sel = st.selectbox("Selecione o Paciente Comprador:", lista_pacientes, format_func=lambda x: f"Pront: {x(1)} - {x(2)}")lista_itens = itens_disponiveis.values.tolist()item_sel = st.selectbox("Selecione a Caixa/Item a ser Vendido:", lista_itens, format_func=lambda x: f"{x(1)} ({x(2)}) - R$ {x(8)}")forma_pag = st.selectbox("Forma de Recebimento:", ("Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto"))nf = st.text_input("Número do Documento / Nota Fiscal")if st.form_submit_button("Confirmar e Efetivar Venda"):# Deduz 1 unidade do estoque do item selecionadodf_e.loc[df_e('id') == item_sel(0, 'qtd') -= 1salvar_dados(df_e, 'estoque.csv')# Regra de negócio: Cálculo automático para renovação após 6 meses (180 dias)proxima_renovacao = hoje + timedelta(days=180)# Registra a transação comercialdf_v = carregar_dados('vendas.csv')nova_venda = {'id': gerar_id(df_v),'paciente_id': paciente_sel(0),'paciente_name': paciente_sel(2),'item': item_sel(1),'valor': item_sel(8),'forma_pagamento': forma_pag,'nota_fiscal': nf,'data_venda': str(hoje),'proxima_renovacao': str(proxima_renovacao)}df_v = pd.concat([df_v, pd.DataFrame((nova_venda, )), ignore_index=True)salvar_dados(df_v, 'vendas.csv')# Registra a entrada financeira no Livro de Caixa da clínicadf_c = carregar_dados('caixa.csv')novo_lancamento = {'id': gerar_id(df_c),'tipo': 'Entrada','descricao': f"Venda de LC - Paciente: {paciente_sel(2)} (Médico: {paciente_sel(5)})",'valor': item_sel(8),'data': str(hoje)}df_c = pd.concat([df_c, pd.DataFrame((novo_lancamento, )), ignore_index=True)salvar_dados(df_c, 'caixa.csv')st.success(f"Venda registrada com sucesso! Ciclo de 6 meses calculado. Retorno obrigatório em: {proxima_renovacao.strftime('%d/%m/%Y')}")st.rerun()else:st.warning("Verifique as dependências: É necessário ter pelo menos um paciente cadastrado e produtos com saldo positivo no estoque.")----------------- 6. FLUXO DE CAIXA E RELATÓRIOS -----------------elif menu == "💰 Fluxo de Caixa e Relatórios":st.title("Gestão Financeira e Produtividade do Corpo Médico")aba1, aba2 = st.tabs(("💵 Fluxo de Caixa Diário", "📊 Relatório por Profissional"))with aba1:st.subheader("Movimentações Manuais de Entrada/Saída")with st.form("form_caixa"):tipo_cx = st.selectbox("Natureza do Lançamento", ("Entrada", "Saída"))desc_cx = st.text_input("Descrição do Lançamento (Ex: Compra de estojos fornecedor)")val_cx = st.number_input("Valor da Operação (R$)", min_value=0.01, value=10.0)if st.form_submit_button("Registrar Movimento"):df_c = carregar_dados('caixa.csv')novo_id = gerar_id(df_c)nova_linha = {'id': novo_id, 'tipo': tipo_cx, 'descricao': desc_cx, 'valor': val_cx, 'data': str(hoje)}df_c = pd.concat([df_c, pd.DataFrame((nova_linha, )), ignore_index=True)salvar_dados(df_c, 'caixa.csv')st.success("Fluxo de caixa atualizado.")st.rerun()st.markdown("---")df_c = carregar_dados('caixa.csv')if not df_c.empty:st.dataframe(df_c.sort_values(by='id', ascending=False), use_container_width=True)else:st.info("Nenhum registro financeiro computado.")with aba2:st.subheader("Produtividade e Faturamento Separado por Médico")df_v = carregar_dados('vendas.csv')df_p = carregar_dados('pacientes.csv')if not df_v.empty and not df_p.empty:# Vincula as tabelas para saber qual médico atendeu o paciente daquela vendadf_p('id') = df_p('id').astype(int)df_v('paciente_id') = df_v('paciente_id').astype(int)df_v('valor') = pd.to_numeric(df_v('valor'), errors='coerce').fillna(0)df_relatorio = df_v.merge(df_p[('id', 'medico'), left_on='paciente_id', right_on='id', how='left')faturamento_total = df_relatorio('valor').sum()st.markdown(f"### Faturamento Total Acumulado do Setor: R$ {faturamento_total:,.2f}")st.markdown("---")medicos = ("Dr. Edmar", "Dr. Gustavo", "Amparo")col1, col2, col3 = st.columns(3)colunas_medicos = (col1, col2, col3)for i, m in enumerate(medicos):sub_df = df_relatorio[df_relatorio('medico', == m)faturamento_m = sub_df('valor').sum()vendas_m = len(sub_df)colunas_medicos(i).metric(f"{m}", f"R$ {faturamento_m:,.2f}", f"{vendas_m} lentes adaptadas")else:st.info("Dados insuficientes para gerar a segmentação de faturamento médico.")
