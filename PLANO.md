# Plano do time — Case 1, Termômetro do Focus (uso interno; os jurados leem o README)

**Cena da demo:** rodamos um comando; o agente baixa o Focus, calcula, confere e o e-mail chega na hora com o que mudou na semana e o gráfico "o Focus acertou?". Depois estragamos um dado de propósito e o agente para e manda o alerta em vez do relatório.

## Stack

- **Python 3.12 + `.venv`** (uv): `requests` (APIs do BC), `pandas`, `matplotlib`.
- **Claude via `claude -p`** (plano pago, sem chave de API).
- **Gmail por SMTP** com senha de app no `.env` (fora do Git).
- **Agendador de Tarefas do Windows** para rodar toda segunda às 10h.
- **Artefato público:** `relatorio_semana.html` publicado no claude.ai.

## Estado em 06/11, 11h50 (já testado)

- Download do BC corrigido (a API Olinda passou a recusar `+` como espaço; usamos `%20`).
- Agente roda de ponta a ponta com `--sem-email` em ~37 s.
- Histórico 2021–2025 de IPCA e Selic no JSON e em `acuracia.png`.
- Checagens param o agente com Focus desatualizado e com valor fora da faixa.

## Divisão (cada um edita só os seus arquivos)

Regras completas para os agentes em [AGENTS.md](AGENTS.md); cada frente tem a sua tarefa em [tarefas/](tarefas/). Para começar num computador novo, cole no agente:

> Leia AGENTS.md e tarefas/X_….md deste repositório e execute a tarefa da Frente X, na branch indicada, abrindo PR para main ao fim de cada passo que funcionar.

Além das frentes A–D abaixo: **V (Codex)** recalcula tudo de forma independente e revisa os PRs ([tarefas/V_validacao.md](tarefas/V_validacao.md)); **Integração (José)** faz merge na `main` e é dono do `agente_semanal.py` e do `CONTRATO.md`.

| Pessoa | Frente | Arquivos | Pronto quando |
|---|---|---|---|
| **A** | Termômetro e checagens | `termometro.py` | limiares calibrados pelo histórico (ex.: 2 DP das variações de 4 semanas); 1 checagem nova (respondentes baixos ou semana repetida) testada estragando um dado; 2 números conferidos no [Relatório Focus](https://www.bcb.gov.br/publicacoes/focus) oficial |
| **B** | Histórico de acerto | `historico.py`, `inicio_focus.py` | gráfico legível de expectativa × realizado 2021–2025; frase "o mercado erra mais para cima ou para baixo?" sustentada pelos números; 1 valor conferido à mão no SGS |
| **C** | Análise do Claude | `analise.py`, `prompt_analise.md` | reescrita automática (até 2 tentativas) quando `conferir()` acusar número fora do JSON; testado com um número inventado de propósito |
| **D** | Relatório, e-mail, agenda, entrega | `relatorio.py`, `enviar_email.py`, `.env` (local), `README.md` | e-mail com o gráfico chegando na caixa; tarefa agendada criada; artefato publicado e aberto em aba anônima; README e vídeo |

O `agente_semanal.py` só orquestra. Mudança nele: avise o grupo.

**D precisa começar já pelo Gmail:** a senha de app exige verificação em duas etapas ativa. Se não der, o plano B é outra conta do time.

## Marcos (deadline 16h00; meta 15h45)

| Hora | O que precisa estar pronto |
|---|---|
| 12h30 | e-mail de teste chegou (D); limiares e checagem nova (A); gráfico novo (B); reescrita esboçada (C) |
| 13h00 | um e-mail real completo enviado pelo agente |
| 15h00 | tarefa agendada; artefato publicado; README preenchido; números conferidos no Focus oficial |
| 15h30 | vídeo de 2 min: agente rodando → e-mail chegando → agente parando com dado ruim |
| 15h45 | formulário de entrega enviado |

## Registro de conferências e erros pegos (para o vídeo e o README)

| Hora | Quem | O que conferimos / o que estava errado | Resultado |
|---|---|---|---|
| 11h20 | — | Download do Focus quebrado (HTTP 400) | corrigida a codificação da URL |
| 11h50 | — | IPCA composto × `ipca_12m` de dezembro, 2021–2025 | bate; 2022 difere 0,01 p.p. (arredondamento) |
| 11h50 | — | Focus de 02/10 simulado e IPCA = 52,2 | agente parou nos dois casos |
| 12h25 | Thomas (A) | 32 números do resumo (há 4 semanas, há 1 semana, hoje e respondentes das 8 séries) × PDF oficial do Focus de 30/10/2026 (bcb.gov.br/content/focus/focus/R20261030.pdf) | bate 32/32; virou teste automático (`test_dados_reais_batem_com_o_focus_oficial`) |
| 12h25 | Thomas (A) | var. de 4 semanas do IPCA 2026 saía 0,20 (diferença das medianas sem arredondar); o PDF mostra 5,01 → 5,22 = 0,21 | corrigido: variações calculadas com as medianas arredondadas |
| 12h25 | Thomas (A) | limiar calibrado com 2020 (pandemia) dava 1,21 p.p. em 4 semanas para o PIB do ano | calibração de 2021 em diante: 0,49 p.p.; demais limiares mudam pouco |
| 12h25 | Thomas (A) | Selic 2027 saltou 11,75 → 12,50 em 30/10 (dado real) | dispara ALERTA (limiar semanal 0,33 p.p.), não a checagem de erro |
