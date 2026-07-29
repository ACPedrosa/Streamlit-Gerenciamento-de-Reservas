import pandas as pd
import json
import os

ARQUIVO_DADOS = "reservas_carrinho.json"
ARQUIVO_NOTAS = "notas_adicionais.json"

def carregar_reservas():
    """Carrega a lista de reservas cadastradas."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_reserva(nova_reserva):
    """Adiciona uma nova reserva ao armazenamento."""
    reservas = carregar_reservas()
    reservas.append(nova_reserva)
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(reservas, f, ensure_ascii=False, indent=4)

def deletar_reserva(index):
    """Remove uma reserva pelo indice."""
    reservas = carregar_reservas()
    if 0 <= index < len(reservas):
        reservas.pop(index)
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(reservas, f, ensure_ascii=False, indent=4)

def carregar_notas():
    """Carrega as notas de Informacoes Adicionais."""
    if os.path.exists(ARQUIVO_NOTAS):
        try:
            with open(ARQUIVO_NOTAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return ["Product Tip", "Customer Review Reel"]

def salvar_nota(texto_nota):
    """Salva uma nova nota de informacao adicional."""
    notas = carregar_notas()
    if texto_nota and texto_nota not in notas:
        notas.insert(0, texto_nota)  # Adiciona no topo
        with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
            json.dump(notas[:5], f, ensure_ascii=False, indent=4) # Mantem as 5 mais recentes