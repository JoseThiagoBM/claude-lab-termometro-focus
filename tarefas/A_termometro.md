# Frente A — Termômetro e checagens

**Branch:** `frente-a` · **Seus arquivos:** `avancado/case1_focus/termometro.py`, `testes/test_termometro.py` · Leia antes o `AGENTS.md`.

## Objetivo

Toda segunda, o gestor vê os 3 ou 4 números que importam e os alertas certos. Se o dado estiver errado ou atrasado, o agente **para** em vez de mandar relatório.

## Interface fixa (o `agente_semanal.py` chama assim; não mude as assinaturas)

- `calcular() -> dict`: devolve o `resumo` (formato em `CONTRATO.md`): `data_focus`, `gerado_em`, `indicadores`, `alertas`.
- `checar(resumo: dict) -> list[str]`: lista de problemas; lista vazia = pode seguir.

## Passos

1. **Calibrar os alertas.** Troque `LIMIAR_4S` (valores chutados) por limiares tirados do histórico desde 2020: por exemplo, 2 desvios-padrão das variações de 4 semanas, por indicador e por horizonte (ano corrente e ano seguinte). Guarde no JSON o limiar usado (ex.: `indicadores[*].limiar_4s`) para a análise poder explicar o alerta.
2. **O que o gestor quer ver.** Acrescente um bloco `resumo["termometro"]` com: Selic meta atual (série `selic_meta` do SGS) × Selic esperada para o fim do ano; IPCA 12 meses atual (`ipca_12m`) × meta de 3%. Registre os campos novos em `CONTRATO.md` no seu PR.
3. **Duas checagens novas, no mínimo:** respondentes abaixo de um mínimo; semana repetida (mesma `data_focus` do último resumo enviado); uma série do SGS que parou de vir, com **janela por série** (o IPCA sai com ~1 mês de atraso e o IBC-Br com ~2).
4. **Testes** em `testes/test_termometro.py`: um teste por checagem, estragando um `resumo` de propósito (use `testes/fixtures/resumo_exemplo.json` como base).
5. **Confira 2 números** do seu `resumo` contra o [Relatório Focus oficial de 30/10/2026](https://www.bcb.gov.br/publicacoes/focus) e anote em `PLANO.md`.

Se `referencia/` existir, o chat do claude.ai já escreveu alertas calibrados e 11 checagens: porte de lá para `termometro.py`, rode com os dados reais e ajuste o que quebrar.

## Cuidados

- Filtre `baseCalculo = 0` (já feito em `carregar_focus`). `Data` é a coleta, `DataReferencia` é o ano.
- As funções de `inicio_focus.py` são da Frente B. Precisa mudar alguma? Peça no PR; não edite.
- Em 30/10 a Selic 2027 saltou de 12,00 para 12,50 num dia só. É dado real: o alerta deve disparar, não a checagem de erro.

## Pronto quando

- [ ] `pytest -q testes` passa e `agente_semanal.py --sem-download --sem-email` roda até o fim.
- [ ] Alertas usam limiares calculados, e o limiar aparece no JSON.
- [ ] Pelo menos 2 checagens novas, cada uma com um teste que faz o agente parar.
- [ ] 2 números conferidos no Focus oficial e anotados em `PLANO.md`.

**Marco:** PR aberto até 12h45; pronto até 14h30.
