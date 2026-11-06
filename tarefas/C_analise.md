# Frente C — Análise do Claude, sem número inventado

**Branch:** `frente-c` · **Seus arquivos:** `avancado/case1_focus/analise.py`, `avancado/case1_focus/prompt_analise.md`, `testes/test_analise.py` · Leia antes o `AGENTS.md`.

## Objetivo

A análise que o gestor lê é curta, útil e **só usa números que estão no JSON**. Se o Claude inventar um número, o agente pede para reescrever; se mesmo assim falhar, o agente **para** e não envia.

## Interface fixa

- `analisar_conferido(resumo, gerar=None, tentativas=2) -> tuple[str, list[str]]`: devolve `(html, suspeitos)`. Se `suspeitos` não vier vazio, o `agente_semanal.py` para e manda o alerta.
- `gerar` é injetável: nos testes, passe uma função falsa em vez de chamar o Claude.
- O HTML usa só `<h3>`, `<p>`, `<ul>`, `<li>`, `<strong>` (a Frente D o encaixa no e-mail).

## Passos

1. **Reescrita automática:** se `conferir()` acusar suspeitos, chame **o mesmo `gerar` que recebeu** de novo, até `tentativas` vezes, como `gerar(resumo, instrucao_extra)`. Em `instrucao_extra`, mande o texto anterior e a lista dos números que não existem no JSON. Devolva o primeiro texto que passar. `analisar()` deve aceitar o mesmo parâmetro opcional `instrucao_extra=""`. **Não chame `claude -p` direto na reescrita:** o agente usa o Codex como reserva quando o Claude falha (`reserva.py`, `MIGRAR_PARA_CODEX.md`).
2. **Melhorar o `prompt_analise.md`:** comece pelos alertas; explique cada alerta com o limiar que o disparou (campo da Frente A); traga uma frase do histórico de acerto (campo `acuracia_resumo` da Frente B, quando existir); diga a data do Focus; nada de recomendação de investimento.
3. **Fortalecer `conferir()`:** hoje ele só pega números decimais. Pense em percentuais inteiros ("5%"), datas e anos (2026 não é suspeito) e números por extenso. Não deixe passar o que o JSON não tem.
4. **Testes** em `testes/test_analise.py`, todos **sem chamar o Claude**:
   - um número inventado é pego;
   - a reescrita conserta na 2ª tentativa;
   - depois de 2 falhas, `suspeitos` volta preenchido.
5. **Teste real uma vez:** rode o agente com `--sem-download --sem-email` e confira, lendo o texto gerado, 3 números contra o `resumo_semana.json`.

Se `referencia/` existir, o chat do claude.ai já escreveu a reescrita: porte de lá respeitando a interface acima.

## Cuidados

- A chamada ao Claude é `claude -p` (usa o plano pago, sem chave). Ela leva de 10 a 30 s; não chame em loop nos testes.
- O que entra no JSON é responsabilidade de A e B. Precisa de um campo? Peça a eles.

## Pronto quando

- [ ] `pytest -q testes` passa (sem rede, sem Claude) e o agente roda até o fim.
- [ ] Reescrita até 2 vezes funcionando, com teste.
- [ ] Prompt novo produz análise que começa pelos alertas e cita a data do Focus.
- [ ] 3 números do texto conferidos contra o JSON, anotados em `PLANO.md`.

**Marco:** PR aberto até 12h45; pronto até 14h30.
