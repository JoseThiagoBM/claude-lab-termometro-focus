# Plano B: se o limite do Claude acabar

O projeto depende do Claude em **três** lugares. Para cada um, a troca pelo Codex já está pronta ou tem um passo a passo.

| Onde o Claude entra | Se acabar o limite | O que fazer |
|---|---|---|
| **1. A análise dentro do agente** (`claude -p`) | o agente cai sozinho para o Codex e, se o Codex também falhar, para um texto sem IA | nada: já é automático (testado em 06/11 às 12h55) |
| **2. Os agentes que programam** (Claude Code de cada pessoa) | a pessoa troca para o Codex na mesma pasta | seção 2 abaixo |
| **3. A publicação do artefato** (claude.ai) | não dá para publicar no claude.ai | seção 3 abaixo: GitHub Pages |

---

## 1. A análise dentro do agente (já automático)

O `agente_semanal.py` tenta os motores em ordem (`reserva.py`) e só aceita a análise que passar na conferência de números:

1. **Claude** (`claude -p`, plano pago);
2. **Codex** (`codex exec`, conta do ChatGPT): mesmo prompt, em modo somente leitura;
3. **Sem IA**: texto montado só com os números do JSON. Nunca falha na conferência; o relatório avisa que saiu sem IA.

O rodapé do relatório diz qual motor escreveu ("Análise escrita por Codex"), e o `resumo_semana.json` guarda `motor_analise` e, se houver, `motor_analise_falhas`.

Para forçar um motor (por exemplo, para o vídeo, se o Claude estiver lento):

```bash
$env:MOTOR_ANALISE = "codex"; .venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py
```

Valores: `claude`, `codex`, `sem_ia` ou uma lista em ordem (`codex,sem_ia`). Sem a variável: `claude,codex,sem_ia`. A tarefa agendada usa o padrão, então já tem a reserva.

**Para o Codex funcionar como motor no seu computador:** instale o Codex CLI e rode `codex login` uma vez. O agente chama o Codex com `--ignore-user-config`, para o `config.toml` pessoal (modelo, MCPs) não atrapalhar. Testado com `codex-cli 0.153.4`, que usou o modelo `gpt-6-astra`.

---

## 2. Os agentes que programam: trocar Claude Code por Codex

O repositório já está pronto para o Codex: ele lê o `AGENTS.md` sozinho (o Claude Code lê o mesmo arquivo pelo `CLAUDE.md`). As regras, as branches, as tarefas e os testes são os mesmos.

**Passo a passo (cada pessoa, no próprio computador):**

1. **Salve o que está feito**, antes de trocar: `git add -A && git commit -m "wip: [Frente X] ..." && git push`. Assim o Codex começa do ponto exato.
2. Na pasta do repositório, rode `git switch <sua-branch> && git pull && git merge main`.
3. Abra o Codex nessa pasta (app do Codex ou `codex` no terminal).
4. Cole o **prompt de retomada**:

```text
Você vai continuar o trabalho da Frente X neste repositório, que estava sendo feito com o Claude Code.
1. Leia AGENTS.md e tarefas/X_….md. Siga as regras à risca: só os arquivos da sua frente, branch <sua-branch>, PR para main.
2. Veja o que já foi feito: git log --oneline main..HEAD, gh pr list e a tabela "Registro de conferências" do PLANO.md.
3. Rode os dois comandos de aceitação do AGENTS.md e me mostre o resultado.
4. Compare o que está feito com o "Pronto quando" da tarefa e me diga, em 5 linhas, o que falta e por onde começa.
5. Continue a partir daí, um passo por vez, com commit, push e PR a cada passo que funcionar.
```

**Erro "model is not supported when using Codex with a ChatGPT account"?** O `config.toml` do Codex aponta para um modelo que a conta não tem. Abra o Codex com `codex -m gpt-6-astra`, ou troque a linha `model = ...` do `~/.codex/config.toml`.

**O que o Codex não faz pelo Claude:** publicar artefato no claude.ai (veja a seção 3) e usar as Skills do Claude Code. O resto (código, testes, git, `gh`) funciona igual.

**Integração (José):** se o Claude Code da integração parar, o Codex assume a revisão e os merges com o mesmo roteiro do prompt "José — Frente D + integração" em `tarefas/PROMPTS.md`. Para o Codex, a regra é a mesma: merge só depois do "pode" do José.

---

## 3. O artefato público sem o claude.ai: GitHub Pages

O `relatorio_semana.html` já é autocontido (gráfico em base64), então serve de página estática.

1. Gere o relatório: `.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download --sem-email`.
2. Copie para a pasta publicada: `New-Item -ItemType Directory -Force docs; Copy-Item avancado\case1_focus\saida\relatorio_semana.html docs\index.html`.
3. Commit e push em `main` (via PR, como sempre).
4. Ligue o Pages, uma vez (o José, que é dono do repositório):

```bash
gh api -X POST repos/JoseThiagoBM/claude-lab-termometro-focus/pages -f "source[branch]=main" -f "source[path]=/docs"
```

5. Em 1 ou 2 minutos, o artefato fica em `https://josethiagobm.github.io/claude-lab-termometro-focus/`. Abra numa aba anônima antes de colocar no formulário.

---

## Antes de trocar, em qualquer caso

- **Commit e push do que estiver feito.** Nenhum agente vê o trabalho não commitado do outro.
- Avise no grupo: `Frente X: migrando para o Codex; último commit <hash>`.
- O `.env` não muda: o e-mail independe de qual IA está em uso.
