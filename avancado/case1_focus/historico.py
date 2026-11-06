"""
Etapa 2b do agente: HISTÓRICO DE ACERTO — o Focus acertou IPCA e Selic nos últimos 5 anos fechados?
Dono: Pessoa B. Saída: lista em resumo["acuracia"] (formato em CONTRATO.md) + saida/acuracia.png.

Versão mínima que já funciona: compara a expectativa do "início do ano" (mediana em 15/01 do próprio ano)
com o realizado (IPCA composto no ano; Selic meta no fim do ano).
"""
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from inicio_focus import carregar_focus, carregar_sgs, tabela_acuracia

ANOS = 5
HORIZONTE = "início do ano"   # TODO: comparar também "12 meses antes" e "meio do ano"?


def historico(saida: Path) -> list[dict]:
    acc = tabela_acuracia(carregar_focus(), carregar_sgs())
    ultimo_fechado = date.today().year - 1
    acc = acc[(acc["quando"] == HORIZONTE) & (acc["ano"].between(ultimo_fechado - ANOS + 1, ultimo_fechado))]
    linhas = [{k: (int(v) if k == "ano" else v) for k, v in r.items()} for r in acc.to_dict("records")]

    fig, eixos = plt.subplots(1, 2, figsize=(10, 4))
    for ax, ind in zip(eixos, ("IPCA", "Selic")):
        d = acc[acc["indicador"] == ind]
        x = range(len(d))
        ax.bar([i - 0.2 for i in x], d["esperado"], width=0.4, label="Esperado (Focus, jan.)")
        ax.bar([i + 0.2 for i in x], d["realizado"], width=0.4, label="Realizado")
        ax.set_xticks(list(x), d["ano"].astype(str))
        ax.set_title(f"{ind}: esperado × realizado (%)")
    eixos[0].legend(fontsize=8)
    fig.text(0.01, 0.01, "Fonte: BCB (Focus e SGS). IPCA composto no ano; Selic meta no fim do ano.", fontsize=8)
    saida.mkdir(exist_ok=True)
    fig.savefig(saida / "acuracia.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return linhas
