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


def test_identidade_aprovada_no_cabecalho(resumo):
    import re
    documento = montar(resumo, '')
    titulo = re.search(r'<h1[^>]*>(.*?)</h1>', documento).group(1)
    assert titulo == 'Termômetro do Focus'
    assert re.search(r'<td[^>]*aria-hidden="true"[^>]*>TF</td>', documento)
    assert 'Compasso' not in documento and 'COMPASSO' not in documento


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


def test_termometro_e_incerteza_aparecem(resumo, tmp_path):
    resumo["termometro"] = {"selic_hoje": 13.75, "selic_esperada_fim_do_ano": 13.5, "selic_esperada_menos_hoje": -0.25,
                            "ipca_12m": 4.58, "ipca_12m_mes": "09/2026", "ipca_12m_menos_meta": 1.58,
                            "meta_inflacao": 3.0, "teto_da_meta": 4.5, "dolar_ptax": 5.46, "dolar_ptax_data": "05/11/2026"}
    resumo["sinais_de_incerteza"] = ["IPCA 2027: dispersão de 0,42 para 0,62 em 4 semanas"]
    html = montar(resumo, "", tmp_path)
    assert "13,75%" in html and "4,58%" in html and "R$ 5,46" in html
    assert "dispersão de 0,42 para 0,62" in html


def test_agente_nao_manda_integridade_ao_claude():
    import agente_semanal
    assert "integridade" in agente_semanal.CAMPOS_INTERNOS


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


def test_preheader_data_e_contagem(resumo):
    from html.parser import HTMLParser
    class Preheader(HTMLParser):
        def __init__(self):
            super().__init__()
            self.texto = ''
            self.dentro = False
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'div' and attrs.get('aria-hidden') == 'true':
                self.dentro = True
                assert 'display:none' in attrs.get('style', '')
                assert 'mso-hide:all' in attrs.get('style', '')
        def handle_data(self, data):
            if self.dentro:
                self.texto += data
        def handle_endtag(self, tag):
            if tag == 'div':
                self.dentro = False
    resumo['alertas'] = ['A', 'B']
    parser = Preheader()
    parser.feed(montar(resumo, ''))
    assert resumo['data_focus'] in parser.texto
    assert '2 alerta(s)' in parser.texto


def test_tabela_formato_focus_e_sequencia(resumo):
    from html.parser import HTMLParser
    class Celulas(HTMLParser):
        def __init__(self):
            super().__init__()
            self.celulas = []
            self.atual = None
        def handle_starttag(self, tag, attrs):
            if tag in ('td', 'th'):
                self.atual = ''
        def handle_data(self, data):
            if self.atual is not None:
                self.atual += data
        def handle_endtag(self, tag):
            if tag in ('td', 'th') and self.atual is not None:
                self.celulas.append(self.atual.strip())
                self.atual = None
    resumo['indicadores'] = [dict(indicador='IPCA', ano=2027, mediana_4_semanas_atras=4.30,
        mediana_semana_anterior=4.34, mediana=4.76, var_semana=0.42, sequencia_semanas=3, respondentes=144)]
    p = Celulas()
    p.feed(montar(resumo, ''))
    start = p.celulas.index('Há 4 semanas')
    assert p.celulas[start:start+5] == ['Há 4 semanas', 'Há 1 semana', 'Hoje', 'Comp. semanal', 'Resp.']
    start = p.celulas.index('4,30')
    assert p.celulas[start:start+5] == ['4,30', '4,34', '4,76', '▲ (3)', '144']
    resumo['indicadores'][0].update(var_semana=-0.42, sequencia_semanas=2)
    assert '▼ (2)' in montar(resumo, '')
    resumo['indicadores'][0].update(var_semana=0, sequencia_semanas=1)
    assert '= (1)' in montar(resumo, '')


def test_tamanho_html_sem_imagem_abaixo_de_100kb(resumo, tmp_path):
    import re
    (tmp_path / 'acuracia.png').write_bytes(PNG)
    documento = montar(resumo, '<p>Análise da semana.</p>', tmp_path)
    sem_imagem = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', '', documento)
    assert len(sem_imagem.encode('utf-8')) < 100_000
    assert '<style' not in documento and '<script' not in documento
    assert 'max-width:640px' in documento


def test_opcionais_ausentes_na_tabela_e_ordem(resumo):
    resumo['indicadores'] = [{'indicador': 'IPCA', 'ano': 2027, 'mediana': 4.76}]
    resumo['termometro'] = {'selic_hoje': 13.75}
    documento = montar(resumo, '<p>Texto original conferido.</p>')
    assert '4,76' in documento and '—' in documento
    assert 'Texto original conferido.' in documento
    titulos = ['O que já aconteceu × o que o mercado espera', 'Alertas da semana', 'Análise da semana', 'Números da semana', 'O Focus acertou?']
    assert [documento.index(t) for t in titulos] == sorted(documento.index(t) for t in titulos)
    assert '<html' in montar({}, '')
