"""Frente B. Teste inicial: o IPCA composto bate com a série oficial de 12 meses (cuidado nº 3 do case)."""
import pytest

from inicio_focus import carregar_sgs, ipca_realizado_ano


@pytest.mark.parametrize("ano", [2021, 2022, 2023, 2024, 2025])
def test_ipca_composto_bate_com_ipca_12m_de_dezembro(ano):
    sgs = carregar_sgs()
    dez = sgs[(sgs["serie"] == "ipca_12m") & (sgs["data"].dt.year == ano) & (sgs["data"].dt.month == 12)]
    assert not dez.empty
    # tolerância de 0,011 p.p.: em 2022 o composto dá 5,78 e a série oficial 5,79 (arredondamento)
    assert abs(ipca_realizado_ano(sgs, ano) - float(dez["valor"].iloc[0])) <= 0.011
