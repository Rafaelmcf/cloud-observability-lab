import json
import os
import random
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://helpdesk-container:8000")

TITULOS = [
    "Impressora não imprime",
    "Sem acesso à VPN",
    "Computador lento",
    "Esqueci a senha",
    "Erro ao abrir o sistema",
    "Monitor sem sinal",
    "Wi-Fi caindo",
]
STATUS = ["aberto", "em_andamento", "resolvido"]

ids_criados = []


def chamar(metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode() if corpo else None
    req = urllib.request.Request(
        BASE_URL + caminho,
        data=dados,
        method=metodo,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        print(f"falha de conexão: {e}", flush=True)
        return 0, b""


def criar_chamado():
    titulo = random.choice(TITULOS)
    status, corpo = chamar(
        "POST",
        "/chamados",
        {"titulo": titulo, "descricao": "Gerado pelo gerador de carga"},
    )
    if status == 200:
        ids_criados.append(json.loads(corpo)["id"])
    return status


def atualizar_chamado():
    if not ids_criados:
        return criar_chamado()
    chamado_id = random.choice(ids_criados)
    novo = random.choice(STATUS)
    status, _ = chamar("PUT", f"/chamados/{chamado_id}?novo_status={novo}")
    return status


def listar_chamados():
    status, _ = chamar("GET", "/chamados")
    return status


def rota_inexistente():
    status, _ = chamar("GET", "/rota-que-nao-existe")
    return status


def home():
    status, _ = chamar("GET", "/")
    return status


ACOES = [
    (listar_chamados, 50),
    (criar_chamado, 25),
    (atualizar_chamado, 15),
    (home, 5),
    (rota_inexistente, 5),
]

funcoes = [a[0] for a in ACOES]
pesos = [a[1] for a in ACOES]

print(f"Gerador de carga iniciado: {BASE_URL}", flush=True)

while True:
    acao = random.choices(funcoes, weights=pesos)[0]
    status = acao()
    print(f"{acao.__name__} -> {status}", flush=True)
    time.sleep(random.uniform(0.5, 3))