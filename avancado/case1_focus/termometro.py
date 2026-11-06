"""
Etapas 2 e 3 do agente: CALCULAR o termômetro da semana e CHECAR os dados.
Dono: Pessoa A. Saída: o dicionário `resumo` (formato em CONTRATO.md), salvo em saida/resumo_semana.json.
"""
from datetime import date

from inicio_focus import META_INFLACAO, carregar_focus, serie_semanal

INDICADORES = ["IPCA", "Selic", "Câmbio", "PIB Total"]
# TODO: limiares chutados. Calibrem com o histórico (ex.: 2 desvios-padrão das variações de 4 semanas).
LIMIAR_4S = {"IPCA": 0.3, "Selic": 0.5, "Câmbio": 0.15, "PIB Total": 0.3}
# Faixas plausíveis para a checagem: fora disso, provavelmente é erro de dado.
FAIXA = {"IPCA": (0, 20), "Selic": (0, 30), "Câmbio": (2, 10), "PIB Total": (-10, 10)}
MAX_DIAS_DEFASAGEM = 10


def calcular() -> dict:
    focus = carregar_focus()
    data_focus = focus["Data"].max()
    resumo = {"data_focus": f"{data_focus:%d/%m/%Y}", "gerado_em": f"{date.today():%d/%m/%Y}",
              "indicadores": [], "alertas": []}
    for ind in INDICADORES:
        for ano in (data_focus.year, data_focus.year + 1):
            s = serie_semanal(focus, ind, ano)
            if len(s) < 5:
                continue
            linha = {"indicador": ind, "ano": int(ano), "mediana": round(float(s.iloc[-1]), 2),
                     "var_semana": round(float(s.iloc[-1] - s.iloc[-2]), 2),
                     "var_4_semanas": round(float(s.iloc[-1] - s.iloc[-5]), 2)}
            disp = focus[(focus["Indicador"] == ind) & (focus["DataReferencia"] == ano)
                         & (focus["Data"] == focus["Data"].max())]["DesvioPadrao"]
            if not disp.empty:
                linha["desvio_padrao"] = round(float(disp.iloc[0]), 2)
            if ind == "IPCA":
                linha["distancia_da_meta"] = round(linha["mediana"] - META_INFLACAO, 2)
            resumo["indicadores"].append(linha)
            if abs(linha["var_4_semanas"]) >= LIMIAR_4S[ind]:
                resumo["alertas"].append(f"{ind} {ano}: variou {linha['var_4_semanas']:+.2f} em 4 semanas")
    # TODO: o que mais um gestor quer ver toda segunda? Acurácia do ano passado? Selic atual vs. esperada?
    #       O histórico de acerto (tabela_acuracia em inicio_focus.py) entra em resumo["acuracia"].
    return resumo


def checar(resumo: dict) -> list[str]:
    problemas = []
    dias = (date.today() - date(*map(int, reversed(resumo["data_focus"].split("/"))))).days
    if dias > MAX_DIAS_DEFASAGEM:
        problemas.append(f"o Focus mais recente é de {resumo['data_focus']} ({dias} dias atrás)")
    if not resumo["indicadores"]:
        problemas.append("nenhum indicador calculado")
    for l in resumo["indicadores"]:
        lo, hi = FAIXA[l["indicador"]]
        if not lo <= l["mediana"] <= hi:
            problemas.append(f"{l['indicador']} {l['ano']} = {l['mediana']} fora da faixa plausível")
    # TODO: outras checagens? (ex.: número de respondentes muito baixo, semana repetida)
    return problemas
