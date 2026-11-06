# Roteiro do vídeo — Termômetro do Focus

Até 2 minutos. Focus de 30/10/2026, edição gerada em 06/11/2026. Tempos definidos no plano de entrega. Números econômicos do resumo da semana; 126/126 e 32 do relatório da Frente V.

## Cenas

| Tempo | Tela | Fala | Comando / ação |
|---|---|---|---|
| 0:00–0:20 | Título, PDF do Focus e caixa de entrada preparada | “Toda segunda, alguém compara o Focus, explica o que mudou e confere os números. Nosso agente entrega o resumo por e-mail e mostra quanto o mercado acertou no passado. Se o dado estiver errado, ele para.” | Abrir o artefato e o PDF antes de gravar. |
| 0:20–1:20 | Terminal; depois e-mail com data, alertas, cartões, análise e gráfico | “Um comando executa o fluxo. Aqui usamos a cópia do Focus de 30 de outubro. O IPCA de 2027 subiu 0,46 ponto em quatro semanas. Os cartões separam o observado do esperado. O gráfico compara previsão e resultado. O rodapé identifica o motor da análise.” | Rodar o comando principal abaixo. Mostrar a chegada real, rolar pelas seções e ampliar o gráfico. Encurtar a espera na edição com indicação de corte. |
| 1:20–1:40 | Sabotagem identificada; PAROU no terminal; e-mail de alerta | “Agora alteramos o IPCA de propósito, apenas na memória. A checagem bloqueia o relatório e envia um aviso. Uma revisão de mercado gera alerta; um dado inválido interrompe o fluxo.” | Rodar o bloco de sabotagem ensaiado. Mostrar o assunto do aviso e o motivo. |
| 1:40–2:00 | Como verificamos, PDF e equipe | “A validação refez os cálculos direto dos arquivos: 126 de 126 campos bateram, e 32 também no PDF oficial. Isso ajuda analistas e gestores a acompanhar mudanças. A conferência do texto ainda precisa melhorar. Não é recomendação de investimento.” | Mostrar README, evidência da branch validacao e PDF. Encerrar com fonte e aviso. |

## Comando principal

Configurar destinatários autorizados e testar o e-mail antes de gravar. Não abrir credenciais nem executar sua configuração na gravação. Deixar a caixa de entrada pronta.

A demonstração usa dados locais para manter a mesma edição. Dizer isso na fala. O modo agendado completo baixa dados automaticamente. O primeiro comando abaixo é preparação fora da tomada; o segundo é o comando mostrado.

```powershell
Remove-Item Env:MOTOR_ANALISE -ErrorAction SilentlyContinue
.venv\Scripts\python.exe avancado\case1_focus\agente_semanal.py --sem-download
```

A ordem padrão é Claude → Codex → sem IA. Confirmar a chegada na caixa de entrada antes de afirmar que houve entrega. Para ensaio sem envio, acrescentar `--sem-email`.

## Sabotagem controlada

O valor simulado **52,2** vem do registro em `PLANO.md`. Este bloco altera o resumo só em memória. Não grava nos CSVs nem edita o código. Usa as funções reais de checagem e parada: demonstra essa barreira, não um novo download completo.

**O bloco envia o aviso aos destinatários configurados.** Rodar somente no ensaio combinado com o time e na gravação autorizada. Não foi executado durante a redação deste roteiro.

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

O código de saída de erro é esperado: o fluxo parou. Para ensaio sem envio, trocar `com_email=True` por `com_email=False` e mostrar apenas o bloqueio. Não apresentar esse ensaio como e-mail enviado. Uma nova execução normal recarrega os dados intactos.

## Plano B

- Guardar uma gravação real pronta: execução, chegada do e-mail com gráfico e parada com aviso. Identificar como gravação anterior e manter a data do Focus visível.
- Guardar prints do e-mail, dos cartões, do gráfico, de PAROU e da tabela de verificação. Identificá-los como registros do ensaio; não simular chegada ao vivo.
- Se a IA estiver lenta, preparar `$env:MOTOR_ANALISE = 'sem_ia'` antes do comando. Mostrar o rodapé correspondente e não atribuir esse texto à IA.
- Se a rede ou o e-mail falhar, abrir o HTML com `Start-Process avancado\case1_focus\saida\relatorio_semana.html`. Mostrar o envio pela gravação anterior, se ela existir.

## Checklist antes de gravar

- [ ] Preencher equipe, vídeo e artefato no README; abrir o artefato em aba anônima.
- [ ] Confirmar Focus de 30/10/2026 no resumo e no e-mail desta edição.
- [ ] Rodar `.venv\Scripts\python.exe -m pytest -q testes` e o agente com `--sem-download --sem-email`.
- [ ] Não apresentar 126/126 como cobertura dos campos posteriores à auditoria.
- [ ] Ter relatório da Frente V e PDF abertos; conferir gráfico legível no e-mail.
- [ ] Confirmar destinatários autorizados e ensaiar envio normal e aviso de parada.
- [ ] Ensaiar a sabotagem em memória e conferir o motivo da parada.
- [ ] Ocultar notificações, endereços pessoais e credenciais; não abrir a configuração na gravação.
- [ ] Cronometrar a fala e preparar gravação de reserva e prints.
- [ ] Mostrar as limitações da conferência textual; não afirmar que o texto é infalível.

Fonte: Banco Central do Brasil

Não constitui recomendação de investimento
