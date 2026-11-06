# Frente D — Relatório, e-mail, agendamento e entrega

**Branch:** `frente-d` · **Seus arquivos:** `avancado/case1_focus/relatorio.py`, `avancado/case1_focus/enviar_email.py`, `agendar/`, `README.md`, `testes/test_relatorio.py` · Leia antes o `AGENTS.md`.

## Objetivo

O e-mail chega bonito, com o gráfico, toda segunda às 10h. A versão web do mesmo relatório é o **artefato público**. O README e o vídeo contam a história.

## Comece por aqui (é o maior risco do case)

**A pessoa** (não o agente) gera uma senha de app do Gmail em `myaccount.google.com/apppasswords`. Precisa de verificação em duas etapas ativa. Depois copia `avancado/case1_focus/.env.exemplo` para `.env` e preenche à mão. Teste com:

```bash
.venv/Scripts/python.exe avancado/case1_focus/enviar_email.py
```

Não deu até 12h30? Usem a conta de outra pessoa do time. **O `.env` nunca vai para o Git.**

## Interface fixa

- `montar(resumo, analise, saida) -> str`: HTML completo. `saida` é a pasta com `acuracia.png`.
- `enviar(assunto, html, imagens=None) -> list[str]`: `imagens` são os PNGs a embutir no corpo (Content-ID). Devolve os destinatários.

## Passos

1. **E-mail de teste chegando** (acima).
2. **`montar()`:** layout com a cara do time; seções na ordem alertas → análise → números da semana → histórico de acerto (gráfico); data do Focus no topo; fonte e aviso no rodapé. Use campos novos de A e B só depois que estiverem em `CONTRATO.md`, e com `.get()` para não quebrar se ainda não existirem.
3. **Imagem no e-mail:** em `enviar()`, embuta cada imagem com Content-ID (`MIMEImage` + `Content-ID`). Na versão web (artefato), use a imagem em base64 dentro do HTML.
4. **Agendamento:** em `agendar/`, um script que cria a tarefa semanal no Agendador do Windows (segunda, 10h, `python.exe` da `.venv` + caminho do `agente_semanal.py`). **Quem roda o script é a pessoa**, não o agente. Teste com "Executar agora" no Agendador.
5. **Artefato público:** publique `saida/relatorio_semana.html` (com o gráfico em base64) no claude.ai e abra o link numa aba anônima.
6. **README:** complete a equipe, o artefato, o vídeo, as limitações e o "Como verificamos" com o que as frentes anotarem em `PLANO.md`.
7. **Vídeo (2 min):** problema (20 s) → agente rodando e e-mail chegando (60 s) → dado estragado de propósito e o agente parando (20 s) → quem usaria (20 s). Guardem uma gravação de plano B.
8. **Testes** em `testes/test_relatorio.py`: o HTML tem a data do Focus, a fonte e o aviso; não quebra se faltar `acuracia` ou `termometro`.

## Pronto quando

- [ ] E-mail real chegou com o gráfico embutido.
- [ ] Tarefa agendada criada e testada com "Executar agora".
- [ ] Artefato abre em aba anônima.
- [ ] README completo, com os links do vídeo e do artefato.
- [ ] `pytest -q testes` passa.

**Marcos:** e-mail de teste até 12h30 · e-mail real completo até 13h · artefato e README até 15h · vídeo até 15h30 · formulário até 15h45.
