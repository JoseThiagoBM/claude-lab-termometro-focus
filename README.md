# Termômetro do Focus — Case 1

> Claude Lab · Economia & Finanças · PUC-Rio · 06/11/2026

**🎬 Vídeo (2 min):** [preencher]
**🔗 Artefato público:** [preencher]

## Equipe

| Nome | Curso / período | Papel no projeto | LinkedIn / GitHub |
|---|---|---|---|
| | | A — termômetro e checagens | |
| | | B — histórico de acerto | |
| | | C — análise do Claude | |
| | | D — relatório, e-mail, agenda e entrega | |

## O problema

Toda segunda, alguém copia o Relatório Focus do Banco Central para uma planilha, compara com a semana anterior e escreve um resumo para os gestores. É manual, repetitivo e sujeito a erro. E fica a pergunta: o Focus costuma acertar?

## A solução

Um agente que roda sozinho toda segunda: baixa o Focus e as séries do SGS, calcula o que mudou, para e avisa se o dado vier errado ou atrasado, pede ao Claude uma análise curta, confere se todo número do texto existe nos dados e manda o relatório por e-mail com o histórico de acerto de 5 anos.

## Como funciona

```
baixar (BCB) → calcular (termometro.py) → histórico (historico.py) → checar (termometro.py)
→ analisar com claude -p (analise.py) → conferir números → montar HTML (relatorio.py) → enviar (enviar_email.py)
```

Formato dos dados entre as etapas: [CONTRATO.md](CONTRATO.md).

## Dados usados

- Banco Central do Brasil, Sistema de Expectativas de Mercado (Focus), API Olinda: IPCA, Selic, Câmbio e PIB Total, desde 2020, `baseCalculo = 0`.
- Banco Central do Brasil, SGS: IPCA mensal (433), IPCA 12 meses (13522), Selic meta (432), PTAX venda (1), IBC-Br (24363).
- Dados desta versão: Focus de 30/10/2026, baixado em 06/11/2026.

## Como verificamos os resultados

| O que | Onde conferimos | Resultado |
|---|---|---|
| IPCA 2026 = 5,22; Selic 2026 = 13,50; Câmbio 2026 = 5,34 (de 5,05) | Relatório Focus oficial de 30/10/2026 | bate |
| IPCA anual composto de 2021 a 2025 | série SGS 13522 (12 meses) de dezembro | bate; 2022 difere 0,01 p.p. por arredondamento |
| Focus desatualizado (35 dias) e IPCA = 52,2 simulados | etapa `checar` | o agente parou nos dois casos |
| Download do Focus quebrado (HTTP 400) | API Olinda | a API recusa `+` como espaço; corrigido para `%20` |

## Como reproduzir

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
.venv/Scripts/python.exe avancado/case1_focus/agente_semanal.py --sem-email
```

Para o e-mail: copie `avancado/case1_focus/.env.exemplo` para `.env` e preencha com uma senha de app do Gmail. O `.env` não vai para o GitHub.

## Limitações e próximos passos

- O agendamento depende do computador estar ligado e com o Claude Code logado às 10h de segunda.
- [preencher]

## Aviso

Projeto acadêmico desenvolvido em workshop. Não constitui recomendação de investimento.

**Feito com:** Claude Code, Python (pandas, requests, matplotlib), APIs públicas do Banco Central.
