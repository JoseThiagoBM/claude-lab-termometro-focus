"""
Etapa 2b do agente: HISTÓRICO DE ACERTO — o Focus acertou IPCA e Selic nos últimos 5 anos fechados?
Dono: Pessoa B. Saída: lista em resumo["acuracia"] (formato em CONTRATO.md) + saida/acuracia.png.
Resumo numérico para a análise: resumo_acuracia(linhas) -> resumo["acuracia_resumo"].

Compara a mediana do Focus em três momentos com o realizado (IPCA composto no ano; Selic meta no fim do ano):
  "12 meses antes" = 15/01 do ano anterior · "início do ano" = 15/01 · "meio do ano" = 15/07.
erro_pp = realizado − esperado. Positivo: o mercado SUBESTIMOU (esperava menos do que veio).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from inicio_focus import carregar_focus, carregar_sgs, tabela_acuracia

ANOS = 5
HORIZONTES = ("12 meses antes", "início do ano", "meio do ano")   # do mais distante ao mais próximo
HORIZONTE_PRINCIPAL = "início do ano"
INDICADORES = ("IPCA", "Selic")
CURTO = {"12 meses antes": "12m antes", "início do ano": "jan.", "meio do ano": "jul."}
LARGURA_PX = 700                                                  # vai embutido no e-mail (Frente D)


def _anos_fechados(acc) -> list[int]:
    """Últimos ANOS anos com realizado completo. tabela_acuracia só traz ano com 12 meses de IPCA
    e Selic de dezembro, então o ano corrente (ou um dezembro ainda não divulgado) nunca entra."""
    fechados = sorted(set(acc.loc[acc["indicador"] == "IPCA", "ano"]) & set(acc.loc[acc["indicador"] == "Selic", "ano"]))
    return [int(a) for a in fechados[-ANOS:]]


def resumo_acuracia(linhas: list[dict]) -> dict:
    """Números para a análise citar (vão em resumo["acuracia_resumo"]; formato em CONTRATO.md)."""
    out = {}
    for ind in INDICADORES:
        por_horizonte = {}
        for h in HORIZONTES:
            erros = [l["erro_pp"] for l in linhas if l["indicador"] == ind and l["quando"] == h]
            if not erros:
                continue
            por_horizonte[h] = {
                "erro_medio": round(sum(erros) / len(erros), 2),
                "erro_abs_medio": round(sum(abs(e) for e in erros) / len(erros), 2),
                "anos_subestimou": sum(e > 0 for e in erros),    # realizado acima do esperado
                "anos_superestimou": sum(e < 0 for e in erros),  # realizado abaixo do esperado
                "anos_exato": sum(e == 0 for e in erros),
                "n_anos": len(erros),
            }
        anos = sorted({l["ano"] for l in linhas if l["indicador"] == ind})
        out[ind] = {"anos": f"{anos[0]}–{anos[-1]}" if anos else "", "horizonte_principal": HORIZONTE_PRINCIPAL,
                    **por_horizonte.get(HORIZONTE_PRINCIPAL, {}), "por_horizonte": por_horizonte}
    return out


def _titulo(res: dict) -> str:
    """A mensagem do gráfico, derivada dos números (nada escrito à mão)."""
    sub = sum(res[i].get("anos_subestimou", 0) for i in INDICADORES)
    sup = sum(res[i].get("anos_superestimou", 0) for i in INDICADORES)
    n = sum(res[i].get("n_anos", 0) for i in INDICADORES)
    if sub > n / 2:
        frase = "Em janeiro, o Focus subestimou IPCA e Selic na maioria dos anos"
    elif sup > n / 2:
        frase = "Em janeiro, o Focus superestimou IPCA e Selic na maioria dos anos"
    else:
        frase = "Em janeiro, o Focus errou IPCA e Selic para os dois lados"

    def caindo(ind: str) -> bool:
        e = [res[ind]["por_horizonte"][h]["erro_abs_medio"] for h in HORIZONTES if h in res[ind]["por_horizonte"]]
        return all(a > b for a, b in zip(e, e[1:]))

    return frase + ("\ne o erro cai à medida que o ano passa" if all(caindo(i) for i in INDICADORES) else "")


def _grafico(linhas: list[dict], res: dict, data_focus: str, destino: Path) -> None:
    cores = {"12 meses antes": "#c6dbef", "início do ano": "#4292c6", "meio do ano": "#08306b"}
    fig, eixos = plt.subplots(1, 2, figsize=(LARGURA_PX / 100, 4.3), dpi=100)
    for ax, ind in zip(eixos, INDICADORES):
        d = [l for l in linhas if l["indicador"] == ind]
        anos = sorted({l["ano"] for l in d})
        larg = 0.2
        for k, h in enumerate(HORIZONTES):
            v = {l["ano"]: l["esperado"] for l in d if l["quando"] == h}
            ax.bar([i + (k - 1.5) * larg for i in range(len(anos))], [v.get(a, 0) for a in anos], width=larg,
                   color=cores[h], label=f"Focus {CURTO[h]}")
        real = {l["ano"]: l["realizado"] for l in d}
        ax.bar([i + 1.5 * larg for i in range(len(anos))], [real[a] for a in anos], width=larg,
               color="#d94801", label="Realizado")
        ax.set_xticks(range(len(anos)), [str(a) for a in anos], fontsize=8)
        ax.tick_params(axis="y", labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ph = res[ind]["por_horizonte"]
        erros = " · ".join(f"{CURTO[h]} {ph[h]['erro_abs_medio']:.2f}" for h in HORIZONTES if h in ph)
        ax.set_title(f"{ind} (% no ano)", fontsize=9.5, fontweight="bold", loc="left", pad=16)
        ax.text(0, 1.015, f"erro absoluto médio (p.p.): {erros}", transform=ax.transAxes,
                fontsize=6.8, color="#444", va="bottom")
    h, r = eixos[0].get_legend_handles_labels()
    fig.legend(h, r, ncol=4, fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.885))
    fig.suptitle(_titulo(res), fontsize=10.5, fontweight="bold", y=0.985)
    fig.text(0.01, 0.01, f"Fonte: Banco Central do Brasil (Focus e SGS), Focus até {data_focus}. "
                         "IPCA composto no ano; Selic meta no fim do ano.\n"
                         "Não constitui recomendação de investimento.", fontsize=6.5, color="#555")
    fig.tight_layout(rect=(0, 0.06, 1, 0.86))
    fig.savefig(destino, dpi=100)        # sem bbox_inches="tight" para manter exatamente LARGURA_PX
    plt.close(fig)


def historico(saida: Path) -> list[dict]:
    focus = carregar_focus()
    acc = tabela_acuracia(focus, carregar_sgs())
    acc = acc[acc["quando"].isin(HORIZONTES) & acc["ano"].isin(_anos_fechados(acc))]
    linhas = [{k: (int(v) if k == "ano" else float(v) if k in ("esperado", "realizado", "erro_pp") else v)
               for k, v in r.items()} for r in acc.to_dict("records")]

    saida.mkdir(exist_ok=True)
    _grafico(linhas, resumo_acuracia(linhas), f"{focus['Data'].max():%d/%m/%Y}", saida / "acuracia.png")
    return linhas
