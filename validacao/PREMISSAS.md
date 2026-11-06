# Sensibilidade das conclusões

Focus de 30/10/2026. Resultados reproduzíveis em `recalcular.py` e `evidencias.json`.

## (a) Limiar dos alertas

Recálculo com desvio-padrão amostral das variações semanais e de quatro semanas desde 2021, separado por indicador e horizonte (ano corrente ou seguinte). Cada série anual é agrupada pela última observação da semana terminada na sexta. Não se conectam anos de referência diferentes. Excluem-se as primeiras 1 ou 4 semanas do ano de coleta; dados posteriores ao Focus não entram. As diferenças históricas usam a precisão original do CSV; a variação atual usa medianas arredondadas. Contagem é de pares indicador/ano com pelo menos um dos dois gatilhos, sem dupla contagem.

| Multiplicador | Alertas nesta semana | Mudança |
|---|---:|---|
| 1,5 | 6 | Acrescenta Selic 2026 |
| 2,0 | 5 | IPCA 2027, Selic 2027, Câmbio 2026 e 2027, PIB Total 2027 |
| 2,5 | 5 | Mantém os cinco |

Selic 2026 varia 0,25 p.p.; sigma semanal independente = 0,132759. PIB 2027 permanece por margem pequena em 2,5: variação absoluta 0,11 e limiar não arredondado 0,109359. Comparar com limiar arredondado a 0,11 alteraria esse resultado; adotei a precisão integral. Há 299 diferenças semanais e 281 de quatro semanas por série/horizonte, exceto Selic corrente (287 e 269). Não significa probabilidade de erro nem intervalo de confiança: há dependência entre janelas sobrepostas. A conclusão sobre Selic corrente depende da régua escolhida.

## (b) Horizonte da expectativa

Mesmos cinco anos completos, 2021–2025. Janeiro = última mediana coletada até 15/01 do próprio ano; julho = última até 15/07. IPCA realizado é o produto das 12 taxas mensais; Selic é a última meta observada em dezembro. Erro = realizado menos esperado, calculado antes do arredondamento. Valores em pontos percentuais.

| Indicador | Erro médio janeiro | Erro médio julho | Erro absoluto médio janeiro | Erro absoluto médio julho |
|---|---:|---:|---:|---:|
| IPCA | 1,3485 | 0,3259 | 1,9731 | 1,5244 |
| Selic | 2,1000 | 0,8000 | 2,4000 | 0,9000 |

Julho melhora o erro absoluto médio de ambas as séries, mas dispõe de seis meses adicionais de informação. Não sustenta afirmar melhora do método de previsão. Tampouco melhora todos os anos: IPCA 2022 passa de erro +0,6916 para -1,7596; em 2025, de -0,7907 para -0,9056. O erro médio com sinal esconde compensações, por isso apresento também o absoluto.

## (c) Conferência dos números do texto

A regra atual compara decimais com um conjunto global de números do JSON e seus valores absolutos; não associa indicador, ano, campo ou sinal e ignora inteiros no texto. As sondas independentes foram confirmadas chamando somente `conferir`, sem IA, no script separado `verificar_conferencia_texto.py`.

| Texto sintético | Verdade esperada | Regra atual |
|---|---|---|
| IPCA 2026 = 13.50 | Errado: valor pertence à Selic | Aceita |
| IPCA 2026 = 999% | Errado: inteiro inventado | Aceita |
| PIB Total 2027 variou +0,11 | Errado: variação semanal é -0,11 | Aceita |
| IPCA 2026 = 5,22 | Correto | Aceita |

Assim, três erros deliberados passam e um controle correto passa. Uma regra que exigisse indicador, ano, campo, sinal e valor rejeitaria os três erros e preservaria o controle. Essa classificação semântica é o gabarito manual das quatro sondas, não uma funcionalidade implementada. Não é uma estimativa de taxa de falha em textos reais. A execução sem IA não avalia qualidade narrativa nem reescrita de uma IA. A verificação atual não prova correção factual do texto, mesmo quando todos os seus números estão no JSON.

Fonte: Banco Central do Brasil

Não constitui recomendação de investimento
