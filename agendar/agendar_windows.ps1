<#
Agenda o agente do Focus para toda segunda-feira às 10h, no Agendador de Tarefas do Windows.
Dono: Frente D. Quem roda este script é a PESSOA (não o agente), no próprio computador.

Uso, na raiz do repositório (PowerShell):
    powershell -ExecutionPolicy Bypass -File agendar\agendar_windows.ps1            # cria/atualiza a tarefa
    powershell -ExecutionPolicy Bypass -File agendar\agendar_windows.ps1 -Remover   # apaga a tarefa

Depois: abra o Agendador de Tarefas, ache "Termometro do Focus" e use "Executar" para testar.
A saída de cada execução vai para agendar\ultima_execucao.log.

Limitação: o computador precisa estar ligado, com o usuário logado e o Claude Code com login feito às 10h.
Se o computador estiver desligado, a tarefa roda assim que ele ligar (StartWhenAvailable).
#>
param([switch]$Remover, [string]$Hora = "10:00")

$Nome = "Termometro do Focus"
$Raiz = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Raiz ".venv\Scripts\python.exe"
$Agente = Join-Path $Raiz "avancado\case1_focus\agente_semanal.py"
$Log = Join-Path $PSScriptRoot "ultima_execucao.log"

if ($Remover) {
    Unregister-ScheduledTask -TaskName $Nome -Confirm:$false
    Write-Host "Tarefa '$Nome' removida."
    exit 0
}

foreach ($p in @($Python, $Agente)) {
    if (-not (Test-Path $p)) { Write-Error "Não encontrei $p. Crie a .venv antes (veja o README)."; exit 1 }
}

# cmd /c para gravar a saída no log; PYTHONIOENCODING evita erro com acentos no console
$Comando = "/c set PYTHONIOENCODING=utf-8 && `"$Python`" `"$Agente`" > `"$Log`" 2>&1"
$Acao = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $Comando -WorkingDirectory $Raiz
$Gatilho = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $Hora
$Config = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $Nome -Action $Acao -Trigger $Gatilho -Settings $Config `
    -Description "Claude Lab PUC-Rio: baixa o Focus, confere e envia o Termômetro por e-mail." -Force | Out-Null

$t = Get-ScheduledTask -TaskName $Nome
Write-Host "Tarefa '$Nome' criada: toda segunda às $Hora. Estado: $($t.State)."
Write-Host "Próxima execução: $((Get-ScheduledTaskInfo -TaskName $Nome).NextRunTime)"
Write-Host "Log: $Log"
