# Contrato entre as frentes — `saida/resumo_semana.json`

O `resumo` é **a única fonte dos números** do e-mail e do relatório. Quem calcula escreve nele; quem analisa e quem monta só leem. Campo novo: combine aqui antes de usar.

```json
{
  "data_focus": "30/10/2026",          // data de coleta mais recente do Focus (A)
  "gerado_em": "06/11/2026",
  "indicadores": [                     // A — termometro.py
    {"indicador": "IPCA", "ano": 2026, "mediana": 5.22, "var_semana": 0.03, "var_4_semanas": 0.2,
     "desvio_padrao": 0.14, "distancia_da_meta": 2.22}
  ],
  "alertas": ["IPCA 2027: variou +0.46 em 4 semanas"],   // A
  "acuracia": [                        // B — historico.py; 1 linha por indicador/ano, sempre "início do ano"
    {"indicador": "IPCA", "ano": 2025, "quando": "início do ano", "esperado": 5.06, "realizado": 4.26, "erro_pp": -0.79}
  ],
  "acuracia_horizontes": [             // B — historico.extras_historico(); mesmas chaves de "acuracia", 3 linhas
    {"indicador": "IPCA", "ano": 2025, "quando": "12 meses antes", ...}   // por indicador/ano: "12 meses antes"
  ],                                   //   (15/01 do ano anterior), "início do ano" (15/01), "meio do ano" (15/07)
  "acuracia_resumo": {                 // B — historico.extras_historico()
    "IPCA": {"anos": "2021–2025", "horizonte_principal": "início do ano",
             "erro_medio": 1.35, "erro_abs_medio": 1.97, "anos_subestimou": 3, "anos_superestimou": 2,
             "anos_exato": 0, "n_anos": 5,             // = por_horizonte["início do ano"]
             "por_horizonte": {"12 meses antes": {...mesmas chaves...}, "início do ano": {...}, "meio do ano": {...}}},
    "Selic": {...}
  }
}
```

### Campos novos da Frente B (historico.py)

- `acuracia_horizontes` (list) e `acuracia_resumo` (dict), acima. `erro_pp = realizado − esperado` (p.p.).
  **Positivo = o mercado subestimou** (veio mais do que o esperado) → conta em `anos_subestimou`; negativo → `anos_superestimou`.
  No agente: `resumo.update(extras_historico())` logo depois de `historico(SAIDA)`.

### Campos novos da Frente A (termometro.py)

- `sexta_referencia` (str): a sexta-feira do último Focus publicado; o `checar` para se `data_focus` não for ela.
- `indicadores[*]`: `mediana_semana_anterior`, `mediana_4_semanas_atras`, `limiar_4s` e `limiar_semana` (2 desvios-padrão
  do histórico, na unidade do indicador), `desvios_4s` (variação de 4 semanas em desvios-padrão), `desvio_padrao_semana_anterior`,
  `desvio_padrao_4_semanas_atras`, `respondentes`, `data_ultima_coleta`; no IPCA, `distancia_do_teto`.
  As variações saem das medianas já arredondadas, como no PDF oficial (5,01 → 5,22 = +0,21).
- `indicadores[*]` (pedido da Frente C): `sequencia_direcao` ("alta" | "queda" | "estável") e `sequencia_semanas` (int):
  direção da última variação semanal e há quantas semanas seguidas ela se repete, com medianas arredondadas
  (13 = "subiu pela 13ª semana seguida"); `percentil_4s` (0–100): % das variações de 4 semanas dos últimos 6 anos
  (mesmo indicador e horizonte, em módulo, sem a semana atual) menores que a atual; `raridade_4s`: "rara" (≥ 95),
  "incomum" (≥ 80) ou "normal"; `n_historico_4s`: quantas semanas entraram na comparação.
- `sinais_de_incerteza` (list[str]): séries cuja dispersão subiu 25% ou mais em 4 semanas. `regra_de_alerta` (str): a régua, em texto.
- `termometro` (dict): `selic_hoje`, `selic_hoje_data`, `selic_esperada_fim_do_ano`, `selic_esperada_menos_hoje`, `ipca_12m`,
  `ipca_12m_mes`, `ipca_12m_menos_meta`, `dolar_ptax`, `dolar_ptax_data`, `meta_inflacao`, `teto_da_meta`.
- `integridade` (dict): insumos das checagens (`linhas_duplicadas`, `sgs_ultima_data`, `ipca_composto_x_oficial`).
  **Uso interno do `checar`**: a análise (C) não deve receber nem citar esses números.

Arquivos gerados em `avancado/case1_focus/saida/`: `resumo_semana.json`, `acuracia.png` (B), `relatorio_semana.html` (D).

## Regras de dado (cuidados do case)

- `baseCalculo = 0` sempre (já filtrado em `carregar_focus`).
- `Data` = quando a expectativa foi coletada; `DataReferencia` = ano a que ela se refere.
- IPCA do ano = composição das 12 variações mensais; conferido contra `ipca_12m` de dezembro (2021–2025 batem; 2022 dá 5,78 × 5,79 por arredondamento).
- Selic do Focus = taxa no **fim** do ano.
- Números com 2 casas decimais. O `conferir()` compara com essa precisão.
- Todo texto diz a data do Focus. Rodapé: fonte BCB + "não constitui recomendação de investimento".
