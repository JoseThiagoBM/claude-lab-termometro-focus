"""Frente A. Teste inicial: as checagens param o agente com dado ruim. Acrescente um teste por checagem nova."""
from datetime import date

from termometro import checar


def _hoje() -> str:
    return f"{date.today():%d/%m/%Y}"


def test_dado_bom_passa(resumo):
    resumo["data_focus"] = _hoje()
    assert checar(resumo) == []


def test_focus_desatualizado_para(resumo):
    resumo["data_focus"] = "02/10/2020"
    assert any("dias atrás" in p for p in checar(resumo))


def test_valor_fora_da_faixa_para(resumo):
    resumo["data_focus"] = _hoje()
    resumo["indicadores"][0]["mediana"] = 52.2
    assert any("fora da faixa" in p for p in checar(resumo))
