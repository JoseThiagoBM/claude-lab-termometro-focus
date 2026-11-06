# Prompts do time

Cada pessoa faz o **preparo** (uma vez) e cola o **prompt da sua frente** no seu agente. Quem fica com qual frente é uma sugestão: se trocarem, troquem só a letra da frente no prompt.

| Pessoa | GitHub | Frente | Agente |
|---|---|---|---|
| Thomas | `thomaschung44-ai` | **A** Termômetro e checagens | Claude Code (ou o chat do claude.ai) |
| Thiago | `thiagosigleal-stack` | **B** Histórico de acerto | Claude Code |
| Theo | `abreutheo1-sys` | **C** Análise do Claude | Claude Code |
| José | `JoseThiagoBM` | **D** Entrega + integração | Claude Code |
| José | — | **V** Validação | Codex |

## Combinados do grupo

- **Status no grupo do WhatsApp** às 12h45, 13h30, 14h30 e 15h15, numa linha: `Frente X: feito … | travado em … | preciso de …`.
- **Travou por mais de 15 min?** Avise no grupo e chame um mentor. Não espere.
- **Precisa de algo de outra frente** (um campo no JSON, uma função)? Peça no grupo e no seu PR. Não edite o arquivo do outro.
- **Só o José faz merge** na `main`. Depois de cada merge, ele avisa no grupo; aí cada um roda `git switch <sua-branch> && git merge main`.
- **Número só vale se estiver no JSON e tiver sido conferido.** Toda conferência vai para a tabela de `PLANO.md`. É o que a banca vai perguntar.

## Preparo (uma vez, no seu computador)

1. Aceite o convite do repositório em github.com/notifications.
2. No terminal (PowerShell), na pasta onde quer trabalhar:

```bash
git clone https://github.com/JoseThiagoBM/claude-lab-termometro-focus
```

```bash
cd claude-lab-termometro-focus
```

```bash
uv venv --python 3.12 .venv
```

```bash
uv pip install --python .venv -r requirements.txt
```

Sem `uv`? Instale com `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` e abra um terminal novo. Sem Claude Code logado? Rode `claude` uma vez no terminal e faça o login.

3. Abra o Claude Code **nessa pasta** e cole o prompt da sua frente.

---

## Thomas — Frente A (termômetro e checagens)

```text
Você é o agente da Frente A no repositório claude-lab-termometro-focus (Claude Lab PUC-Rio, Case 1: agente semanal do Relatório Focus). Somos 4 pessoas, cada uma com um agente em um computador diferente, mais um validador. A entrega é às 16h00 de hoje.

1. Leia AGENTS.md inteiro e tarefas/A_termometro.md. Siga as regras do AGENTS.md à risca: você só edita avancado/case1_focus/termometro.py e testes/test_termometro.py, e a linha nova do CONTRATO.md quando criar um campo.
2. Trabalhe na branch frente-a (git switch frente-a && git merge main).
3. Antes de escrever código, rode os dois comandos de aceitação do AGENTS.md e me mostre que passam. Depois me diga em 5 linhas o seu plano para os passos da tarefa.
4. Eu tenho código pronto de alertas calibrados e de 11 checagens, feito no chat do claude.ai. Se eu colar trechos aqui ou se existir a pasta referencia/, porte de lá para termometro.py respeitando a interface fixa (calcular() e checar()). Teste com os dados reais de data/case1_focus/, não com dados sintéticos.
5. Faça um passo por vez. Ao fim de cada passo que funcionar: rode os dois comandos de aceitação, faça commit e push, e abra ou atualize o PR para main com gh pr create, título "[Frente A] ...". No corpo: o que mudou, como testou e qual número conferiu.
6. Ao conferir um número contra o Relatório Focus oficial de 30/10/2026, anote em PLANO.md (tabela "Registro de conferências").
7. Se precisar mudar algo fora dos seus arquivos, pare e me diga o que pedir para o dono.

Marcos: PR aberto até 12h45; tarefa pronta até 14h30.
```

**Se o Thomas preferir ficar no chat do claude.ai:** cole o mesmo prompt lá, anexe `AGENTS.md`, `tarefas/A_termometro.md`, `avancado/case1_focus/termometro.py`, `avancado/case1_focus/inicio_focus.py` e `testes/fixtures/resumo_exemplo.json`, e peça só o `termometro.py` e o `testes/test_termometro.py` novos. Suba os dois pelo GitHub (branch `frente-a` → **Add file → Upload files**) e abra o PR pelo site. O José roda os testes com os dados reais antes do merge.

---

## Thiago — Frente B (histórico de acerto)

```text
Você é o agente da Frente B no repositório claude-lab-termometro-focus (Claude Lab PUC-Rio, Case 1: agente semanal do Relatório Focus). Somos 4 pessoas, cada uma com um agente em um computador diferente, mais um validador. A entrega é às 16h00 de hoje.

1. Leia AGENTS.md inteiro e tarefas/B_historico.md. Siga as regras do AGENTS.md à risca: você só edita avancado/case1_focus/historico.py, avancado/case1_focus/inicio_focus.py e testes/test_historico.py, e a linha nova do CONTRATO.md quando criar um campo. A Frente A usa carregar_focus, serie_semanal e META_INFLACAO de inicio_focus.py: não mude essas assinaturas.
2. Trabalhe na branch frente-b (git switch frente-b && git merge main).
3. Antes de escrever código, rode os dois comandos de aceitação do AGENTS.md e me mostre que passam. Depois me diga em 5 linhas o seu plano.
4. O objetivo é responder "nos últimos 5 anos fechados (2021–2025), o Focus acertou o IPCA e a Selic?" com um gráfico que se entende em 5 segundos (saida/acuracia.png, até ~700 px de largura, porque vai embutido no e-mail) e com o campo acuracia_resumo no JSON (erro médio, erro absoluto médio, quantos anos errou para cima e para baixo).
5. Faça um passo por vez. Ao fim de cada passo que funcionar: rode os dois comandos de aceitação, faça commit e push, e abra ou atualize o PR para main com gh pr create, título "[Frente B] ...". No corpo: o que mudou, como testou e qual número conferiu. Se mudar o método e os números da tabela da tarefa mudarem, explique o porquê no PR.
6. Abra o gráfico gerado e me mostre antes de dar o passo por concluído.
7. Confira 1 valor à mão no SGS do Banco Central (ex.: IPCA 2024 = 4,83) e anote em PLANO.md.

Marcos: PR aberto até 12h45; tarefa pronta até 14h30.
```

---

## Theo — Frente C (análise do Claude)

```text
Você é o agente da Frente C no repositório claude-lab-termometro-focus (Claude Lab PUC-Rio, Case 1: agente semanal do Relatório Focus). Somos 4 pessoas, cada uma com um agente em um computador diferente, mais um validador. A entrega é às 16h00 de hoje.

1. Leia AGENTS.md inteiro e tarefas/C_analise.md. Siga as regras do AGENTS.md à risca: você só edita avancado/case1_focus/analise.py, avancado/case1_focus/prompt_analise.md e testes/test_analise.py.
2. Trabalhe na branch frente-c (git switch frente-c && git merge main).
3. Antes de escrever código, rode os dois comandos de aceitação do AGENTS.md e me mostre que passam. Depois me diga em 5 linhas o seu plano.
4. Hoje o agente PARA se a análise citar um número que não está no JSON. A sua prioridade número 1 é a reescrita automática dentro de analisar_conferido() (até 2 tentativas, mandando ao Claude os números que não existem no JSON), porque sem ela um texto ruim impede o envio do e-mail. Mantenha a assinatura analisar_conferido(resumo, gerar=None, tentativas=2) -> (html, suspeitos).
5. Os testes não podem chamar o Claude: use o parâmetro gerar com uma função falsa. Escreva o teste "erra na 1ª, acerta na 2ª" e o "falha 2 vezes e devolve suspeitos".
6. Faça um passo por vez. Ao fim de cada passo que funcionar: rode os dois comandos de aceitação, faça commit e push, e abra ou atualize o PR para main com gh pr create, título "[Frente C] ...". No corpo: o que mudou, como testou e qual número conferiu.
7. Depois da reescrita, melhore o prompt_analise.md (começar pelos alertas, citar a data do Focus, usar o histórico de acerto quando o campo existir) e confira 3 números do texto gerado contra saida/resumo_semana.json. Anote em PLANO.md.

Marcos: reescrita em PR até 12h45; tarefa pronta até 14h30.
```

---

## José — Frente D (entrega) + integração

```text
Você é o agente da Frente D e da integração no repositório claude-lab-termometro-focus (Claude Lab PUC-Rio, Case 1). Somos 4 pessoas, cada uma com um agente, mais o Codex como validador. A entrega é às 16h00 de hoje; a meta é 15h45.

1. Leia AGENTS.md e tarefas/D_entrega.md. Como Frente D, você edita relatorio.py, enviar_email.py, agendar/, README.md e testes/test_relatorio.py, na branch frente-d. Como integração, você cuida de agente_semanal.py, CONTRATO.md e dos testes do contrato, na main.
2. Primeiro, o e-mail (maior risco): eu mesmo crio a senha de app do Gmail e preencho o .env. Você só me diz o passo a passo e roda o teste de envio depois. Nunca leia, mostre ou commite o .env.
3. Integração: a cada 30 minutos, rode gh pr list. Para cada PR aberto: confira se ele só toca os arquivos da frente, rode os dois comandos de aceitação na branch do PR e leia o comentário do Codex. Me diga se está pronto para merge. Eu decido; você faz o merge só depois do meu "pode".
4. Depois de cada merge, rode o agente com --sem-download --sem-email na main e me avise para eu mandar no grupo.
5. Frente D: e-mail com o gráfico embutido, script de agendamento em agendar/ (eu rodo), relatorio_semana.html com o gráfico em base64 para publicar como artefato, README completo e roteiro do vídeo.

Marcos: e-mail de teste até 12h30 · e-mail real até 13h · artefato e README até 15h · vídeo até 15h30 · formulário até 15h45.
```

---

## José — Codex (validação)

Clone numa pasta só do Codex (`C:\Users\joseb\Documents\Codex\Hackathon-PUC-Rio`), faça o preparo e cole:

```text
Você é o validador independente do repositório claude-lab-termometro-focus (Claude Lab PUC-Rio, Case 1: agente semanal do Relatório Focus). Quatro agentes, em computadores diferentes, implementam as frentes A, B, C e D. Você não implementa funcionalidade: você prova ou derruba os números deles.

1. Leia AGENTS.md e tarefas/V_validacao.md. Você só edita a pasta validacao/, na branch validacao. Nunca faça merge, aprovação ou push em main.
2. Escreva validacao/recalcular.py SEM importar nada de avancado/: leia data/case1_focus/*.csv e recalcule do zero as medianas, as variações (semana e 4 semanas) e a tabela de acurácia. Compare com avancado/case1_focus/saida/resumo_semana.json e com validacao/gabarito_focus_2026-10-30.json. Divergência maior que 0,01: imprima a linha e saia com código 1.
3. A cada 30 minutos, rode gh pr list. Revise cada PR novo com o checklist da tarefa e comente com gh pr review --comment: quais arquivos tocou, se os testes passam na branch do PR, se entrou algum número sem estar no JSON, se apareceu algum segredo no diff, se os cuidados do case foram respeitados.
4. Registre em validacao/PREMISSAS.md o que muda na conclusão se mudarmos os limiares de alerta, o horizonte do histórico ou a regra de conferência de números.
5. Às 15h: clone limpo de main, ambiente novo, comandos do README do zero. Registre o resultado em validacao/RELATORIO.md e abra um PR "[Validação] ...".
```
