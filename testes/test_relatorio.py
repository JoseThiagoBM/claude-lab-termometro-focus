"""Frente D. Relatório e e-mail, sem rede e sem Gmail."""
import base64

from enviar_email import preparar_mensagem
from relatorio import montar

# PNG de 1x1 pixel, para não depender do gráfico real
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")


def test_relatorio_tem_data_fonte_e_aviso(resumo, tmp_path):
    html = montar(resumo, "<p>análise</p>", tmp_path)
    assert resumo["data_focus"] in html
    assert "Banco Central do Brasil" in html
    assert "recomendação de investimento" in html


def test_relatorio_sem_campos_opcionais(resumo, tmp_path):
    resumo.pop("acuracia", None)
    resumo.pop("termometro", None)
    assert "<html" in montar(resumo, "<p>análise</p>", tmp_path)


def test_relatorio_usa_numeros_do_json_com_virgula(resumo, tmp_path):
    ipca = resumo["indicadores"][0]
    assert f"{ipca['mediana']:.2f}".replace(".", ",") in montar(resumo, "", tmp_path)


def test_alertas_aparecem(resumo, tmp_path):
    resumo["alertas"] = ["IPCA 2027: variou +0.46 em 4 semanas"]
    assert "IPCA 2027: variou +0.46" in montar(resumo, "", tmp_path)


def test_grafico_entra_em_base64(resumo, tmp_path):
    (tmp_path / "acuracia.png").write_bytes(PNG)
    assert 'src="data:image/png;base64,' in montar(resumo, "", tmp_path)


def test_email_troca_base64_por_content_id(resumo, tmp_path):
    (tmp_path / "acuracia.png").write_bytes(PNG)
    html = montar(resumo, "", tmp_path)
    msg = preparar_mensagem("assunto", html, "time@exemplo.com", ["banca@exemplo.com"])
    partes = list(msg.walk())
    imagens = [p for p in partes if p.get_content_maintype() == "image"]
    corpo = next(p for p in partes if p.get_content_type() == "text/html").get_payload(decode=True).decode()
    assert len(imagens) == 1 and imagens[0]["Content-ID"] == "<img1>"
    assert 'src="cid:img1"' in corpo and "base64," not in corpo
