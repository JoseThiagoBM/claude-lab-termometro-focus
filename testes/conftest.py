"""Configuração comum dos testes (dono: integração). Rode da raiz: python -m pytest -q testes"""
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "avancado" / "case1_focus"))

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "resumo_exemplo.json"


@pytest.fixture
def resumo() -> dict:
    """Um resumo real (Focus de 30/10/2026). Cada teste recebe uma cópia nova, pode estragar à vontade."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))
