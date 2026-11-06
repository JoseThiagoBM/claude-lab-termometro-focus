# Roteiro do vídeo: Termômetro do Focus

## O que é este vídeo

O vídeo é uma gravação de tela com narração. Ele mostra a ferramenta funcionando de verdade: o comando roda, o e-mail chega e o agente para quando o dado está errado.

O vídeo tem um limite de **2:00**. A banca para de assistir em 2:00. Por isso, o vídeo final deve ter **1:55 ou menos**.

O roteiro usa três técnicas para caber no limite:

- **Cortes:** cada cena é gravada separadamente e as cenas são juntadas na edição.
- **Aceleração:** as esperas do terminal ficam 2 a 4 vezes mais rápidas na edição.
- **Legendas:** os números e as definições aparecem escritos na tela. A narração não precisa ler tudo.

A narração tem 256 palavras. Numa fala calma (2,4 palavras por segundo), isso dá cerca de 1:47. Sobram 8 segundos para pausas.

## Dados usados

- **Edição do Focus:** 30/10/2026.
- **Data do relatório:** 06/11/2026.
- **Origem dos números falados:** `avancado/case1_focus/saida/resumo_semana.json`, `PLANO.md` e `validacao/saida_recalculo.txt`. Todos foram conferidos em 06/11/2026.

## Termos usados nas legendas

Use estas definições quando o termo aparecer pela primeira vez na tela.

| Termo | Definição |
|---|---|
| Relatório Focus | Relatório semanal do Banco Central (BC) com a mediana das previsões de mais de 110 instituições financeiras. |
| Mediana | Valor do meio: metade das instituições prevê um valor maior e metade prevê um valor menor. |
| IPCA | Índice de Preços ao Consumidor Amplo, o índice oficial de inflação do Brasil. |
| Selic | Taxa básica de juros, definida pelo Banco Central. |
| p.p. | Ponto percentual. Exemplo: de 4,30% para 4,76% é uma alta de 0,46 p.p. |
| Alerta | Mudança na previsão maior do que 2 desvios-padrão das mudanças desde 2021. |

## Antes de gravar

Faça estes passos nesta ordem.

1. Ligue o modo **Não perturbe** do Windows (Win+N). Assim, nenhuma notificação aparece na gravação.
2. Abra o **artefato** numa aba anônima: `https://claude.ai/artifact/VMPDBGXPmhFpsbbG3pXbgB`. Se a página pedir login, o link ainda não é público. Compartilhe o link antes de gravar.
3. Abra o **README** do GitHub na tabela da equipe. Confira se os nomes estão preenchidos.
4. Abra o **terminal** (PowerShell) na pasta `time-case1`. Aumente a fonte com Ctrl + roda do mouse.
5. Abra o **Gmail** do destinatário. Esconda endereços pessoais.
6. Abra o **PDF oficial do Focus**: `https://www.bcb.gov.br/content/focus/focus/R20261030.pdf`.
7. Abra o arquivo **`validacao/saida_recalculo.txt`** na última linha (`TOTAL: 126 campos; 126 batem`).

**Como gravar:** o atalho Win+Alt+R grava a janela ativa. Grave uma cena por vez. Depois, junte as cenas no **Clipchamp**, o editor que vem com o Windows 11. No Clipchamp, você corta, acelera, coloca legendas e aplica zoom.

## Cenas

A coluna **Narração** é o texto exato para ler. Cada frase tem uma ideia só.

| Tempo | O que aparece na tela | Narração | Legenda e zoom |
|---|---|---|---|
| **0:00–0:16** | Artefato: cabeçalho e alertas | "Toda segunda, o Banco Central publica o Relatório Focus. Ele reúne as previsões de mais de 110 instituições para inflação, juros, câmbio e PIB. Hoje, um analista copia esses números à mão. O nosso agente faz esse trabalho." | **Termômetro do Focus** · Claude Lab PUC-Rio |
| **0:16–0:23** | README: tabela da equipe | "Somos Thomas, Thiago, Theo e José. Cada um construiu uma parte do agente, com o Claude." | Thomas: alertas e checagens · Thiago: histórico · Theo: análise · José: relatório e e-mail |
| **0:23–0:45** | Terminal: o comando roda e as etapas aparecem (acelerar 4×) | "Um comando executa tudo. Primeiro, o agente baixa os dados do Banco Central. Depois, o código calcula as mudanças da semana e verifica se os dados estão corretos. Em seguida, o Claude escreve a análise. Por fim, o agente confere cada número do texto e envia o e-mail." | As etapas, uma por vez: **baixar → calcular → verificar → analisar → conferir → enviar** · "acelerado 4×" |
| **0:45–1:05** | Gmail: o e-mail chega e você rola até a tabela | "O e-mail começa pelos alertas. Um alerta aparece quando uma previsão muda mais do que o normal. Nesta semana, a previsão de inflação para 2027 subiu 0,46 ponto percentual em quatro semanas. Essa alta é maior do que 96% das altas dos últimos seis anos." | Zoom no alerta: **IPCA 2027: +0,46 p.p. em 4 semanas · rara (percentil 96)** · depois zoom no cartão **Selic hoje 13,75% · esperada para o fim do ano 13,50%** |
| **1:05–1:20** | Gmail: o gráfico "O Focus acertou?" | "O e-mail também mostra se o Focus acertou no passado. De 2021 a 2025, a inflação ficou, em média, 1,35 ponto percentual acima da previsão de janeiro. Em julho, a previsão erra menos." | Zoom no gráfico · **Erro médio do IPCA: 1,97 p.p. em janeiro → 1,53 p.p. em julho** |
| **1:20–1:34** | Terminal: o comando de teste e a mensagem `PAROU` | "O agente também se protege de dados errados. Aqui, nós mudamos a inflação para 52% de propósito. O agente detecta o valor impossível, não envia o relatório e avisa o time." | Zoom em **PAROU: IPCA 2026 = 52.2 fora da faixa plausível** |
| **1:34–1:46** | PDF do BC ao lado de `saida_recalculo.txt` | "Para provar os números, um segundo programa recalculou 126 valores direto dos dados do Banco Central. Os 126 coincidem. Nós também comparamos 32 valores com o PDF oficial." | **126 de 126 iguais · 0 divergências · 32 conferidos no PDF oficial** |
| **1:46–1:55** | Artefato: rolar até o rodapé | "Gestores e economistas recebem o resumo pronto toda segunda, às 10h. O código está aberto no GitHub." | **Para:** gestores · economistas · analistas · **Agendado:** segunda, 10h · link do GitHub |

**Se sobrar tempo**, acrescente uma destas frases na última cena:

- "A análise só cita números que o código calculou."
- "Se o Claude falhar, o agente usa o Codex ou um texto sem IA."

## Comandos

### Cena 0:23: o comando principal

Este comando usa os dados já baixados. Assim, o vídeo mostra a edição de 30/10. O comando envia o e-mail de verdade.

```powershell
.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download
```

No ensaio, acrescente `--sem-email`. Com essa opção, o agente gera o relatório mas não envia o e-mail.

### Cena 1:20: o teste com dado errado

Este comando muda o IPCA para 52,2% só na memória. Ele não altera nenhum arquivo. Depois, ele chama as checagens reais do agente.

- **Confirmado:** testado em 06/11/2026 às 13h50. O agente para com a mensagem `IPCA 2026 = 52.2 fora da faixa plausível` e termina com código de erro 1.
- **Atenção:** com `com_email=True`, o agente envia o e-mail de alerta ao time. No ensaio, use `com_email=False`.

```powershell
@'
import sys
sys.path.insert(0, 'avancado/case1_focus')
from agente_semanal import calcular, checar, parar
resumo = calcular()
item = next(x for x in resumo['indicadores'] if x['indicador'] == 'IPCA')
item['mediana'] = 52.2
problemas = checar(resumo)
if not problemas:
    raise RuntimeError('Sabotagem nao foi detectada; nao gravar como sucesso')
parar(problemas, com_email=True)
'@ | .venv\Scripts\python.exe -
```

## Se algo falhar

| Problema | O que fazer |
|---|---|
| Uma cena sai errada | Grave só essa cena de novo. As outras continuam válidas. |
| O Claude demora a responder | Acelere a espera na edição. Ou, antes do comando, rode `$env:MOTOR_ANALISE = 'codex'`. O rodapé do e-mail mostra qual motor escreveu a análise. Não diga "o Claude" se outro motor escreveu. |
| O e-mail não chega | Abra `avancado\case1_focus\saida\relatorio_semana.html` no navegador. Diga: "Esta é a versão que vai por e-mail." |
| Tudo falha na hora | Use a gravação completa e os prints feitos no ensaio. |

## Situação em 06/11/2026, 14h05

- **Confirmado:** os dois comandos funcionam. O Gmail aceitou o envio do teste e do agente completo. A validação deu 126 de 126.
- **Ainda não confirmado:** o e-mail chegou com o gráfico visível; o artefato está público; os nomes da equipe estão no README.
- **Recomendação:** confirme os três itens acima antes de gravar a versão final.

## Checklist final

- [ ] O artefato abre numa aba anônima.
- [ ] O ensaio completo dura 1:55 ou menos.
- [ ] Nenhuma senha, arquivo `.env` ou endereço pessoal aparece na tela.
- [ ] A fonte do terminal está grande e os números da tabela de cenas têm zoom.
- [ ] O vídeo está no YouTube como "não listado" ou no Drive com "qualquer pessoa com o link".
- [ ] O link do vídeo abre numa aba anônima.
- [ ] O link do vídeo está no README e no formulário.

Fonte: Banco Central do Brasil, Relatório Focus de 30/10/2026. Projeto acadêmico. Não constitui recomendação de investimento.
