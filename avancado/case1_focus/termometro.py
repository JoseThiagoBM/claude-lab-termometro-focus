"""
Etapas 2 e 3 do agente: CALCULAR o termômetro da semana e CHECAR os dados.
Dono: Pessoa A (Thomas). Saída: o dicionário `resumo` (formato em CONTRATO.md), salvo em saida/resumo_semana.json.

Interface fixa (o agente_semanal.py chama assim):
    calcular() -> dict          # o resumo da semana
    checar(resumo) -> list[str] # problemas; lista vazia = pode seguir

O que mudou em relação à versão inicial:
  - A semana é a do Focus PUBLICADO: a sexta da semana passada (o relatório sai na segunda com os dados
    da sexta). Rodar numa quinta não pega um dado de meio de semana.
  - As variações saem das medianas já arredondadas, como no PDF oficial (5,01 -> 5,22 = +0,21).
  - Alertas calibrados: 2 desvios-padrão das variações históricas (de 2021 em diante; 2020 fica fora por
    causa da pandemia), por indicador e por horizonte (ano corrente / ano seguinte), na semana e em
    4 semanas. O limiar usado vai para o JSON (limiar_4s, limiar_semana).
  - Bloco resumo["termometro"]: Selic hoje x esperada no fim do ano; IPCA 12 meses x meta; dólar PTAX.
  - Checagens novas: Focus da sexta de referência disponível, linhas duplicadas, indicador faltando,
    série do Focus que parou, respondentes abaixo do mínimo, semana congelada (dado repetido),
    série do SGS parada (janela por série) e IPCA anual composto x oficial.
  - Pedido da Frente C: sequencia_direcao/sequencia_semanas (há quantas semanas seguidas o indicador anda
    na mesma direção) e percentil_4s/raridade_4s (quão rara é a variação de 4 semanas nos últimos 6 anos).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from inicio_focus import META_INFLACAO, carregar_focus, carregar_sgs, ipca_realizado_ano

INDICADORES = ["IPCA", "Selic", "Câmbio", "PIB Total"]
TOLERANCIA_META = 1.5             # meta contínua: 3% com intervalo de 1,5% a 4,5%
N_DESVIOS = 2.0                   # alerta = variação maior que 2 desvios-padrão do histórico
INICIO_CALIBRACAO = "2021-01-01"  # com 2020, o limiar de 4 semanas do PIB do ano iria de 0,49 para 1,21 p.p.
ALTA_DISPERSAO = 0.25             # sinal de incerteza: desvio-padrão entre instituições +25% em 4 semanas
# Faixas plausíveis para a checagem: fora disso, provavelmente é erro de dado.
FAIXA = {"IPCA": (0, 20), "Selic": (0, 30), "Câmbio": (2, 10), "PIB Total": (-10, 10)}
MAX_DIAS_DEFASAGEM = 10
MIN_RESPONDENTES = 20
TOLERANCIA_IPCA_COMPOSTO = 0.05
# Janela por série do SGS (dias desde a última observação): Selic e dólar são diários; o IPCA sai ~40 dias
# depois do mês (a observação de setembro tem data 01/09 e só chega em outubro); o IBC-Br, ~75 dias.
JANELA_SGS = {"selic_meta": 10, "dolar_ptax_venda": 10, "ipca_mensal": 80, "ipca_12m": 80, "ibc_br": 125}
UNIDADE = {"IPCA": "p.p.", "Selic": "p.p.", "Câmbio": "R$", "PIB Total": "p.p."}
ANOS_RARIDADE = 6                 # janela da comparação da variação de 4 semanas
RARA, INCOMUM = 95, 80            # percentis: >= 95 rara, >= 80 incomum, abaixo disso normal


# ---------------------------------------------------------------- auxiliares
def _d(texto: str) -> date:
    return datetime.strptime(texto, "%d/%m/%Y").date()


def _br(x: float, casas: int = 2, sinal: bool = False) -> str:
    return (f"{x:+.{casas}f}" if sinal else f"{x:.{casas}f}").replace(".", ",")


def sexta_de_referencia(hoje: date) -> date:
    """Em qualquer dia da semana, o último Focus publicado é o da sexta da semana passada."""
    return hoje - timedelta(days=hoje.weekday()) - timedelta(days=3)


def _serie(focus: pd.DataFrame, ind: str, ano: int, ate: pd.Timestamp) -> pd.Series:
    """Mediana semanal (última observação de cada semana terminando na sexta), só até `ate`."""
    f = focus[(focus["Indicador"] == ind) & (focus["DataReferencia"] == ano) & (focus["Data"] <= ate)]
    return f.set_index("Data")["Mediana"].sort_index().resample("W-FRI").last().dropna()


def _valor(focus: pd.DataFrame, ind: str, ano: int, ate: pd.Timestamp, coluna: str) -> float | None:
    f = focus[(focus["Indicador"] == ind) & (focus["DataReferencia"] == ano) & (focus["Data"] <= ate)]
    return None if f.empty else float(f.sort_values("Data")[coluna].iloc[-1])


def desvio_historico(focus: pd.DataFrame, ind: str, horizonte: int, ate: pd.Timestamp,
                     semanas: int) -> float | None:
    """Desvio-padrão das variações de `semanas` semanas da mediana. Cada ano de referência é uma série
    separada, e só entram as variações de quando aquele ano era o corrente (horizonte 0) ou o seguinte (1)."""
    partes = []
    for ano_ref in sorted(focus["DataReferencia"].unique()):
        s = _serie(focus, ind, int(ano_ref), ate)
        if len(s) <= semanas:
            continue
        d = s.diff(semanas).dropna()
        d = d[(d.index.year == ano_ref - horizonte)
              & (d.index >= pd.Timestamp(f"{ano_ref - horizonte}-01-01") + pd.Timedelta(weeks=semanas))
              & (d.index >= pd.Timestamp(INICIO_CALIBRACAO))]
        partes.append(d)
    return float(pd.concat(partes).std()) if partes else None


def sequencia(s: pd.Series) -> tuple[str, int]:
    """Direção da última variação semanal (medianas arredondadas, como no relatório oficial) e há quantas
    semanas seguidas ela se repete. Ex.: ("alta", 13) = "subiu pela 13ª semana seguida"."""
    d = s.round(2).diff().round(2).dropna()
    if d.empty:
        return "estável", 0
    sinal = int(np.sign(d.iloc[-1]))
    n = 0
    for v in reversed(d.to_numpy()):
        if int(np.sign(v)) != sinal:
            break
        n += 1
    return {1: "alta", -1: "queda", 0: "estável"}[sinal], n


def raridade_4s(focus: pd.DataFrame, ind: str, horizonte: int, ate: pd.Timestamp, semana_atual: pd.Timestamp,
                var_4s: float) -> dict:
    """Percentil da variação de 4 semanas (em módulo) entre todas as dos últimos ANOS_RARIDADE anos, do mesmo
    indicador e horizonte, sem contar a semana atual. percentil 97 = 97% das variações foram menores."""
    inicio = ate - pd.DateOffset(years=ANOS_RARIDADE)
    partes = []
    for ano_ref in sorted(focus["DataReferencia"].unique()):
        s = _serie(focus, ind, int(ano_ref), ate).round(2)
        if len(s) <= 4:
            continue
        d = s.diff(4).round(2).dropna()
        d = d[(d.index.year == ano_ref - horizonte)
              & (d.index >= pd.Timestamp(f"{ano_ref - horizonte}-01-01") + pd.Timedelta(weeks=4))
              & (d.index > inicio) & (d.index < semana_atual)]
        partes.append(d.abs())
    hist = pd.concat(partes) if partes else pd.Series(dtype=float)
    if hist.empty:
        return {"percentil_4s": None, "raridade_4s": None, "n_historico_4s": 0}
    p = round(100 * float((hist < abs(var_4s)).mean()))
    return {"percentil_4s": p, "raridade_4s": "rara" if p >= RARA else "incomum" if p >= INCOMUM else "normal",
            "n_historico_4s": int(len(hist))}


def _ultimo_sgs(sgs: pd.DataFrame, serie: str) -> tuple[float, pd.Timestamp] | None:
    s = sgs[sgs["serie"] == serie].dropna(subset=["valor"]).sort_values("data")
    return None if s.empty else (float(s["valor"].iloc[-1]), s["data"].iloc[-1])


# ---------------------------------------------------------------- 2. calcular
def calcular(hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    focus, sgs = carregar_focus(), carregar_sgs()
    sexta = sexta_de_referencia(hoje)
    corte = focus.loc[focus["Data"] <= pd.Timestamp(sexta), "Data"].max()
    ano = corte.year
    resumo = {"data_focus": f"{corte:%d/%m/%Y}", "gerado_em": f"{hoje:%d/%m/%Y}",
              "sexta_referencia": f"{sexta:%d/%m/%Y}",
              "indicadores": [], "alertas": [], "sinais_de_incerteza": [],
              "regra_de_alerta": "variação maior que 2 desvios-padrão das variações históricas do mesmo "
                                 "indicador e horizonte, de 2021 em diante"}
    for ind in INDICADORES:
        for h, a in ((0, ano), (1, ano + 1)):
            s = _serie(focus, ind, a, corte)
            if len(s) < 5:
                continue
            med, ant, m4 = (round(float(s.iloc[i]), 2) for i in (-1, -2, -5))  # arredonda antes, como o PDF
            d4, d1 = desvio_historico(focus, ind, h, corte, 4), desvio_historico(focus, ind, h, corte, 1)
            dp = _valor(focus, ind, a, corte, "DesvioPadrao")
            dp_ant = _valor(focus, ind, a, s.index[-2], "DesvioPadrao")
            dp_4s = _valor(focus, ind, a, s.index[-5], "DesvioPadrao")
            ultima = focus[(focus["Indicador"] == ind) & (focus["DataReferencia"] == a)
                           & (focus["Data"] <= corte)]["Data"].max()
            linha = {"indicador": ind, "ano": int(a), "mediana": med,
                     "var_semana": round(med - ant, 2), "var_4_semanas": round(med - m4, 2),
                     "mediana_semana_anterior": ant, "mediana_4_semanas_atras": m4,
                     "limiar_4s": round(N_DESVIOS * d4, 2) if d4 else None,
                     "limiar_semana": round(N_DESVIOS * d1, 2) if d1 else None,
                     "desvios_4s": round((med - m4) / d4, 1) if d4 else None,
                     "desvio_padrao": round(dp, 2) if dp is not None else None,
                     "desvio_padrao_semana_anterior": round(dp_ant, 2) if dp_ant is not None else None,
                     "desvio_padrao_4_semanas_atras": round(dp_4s, 2) if dp_4s is not None else None,
                     "respondentes": int(_valor(focus, ind, a, corte, "numeroRespondentes") or 0),
                     "data_ultima_coleta": f"{ultima:%d/%m/%Y}"}
            direcao, semanas = sequencia(s)
            linha.update(sequencia_direcao=direcao, sequencia_semanas=semanas,
                         **raridade_4s(focus, ind, h, corte, s.index[-1], linha["var_4_semanas"]))
            if ind == "IPCA":
                linha["distancia_da_meta"] = round(med - META_INFLACAO, 2)
                linha["distancia_do_teto"] = round(med - (META_INFLACAO + TOLERANCIA_META), 2)
            resumo["indicadores"].append(linha)

            u, nome = UNIDADE[ind], f"{ind} {a}"
            if linha["limiar_4s"] and abs(linha["var_4_semanas"]) >= linha["limiar_4s"]:
                resumo["alertas"].append(
                    f"{nome}: variou {_br(linha['var_4_semanas'], sinal=True)} {u} em 4 semanas "
                    f"({_br(abs(linha['desvios_4s']), 1)} desvios-padrão; limiar {_br(linha['limiar_4s'])} {u})")
            elif linha["limiar_semana"] and abs(linha["var_semana"]) >= linha["limiar_semana"]:
                resumo["alertas"].append(
                    f"{nome}: variou {_br(linha['var_semana'], sinal=True)} {u} em uma semana "
                    f"(limiar {_br(linha['limiar_semana'])} {u})")
            if dp and dp_4s and (dp / dp_4s - 1) >= ALTA_DISPERSAO:
                resumo["sinais_de_incerteza"].append(
                    f"{nome}: dispersão de {_br(dp_4s)} para {_br(dp)} em 4 semanas")

    # o que o gestor quer ver: o que já aconteceu x o que o mercado espera
    t = {"meta_inflacao": META_INFLACAO, "teto_da_meta": META_INFLACAO + TOLERANCIA_META}
    sel = _ultimo_sgs(sgs, "selic_meta")
    sel_esp = next((l for l in resumo["indicadores"] if l["indicador"] == "Selic" and l["ano"] == ano), None)
    if sel and sel_esp:
        t.update(selic_hoje=round(sel[0], 2), selic_hoje_data=f"{sel[1]:%d/%m/%Y}",
                 selic_esperada_fim_do_ano=sel_esp["mediana"],
                 selic_esperada_menos_hoje=round(sel_esp["mediana"] - sel[0], 2))
    ipca12 = _ultimo_sgs(sgs, "ipca_12m")
    if ipca12:
        t.update(ipca_12m=round(ipca12[0], 2), ipca_12m_mes=f"{ipca12[1]:%m/%Y}",
                 ipca_12m_menos_meta=round(ipca12[0] - META_INFLACAO, 2))
    ptax = _ultimo_sgs(sgs, "dolar_ptax_venda")
    if ptax:
        t.update(dolar_ptax=round(ptax[0], 2), dolar_ptax_data=f"{ptax[1]:%d/%m/%Y}")
    resumo["termometro"] = t

    # insumos das checagens de integridade (o checar() só recebe o resumo)
    integ = {"linhas_duplicadas": int(focus.duplicated(["Indicador", "Data", "DataReferencia"]).sum()),
             "sgs_ultima_data": {}, "ipca_composto_x_oficial": []}
    for serie in JANELA_SGS:
        v = _ultimo_sgs(sgs, serie)
        if v:
            integ["sgs_ultima_data"][serie] = f"{v[1]:%d/%m/%Y}"
    for a in range(ano - 5, ano):
        comp = ipca_realizado_ano(sgs, a)
        of = sgs[(sgs["serie"] == "ipca_12m") & (sgs["data"].dt.year == a) & (sgs["data"].dt.month == 12)]
        if comp is not None and not of.empty:
            integ["ipca_composto_x_oficial"].append(
                {"ano": a, "composto": round(comp, 2), "oficial": round(float(of["valor"].iloc[-1]), 2)})
    resumo["integridade"] = integ
    return resumo


# ---------------------------------------------------------------- 3. checar
def checar(resumo: dict) -> list[str]:
    """Lista de problemas (vazia = pode seguir). As checagens que dependem de campos novos só rodam
    quando o campo existe, para o resumo antigo da fixture continuar válido."""
    problemas = []
    hoje = date.today()
    dias = (hoje - _d(resumo["data_focus"])).days
    if dias > MAX_DIAS_DEFASAGEM:
        problemas.append(f"o Focus mais recente é de {resumo['data_focus']} ({dias} dias atrás)")
    if "sexta_referencia" in resumo and (_d(resumo["sexta_referencia"]) - _d(resumo["data_focus"])).days > 1:
        problemas.append(f"o Focus da sexta {resumo['sexta_referencia']} ainda não está nos dados "
                         f"(último: {resumo['data_focus']})")
    if not resumo["indicadores"]:
        problemas.append("nenhum indicador calculado")

    ano = _d(resumo["data_focus"]).year
    presentes = {(l["indicador"], l["ano"]) for l in resumo["indicadores"]}
    faltam = [f"{i} {a}" for i in INDICADORES for a in (ano, ano + 1) if (i, a) not in presentes]
    if resumo["indicadores"] and faltam:
        problemas.append(f"indicadores faltando: {', '.join(faltam)}")

    for l in resumo["indicadores"]:
        lo, hi = FAIXA[l["indicador"]]
        if not lo <= l["mediana"] <= hi:
            problemas.append(f"{l['indicador']} {l['ano']} = {l['mediana']} fora da faixa plausível")
        if "respondentes" in l and l["respondentes"] < MIN_RESPONDENTES:
            problemas.append(f"{l['indicador']} {l['ano']}: só {l['respondentes']} respondentes "
                             f"(mínimo {MIN_RESPONDENTES})")
        if "data_ultima_coleta" in l and l["data_ultima_coleta"] != resumo["data_focus"]:
            problemas.append(f"a série {l['indicador']} {l['ano']} parou em {l['data_ultima_coleta']}")

    com_dp = [l for l in resumo["indicadores"] if "desvio_padrao_semana_anterior" in l]
    if com_dp and len(com_dp) == len(resumo["indicadores"]) and all(
            l["var_semana"] == 0 and l["desvio_padrao"] == l["desvio_padrao_semana_anterior"] for l in com_dp):
        problemas.append("semana repetida: medianas e dispersões idênticas às da semana anterior")

    integ = resumo.get("integridade", {})
    if integ.get("linhas_duplicadas"):
        problemas.append(f"{integ['linhas_duplicadas']} linhas duplicadas no Focus")
    for serie, ultima in integ.get("sgs_ultima_data", {}).items():
        atraso = (hoje - _d(ultima)).days
        if atraso > JANELA_SGS.get(serie, MAX_DIAS_DEFASAGEM):
            problemas.append(f"a série {serie} do SGS parou em {ultima} ({atraso} dias; "
                             f"janela de {JANELA_SGS.get(serie)} dias)")
    for x in integ.get("ipca_composto_x_oficial", []):
        if abs(x["composto"] - x["oficial"]) > TOLERANCIA_IPCA_COMPOSTO:
            problemas.append(f"IPCA {x['ano']}: composto {x['composto']} x oficial {x['oficial']} não bate")
    return problemas
