"""Integração. Motores de reserva da análise (reserva.py), sem chamar Claude nem Codex."""
import pytest

from analise import analisar_conferido
from relatorio import montar
from reserva import motores, texto_sem_ia


def test_texto_sem_ia_sempre_passa_na_conferencia(resumo):
    texto, suspeitos = analisar_conferido(resumo, gerar=texto_sem_ia)
    assert suspeitos == []
    assert resumo["data_focus"] in texto and "sem IA" in texto


def test_ordem_padrao_e_claude_codex_sem_ia(monkeypatch):
    monkeypatch.delenv("MOTOR_ANALISE", raising=False)
    assert [n for n, _ in motores()] == ["claude", "codex", "sem_ia"]


def test_motor_escolhido_pela_variavel(monkeypatch):
    monkeypatch.setenv("MOTOR_ANALISE", "codex,sem_ia")
    assert [n for n, _ in motores()] == ["codex", "sem_ia"]


def test_motor_desconhecido_para(monkeypatch):
    monkeypatch.setenv("MOTOR_ANALISE", "gpt")
    with pytest.raises(SystemExit):
        motores()


def test_rodape_diz_qual_motor_escreveu(resumo, tmp_path):
    resumo["motor_analise"] = "codex"
    assert "Análise escrita por Codex" in montar(resumo, "", tmp_path)
