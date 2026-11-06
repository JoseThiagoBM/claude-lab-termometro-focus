# Frente B — Histórico de acerto ("o Focus acertou?")

**Branch:** `frente-b` · **Seus arquivos:** `avancado/case1_focus/historico.py`, `avancado/case1_focus/inicio_focus.py`, `testes/test_historico.py` · Leia antes o `AGENTS.md`.

## Objetivo

Responder à pergunta da diretora: **nos últimos 5 anos fechados (2021–2025), o Focus acertou o IPCA e a Selic?** Com um gráfico que se entende em 5 segundos e uma conclusão sustentada pelos números.

## Interface fixa

- `historico(saida: Path) -> list[dict]`: devolve a lista que vai em `resumo["acuracia"]` e grava `saida/acuracia.png`. Cada item tem ao menos `indicador`, `ano`, `quando`, `esperado`, `realizado`, `erro_pp` (`CONTRATO.md`).
- `inicio_focus.py` também é usado pela Frente A (`carregar_focus`, `serie_semanal`, `META_INFLACAO`). **Não mude essas assinaturas.**

## Passos

1. **Escolher os horizontes.** Hoje é só "início do ano" (mediana de 15/01). Acrescente "12 meses antes" e/ou "meio do ano" e mostre como o erro diminui à medida que o ano passa.
2. **Gráfico final** em `saida/acuracia.png`: esperado × realizado de IPCA e Selic, 2021–2025. Título com a mensagem, fonte e data dos dados no rodapé. Ele vai embutido no e-mail (Frente D), então largura de até ~700 px.
3. **Resumo numérico** para a análise usar, em `resumo["acuracia_resumo"]` (registre em `CONTRATO.md`): erro médio, erro absoluto médio e quantos anos o mercado errou para cima e para baixo, por indicador.
4. **Testes** em `testes/test_historico.py`: o IPCA composto bate com `ipca_12m` de dezembro (tolerância de 0,011 p.p.; em 2022 dá 5,78 × 5,79); a Selic do fim do ano é a última de dezembro; só entram anos fechados.
5. **Confira 1 valor à mão** no SGS (ex.: IPCA 2024 = 4,83) e anote em `PLANO.md`.

## Valores que a versão atual já calcula (horizonte "início do ano")

| Ano | IPCA esp. | IPCA real. | Selic esp. | Selic real. |
|---|---|---|---|---|
| 2021 | 3,43 | 10,06 | 3,25 | 9,25 |
| 2022 | 5,09 | 5,78 | 11,75 | 13,75 |
| 2023 | 5,39 | 4,62 | 12,50 | 11,75 |
| 2024 | 3,85 | 4,83 | 9,00 | 12,25 |
| 2025 | 5,06 | 4,26 | 15,00 | 15,00 |

Se mudar o método e os números mudarem, explique o porquê no PR.

## Pronto quando

- [ ] `pytest -q testes` passa e o agente roda até o fim.
- [ ] `acuracia.png` com título-mensagem, fonte e 2021–2025 para IPCA e Selic.
- [ ] `acuracia_resumo` no JSON e em `CONTRATO.md`.
- [ ] 1 valor conferido à mão no SGS, anotado em `PLANO.md`.

**Marco:** PR aberto até 12h45; pronto até 14h30.
