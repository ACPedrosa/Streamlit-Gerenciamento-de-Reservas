from PIL import Image, ImageDraw, ImageFont
import os

# =============================================================================
# CONSTANTES E PALETA DE CORES
# =============================================================================
PADDING = 8
SMALL_PADDING = 5
CARD_MARGIN = 4
LINE_SPACING = 3
RADIUS = 6

COLOR_BG = "#FAFAFA"
COLOR_CARD_NOTEBOOK = "#78A8BA"  # Mantido tom próximo à imagem original
COLOR_CARD_LAB = "#8BB3E2"
COLOR_NOTE_BG = "#FEF9C3"
COLOR_RESP_BG = "#E0F2FE"
COLOR_HEADER_DAY = "#FFFFFF"
COLOR_PERIOD_BG = "#FFFFFF"

COLOR_TEXT_MAIN = "#1F2937"
COLOR_TEXT_MUTED = "#4B5563"
COLOR_BORDER = "#1F2937"  # Bordas bem definidas como na imagem
COLOR_WHITE = "#FFFFFF"

FONT_SIZE_TITLE = 26
FONT_SIZE_SUBTITLE = 16
FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 10
FONT_SIZE_LEGEND = 9


# =============================================================================
# CORREÇÃO DE ACENTOS NO STREAMLIT (SISTEMA MULTIPLATAFORMA / LINUX STREAMLIT CLOUD)
# =============================================================================
def carregar_fonte(tamanho, negrito=False):
    """
    Busca fontes do sistema operacional (Windows/Linux) para garantir
    que acentos (ç, ã, é) e caracteres especiais sejam renderizados no Streamlit.
    """
    opcoes_fontes = [
        "arialbd.ttf" if negrito else "arial.ttf",
        "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf",  # Padrão no Linux/Streamlit Cloud
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrito else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "LiberationSans-Bold.ttf" if negrito else "LiberationSans-Regular.ttf"
    ]
    
    for nome in opcoes_fontes:
        try:
            return ImageFont.truetype(nome, tamanho)
        except IOError:
            continue
            
    # Fallback apenas se nenhuma fonte do SO for encontrada
    return ImageFont.load_default()


FONTE_TITULO = carregar_fonte(FONT_SIZE_TITLE, negrito=True)
FONTE_SUBTITULO = carregar_fonte(FONT_SIZE_SUBTITLE, negrito=True)
FONTE_CORPO = carregar_fonte(FONT_SIZE_BODY)
FONTE_DESTAQUE = carregar_fonte(FONT_SIZE_SMALL, negrito=True)
FONTE_PEQUENA = carregar_fonte(FONT_SIZE_SMALL)
FONTE_LEGENDA = carregar_fonte(FONT_SIZE_LEGEND)


def desenhar_retangulo_arredondado(draw, xy, fill, outline=COLOR_BORDER, radius=RADIUS):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=1)


# =============================================================================
# FUNÇÕES DE TEXTO E ÍCONE DO MOUSE
# =============================================================================
def quebrar_texto(texto, fonte, largura_max, draw):
    palavras = str(texto).split(' ')
    linhas = []
    linha_atual = []

    for palavra in palavras:
        test_line = ' '.join(linha_atual + [palavra])
        bbox = draw.textbbox((0, 0), test_line, font=fonte)
        if (bbox[2] - bbox[0]) <= largura_max:
            linha_atual.append(palavra)
        else:
            if linha_atual:
                linhas.append(' '.join(linha_atual))
                linha_atual = [palavra]
            else:
                linhas.append(palavra)
                linha_atual = []

    if linha_atual:
        linhas.append(' '.join(linha_atual))

    return linhas


def desenhar_texto_em_caixa(draw, box, texto, fonte, cor=COLOR_TEXT_MAIN, 
                            alinhar="left", max_linhas=None, espacamento=LINE_SPACING):
    x1, y1, x2, y2 = box
    largura_disponivel = (x2 - x1) - (2 * PADDING)
    altura_disponivel = (y2 - y1) - (2 * PADDING)

    if largura_disponivel <= 0 or altura_disponivel <= 0:
        return

    linhas_originais = str(texto).split('\n')
    linhas_processadas = []

    for l in linhas_originais:
        linhas_processadas.extend(quebrar_texto(l, fonte, largura_disponivel, draw))

    bbox_ref = draw.textbbox((0, 0), "Agyçá", font=fonte)
    altura_linha = (bbox_ref[3] - bbox_ref[1]) + espacamento

    linhas_finais = []
    y_atual = y1 + PADDING

    for idx, linha in enumerate(linhas_processadas):
        if (y_atual + altura_linha - espacamento) > (y2 - PADDING):
            if linhas_finais:
                ultima = linhas_finais[-1]
                while len(ultima) > 0:
                    test_str = ultima + "..."
                    test_bbox = draw.textbbox((0, 0), test_str, font=fonte)
                    if test_bbox[2] - test_bbox[0] <= largura_disponivel:
                        linhas_finais[-1] = test_str
                        break
                    ultima = ultima[:-1]
            break

        if max_linhas and len(linhas_finais) >= max_linhas:
            break

        linhas_finais.append(linha)
        y_atual += altura_linha

    y_cursor = y1 + PADDING
    for linha in linhas_finais:
        bbox_l = draw.textbbox((0, 0), linha, font=fonte)
        w_l = bbox_l[2] - bbox_l[0]

        if alinhar == "center":
            x_cursor = x1 + PADDING + (largura_disponivel - w_l) / 2
        elif alinhar == "right":
            x_cursor = x2 - PADDING - w_l
        else:
            x_cursor = x1 + PADDING

        draw.text((x_cursor, y_cursor), linha, fill=cor, font=fonte)
        y_cursor += altura_linha


# =============================================================================
# ÍCONE DO MOUSE (Com coordenadas corrigidas)
# =============================================================================
def desenhar_icone_mouse(draw, x, y, tamanho=14, cor=COLOR_TEXT_MAIN):
    """
    Desenha um ícone vetorial de mouse perfeitamente visível.
    x, y: Canto superior esquerdo onde o ícone será desenhado.
    """
    w = int(tamanho * 0.7)
    h = int(tamanho)
    
    # Corpo externo do mouse
    draw.ellipse((x, y, x + w, y + h), outline=cor, width=2)
    
    # Linha vertical central (divisão dos botões)
    draw.line((x + w // 2, y, x + w // 2, y + int(h * 0.45)), fill=cor, width=1)
    
    # Botão/Roda de rolagem central
    draw.line((x + w // 2, y + int(h * 0.15), x + w // 2, y + int(h * 0.35)), fill=cor, width=2)


def desenhar_card(draw, box, cor_fundo, titulo, subtitulo="", conteudo="", 
                  com_mouse=False, outline=COLOR_BORDER):
    desenhar_retangulo_arredondado(draw, box, fill=cor_fundo, outline=outline, radius=4)
    x1, y1, x2, y2 = box

    # Se precisa de mouse, reserva espaço no canto superior direito do card
    largura_reservada_mouse = 22 if com_mouse else 0
    
    # 1. Título do Card
    box_head = (x1, y1, x2 - largura_reservada_mouse, y1 + 20)
    desenhar_texto_em_caixa(draw, box_head, titulo, FONTE_DESTAQUE, max_linhas=1)

    # Desenha o mouse no canto superior direito dentro das margens do card
    if com_mouse:
        x_mouse = x2 - PADDING - 12
        y_mouse = y1 + PADDING
        desenhar_icone_mouse(draw, x_mouse, y_mouse, tamanho=14, cor=COLOR_TEXT_MAIN)

    # 2. Subtítulo (Número dos equipamentos ou nome do professor)
    y_cursor = y1 + 18
    if subtitulo:
        box_sub = (x1, y_cursor, x2 - largura_reservada_mouse, y_cursor + 18)
        desenhar_texto_em_caixa(draw, box_sub, subtitulo, FONTE_PEQUENA, max_linhas=1)
        y_cursor += 18

    # 3. Conteúdo (Nome do Professor / Curso)
    if conteudo and y_cursor < y2:
        box_conteudo = (x1, y_cursor - 2, x2, y2)
        desenhar_texto_em_caixa(draw, box_conteudo, conteudo, FONTE_LEGENDA, cor=COLOR_TEXT_MUTED)


# =============================================================================
# BLOCOS DO LAYOUT
# =============================================================================
def desenhar_topo(draw, tipo_visao, largura):
    box_topo = (300, 20, 750, 70)
    desenhar_retangulo_arredondado(draw, box_topo, fill=COLOR_WHITE)
    
    txt_titulo = "Reserva Lab. Móvel SENAI"
    bbox_t = draw.textbbox((0, 0), txt_titulo, font=FONTE_TITULO)
    w_t = bbox_t[2] - bbox_t[0]
    x_t = 300 + ((450 - w_t) / 2)
    draw.text((x_t, 30), txt_titulo, fill=COLOR_TEXT_MAIN, font=FONTE_TITULO)

    draw.text((770, 35), tipo_visao.capitalize(), fill=COLOR_TEXT_MAIN, font=FONTE_SUBTITULO)


def desenhar_coluna_lateral(draw, notas_add, responsaveis):
    # Informações Add.
    desenhar_retangulo_arredondado(draw, (20, 90, 230, 410), fill=COLOR_WHITE)
    desenhar_texto_em_caixa(draw, (20, 95, 230, 125), "Informações add.", FONTE_SUBTITULO, alinhar="center")

    y_nota = 130
    for nota in notas_add[:2]:
        box_nota = (30, y_nota, 220, y_nota + 125)
        desenhar_retangulo_arredondado(draw, box_nota, fill=COLOR_NOTE_BG, outline=None)
        desenhar_texto_em_caixa(draw, box_nota, nota, FONTE_CORPO)
        y_nota += 135

    # Responsáveis
    desenhar_retangulo_arredondado(draw, (20, 430, 230, 720), fill=COLOR_WHITE)
    desenhar_texto_em_caixa(draw, (20, 435, 230, 465), "Responsáveis", FONTE_SUBTITULO, alinhar="center")

    y_resp = 470
    for resp in responsaveis[:2]:
        box_resp = (30, y_resp, 220, y_resp + 110)
        desenhar_retangulo_arredondado(draw, box_resp, fill=COLOR_RESP_BG, outline=None)
        
        box_nome = (30, y_resp, 220, y_resp + 50)
        desenhar_texto_em_caixa(draw, box_nome, resp.get('nome', ''), FONTE_DESTAQUE, max_linhas=2)
        
        box_email = (30, y_resp + 50, 220, y_resp + 105)
        desenhar_texto_em_caixa(draw, box_email, resp.get('email', ''), FONTE_LEGENDA, cor=COLOR_TEXT_MUTED)
        
        y_resp += 120


def desenhar_calendario_semanal(draw, x_grid, y_grid, largura_grid, altura_grid, reservas, semana_dias=None):
    dias_semana = ["Seg", "Ter", "Quar", "Quin", "Sex", "Sab", "Dom"]
    largura_col = largura_grid / 7
    altura_cabecalho = 35
    altura_faixa = (altura_grid - altura_cabecalho) / 3
    periodos = ["Matutino", "Vespertino", "Noturno"]

    # Renderiza o cabeçalho dos dias
    for i, dia in enumerate(dias_semana):
        x_col = x_grid + (i * largura_col)
        box_h = (x_col, y_grid, x_col + largura_col, y_grid + altura_cabecalho)
        desenhar_texto_em_caixa(draw, box_h, dia, FONTE_SUBTITULO, alinhar="center")
        draw.line((x_col, y_grid, x_col, y_grid + altura_grid), fill=COLOR_BORDER, width=1)

    draw.line((x_grid, y_grid + altura_cabecalho, x_grid + largura_grid, y_grid + altura_cabecalho), fill=COLOR_BORDER, width=2)

    for p_idx in range(1, 3):
        y_f = y_grid + altura_cabecalho + (p_idx * altura_faixa)
        draw.line((x_grid, y_f, x_grid + largura_grid, y_f), fill=COLOR_BORDER, width=1)

    # Adiciona o número do dia do mês (igual à foto de referência)
    if semana_dias and len(semana_dias) == 7:
        for i, num_dia in enumerate(semana_dias):
            if num_dia:
                x_num = x_grid + (i * largura_col) + 6
                y_num = y_grid + altura_cabecalho + 6
                draw.text((x_num, y_num), str(num_dia), fill=COLOR_TEXT_MAIN, font=FONTE_DESTAQUE)

    # Preenche as reservas
    for r in reservas:
        if r.get('periodo') in periodos and r.get('dia_idx') is not None:
            col_idx = r['dia_idx']
            p_idx = periodos.index(r['periodo'])

            x_card = x_grid + (col_idx * largura_col) + CARD_MARGIN
            y_card = y_grid + altura_cabecalho + (p_idx * altura_faixa) + CARD_MARGIN + (15 if p_idx == 0 and semana_dias else 0)
            w_card = largura_col - (2 * CARD_MARGIN)
            h_card = altura_faixa - (2 * CARD_MARGIN) - (15 if p_idx == 0 and semana_dias else 0)

            cor_card = COLOR_CARD_NOTEBOOK if r['tipo'] == 'Notebooks' else COLOR_CARD_LAB
            
            titulo = f"{r.get('qtd', 1)} Notebooks" if r['tipo'] == 'Notebooks' else "Laboratório Móvel SN1"
            subtitulo = f"nº {r['numeros']}" if r.get('numeros') else ""
            conteudo = f"Prof. {r.get('solicitante', '')}"

            desenhar_card(
                draw=draw,
                box=(x_card, y_card, x_card + w_card, y_card + h_card),
                cor_fundo=cor_card,
                titulo=titulo,
                subtitulo=subtitulo,
                conteudo=conteudo,
                com_mouse=r.get('com_mouse', False)
            )


def desenhar_rodape(draw, reservas):
    # Quantidade de Reservas
    box_est = (250, 590, 710, 720)
    desenhar_retangulo_arredondado(draw, box_est, fill=COLOR_WHITE)
    
    draw.line((450, 590, 450, 720), fill=COLOR_BORDER, width=1)
    draw.line((570, 590, 570, 720), fill=COLOR_BORDER, width=1)

    desenhar_texto_em_caixa(draw, (255, 595, 445, 620), "Quantidade de Reservas", FONTE_DESTAQUE)
    desenhar_texto_em_caixa(draw, (255, 680, 445, 710), f"Total: {len(reservas)}", FONTE_PEQUENA, cor=COLOR_TEXT_MUTED)

    tot_mouses = sum(1 for r in reservas if r.get('com_mouse'))
    tot_notebooks = sum(r.get('qtd', 1) for r in reservas if r['tipo'] == 'Notebooks')

    desenhar_texto_em_caixa(draw, (455, 595, 565, 620), "Mouses", FONTE_DESTAQUE)
    desenhar_texto_em_caixa(draw, (455, 630, 565, 680), str(tot_mouses), FONTE_SUBTITULO, alinhar="center")

    desenhar_texto_em_caixa(draw, (575, 595, 705, 620), "Notebooks", FONTE_DESTAQUE)
    desenhar_texto_em_caixa(draw, (575, 630, 705, 680), str(tot_notebooks), FONTE_SUBTITULO, alinhar="center")

    # Legenda
    box_leg = (730, 590, 1170, 720)
    desenhar_retangulo_arredondado(draw, box_leg, fill=COLOR_WHITE)
    desenhar_texto_em_caixa(draw, (730, 595, 1170, 620), "Legenda de Reserva", FONTE_DESTAQUE, alinhar="center")

    # Amostra Notebooks
    draw.rectangle((750, 628, 765, 642), fill=COLOR_CARD_NOTEBOOK)
    draw.text((772, 627), "Notebooks", fill=COLOR_TEXT_MAIN, font=FONTE_PEQUENA)

    # Amostra Lab Móvel
    draw.rectangle((850, 628, 865, 642), fill=COLOR_CARD_LAB)
    draw.text((872, 627), "Lab Móvel", fill=COLOR_TEXT_MAIN, font=FONTE_PEQUENA)

    # Ícone do Mouse
    desenhar_icone_mouse(draw, 752, 655, tamanho=12)
    draw.text((772, 654), "Sinalização de que precisa de mouse", fill=COLOR_TEXT_MUTED, font=FONTE_PEQUENA)


def gerar_imagem_relatorio(tipo_visao, ano, mes, semana_dias, reservas, notas_add, responsaveis):
    largura, altura = 1200, 750
    img = Image.new("RGB", (largura, altura), COLOR_BG)
    draw = ImageDraw.Draw(img)

    desenhar_topo(draw, tipo_visao, largura)
    desenhar_coluna_lateral(draw, notas_add, responsaveis)

    x_grid_inicio, y_grid_inicio = 250, 90
    largura_grid, altura_grid = 920, 480
    
    desenhar_retangulo_arredondado(draw, (x_grid_inicio, y_grid_inicio, x_grid_inicio + largura_grid, y_grid_inicio + altura_grid), fill=COLOR_WHITE)

    if tipo_visao == "semanal":
        desenhar_calendario_semanal(draw, x_grid_inicio, y_grid_inicio, largura_grid, altura_grid, reservas, semana_dias)

    desenhar_rodape(draw, reservas)

    return img