"""Frente C. Testes iniciais, sem chamar o Claude (o `gerar` é falso)."""
from analise import analisar_conferido, conferir


def test_numero_inventado_e_pego(resumo):
    assert "4,73" in conferir("<p>O IPCA 2026 foi a 4,73%.</p>", resumo)


def test_numero_do_json_passa(resumo):
    assert conferir("<p>O IPCA 2026 está em 5,22%.</p>", resumo) == []


def test_analisar_conferido_devolve_suspeitos(resumo):
    texto, suspeitos = analisar_conferido(resumo, gerar=lambda r: "<p>Selic em 99,99%.</p>")
    assert "99,99" in suspeitos

# TODO (Frente C): teste da reescrita — gerar falso que erra na 1ª chamada e acerta na 2ª.
