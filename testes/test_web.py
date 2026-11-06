"""Frente D. Versão web do relatório (artefato público), sem rede."""
import base64

from web import montar_web

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")


def test_pagina_tem_titulo_fonte_aviso_e_tema(resumo, tmp_path):
    html = montar_web(resumo, "<p>análise</p>", tmp_path)
    assert html.startswith("<title>Termômetro do Focus</title>")
    assert resumo["data_focus"] in html and "Banco Central do Brasil" in html
    assert "recomendação de investimento" in html
    assert "prefers-color-scheme: dark" in html and ':root[data-theme="dark"]' in html


def test_tabela_no_formato_do_focus(resumo, tmp_path):
    resumo["indicadores"][0].update(mediana_4_semanas_atras=5.01, mediana_semana_anterior=5.19,
                                    sequencia_semanas=1, raridade_4s="normal", percentil_4s=52)
    html = montar_web(resumo, "", tmp_path)
    assert "Há 4 semanas" in html and "5,01" in html and "5,19" in html and "▲ (1)" in html


def test_grafico_embutido_e_sem_campos_opcionais(resumo, tmp_path):
    (tmp_path / "acuracia.png").write_bytes(PNG)
    for campo in ("termometro", "contas_frente_c", "acuracia_resumo", "sinais_de_incerteza"):
        resumo.pop(campo, None)
    html = montar_web(resumo, "", tmp_path)
    assert 'src="data:image/png;base64,' in html
