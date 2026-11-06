"""O contrato do resumo_semana.json (CONTRATO.md). Dono: integração.
Se este teste quebrar, alguém renomeou ou removeu um campo que outra frente usa."""
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
REAL = RAIZ / "avancado" / "case1_focus" / "saida" / "resumo_semana.json"

CAMPOS_TOPO = {"data_focus": str, "gerado_em": str, "indicadores": list, "alertas": list, "acuracia": list}
CAMPOS_INDICADOR = {"indicador": str, "ano": int, "mediana": (int, float), "var_semana": (int, float),
                    "var_4_semanas": (int, float)}
CAMPOS_ACURACIA = {"indicador": str, "ano": int, "quando": str, "esperado": (int, float),
                   "realizado": (int, float), "erro_pp": (int, float)}


def _conferir(resumo: dict) -> None:
    for campo, tipo in CAMPOS_TOPO.items():
        assert isinstance(resumo.get(campo), tipo), f"campo '{campo}' ausente ou com tipo errado"
    assert resumo["indicadores"], "nenhum indicador"
    for linha in resumo["indicadores"]:
        for campo, tipo in CAMPOS_INDICADOR.items():
            assert isinstance(linha.get(campo), tipo), f"indicadores[*].{campo} ausente ou com tipo errado: {linha}"
    for linha in resumo["acuracia"]:
        for campo, tipo in CAMPOS_ACURACIA.items():
            assert isinstance(linha.get(campo), tipo), f"acuracia[*].{campo} ausente ou com tipo errado: {linha}"


def test_fixture_segue_o_contrato(resumo):
    _conferir(resumo)


@pytest.mark.skipif(not REAL.exists(), reason="rode o agente antes para gerar saida/resumo_semana.json")
def test_resumo_gerado_segue_o_contrato():
    _conferir(json.loads(REAL.read_text(encoding="utf-8")))
