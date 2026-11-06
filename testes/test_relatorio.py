"""Frente D. Teste inicial: o relatório tem data, fonte e aviso, e não quebra sem os campos opcionais."""
from relatorio import montar


def test_relatorio_tem_data_fonte_e_aviso(resumo, tmp_path):
    html = montar(resumo, "<p>análise</p>", tmp_path)
    assert resumo["data_focus"] in html
    assert "Banco Central do Brasil" in html
    assert "recomendação de investimento" in html


def test_relatorio_sem_campos_opcionais(resumo, tmp_path):
    resumo.pop("acuracia", None)
    resumo.pop("termometro", None)
    assert "<html" in montar(resumo, "<p>análise</p>", tmp_path)
