# Validação independente — Frente V

Execução em 06/11/2026, Focus de 30/10/2026, branch `validacao`, base `0dc1b7b6c207bf3da0ed037398396c4b0cd2bbf3`. Não é uma certificação de outra branch ou de alterações posteriores.

## Comandos e resultados

1. Com `MOTOR_ANALISE=sem_ia`, `.venv\Scripts\python.exe -m pytest -q testes`: código 1, 28 passaram, 1 ignorado e 8 erros de criação de diretório temporário do sandbox. Não foram falhas de asserção do projeto.
2. Com a mesma variável, `.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download --sem-email`: código 0; gerou resumo e relatório, motor confirmado `sem_ia`, sem download e sem envio.
3. Repetição com `--basetemp=validacao/.pytest_tmp -p no:cacheprovider`: código 0, 37 testes passaram, 374 avisos de depreciação. Saída em `testes.txt`. A mudança da pasta temporária permitiu executar inclusive o teste anteriormente ignorado.
4. `.venv\Scripts\python.exe validacao/recalcular.py`: código 0. Saída completa em `saida_recalculo.txt`, cálculos auxiliares e hashes SHA-256 dos insumos em `evidencias.json`.

## O que bateu

126 campos numéricos confrontados com os CSVs; 126 dentro da tolerância de 0,01 e nenhuma divergência acima dela. São 96 campos dos oito pares indicador/ano (incluindo medianas, diferenças, respondentes, dispersões atuais e anteriores, limiares e número de desvios) e 30 campos da acurácia. Dentro desses 126, 32 campos foram também confrontados com o PDF externo; não são 32 campos adicionais.

O recálculo usa apenas biblioteca padrão: lê diretamente os dois CSVs e o JSON, sem importar qualquer módulo de `avancado/`. Filtra baseCalculo=0, separa data de coleta e ano de referência, usa semanas de calendário terminadas na sexta, exige observação nas semanas comparadas e arredonda medianas antes das variações. A dispersão entre respondentes é conferida contra o campo DesvioPadrao do CSV; não se pode reconstruí-la a partir de respostas individuais ausentes.

Acurácia usa última expectativa até 15/01, composição de exatamente 12 meses do IPCA e última meta Selic observada em dezembro (inclusive quando 31/12 não tem observação). Os erros usam precisão integral antes de arredondar. Isso explica IPCA 2025: esperado bruto 5,0551, realizado 4,2643849, erro arredondado -0,79, embora a subtração dos valores exibidos 4,26 - 5,06 produza -0,80. Não é divergência do cálculo; é efeito de apresentação.

## Gabarito externo

[PDF oficial do Banco Central](https://www.bcb.gov.br/content/focus/focus/R20261030.pdf), página 1, Mediana - Agregado, anos 2026 e 2027, colunas há quatro semanas, há uma semana, hoje e respondentes dos últimos 30 dias. Os 32 valores foram transcritos da fonte acessada pela ferramenta web; `fonte_acessada=true`. O download por curl falhou por resolução DNS (`Could not resolve host`), mas a ferramenta web abriu o PDF e disponibilizou o texto de suas duas páginas. Portanto, acesso à fonte confirmado, cópia binária local indisponível. A tentativa de screenshot não disponibilizou imagem inspecionável; a conferência usou a extração textual com cabeçalhos e notas.

## O que não foi aprovado

Nenhuma divergência numérica acima de 0,01 no escopo conferido. Há, porém, fragilidade factual na conferência textual da Frente C: três frases deliberadamente incorretas passam na regra atual (troca de indicador, inteiro inventado, sinal invertido). `PREMISSAS.md` detalha as quatro sondas, incluindo um controle correto; `verificar_conferencia_texto.py` reproduz a chamada real ao conferidor, separada do recálculo independente. Correção cabe à Frente C; nenhum arquivo dela foi editado.

Sensibilidade: 6 alertas com 1,5 desvio, 5 com 2 e 5 com 2,5. Trocar expectativa de janeiro por julho reduz erro absoluto médio de IPCA de 1,9731 para 1,5244 p.p. e de Selic de 2,4000 para 0,9000 p.p.; isso encurta o horizonte e não demonstra superioridade de um modelo.

## Limitações e decisões

- Segui a ordem e o escopo explícitos desta execução: sem merge, revisão/comentário/aprovação de PR ou criação de clone. Não atualizei main. O resultado não certifica clone limpo, instalação nova ou branch main remota.
- Só criei/editei fontes de validação dentro de `validacao/`; os artefatos em `saida/` foram produzidos pelo comando expressamente solicitado. Não consultei arquivos de credenciais. Não instalei dependências.
- Não alterei `PLANO.md` porque fica fora da frente autorizada; este relatório é o registro para o integrador transferir. Não usei números da tarefa como substituto da fonte.
- Não houve download dos CSVs, teste de e-mail, agendamento, IA ou reescrita. O histórico SGS foi recalculado sobre a cópia local, sem reconfirmar cada observação em serviço externo. O PDF valida as expectativas selecionadas, não todo o histórico dos CSVs.
- Os blocos termometro e integridade e suas políticas completas não foram auditados independentemente nesta execução. As medianas representam agregados do CSV, não uma recomputação de respostas individuais indisponíveis.
- Os hashes fixam os arquivos efetivamente conferidos. O gabarito só é aplicado quando sua data coincide com a do resumo. Datas ausentes, duplicatas base 0 e meses incompletos interrompem o auditor em vez de fabricar valores.
- Não há validação prospectiva da calibração dos alertas; a amostra inclui a própria semana observada. Sensibilidades são descritivas.

## Entrega Git

Os comandos de aceitação foram repetidos antes da entrega (pasta temporária `validacao/.pytest_tmp_final`): 37 testes passaram; agente sem IA terminou com código 0; recálculo novamente com 126 campos conformes. Commit solicitado: `[Validação] Recálculo independente e gabarito do Focus de 30/10`. A tentativa de push ocorre após este commit; eventual falha será registrada abaixo, sem nova tentativa, para entrega pelo integrador.

Fonte: Banco Central do Brasil

Não constitui recomendação de investimento
