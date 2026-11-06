# Frente V — Validação independente (Codex)

**Branch:** `validacao` · **Seus arquivos:** só a pasta `validacao/` · Leia antes o `AGENTS.md`.

Você **não implementa funcionalidade**. Seu trabalho é provar ou derrubar os números das outras frentes, de forma independente. É o que sustenta o critério "Rigor e verificação" (20 pontos).

## Regra de ouro

`validacao/recalcular.py` **não importa nada de `avancado/`**. Ele lê direto `data/case1_focus/*.csv` e recalcula do zero, com código seu. Se importar o código das frentes, a conferência deixa de ser independente.

## Passos

1. **`validacao/recalcular.py`:** recalcula, a partir dos CSVs, a mediana, a variação na semana e em 4 semanas de cada indicador/ano do `resumo_semana.json`, e a tabela `acuracia`. Compara com `avancado/case1_focus/saida/resumo_semana.json`; diverge mais que 0,01 → imprime a linha e sai com código 1.
2. **Gabarito externo:** em `validacao/gabarito_focus_2026-10-30.json`, os números do Focus oficial de 30/10/2026 (publicado em 03/11), com a fonte: IPCA 2026 = 5,22; Selic 2026 = 13,50; Câmbio 2026 = 5,34 (de 5,05). `recalcular.py` compara com eles também.
3. **Revisar PRs** (`gh pr list`, `gh pr diff <n>`) com este checklist, comentando no PR (`gh pr review --comment`):
   - o PR só toca os arquivos da frente (AGENTS.md)?
   - campo novo no JSON está em `CONTRATO.md`?
   - os dois comandos de aceitação passam na branch do PR?
   - algum número entrou em texto sem estar no JSON?
   - algum `.env`, senha ou token no diff?
   - os cuidados do case foram respeitados (`baseCalculo`, `Data` × `DataReferencia`, IPCA composto, Selic de fim de ano)?
4. **Questionar premissas** em `validacao/PREMISSAS.md`: limiares de alerta (A), horizonte do histórico (B), regra de conferência de números (C). Para cada uma: o que muda na conclusão se a premissa mudar?
5. **Antes da entrega (15h):** rode tudo a partir de um clone limpo de `main` (ambiente novo, comandos do README) e registre o resultado em `validacao/RELATORIO.md`.

## Você não faz

Não aprova nem faz merge de PR (só comenta). Não edita fora de `validacao/`. Não roda o envio de e-mail nem o agendamento.

## Pronto quando

- [ ] `recalcular.py` passa contra o `resumo_semana.json` da `main` e contra o gabarito.
- [ ] Todo PR das frentes tem um comentário de revisão.
- [ ] `RELATORIO.md` diz: clone limpo funciona? números batem? o que ficou sem verificar?
