<#
Cria o avancado/case1_focus/.env perguntando os valores no terminal. Dono: Frente D.
A senha é digitada sem aparecer na tela e só é gravada no .env (que o .gitignore ignora).
Quem roda é a PESSOA, no próprio computador:

    powershell -ExecutionPolicy Bypass -File avancado\case1_focus\configurar_env.ps1
#>
$Env = Join-Path $PSScriptRoot ".env"
if (Test-Path $Env) {
    $r = Read-Host "Já existe um .env. Sobrescrever? (s/n)"
    if ($r -ne "s") { Write-Host "Nada foi alterado."; exit 0 }
}

$Usuario = (Read-Host "Gmail que vai ENVIAR (ex.: voce@gmail.com)").Trim()
$Seguro = Read-Host "Senha de app de 16 letras (não aparece ao digitar)" -AsSecureString
$Destinatarios = (Read-Host "Quem RECEBE, separado por vírgula (Enter = o mesmo Gmail)").Trim()
if (-not $Destinatarios) { $Destinatarios = $Usuario }

$Ponteiro = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Seguro)
try { $Senha = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ponteiro) -replace "\s", "" }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ponteiro) }

if ($Usuario -notmatch "^[^@\s]+@[^@\s]+$") { Write-Error "Gmail inválido: '$Usuario'"; exit 1 }
if ($Senha.Length -ne 16) { Write-Error "A senha de app tem 16 letras; recebi $($Senha.Length). Nada foi gravado."; exit 1 }

$Conteudo = @"
# Gerado por configurar_env.ps1. O .env nunca vai para o GitHub.
GMAIL_USUARIO=$Usuario
GMAIL_SENHA_DE_APP=$Senha
DESTINATARIOS=$Destinatarios
"@
[IO.File]::WriteAllText($Env, $Conteudo, (New-Object Text.UTF8Encoding($false)))
$Senha = $null
Write-Host ".env gravado em $Env"
Write-Host "Envia de: $Usuario  ->  para: $Destinatarios"
