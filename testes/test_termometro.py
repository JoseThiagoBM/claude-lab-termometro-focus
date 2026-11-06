"""Frente A. Cada checagem tem um teste que estraga o resumo de propósito e confere que o agente para.
No fim, um teste com os dados reais (Focus de 30/10/2026) confere os números contra o PDF oficial do BC
e que o salto real da Selic 2027 dispara ALERTA, e não a checagem de erro."""
from datetime import date
from pathlib import Path

import pytest

import termometro
from termometro import checar

RAIZ = Path(__file__).resolve().parents[1]
DADOS_REAIS = RAIZ / "data" / "case1_focus" / "focus_anuais.csv"


def _hoje() -> str:
    return f"{date.today():%d/%m/%Y}"


@pytest.fixture
def bom(resumo):
    """A fixture real, com a data de hoje e os campos novos da Frente A preenchidos com valores bons."""
    resumo["data_focus"] = _hoje()
    resumo["sexta_referencia"] = _hoje()
    for l in resumo["indicadores"]:
        l.update(respondentes=120, data_ultima_coleta=_hoje(),
                 desvio_padrao_semana_anterior=(l.get("desvio_padrao") or 0) + 0.01)
    resumo["integridade"] = {"linhas_duplicadas": 0, "sgs_ultima_data": {"selic_meta": _hoje()},
                             "ipca_composto_x_oficial": [{"ano": 2022, "composto": 5.78, "oficial": 5.79}]}
    return resumo


def test_dado_bom_passa(resumo):
    resumo["data_focus"] = _hoje()
    assert checar(resumo) == []


def test_dado_bom_com_campos_novos_passa(bom):
    assert checar(bom) == []


def test_focus_desatualizado_para(resumo):
    resumo["data_focus"] = "02/10/2020"
    assert any("dias atrás" in p for p in checar(resumo))


def test_valor_fora_da_faixa_para(resumo):
    resumo["data_focus"] = _hoje()
    resumo["indicadores"][0]["mediana"] = 52.2
    assert any("fora da faixa" in p for p in checar(resumo))


def test_focus_da_sexta_ainda_nao_saiu_para(bom):
    bom["sexta_referencia"] = _hoje()
    bom["data_focus"] = f"{date.fromordinal(date.today().toordinal() - 3):%d/%m/%Y}"
    for l in bom["indicadores"]:
        l["data_ultima_coleta"] = bom["data_focus"]
    assert any("ainda não está nos dados" in p for p in checar(bom))


def test_poucos_respondentes_para(bom):
    bom["indicadores"][0]["respondentes"] = 5
    assert any("respondentes" in p for p in checar(bom))


def test_serie_do_focus_parou_para(bom):
    bom["indicadores"][-1]["data_ultima_coleta"] = "02/10/2026"
    assert any("parou em 02/10/2026" in p for p in checar(bom))


def test_indicador_faltando_para(bom):
    bom["indicadores"] = [l for l in bom["indicadores"] if l["indicador"] != "PIB Total"]
    assert any("indicadores faltando" in p for p in checar(bom))


def test_semana_repetida_para(bom):
    for l in bom["indicadores"]:
        l["var_semana"] = 0.0
        l["desvio_padrao_semana_anterior"] = l["desvio_padrao"]
    assert any("semana repetida" in p for p in checar(bom))


def test_linhas_duplicadas_para(bom):
    bom["integridade"]["linhas_duplicadas"] = 8
    assert any("duplicadas" in p for p in checar(bom))


def test_serie_do_sgs_parada_para(bom):
    bom["integridade"]["sgs_ultima_data"]["selic_meta"] = "01/09/2026"
    assert any("selic_meta do SGS parou" in p for p in checar(bom))


def test_ipca_atrasado_dentro_da_janela_passa(bom):
    # o IPCA de setembro tem data 01/09 e só sai em outubro: 60 dias de atraso é normal para ele
    bom["integridade"]["sgs_ultima_data"]["ipca_mensal"] = f"{date.fromordinal(date.today().toordinal() - 60):%d/%m/%Y}"
    assert checar(bom) == []


def test_ipca_composto_nao_bate_para(bom):
    bom["integridade"]["ipca_composto_x_oficial"][0]["composto"] = 6.29
    assert any("não bate" in p for p in checar(bom))


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_dados_reais_batem_com_o_focus_oficial(monkeypatch):
    class Hoje(date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 6)

    monkeypatch.setattr(termometro, "date", Hoje)
    r = termometro.calcular()
    assert r["data_focus"] == "30/10/2026"
    linha = {(l["indicador"], l["ano"]): l for l in r["indicadores"]}
    # PDF oficial do Focus de 30/10/2026 (Mediana - Agregado): há 4 semanas / há 1 semana / hoje / resp.
    oficial = {("IPCA", 2026): (5.01, 5.19, 5.22, 144), ("IPCA", 2027): (4.30, 4.34, 4.76, 144),
               ("Selic", 2026): (13.50, 13.25, 13.50, 143), ("Selic", 2027): (12.00, 11.75, 12.50, 143),
               ("Câmbio", 2026): (5.20, 5.05, 5.34, 120), ("Câmbio", 2027): (5.28, 5.15, 5.40, 119),
               ("PIB Total", 2026): (1.85, 1.80, 1.76, 117), ("PIB Total", 2027): (1.40, 1.31, 1.20, 116)}
    for chave, (h4, h1, hoje, resp) in oficial.items():
        l = linha[chave]
        assert (l["mediana_4_semanas_atras"], l["mediana_semana_anterior"], l["mediana"], l["respondentes"]) \
            == (h4, h1, hoje, resp), chave
    assert linha[("IPCA", 2026)]["var_4_semanas"] == 0.21          # 5,01 -> 5,22 como no PDF
    assert all(l["limiar_4s"] and l["limiar_semana"] for l in r["indicadores"])
    # o salto real da Selic 2027 (11,75 -> 12,50) é ALERTA, não erro de dado
    assert any(a.startswith("Selic 2027") for a in r["alertas"])
    assert checar(r) == []


def test_sequencia_conta_semanas_seguidas():
    import pandas as pd

    def s(v):
        return pd.Series(v, index=pd.date_range("2026-01-02", periods=len(v), freq="W-FRI"))

    assert termometro.sequencia(s([5.0, 5.1, 5.0, 5.1, 5.2, 5.3])) == ("alta", 3)
    assert termometro.sequencia(s([5.3, 5.2, 5.1])) == ("queda", 2)
    assert termometro.sequencia(s([5.0, 5.1, 5.1, 5.1])) == ("estável", 2)
    assert termometro.sequencia(s([5.0, 5.001, 5.004])) == ("estável", 2)   # arredondado a 2 casas, não mudou


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_sequencia_bate_com_o_noticiario():
    # Focus de 05/06/2026: IPCA 2026 subiu pela 13ª semana seguida (5,09 -> 5,11).
    # Focus de 10/07/2026: caiu pela 2ª semana seguida (5,30 -> 5,16).
    for hoje, esperado in ((date(2026, 6, 8), ("alta", 13)), (date(2026, 7, 13), ("queda", 2))):
        l = next(x for x in termometro.calcular(hoje)["indicadores"] if (x["indicador"], x["ano"]) == ("IPCA", 2026))
        assert (l["sequencia_direcao"], l["sequencia_semanas"]) == esperado, hoje


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_raridade_4s_dados_reais():
    r = termometro.calcular(date(2026, 11, 6))
    linha = {(l["indicador"], l["ano"]): l for l in r["indicadores"]}
    assert linha[("IPCA", 2027)]["raridade_4s"] == "rara"      # +0,46 em 4 semanas: também é alerta (3,1 desvios)
    assert linha[("Selic", 2026)]["percentil_4s"] == 0         # não mudou em 4 semanas
    assert all(0 <= l["percentil_4s"] <= 100 and l["n_historico_4s"] >= 200 for l in r["indicadores"])


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_maior_desde_e_erro_mesma_epoca_dados_reais():
    r = termometro.calcular(date(2026, 11, 6))
    linha = {(l["indicador"], l["ano"]): l for l in r["indicadores"]}
    assert r["inicio_dos_dados"] == 2020
    assert linha[("IPCA", 2027)]["var_semana_inedita"] is True               # +0,42: maior alta semanal desde 2020
    assert linha[("Selic", 2027)]["var_semana_maior_desde"] == "20/12/2024"  # +0,75
    assert linha[("IPCA", 2026)]["var_semana_maior_desde"] == "09/10/2026"   # movimento comum: data recente
    e = linha[("Selic", 2027)]["erro_mesma_epoca"]
    assert (e["anos"], e["anos_realizado_acima"], e["erro_medio_pp"]) == (5, 5, 3.45)
    assert linha[("IPCA", 2026)]["erro_mesma_epoca"]["erro_absoluto_medio_pp"] == 0.33
    assert "erro_mesma_epoca" not in linha[("Câmbio", 2026)]


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_conferir_aceita_frases_com_os_campos_novos():
    from analise import conferir
    r = termometro.calcular(date(2026, 11, 6))
    texto = ("<p>A alta semanal do IPCA 2027 é a maior desde o início dos dados, em 2020. A Selic 2027 teve a "
             "maior alta semanal desde 20/12/2024. Na mesma época do ano, nos últimos 5 anos, a Selic do ano "
             "seguinte veio acima do esperado em 5 de 5 anos, em média 3,45 p.p.</p>")
    assert conferir(texto, r) == []


@pytest.mark.skipif(not DADOS_REAIS.exists(), reason="baixe os dados com scripts/baixar_dados_bcb.py")
def test_ancoragem_ipca_dados_reais():
    r = termometro.calcular(date(2026, 11, 6))
    curva = {c["ano"]: c for c in r["ancoragem_ipca"]}
    assert sorted(curva) == [2026, 2027, 2028, 2029]
    assert (curva[2028]["mediana"], curva[2028]["distancia_da_meta"], curva[2028]["maior_desde"]) == (4.0, 1.0, "15/08/2025")
    assert curva[2029]["maior_desde"] == "02/06/2023"       # 3 anos à frente: maior desde jun/2023
    assert curva[2027]["maior_desde"] == "27/12/2024" and curva[2026]["acima_do_teto"]
    from analise import conferir
    texto = ("<p>A mediana do IPCA fica acima da meta até 2029: 4,00% em 2028, a maior para 2 anos à frente "
             "desde 15/08/2025, e 3,98% em 2029, a maior desde 02/06/2023.</p>")
    assert conferir(texto, r) == []
