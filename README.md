# Termômetro do Focus — Case 1

> Claude Lab · Economia & Finanças · PUC-Rio · 06/11/2026

**Vídeo (até 2 minutos):** [preencher]

**Artefato público:** [preencher]

## Equipe

| Integrante | Nome completo | Curso / período | Papel |
|---|---|---|---|
| Thomas | [preencher] | [preencher] | A — termômetro e checagens |
| Thiago | [preencher] | [preencher] | B — histórico de acerto |
| Theo | [preencher] | [preencher] | C — análise do Claude |
| José | [preencher] | [preencher] | D — relatório, e-mail, agendamento e integração |

## O problema

Toda semana, analistas precisam comparar o Focus com a edição anterior e explicar as mudanças a gestores. Copiar números e montar o resumo à mão consome tempo e abre espaço para erros. Falta também contexto: quanto o mercado costuma acertar?

## A solução

Um relatório por e-mail toda segunda, nesta ordem:

- **Alertas:** mudanças que merecem atenção e aumento da dispersão das expectativas.
- **O que já aconteceu × o que o mercado espera:** cartões de inflação, juros e câmbio, com as datas de cada série.
- **Análise:** texto curto, com identificação do motor que o escreveu.
- **Números da semana:** expectativas e mudanças de IPCA, Selic, Câmbio e PIB Total.
- **“O Focus acertou?”:** gráfico de expectativa × realizado e histórico dos anos completos.

Se uma checagem encontra dado inválido ou desatualizado, o agente interrompe o relatório e tenta enviar um aviso ao time. O aviso depende do e-mail estar configurado e disponível.

## Como funciona

```text
baixar → calcular → histórico → checar → analisar → conferir → montar → enviar
```

O código calcula as mudanças e o histórico antes de pedir texto à IA. As etapas trocam um único resumo, descrito em [CONTRATO.md](CONTRATO.md). A checagem de dados vem antes da análise; a conferência dos números vem antes do envio.

A reserva tenta **Claude → Codex → sem IA**. A análise pede reescrita ao mesmo motor quando encontra números suspeitos. Se o motor falha ou o texto continua reprovado, tenta o próximo. Sem IA, o texto é montado com os números do resumo. O relatório identifica o motor usado. Veja [MIGRAR_PARA_CODEX.md](MIGRAR_PARA_CODEX.md) e `reserva.py`. A conferência textual ainda tem limitações descritas abaixo.

## Dados usados

**Focus de 30/10/2026; relatório gerado em 06/11/2026.** Datas de `avancado/case1_focus/saida/resumo_semana.json`.

| Fonte BCB | Dados | Uso |
|---|---|---|
| [Focus / API Olinda](https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/) | IPCA, Selic, Câmbio e PIB Total; coleta desde 2020; `baseCalculo = 0` | Expectativas anuais e revisões semanais |
| [SGS](https://www3.bcb.gov.br/sgspub/) | IPCA mensal (433), IPCA em 12 meses (13522) | Inflação realizada e conferência da composição anual |
| SGS | Selic meta (432), PTAX venda (1), IBC-Br (24363) | Juros e câmbio observados; atualização dos dados |

`Data` é a coleta; `DataReferencia` é o ano previsto. O IPCA anual é composto mês a mês. A Selic esperada é a taxa de fim de ano. Os dados locais ficam em `data/case1_focus/focus_anuais.csv` e `sgs_realizado.csv`.

## Como verificamos

Evidências: [registro de conferências do time](PLANO.md) e `validacao/RELATORIO.md` e `validacao/PREMISSAS.md`, na branch `validacao`. A integração desses arquivos à entrega é **[CONFERIR]**. A auditoria corresponde à versão nela identificada; não certifica automaticamente os campos acrescentados depois.

| O que conferimos | Onde | Resultado |
|---|---|---|
| Medianas, variações, respondentes, dispersões, limiares e acurácia | Frente V: recálculo direto dos CSVs, sem importar o código do projeto | **126/126 campos conformes; 0 divergências acima de 0,01** |
| Medianas de hoje, há 1 e há 4 semanas e respondentes de 2026 e 2027 | [PDF oficial de 30/10/2026](https://www.bcb.gov.br/content/focus/focus/R20261030.pdf), Frentes A e V | **32/32 conferidos**; fazem parte dos 126, não são adicionais |
| IPCA composto de 2021–2025 | SGS: composição mensal × IPCA em 12 meses de dezembro; PLANO | Compatíveis; 2022 difere 0,01 p.p. por arredondamento |
| Download com erro HTTP 400 | API Olinda; PLANO | Corrigida a codificação: espaço como `%20`, em vez de `+` |
| Variação de 4 semanas do IPCA 2026: 0,20 × 0,21 | PDF, resumo e PLANO | Corrigido: arredondar medianas antes de subtrair; 5,01 → 5,22 dá 0,21 p.p. |
| Sabotagem: Focus de 02/10 e IPCA de 52,2 simulados | Etapa `checar`; PLANO | O agente parou nos dois casos; confirmar o envio real do aviso na gravação |
| Efeito da pandemia na calibração do PIB do ano | Frente A; PLANO | Incluir 2020 dava limiar de 1,21 p.p.; começar em 2021 dá 0,49 p.p. |
| Salto da Selic 2027 de 11,75 para 12,50 | Frente A; PLANO e resumo | Supera o limiar semanal de 0,33 p.p.; gera alerta de mercado, não erro de dado |
| IPCA 2024: 4,83 no SGS; composição mensal 4,8313 | Frente B; PLANO, séries 13522 e 433 | Bate com realizado de 4,83 no histórico |
| Selic de 31/12/2024: 12,25 | Frente B; PLANO, série SGS 432 | Bate com realizado de 12,25 no histórico |
| Correção factual do texto | Sondas da Frente V repetidas contra `analise.py` atualizado | Das três falhas originais, o inteiro inventado passou a ser barrado; indicador trocado e sinal invertido ainda passam |

O PDF foi acessado pela ferramenta web da validação; o download local falhou por rede. A auditoria do histórico usa os CSVs locais e não reconfirmou cada observação em uma consulta externa.

## Principais resultados desta semana

Fonte: `avancado/case1_focus/saida/resumo_semana.json`, Focus de **30/10/2026**.

| Alerta | Mudança | Limiar |
|---|---:|---:|
| IPCA 2027 | +0,46 p.p. em 4 semanas | 0,30 p.p. |
| Selic 2027 | +0,75 p.p. na semana | 0,33 p.p. |
| Câmbio 2026 | +R$ 0,29 na semana | R$ 0,08 |
| Câmbio 2027 | +R$ 0,25 na semana | R$ 0,07 |
| PIB Total 2027 | -0,11 p.p. na semana | 0,09 p.p. |

Nos cartões, a Selic observada em **06/11/2026 é 13,75%**, ante **13,50%** esperados para o fim de **2026**. O IPCA em **12 meses até 09/2026 é 4,58%**, acima da meta de **3,00%**. A PTAX venda de **05/11/2026 é R$ 5,46**. São datas e medidas diferentes; expectativa não é valor realizado.

No histórico **2021–2025**, o mercado subestimou IPCA e Selic **em média**, considerando a expectativa de janeiro. Isso não ocorreu em todos os anos. Erro positivo significa realizado acima do esperado.

| Indicador | Erro médio em janeiro | Erro absoluto médio em janeiro | Erro absoluto médio em julho |
|---|---:|---:|---:|
| IPCA | +1,35 p.p. | 1,97 p.p. | 1,53 p.p. |
| Selic | +2,10 p.p. | 2,40 p.p. | 0,90 p.p. |

Os valores vêm de `acuracia_resumo`. O erro absoluto médio cai com a expectativa de julho, quando já há mais informação sobre o ano. Isso não prova melhora do método de previsão. A validação independente calcula a média antes de arredondar cada erro; o resumo atual agrega erros já arredondados. Isso explica a pequena diferença de apresentação do IPCA em julho.

## Como reproduzir

Na raiz do repositório, em PowerShell, prepare o ambiente e rode sem IA, sem baixar novamente e sem enviar e-mail:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
$env:MOTOR_ANALISE = 'sem_ia'
.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download --sem-email
.venv\Scripts\python.exe -m pytest -q testes
Start-Process avancado\case1_focus\saida\relatorio_semana.html
```

O resultado inclui `resumo_semana.json`, `relatorio_semana.html` e `acuracia.png`, em `avancado/case1_focus/saida/`. Em outra data, as checagens podem rejeitar a cópia antiga; nesse caso, rode com download para produzir uma edição atual.

Para configurar e-mail e agendamento, **a pessoa responsável** executa os scripts abaixo no próprio computador. Ela fornece as credenciais fora da gravação e seleciona apenas destinatários que aceitaram receber. Não exponha credenciais em vídeo, logs ou Git.

```powershell
powershell -ExecutionPolicy Bypass -File avancado\case1_focus\configurar_env.ps1
Remove-Item Env:MOTOR_ANALISE -ErrorAction SilentlyContinue
.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py
powershell -ExecutionPolicy Bypass -File agendar\agendar_windows.ps1
```

O comando completo baixa dados e envia o e-mail. Depois, abra o Agendador de Tarefas, encontre **Termometro do Focus** e use **Executar** para testar. O log fica em `agendar/ultima_execucao.log`. Confirme a chegada do gráfico e a abertura do artefato em aba anônima. O [roteiro do vídeo](entrega/ROTEIRO_VIDEO.md) inclui a demonstração e o plano B.

## Limitações e próximos passos

- Para entregar no horário, o computador precisa estar ligado e com o usuário conectado às **10h de segunda**. Se estiver desligado, a tarefa está configurada para rodar quando possível.
- Não há calendário de feriados integrado. Se o feriado de segunda adiar a atualização e faltar a coleta exigida, o agente para e tenta avisar. Se a coleta já estiver disponível, ele pode prosseguir; não detecta o feriado por si só. Próximo passo: considerar o calendário de publicação.
- A Frente V encontrou **três furos**: indicador trocado, inteiro inventado e sinal invertido. A atualização da Frente C passou a conferir inteiros e implementou reescrita automática. A repetição das sondas confirmou a correção do inteiro inventado; ainda faltam associação entre número e indicador e conferência do sinal.
- A raridade compara a mudança com uma janela de **6 anos**. A calibração dos alertas usa dados desde **2021**. São critérios diferentes, não probabilidades de acerto.
- A conclusão histórica usa **5 anos completos**, de **2021 a 2025**. Amostra curta e eventos excepcionais limitam a generalização.
- Envio real, tarefa instalada e link público acessível precisam de confirmação na máquina de apresentação: **[CONFERIR]**. Esta atualização da documentação foi executada sem envio.

## Aviso

Projeto acadêmico desenvolvido em workshop. Expectativas de mercado podem mudar e não garantem resultados futuros.

**Feito com:** Claude Code, Codex, Python, pandas, requests, matplotlib e APIs públicas do Banco Central do Brasil.

Fonte: Banco Central do Brasil

Não constitui recomendação de investimento
