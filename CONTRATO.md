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
  "acuracia": [                        // B — historico.py; 3 linhas por indicador/ano, uma por "quando":
    {"indicador": "IPCA", "ano": 2025, "quando": "início do ano", "esperado": 5.06, "realizado": 4.26, "erro_pp": -0.79}
  ],                                   //   "12 meses antes" (15/01 do ano anterior), "início do ano" (15/01), "meio do ano" (15/07)
  "acuracia_resumo": {                 // B — historico.resumo_acuracia(resumo["acuracia"])
    "IPCA": {"anos": "2021–2025", "horizonte_principal": "início do ano",
             "erro_medio": 1.35, "erro_abs_medio": 1.97, "anos_subestimou": 3, "anos_superestimou": 2,
             "anos_exato": 0, "n_anos": 5,             // = por_horizonte["início do ano"]
             "por_horizonte": {"12 meses antes": {...mesmas chaves...}, "início do ano": {...}, "meio do ano": {...}}},
    "Selic": {...}
  }
}
```

`erro_pp = realizado − esperado` (p.p.). **Positivo = o mercado subestimou** (veio mais do que o esperado) → conta em `anos_subestimou`; negativo → `anos_superestimou`. Filtre `acuracia` por `quando` se quiser uma linha por ano.

Arquivos gerados em `avancado/case1_focus/saida/`: `resumo_semana.json`, `acuracia.png` (B), `relatorio_semana.html` (D).

## Regras de dado (cuidados do case)

- `baseCalculo = 0` sempre (já filtrado em `carregar_focus`).
- `Data` = quando a expectativa foi coletada; `DataReferencia` = ano a que ela se refere.
- IPCA do ano = composição das 12 variações mensais; conferido contra `ipca_12m` de dezembro (2021–2025 batem; 2022 dá 5,78 × 5,79 por arredondamento).
- Selic do Focus = taxa no **fim** do ano.
- Números com 2 casas decimais. O `conferir()` compara com essa precisão.
- Todo texto diz a data do Focus. Rodapé: fonte BCB + "não constitui recomendação de investimento".
