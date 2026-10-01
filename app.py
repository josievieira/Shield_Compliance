import os
import pandas as pd
import streamlit as st

# Configuração da página - Título na aba do navegador
st.set_page_config(
    page_title="Shield Compliance",
    page_icon="🛡️",
    layout="wide",
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS PERSONALIZADA (High-Tech / Cyber Red)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Remove a barra superior padrão do Streamlit */
    header {visibility: hidden;}
    
    /* Estilo do Fundo e Fonte Global */
    .main {
        background-color: #f8fafc;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Container do Expander */
    .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Cabeçalho do Expander */
    .stExpander > details > summary,
    .stExpander > details > summary:hover,
    .stExpander > details > summary:focus {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    
    /* Texto do Título do Expander */
    .stExpander summary p, 
    .stExpander summary span,
    .stExpander details summary div {
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    
    /* Conteúdo interno do Expander */
    .stExpander [data-testid="stVerticalBlock"] p,
    .stExpander [data-testid="stVerticalBlock"] span,
    .stExpander [data-testid="stVerticalBlock"] div,
    .stExpander [data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
    }

    .stExpander strong {
        color: #1e3a8a !important;
    }
    
    /* Personalização de Botões */
    .stButton>button {
        background-color: #ef4444;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #dc2626;
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Função para formatar valores monetários no padrão brasileiro
def formatar_moeda_br(valor_raw):
    if (
        pd.isna(valor_raw)
        or str(valor_raw).strip().lower()
        in ["nan", "none", "n/a", "", "0", "0,00"]
    ):
        return "R$ 0,00 (Não consta penalidade pecuniária)"

    v = str(valor_raw).strip().replace(".", "")

    if "," in v:
        partes = v.split(",")
        inteiro = partes[0]
        decimal = partes[1]
    else:
        inteiro = v
        decimal = "00"

    try:
        inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
        return f"R$ {inteiro_formatado},{decimal}"
    except Exception:
        return f"R$ {valor_raw}"


# Função auxiliar para tratar textos vazios
def tratar_texto_vazio(valor, padrao="Não consta"):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "n/a", ""]:
        return padrao
    return str(valor).strip()


# Função para identificar colunas flexivelmente
def obter_valor_coluna(row, df_cols, palavras_chave, padrao="Não consta"):
    for col in df_cols:
        for pal in palavras_chave:
            if pal.lower() in str(col).lower():
                val = row.get(col)
                if not pd.isna(val) and str(val).strip() != "":
                    return str(val).strip()
    return padrao


# 1. CARREGAMENTO DOS DADOS (CSV / EXCEL DO CNEP)
@st.cache_data
def carregar_dados():
    df = None
    for enc in ["utf-8-sig", "latin1", "cp1252", "iso-8859-1"]:
        try:
            df = pd.read_csv("cnep_dados.csv", sep=";", encoding=enc, dtype=str)
            break
        except Exception:
            try:
                df = pd.read_csv("cnep_dados.csv", sep=",", encoding=enc, dtype=str)
                break
            except Exception:
                continue

    if df is None:
        try:
            df = pd.read_excel("cnep_dados.xlsx", dtype=str)
        except Exception:
            pass

    if df is None:
        st.error(
            "⚠️ Não foi possível carregar a base de dados. Verifique se o arquivo 'cnep_dados.csv' ou 'cnep_dados.xlsx' está na mesma pasta do código."
        )
        st.stop()

    df.columns = [str(col).strip() for col in df.columns]
    df = df.fillna("")
    return df


try:
    df = carregar_dados()
except Exception as e:
    st.error(f"⚠️ Erro ao processar o arquivo de dados: {e}")
    st.stop()


# ---------------------------------------------------------
# CONTROLE DE ESTADO DA TELA (INICIAL vs. CONSULTA)
# ---------------------------------------------------------
if "sistema_iniciado" not in st.session_state:
    st.session_state["sistema_iniciado"] = False

# ---------------------------------------------------------
# TELA 1: BOAS-VINDAS / LANDING PAGE
# ---------------------------------------------------------
if not st.session_state["sistema_iniciado"]:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if os.path.exists("logo.png"):
            try:
                st.image("logo.png", use_container_width=True)
            except Exception:
                st.image("logo.png", use_column_width=True)
        else:
            st.info("🛡️ **Shield Compliance System**")

        st.markdown(
            """
            <div style="text-align: center; margin-top: 15px;">
                <p style="color: #334155; font-size: 1.1rem; font-weight: 600; margin-bottom: 6px;">
                    Aplicação Web Interativa para Gestão de Riscos e Reestruturação do Processo de Homologação de Fornecedores Públicos
                </p>
                <p style="color: #64748b; font-weight: 500; font-size: 0.95rem;">
                    Engenharia da Computação & Engenharia de Produção
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            if st.button("🚀 Clique para Começar", use_container_width=True):
                st.session_state["sistema_iniciado"] = True
                st.rerun()

# ---------------------------------------------------------
# TELA 2: PAINEL PRINCIPAL DE PESQUISA E CONSULTA (CNEP/CGU)
# ---------------------------------------------------------
else:
    c_logo, c_title = st.columns([1, 5])

    with c_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120)
        else:
            st.markdown("### 🛡️")

    with c_title:
        st.markdown(
            """
            <div style="padding-top: 20px;">
                <p style="color: #ef4444 !important; margin: 0 !important; font-size: 1.35rem !important; font-weight: 700 !important;">
                    Painel de Monitoramento da Base Oficial de Sanções (CNEP / CGU)
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Opções")
        if st.button("🏠 Voltar à Tela Inicial"):
            st.session_state["sistema_iniciado"] = False
            st.rerun()

    # CAMPO DE PESQUISA
    termo_busca = st.text_input(
        "🔍 Digite a Razão Social, Nome Fantasia ou CNPJ/CPF para pesquisar:"
    ).strip()

    if termo_busca:
        mascara = df.apply(
            lambda col: col.astype(str).str.contains(
                termo_busca, case=False, na=False
            )
        ).any(axis=1)
        resultados = df[mascara]

        qtd_resultados = len(resultados)

        if qtd_resultados > 0:
            if qtd_resultados == 1:
                st.error(
                    "🚨 **ALERTA DE COMPLIANCE:** Foi encontrada **1 ocorrência/sanção** no CNEP para o termo pesquisado!"
                )
            else:
                st.error(
                    f"🚨 **ALERTA DE COMPLIANCE:** Foram encontradas **{qtd_resultados} ocorrências/sanções** no CNEP para o termo pesquisado!"
                )

            # 1. TABELA PRINCIPAL DE RESUMO EXECUTIVO
            st.markdown("#### 📋 Resumo Executivo")
            
            resumo_dados = []
            for idx, row in resultados.iterrows():
                resumo_dados.append({
                    "CNPJ / CPF": obter_valor_coluna(row, df.columns, ["cpf", "cnpj"]),
                    "NOME DO SANCIONADO": obter_valor_coluna(row, df.columns, ["nome do sancionado", "sancionado", "razão social", "nome"]),
                    "NOME FANTASIA": obter_valor_coluna(row, df.columns, ["fantasia"]),
                    "ÓRGÃO SANCIONADOR": obter_valor_coluna(row, df.columns, ["órgão", "orgao"]),
                })
            
            df_resumo_raw = pd.DataFrame(resumo_dados)
            df_resumo_agrupado = df_resumo_raw.groupby(["CNPJ / CPF", "NOME DO SANCIONADO", "NOME FANTASIA", "ÓRGÃO SANCIONADOR"], dropna=False).size().reset_index(name="QTD PROCESSOS EXISTENTES")
            
            st.dataframe(df_resumo_agrupado, use_container_width=True, hide_index=True)

            st.divider()

            # 2. EXPANDERS COM DETALHAMENTO COMPLETO DOS PROCESSOS
            st.markdown("#### 🔍 Detalhamento dos Processos")

            for idx, row in resultados.iterrows():
                num_processo = obter_valor_coluna(row, df.columns, ["processo", "número", "numero"], padrao="Sem número")
                sancionado_tit = obter_valor_coluna(row, df.columns, ["nome do sancionado", "sancionado", "razão social", "nome"])
                cnpj_cpf_tit = obter_valor_coluna(row, df.columns, ["cpf", "cnpj"])

                titulo_expander = f"📌 Processo nº {num_processo} — {sancionado_tit} ({cnpj_cpf_tit})"

                with st.expander(titulo_expander, expanded=True):
                    categoria_san_v = obter_valor_coluna(row, df.columns, ["categoria", "sanção", "sancao"])
                    valor_multa_raw = obter_valor_coluna(row, df.columns, ["multa", "valor"])
                    valor_multa_v = formatar_moeda_br(valor_multa_raw)
                    abrangencia_v = obter_valor_coluna(row, df.columns, ["abrangência", "abragência", "abrangencia"])

                    data_inicio_v = obter_valor_coluna(row, df.columns, ["início", "inicio"])
                    data_final_raw = obter_valor_coluna(row, df.columns, ["fim", "final"])
                    
                    if data_final_raw == "Não consta":
                        data_final_formatada = "🔴 em aberto / sanção ativa"
                    else:
                        data_final_formatada = data_final_raw

                    data_pub_v = obter_valor_coluna(row, df.columns, ["publicação", "publicacao"])
                    esfera_v = obter_valor_coluna(row, df.columns, ["esfera"])
                    uf_v = obter_valor_coluna(row, df.columns, ["uf"])
                    origem_v = obter_valor_coluna(row, df.columns, ["origem"])

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.write(f"**CATEGORIA DA SANÇÃO:** {categoria_san_v}")
                        st.write(f"**VALOR DA MULTA:** {valor_multa_v}")
                        st.write(f"**ABRANGÊNCIA DA SANÇÃO:** {abrangencia_v}")

                    with c2:
                        st.write(f"**DATA INÍCIO SANÇÃO:** {data_inicio_v}")
                        st.write(f"**DATA FINAL SANÇÃO:** {data_final_formatada}")
                        st.write(f"**DATA PUBLICAÇÃO:** {data_pub_v}")

                    with c3:
                        st.write(f"**ESFERA DO ÓRGÃO:** {esfera_v}")
                        st.write(f"**UF DO ÓRGÃO:** {uf_v}")
                        st.write(f"**ORIGEM DA INFORMAÇÃO:** {origem_v}")

                    st.markdown("**FUNDAMENTAÇÃO LEGAL:**")
                    fundamentacao_v = obter_valor_coluna(row, df.columns, ["fundamentação", "fundamentacao", "legal"])
                    st.info(fundamentacao_v, icon="📜")

                    obs_v = obter_valor_coluna(row, df.columns, ["observações", "observacao", "obs"], padrao="")
                    if obs_v and obs_v != "Não consta":
                        st.caption(f"**Observações:** {obs_v}")
        else:
            st.success(
                "✅ **NADA CONSTA:** Nenhum registro de sanção encontrado no CNEP para este termo."
            )
    else:
        st.info("Digite um termo no campo acima para realizar a consulta.")