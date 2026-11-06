"""
Etapas 4 e 5 do agente: ANALISAR (o Claude escreve via `claude -p`) e CONFERIR (todo número do texto existe no JSON).
Dono: Pessoa B. Entrada: `resumo` (CONTRATO.md). Saída: HTML da análise (só <h3>, <p>, <ul>, <li>, <strong>).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def analisar(resumo: dict) -> str:
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("Claude Code não encontrado. Instale e faça login (ver avancado/README.md).")
    prompt = (AQUI / "prompt_analise.md").read_text(encoding="utf-8")
    entrada = prompt + "\n" + json.dumps(resumo, ensure_ascii=False, indent=2)
    r = subprocess.run([claude, "-p"], input=entrada, capture_output=True, text=True,
                       encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"Erro ao chamar o Claude Code:\n{r.stderr}")
    return r.stdout.strip().removeprefix("```html").removesuffix("```").strip()


def conferir(texto: str, resumo: dict) -> list[str]:
    """Todo número decimal do texto precisa aparecer no JSON (pega número inventado)."""
    validos = set()
    for v in re.findall(r"-?\d+(?:[.,]\d+)?", json.dumps(resumo)):
        x = float(v.replace(",", "."))
        validos |= {round(x, 2), round(abs(x), 2)}
    suspeitos = []
    for v in re.findall(r"\d+,\d+|\d+\.\d+", re.sub(r"<[^>]+>", " ", texto)):
        if round(float(v.replace(",", ".")), 2) not in validos:
            suspeitos.append(v)
    return suspeitos

# TODO: quando conferir() acusar suspeitos, pedir ao Claude para reescrever (até 2 tentativas)
#       e só seguir se passar. A função nova fica aqui e o agente_semanal.py só a chama.
