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
  "acuracia": [                        // B — historico.py
    {"indicador": "IPCA", "ano": 2025, "quando": "início do ano", "esperado": 5.06, "realizado": 4.26, "erro_pp": -0.79}
  ]
}
```

Arquivos gerados em `avancado/case1_focus/saida/`: `resumo_semana.json`, `acuracia.png` (B), `relatorio_semana.html` (D).

## Regras de dado (cuidados do case)

- `baseCalculo = 0` sempre (já filtrado em `carregar_focus`).
- `Data` = quando a expectativa foi coletada; `DataReferencia` = ano a que ela se refere.
- IPCA do ano = composição das 12 variações mensais; conferido contra `ipca_12m` de dezembro (2021–2025 batem; 2022 dá 5,78 × 5,79 por arredondamento).
- Selic do Focus = taxa no **fim** do ano.
- Números com 2 casas decimais. O `conferir()` compara com essa precisão.
- Todo texto diz a data do Focus. Rodapé: fonte BCB + "não constitui recomendação de investimento".
