import streamlit as st
import datetime
import calendar
from io import BytesIO

from generator import gerar_imagem_relatorio
from database import carregar_reservas, salvar_reserva, deletar_reserva, carregar_notas, salvar_nota

# Configurações da página do Streamlit
st.set_page_config(
    page_title="Reserva Lab. Móvel SENAI",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CSS Customizado Corporativo (Tema Claro Forçado, Azul Microsoft / SAP)
# -----------------------------------------------------------------------------
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Forçar tema claro em toda a aplicação */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        color: #1E293B !important;
        background-color: #F4F7FC !important;
    }

    /* Ocultar marca e menu do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.02) !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Labels de inputs na sidebar e corpo principal */
    label, p, span, div[data-testid="stMarkdownContainer"] p {
        color: #1E293B !important;
        font-weight: 500;
    }

    /* Estilização Geral de Botões */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        height: 48px !important;
        border-radius: 8px !important;
        border: 1px solid #2563EB !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.12) !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background-color: #1D4ED8 !important;
        border-color: #1D4ED8 !important;
        box-shadow: 0 4px 10px rgba(29, 78, 216, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: none !important;
    }

    /* Download Button */
    .stDownloadButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        height: 48px !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.12) !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stDownloadButton > button:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 10px rgba(29, 78, 216, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    /* Corrigir Campos de Texto, Seletores e Datapickers para Fundo Branco */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input,
    .stTextArea textarea,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Forçar texto dos Selectbox e Popups a ficarem visíveis */
    div[data-baseweb="select"] * {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }

    /* Containers do Streamlit com Borda Padrão (Cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }

    /* Expander Estilizado */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        color: #1E293B !important;
        font-weight: 600 !important;
    }

    /* Títulos da Aplicação */
    .main-title {
        color: #1E3A8A !important;
        font-weight: 700;
        font-size: 1.75rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }

    .main-subtitle {
        color: #64748B !important;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .card-title {
        color: #1E3A8A !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #F4F7FC;
    }
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Componentes de Interface
# -----------------------------------------------------------------------------
def header():
    st.markdown('<div class="main-title">Reserva do Laboratório Móvel</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Sistema de gerenciamento de empréstimos de notebooks e laboratório móvel.</div>', unsafe_allow_html=True)
    st.divider()

def sidebar():
    st.sidebar.markdown("<h2 style='color:#1E3A8A; font-size:1.25rem; font-weight:700;'>Novo Agendamento</h2>", unsafe_allow_html=True)
    st.sidebar.divider()
    
    st.sidebar.markdown("<h3 style='color:#1E3A8A; font-size:1rem; font-weight:600;'>Dados da Reserva</h3>", unsafe_allow_html=True)
    solicitante = st.sidebar.text_input("Professor / Solicitante")
    curso = st.sidebar.text_input("Curso / Turma (Ex: Dev. Sistemas)")
    
    tipo_equipamento = st.sidebar.selectbox(
        "Equipamento",
        ["Notebooks", "Laboratório Móvel SN1"]
    )
    
    qtd_notebooks = 1
    numeros_notebooks = ""
    
    if tipo_equipamento == "Notebooks":
        qtd_notebooks = st.sidebar.number_input("Quantidade de Notebooks", min_value=1, max_value=40, value=2)
        numeros_notebooks = st.sidebar.text_input("Número(s) dos Notebooks (ex: 51, 52)")
        
    com_mouse = st.sidebar.checkbox("Necessita de Mouse", value=True)
    st.sidebar.divider()
    
    st.sidebar.markdown("<h3 style='color:#1E3A8A; font-size:1rem; font-weight:600;'>Períodos</h3>", unsafe_allow_html=True)
    p_matutino = st.sidebar.checkbox("Matutino (Manhã)", value=True)
    p_vespertino = st.sidebar.checkbox("Vespertino (Tarde)")
    p_noturno = st.sidebar.checkbox("Noturno (Noite)")
    
    periodos_selecionados = []
    if p_matutino: periodos_selecionados.append("Matutino")
    if p_vespertino: periodos_selecionados.append("Vespertino")
    if p_noturno: periodos_selecionados.append("Noturno")
    st.sidebar.divider()
    
    st.sidebar.markdown("<h3 style='color:#1E3A8A; font-size:1rem; font-weight:600;'>Datas</h3>", unsafe_allow_html=True)
    datas_selecionadas = st.sidebar.date_input(
        "Selecione o dia ou intervalo de dias",
        value=(datetime.date.today(), datetime.date.today())
    )
    st.sidebar.divider()
    
    st.sidebar.markdown("<h3 style='color:#1E3A8A; font-size:1rem; font-weight:600;'>Observações</h3>", unsafe_allow_html=True)
    nova_nota = st.sidebar.text_area("Nota ou observação para o bloco lateral", height=80)
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    btn_salvar = st.sidebar.button("Salvar", type="primary")
    
    return {
        "solicitante": solicitante,
        "curso": curso,
        "tipo_equipamento": tipo_equipamento,
        "qtd_notebooks": qtd_notebooks,
        "numeros_notebooks": numeros_notebooks,
        "com_mouse": com_mouse,
        "periodos_selecionados": periodos_selecionados,
        "datas_selecionadas": datas_selecionadas,
        "nova_nota": nova_nota,
        "btn_salvar": btn_salvar
    }

def filters():
    with st.container(border=True):
        col_v, col_m, col_a = st.columns([2, 2, 2])
        
        with col_v:
            tipo_visao = st.radio("Visualização:", ["semanal", "mensal"], horizontal=True)
            
        with col_m:
            mes_selecionado = st.selectbox("Mês:", range(1, 13), index=datetime.date.today().month - 1)
            
        with col_a:
            ano_selecionado = st.number_input("Ano:", value=datetime.date.today().year, min_value=2024, max_value=2030)
            
    return tipo_visao, mes_selecionado, ano_selecionado

def export_panel(byte_im, tipo_visao, mes_selecionado, ano_selecionado):
    with st.container(border=True):
        st.markdown('<div class="card-title">Exportação</div>', unsafe_allow_html=True)
        st.download_button(
            label="Baixar Relatório",
            data=byte_im,
            file_name=f"Reserva_{tipo_visao}_{mes_selecionado}_{ano_selecionado}.png",
            mime="image/png",
            type="primary"
        )

def management_panel(reservas_filtradas):
    with st.container(border=True):
        st.markdown('<div class="card-title">Gerenciamento</div>', unsafe_allow_html=True)
        
        with st.expander("Lista de Agendamentos"):
            if reservas_filtradas:
                for idx, r in enumerate(reservas_filtradas):
                    col_info, col_del = st.columns([3, 1])
                    with col_info:
                        st.write(f"**{r['data']}** | {r['periodo']} - {r['solicitante']} ({r['tipo']})")
                    with col_del:
                        if st.button(f"Excluir #{idx}", key=f"del_{idx}"):
                            deletar_reserva(idx)
                            st.rerun()
            else:
                st.info("Nenhuma reserva para este período.")


# -----------------------------------------------------------------------------
# Aplicação Principal
# -----------------------------------------------------------------------------

load_css()

SENHA_CORRETA = "senai123"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        with st.container(border=True):
            st.markdown('<div class="card-title" style="text-align: center;">Autenticação</div>', unsafe_allow_html=True)
            senha_input = st.text_input("Senha de Acesso", type="password")
            if st.button("Entrar", type="primary"):
                if senha_input == SENHA_CORRETA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
    st.stop()

# Dados Fixos dos Responsáveis
RESPONSAVEIS = [
    {"nome": "Ana Caroline Pedrosa", "email": "ana.carsilva@sistemafiep.org.br"},
    {"nome": "Osnir de Souza", "email": "osnir.souza@sistemafiep.org.br"}
]

# Sidebar
form = sidebar()

if form["btn_salvar"]:
    if not form["solicitante"]:
        st.sidebar.error("Por favor, preencha o nome do solicitante.")
    elif not form["periodos_selecionados"]:
        st.sidebar.error("Selecione ao menos um período (Matutino, Vespertino ou Noturno).")
    else:
        datas_selecionadas = form["datas_selecionadas"]
        if isinstance(datas_selecionadas, tuple) or isinstance(datas_selecionadas, list):
            d_inicio = datas_selecionadas[0]
            d_fim = datas_selecionadas[1] if len(datas_selecionadas) > 1 else d_inicio
        else:
            d_inicio = d_fim = datas_selecionadas

        if form["nova_nota"].strip():
            salvar_nota(form["nova_nota"].strip())

        dia_atual = d_inicio
        total_salvos = 0
        while dia_atual <= d_fim:
            for p in form["periodos_selecionados"]:
                reserva = {
                    "solicitante": form["solicitante"],
                    "curso": form["curso"],
                    "tipo": form["tipo_equipamento"],
                    "qtd": form["qtd_notebooks"] if form["tipo_equipamento"] == "Notebooks" else 0,
                    "numeros": form["numeros_notebooks"] if form["tipo_equipamento"] == "Notebooks" else "",
                    "com_mouse": form["com_mouse"],
                    "periodo": p,
                    "data": dia_atual.strftime("%Y-%m-%d"),
                    "dia_idx": dia_atual.weekday(),
                    "dia_mes": dia_atual.day
                }
                salvar_reserva(reserva)
                total_salvos += 1
            dia_atual += datetime.timedelta(days=1)

        st.sidebar.success(f"{total_salvos} agendamento(s) salvo(s) com sucesso!")
        st.rerun()

# Corpo Principal
header()

# Filtros
tipo_visao, mes_selecionado, ano_selecionado = filters()

# Carrega Dados
todas_reservas = carregar_reservas()
notas_add = carregar_notas()

# Filtra reservas pelo mes e ano selecionados
reservas_filtradas = []
for r in todas_reservas:
    try:
        dt = datetime.datetime.strptime(r["data"], "%Y-%m-%d").date()
        if dt.month == mes_selecionado and dt.year == ano_selecionado:
            primeiro_dia_mes = datetime.date(dt.year, dt.month, 1)
            semana_mes_idx = (dt.day + primeiro_dia_mes.weekday() - 1) // 7
            r["semana_mes_idx"] = min(semana_mes_idx, 4)
            reservas_filtradas.append(r)
    except Exception:
        continue

st.markdown("<br>", unsafe_allow_html=True)

# Geração do Relatório Visual
img_relatorio = gerar_imagem_relatorio(
    tipo_visao=tipo_visao,
    ano=ano_selecionado,
    mes=mes_selecionado,
    semana_dias=[],
    reservas=reservas_filtradas,
    notas_add=notas_add,
    responsaveis=RESPONSAVEIS
)

buf = BytesIO()
img_relatorio.save(buf, format="PNG")
byte_im = buf.getvalue()

col_img, col_side = st.columns([3, 1])

with col_img:
    with st.container(border=True):
        st.image(img_relatorio, use_container_width=True)

with col_side:
    export_panel(byte_im, tipo_visao, mes_selecionado, ano_selecionado)
    st.markdown("<br>", unsafe_allow_html=True)
    management_panel(reservas_filtradas)