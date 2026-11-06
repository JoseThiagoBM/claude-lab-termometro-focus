"""Frente C. Testes sem chamar o Claude (o `gerar` é falso, com a forma gerar(resumo, instrucao_extra=""))."""
import pytest

from analise import analisar_conferido, com_contas, conferir, contas_extras, juro_real


class GerarFalso:
    """Motor falso: devolve os textos na ordem e guarda o que recebeu em cada chamada."""

    def __init__(self, *textos):
        self.textos, self.chamadas, self.resumos = list(textos), [], []

    def __call__(self, resumo, instrucao_extra=""):
        self.chamadas.append(instrucao_extra)
        self.resumos.append(resumo)
        return self.textos[min(len(self.chamadas), len(self.textos)) - 1]


MINI = {  # resumo pequeno, para saber exatamente quais números existem
    "data_focus": "30/10/2026",
    "indicadores": [{"indicador": "IPCA", "ano": 2026, "mediana": 5.22, "sequencia_semanas": 13}],
    "alertas": ["IPCA 2026: variou +0,46 p.p. em 4 semanas (limiar 0,30 p.p.)"],
    "termometro": {"ipca_12m": 4.58, "ipca_12m_mes": "09/2026", "meta_inflacao": 3.0},
    "acuracia_resumo": {"IPCA": {"n_anos": 5}},
    "integridade": {"linhas_duplicadas": 7},
}


# ------------------------------------------------------------------ conferir()
def test_numero_inventado_e_pego(resumo):
    assert "4,73" in conferir("<p>O IPCA 2026 foi a 4,73%.</p>", resumo)


def test_numero_do_json_passa(resumo):
    assert conferir("<p>O IPCA 2026 está em 5,22%.</p>", resumo) == []


def test_percentual_inteiro():
    assert conferir("<p>A meta é 3%.</p>", MINI) == []       # 3.0 está no JSON
    assert conferir("<p>Subiu 8%.</p>", MINI) == ["8"]


def test_numero_por_extenso():
    assert conferir("<p>Errou em cinco anos de cinco.</p>", MINI) == []
    assert conferir("<p>Subiu por sete semanas.</p>", MINI) == ["sete"]


def test_ordinal_da_sequencia():
    assert conferir("<p>IPCA sobe pela 13ª semana seguida.</p>", MINI) == []
    assert conferir("<p>IPCA sobe pela 14ª semana seguida.</p>", MINI) == ["14"]


def test_anos_e_datas_do_json_nao_sao_suspeitos():
    texto = "<h3>Focus de 30/10/2026</h3><p>IPCA 2026 e 2027; IPCA em 12 meses até 09/2026: 4,58%.</p>"
    assert conferir(texto, MINI) == []


def test_data_inventada_e_pega():
    assert conferir("<p>Focus de 15/12/2026.</p>", MINI) == ["15/12/2026"]


def test_horizontes_fixos_e_alerta_passam():
    texto = "<p>Variou +0,46 p.p. em 4 semanas (limiar 0,30 p.p.); histórico de 5 anos.</p>"
    assert conferir(texto, MINI) == []


def test_numero_de_integridade_nao_vale():
    assert conferir("<p>Havia 7 linhas duplicadas.</p>", MINI) == ["7"]


def test_formula_do_juro_real_passa(resumo):
    dados = com_contas(resumo)
    texto = "<li>Juro real 2027: 7,39%, calculado como (1 + 12,50%) / (1 + 4,76%) − 1.</li>"
    assert conferir(texto, dados) == []


# ------------------------------------------------------------------ contas extras (valores do fixture)
def test_juro_real_formula_exata():
    assert juro_real(15.0, 4.0) == 10.58      # (1,15 / 1,04 − 1) = 10,577%


def test_contas_extras_com_o_fixture(resumo):
    c = contas_extras(resumo)
    juros = {j["ano"]: j["juro_real"] for j in c["juro_real_esperado"]}
    assert juros == {2026: 7.87, 2027: 7.39}   # 1,135/1,0522 − 1 e 1,125/1,0476 − 1
    assert c["variacao_selic_entre_anos"]["variacao_pp"] == -1.0
    assert c["vies_historico_ipca"]["erro_medio_pp"] == 1.35


def test_vies_cai_para_media_de_erro_pp_sem_acuracia_resumo(resumo):
    resumo.pop("acuracia_resumo", None)
    resumo["acuracia"] = [{"indicador": "IPCA", "erro_pp": 1.0}, {"indicador": "IPCA", "erro_pp": 2.0},
                          {"indicador": "Selic", "erro_pp": 9.0}]
    assert contas_extras(resumo)["vies_historico_ipca"]["erro_medio_pp"] == 1.5


def test_campo_ausente_nao_inventa_conta():
    c = contas_extras({"indicadores": [], "alertas": []})
    assert "juro_real_esperado" not in c and "variacao_selic_entre_anos" not in c
    assert "vies_historico_ipca" not in c


def test_motor_recebe_as_contas_e_pode_cita_las(resumo):
    gerar = GerarFalso("<p>Juro real esperado para 2026: 7,87%.</p>")
    texto, suspeitos = analisar_conferido(resumo, gerar=gerar)
    assert suspeitos == []
    assert "contas_frente_c" in gerar.resumos[0]


# ------------------------------------------------------------------ reescrita automática
def test_analisar_conferido_devolve_suspeitos(resumo):
    texto, suspeitos = analisar_conferido(resumo, gerar=lambda r, instrucao_extra="": "<p>Selic em 99,99%.</p>")
    assert "99,99" in suspeitos


def test_reescrita_conserta_na_segunda_tentativa(resumo):
    gerar = GerarFalso("<p>IPCA 2026 em 4,73%.</p>", "<p>IPCA 2026 em 5,22%.</p>")
    texto, suspeitos = analisar_conferido(resumo, gerar=gerar)
    assert suspeitos == []
    assert texto == "<p>IPCA 2026 em 5,22%.</p>"
    assert len(gerar.chamadas) == 2
    # a reescrita manda o texto anterior e o número que não existe no JSON
    assert "4,73" in gerar.chamadas[1] and "IPCA 2026 em 4,73%" in gerar.chamadas[1]


def test_texto_certo_nao_reescreve(resumo):
    gerar = GerarFalso("<p>IPCA 2026 em 5,22%.</p>")
    _, suspeitos = analisar_conferido(resumo, gerar=gerar)
    assert suspeitos == [] and len(gerar.chamadas) == 1


def test_falha_nas_reescritas_devolve_ultimo_texto_e_suspeitos(resumo):
    gerar = GerarFalso("<p>Selic em 99,99%.</p>", "<p>Selic em 88,88%.</p>", "<p>Selic em 77,77%.</p>")
    texto, suspeitos = analisar_conferido(resumo, gerar=gerar, tentativas=2)
    assert len(gerar.chamadas) == 3  # 1ª versão + 2 reescritas
    assert texto == "<p>Selic em 77,77%.</p>"
    assert suspeitos == ["77,77"]


@pytest.mark.parametrize("tentativas", [0])
def test_tentativas_zero_nao_reescreve(resumo, tentativas):
    gerar = GerarFalso("<p>Selic em 99,99%.</p>", "<p>Selic em 13,75%.</p>")
    _, suspeitos = analisar_conferido(resumo, gerar=gerar, tentativas=tentativas)
    assert suspeitos == ["99,99"] and len(gerar.chamadas) == 1


def test_texto_sem_ia_continua_passando_na_conferencia(resumo):
    from reserva import texto_sem_ia
    texto, suspeitos = analisar_conferido(resumo, gerar=texto_sem_ia)
    assert suspeitos == []
