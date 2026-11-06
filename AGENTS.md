# Regras para os agentes (Claude Code, Codex e qualquer outro)

Este repositório é editado ao mesmo tempo por **4 agentes em 4 computadores** e por **1 agente validador (Codex)**. Estas regras existem para ninguém sobrescrever o trabalho do outro. Leia este arquivo inteiro e depois **só a sua tarefa** em `tarefas/`.

## O projeto em uma frase

Um agente que roda toda segunda, baixa o Relatório Focus do Banco Central, calcula o que mudou, para e avisa se o dado vier errado, pede ao Claude uma análise conferida e manda por e-mail, junto com o histórico "o Focus acertou IPCA e Selic nos últimos 5 anos?". Detalhes do case: `avancado/case1_focus/README.md`. Prazo de entrega: **16h00 de 06/11/2026**.

## Quem é dono de quê

Você **só edita os arquivos da sua frente**. Precisa mudar arquivo de outra frente? Escreva no PR o que precisa e peça ao dono.

| Frente | Tarefa | Branch | Arquivos que só ela edita |
|---|---|---|---|
| A — termômetro e checagens | `tarefas/A_termometro.md` | `frente-a` | `avancado/case1_focus/termometro.py`, `testes/test_termometro.py` |
| B — histórico de acerto | `tarefas/B_historico.md` | `frente-b` | `avancado/case1_focus/historico.py`, `avancado/case1_focus/inicio_focus.py`, `testes/test_historico.py` |
| C — análise do Claude | `tarefas/C_analise.md` | `frente-c` | `avancado/case1_focus/analise.py`, `avancado/case1_focus/prompt_analise.md`, `testes/test_analise.py` |
| D — relatório, e-mail, agenda, entrega | `tarefas/D_entrega.md` | `frente-d` | `avancado/case1_focus/relatorio.py`, `avancado/case1_focus/enviar_email.py`, `agendar/`, `README.md`, `testes/test_relatorio.py` |
| V — validação independente (Codex) | `tarefas/V_validacao.md` | `validacao` | `validacao/` |
| Integração (José) | — | `main` | `avancado/case1_focus/agente_semanal.py`, `CONTRATO.md`, `AGENTS.md`, `CLAUDE.md`, `requirements.txt`, `testes/conftest.py`, `testes/test_contrato.py`, `testes/fixtures/`, `scripts/`, `tarefas/` |

`referencia/` (se existir) é **só leitura**: código de referência gerado no chat do claude.ai. Porte de lá a parte da sua frente; não edite a pasta.

## Como trabalhar

1. Comece de `main` atualizada: `git switch main && git pull`, depois `git switch -c <sua-branch>` (ou `git switch <sua-branch> && git merge main`).
2. **Commits pequenos.** Antes de cada push, rode os dois comandos de aceitação abaixo.
3. Abra **PR para `main`** com `gh pr create`. Título: `[Frente X] o que mudou`. No corpo: o que mudou, como testou e qual número conferiu.
4. **Só o José faz merge em `main`.** Nunca faça push direto em `main`, `--force`, rebase de branch alheia ou merge de PR.
5. Antes de abrir PR, traga a `main` mais recente para a sua branch (`git merge main`) e rode os testes de novo.

## Comandos de aceitação (todo PR passa nos dois)

```bash
.venv/Scripts/python.exe -m pytest -q testes
.venv/Scripts/python.exe avancado/case1_focus/agente_semanal.py --sem-download --sem-email
```

No Mac/Linux, troque `.venv/Scripts/python.exe` por `.venv/bin/python`. Ambiente:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
```

## O contrato entre as frentes

Todas as frentes se falam por **um único JSON**, `avancado/case1_focus/saida/resumo_semana.json`, descrito em `CONTRATO.md`. Um exemplo real está em `testes/fixtures/resumo_exemplo.json`: use-o para trabalhar **sem esperar as outras frentes**.

- Você pode **acrescentar** campos dentro da parte que é sua (ex.: A acrescenta chaves em `indicadores[*]` ou em `termometro`). Registre o campo novo em `CONTRATO.md` **no seu PR**; é a única exceção à regra de dono.
- Você **não pode renomear nem remover** campo existente. `testes/test_contrato.py` quebra se isso acontecer.

## Regras de dado e de número (valem para todo mundo)

- Número só entra em texto, e-mail ou slide depois de **calculado pelo código** e estar no JSON. Nunca escreva número de memória ou do chat.
- `baseCalculo = 0`; `Data` (coleta) ≠ `DataReferencia` (ano); IPCA anual = composição dos meses; Selic do Focus = fim do ano.
- Todo texto diz a data do Focus e termina com "Fonte: Banco Central do Brasil" e "Não constitui recomendação de investimento".
- Ao conferir um número na fonte, anote em `PLANO.md` (tabela "Registro de conferências"), na mesma linha do PR. Isso vira o "Como verificamos" do README.

## Segurança

- **`.env` nunca entra no Git** (já está no `.gitignore`). Nada de senha, chave ou token em código, log, PR ou commit.
- O e-mail só vai para quem pediu para receber (o time e a banca).
- Os agentes não digitam senhas: a pessoa preenche o `.env` com as próprias mãos.
- Não instale pacote fora do `requirements.txt`. Precisa de um novo? Peça ao José no PR.
