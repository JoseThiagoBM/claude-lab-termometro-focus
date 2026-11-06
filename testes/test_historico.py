"""Frente B. Histórico de acerto: realizado certo, só anos fechados, resumo coerente, gráfico cabe no e-mail."""
import matplotlib.image as mpimg
import pytest

from historico import ANOS, HORIZONTES, LARGURA_PX, historico, resumo_acuracia
from inicio_focus import carregar_sgs, ipca_realizado_ano, selic_fim_de_ano


@pytest.fixture(scope="module")
def sgs():
    return carregar_sgs()


@pytest.fixture(scope="module")
def saida_hist(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("saida")
    return pasta, historico(pasta)


@pytest.mark.parametrize("ano", [2021, 2022, 2023, 2024, 2025])
def test_ipca_composto_bate_com_ipca_12m_de_dezembro(sgs, ano):
    dez = sgs[(sgs["serie"] == "ipca_12m") & (sgs["data"].dt.year == ano) & (sgs["data"].dt.month == 12)]
    assert not dez.empty
    # tolerância de 0,011 p.p.: em 2022 o composto dá 5,78 e a série oficial 5,79 (arredondamento)
    assert abs(ipca_realizado_ano(sgs, ano) - float(dez["valor"].iloc[0])) <= 0.011


@pytest.mark.parametrize("ano", [2021, 2022, 2023, 2024, 2025])
def test_selic_do_fim_do_ano_e_a_ultima_de_dezembro(sgs, ano):
    s = sgs[(sgs["serie"] == "selic_meta") & (sgs["data"].dt.year == ano) & (sgs["data"].dt.month == 12)]
    assert not s.empty
    assert selic_fim_de_ano(sgs, ano) == float(s.sort_values("data")["valor"].iloc[-1])


def test_ano_corrente_nao_tem_realizado(sgs):
    ano = int(sgs["data"].max().year)          # 2026: ainda sem dezembro
    assert ipca_realizado_ano(sgs, ano) is None
    assert selic_fim_de_ano(sgs, ano) is None


def test_so_entram_os_ultimos_anos_fechados(saida_hist):
    _, linhas = saida_hist
    assert {l["ano"] for l in linhas} == set(range(2025 - ANOS + 1, 2026))
    for ind in ("IPCA", "Selic"):
        for ano in range(2021, 2026):
            assert {l["quando"] for l in linhas if l["indicador"] == ind and l["ano"] == ano} == set(HORIZONTES)


def test_valores_de_inicio_do_ano_nao_mudaram(saida_hist):
    """Tabela de tarefas/B_historico.md (horizonte 'início do ano')."""
    _, linhas = saida_hist
    esp = {("IPCA", 2021): (3.43, 10.06), ("IPCA", 2024): (3.85, 4.83), ("Selic", 2022): (11.75, 13.75),
           ("Selic", 2025): (15.0, 15.0)}
    got = {(l["indicador"], l["ano"]): (l["esperado"], l["realizado"]) for l in linhas if l["quando"] == "início do ano"}
    for k, v in esp.items():
        assert got[k] == v


def test_erro_e_realizado_menos_esperado(saida_hist):
    _, linhas = saida_hist
    for l in linhas:
        assert abs(l["erro_pp"] - (l["realizado"] - l["esperado"])) <= 0.011


def test_resumo_coerente_com_as_linhas(saida_hist):
    _, linhas = saida_hist
    res = resumo_acuracia(linhas)
    for ind in ("IPCA", "Selic"):
        for h, r in res[ind]["por_horizonte"].items():
            erros = [l["erro_pp"] for l in linhas if l["indicador"] == ind and l["quando"] == h]
            assert r["n_anos"] == len(erros) == r["anos_subestimou"] + r["anos_superestimou"] + r["anos_exato"]
            assert r["anos_subestimou"] == sum(e > 0 for e in erros)
            assert r["erro_abs_medio"] == round(sum(map(abs, erros)) / len(erros), 2)
        assert res[ind]["erro_abs_medio"] == res[ind]["por_horizonte"]["início do ano"]["erro_abs_medio"]


def test_erro_cai_ao_longo_do_ano(saida_hist):
    """A conclusão do gráfico: quanto mais perto do fim do ano, menor o erro absoluto médio."""
    res = resumo_acuracia(saida_hist[1])
    for ind in ("IPCA", "Selic"):
        e = [res[ind]["por_horizonte"][h]["erro_abs_medio"] for h in HORIZONTES]
        assert e == sorted(e, reverse=True)


def test_grafico_cabe_no_email(saida_hist):
    pasta, _ = saida_hist
    img = mpimg.imread(pasta / "acuracia.png")
    assert img.shape[1] <= LARGURA_PX
