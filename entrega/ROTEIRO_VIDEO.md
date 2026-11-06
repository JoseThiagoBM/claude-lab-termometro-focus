# Roteiro do vídeo: gravação de tela do Termômetro do Focus

**Formato:** gravação de tela narrada, mostrando a ferramenta funcionando de verdade, do comando ao e-mail.
**Limite: 2:00.** A banca para de assistir em 2:00. Para caber, o vídeo usa cortes, acelera as esperas (2× a 4×) e põe legendas na tela no lugar de falas longas. Mire em **1:50** de vídeo final.

Edição de referência: Focus de **30/10/2026**, relatório gerado em **06/11/2026**. Todo número falado vem do `resumo_semana.json` ou do `PLANO.md` / `validacao/`.

## Antes de gravar (preparar as janelas)

Deixe abertas, nesta ordem, e feche o resto (notificações desligadas: Win+N → Não perturbe):

1. **Artefato** em aba anônima: `https://claude.ai/artifact/VMPDBGXPmhFpsbbG3pXbgB` (já compartilhado como público).
2. **README** do GitHub, rolado até a tabela da equipe.
3. **Terminal** (PowerShell) na pasta `time-case1`, fonte grande (Ctrl + roda do mouse), já com `.venv` pronta.
4. **Gmail** do destinatário, caixa de entrada limpa, sem endereços pessoais à vista.
5. **PDF oficial do Focus de 30/10/2026**: `https://www.bcb.gov.br/content/focus/focus/R20261030.pdf`.
6. **`validacao/saida_recalculo.txt`** aberto no fim (linha `TOTAL: 126 campos; 126 batem`).

**Gravação:** Win+Alt+R (Xbox Game Bar) grava a janela ativa; para trocar de janela durante a gravação, use OBS ou grave cena por cena e junte no **Clipchamp** (já vem no Windows 11), onde dá para cortar, acelerar e pôr legenda e zoom.

## Cenas

| Tempo | Tela (o que aparece) | Narração | Legenda / zoom na edição |
|---|---|---|---|
| **0:00–0:10** | Artefato: cabeçalho e faixa de alertas | "Toda segunda, analistas copiam o Relatório Focus do Banco Central, comparam com a semana anterior e escrevem um resumo à mão. Nós automatizamos isso." | Título: **Termômetro do Focus** · Claude Lab PUC-Rio |
| **0:10–0:20** | README: tabela da equipe | "Somos Thomas, Thiago, Theo e José. Cada um construiu uma parte do agente, com o Claude." | Nomes + frente: A termômetro e checagens · B histórico · C análise · D relatório e e-mail |
| **0:20–0:45** | Terminal: o comando e as etapas aparecendo (acelerar a espera) | "Um comando roda tudo: baixa o Focus e as séries do BC, calcula o que mudou, checa o dado, pede a análise ao Claude, confere cada número do texto e manda o e-mail." | Legenda acompanha cada linha: *baixar → calcular → checar → analisar → conferir → enviar* · "acelerado 4×" |
| **0:45–1:10** | Gmail: o e-mail chegando e sendo rolado | "Em um minuto, chega isto: os alertas da semana com o limiar de cada um, o que já aconteceu contra o que o mercado espera, a análise e a tabela no formato do Focus." | Zoom no alerta **IPCA 2027: +0,46 p.p. em 4 semanas, rara** e no cartão **Selic hoje 13,75% × 13,50% esperada** |
| **1:10–1:22** | Gmail: o gráfico "O Focus acertou?" | "E responde à pergunta da diretora: o Focus acertou? De 2021 a 2025, o mercado subestimou a inflação, e o erro cai ao longo do ano." | Zoom no gráfico · legenda **erro do IPCA: 1,97 p.p. em janeiro → 1,53 em julho** |
| **1:22–1:36** | Terminal: bloco de sabotagem → `PAROU` | "Se o dado vier errado, ele não manda o relatório. Aqui forçamos um IPCA de 52% e o agente para e avisa o time." | Zoom em **PAROU: IPCA 2026 = 52.2 fora da faixa plausível** |
| **1:36–1:48** | PDF do BC lado a lado com `saida_recalculo.txt` | "Conferimos tudo: um código independente recalculou 126 números direto dos dados do BC, e 32 deles batemos com o PDF oficial. Zero divergências." | **126/126 · 32 no PDF oficial · 0 divergências** |
| **1:48–1:58** | Artefato (página pública), rolando até o rodapé | "Serve para gestoras, economistas e analistas que precisam do Focus toda segunda, sem copiar número à mão. Roda sozinho, agendado, e o código está aberto no GitHub." | **Quem usa:** gestores · economistas · analistas · **Agendado: segunda, 10h** · link do GitHub |

**Utilidades para dizer (escolha 2, se sobrar tempo):** economiza a manhã de segunda; não manda número errado (para e avisa); mostra quanto confiar no Focus (histórico de acerto); a análise só cita números conferidos; tem reserva se a IA falhar (Codex ou texto sem IA).

## Comandos

**Cena 0:20 (comando principal):** usa os dados já baixados para manter a edição de 30/10 e envia o e-mail de verdade. Diga "dados de 30 de outubro" na fala.

```powershell
.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download
```

Para o ensaio, sem enviar e-mail, acrescente `--sem-email`.

**Cena 1:22 (sabotagem):** altera o IPCA só na memória; não mexe nos arquivos. Testado em 06/11 às 13h50: o agente para com `IPCA 2026 = 52.2 fora da faixa plausível` e sai com código 1. Com `com_email=True`, ele também manda o e-mail de alerta; para o ensaio, use `com_email=False`.

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

## Plano B

- **Grave cena por cena** e junte no Clipchamp: se uma cena falhar, refaça só ela.
- **Se o Claude demorar:** acelere a espera na edição, ou rode antes `$env:MOTOR_ANALISE = 'codex'` (ou `'sem_ia'`). O rodapé mostra o motor; não diga que foi o Claude se não foi.
- **Se o e-mail não chegar:** mostre o `saida\relatorio_semana.html` aberto no navegador e diga "esta é a versão que vai por e-mail".
- **Guarde uma gravação completa** e prints (e-mail, alertas, gráfico, PAROU) antes da versão final.

## Checklist

- [ ] Artefato aberto em aba anônima (prova que está público).
- [ ] Ensaio com `--sem-email` e com a sabotagem `com_email=False`, cronometrado: total ≤ 1:55.
- [ ] Notificações desligadas; nada de senha, `.env` ou endereço pessoal na tela.
- [ ] Fonte grande no terminal; zoom nos números da tabela de cenas.
- [ ] Vídeo final ≤ 2:00, no YouTube "não listado" ou Drive "qualquer pessoa com o link"; link testado em aba anônima.
- [ ] Link do vídeo no README e no formulário.

Fonte: Banco Central do Brasil, Relatório Focus de 30/10/2026. Projeto acadêmico. Não constitui recomendação de investimento.
