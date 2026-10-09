# Instalador do Editai para Windows
# Pode rodar quantas vezes quiser: o que ja estiver instalado e pulado.

$ErrorActionPreference = "Stop"
$Pacote  = $PSScriptRoot
$Editai  = Join-Path $env:USERPROFILE "Editai"
$Venv    = Join-Path $Editai ".python"
$Skills  = Join-Path $env:USERPROFILE ".claude\skills"
$Total   = 6

function Etapa($n, $texto) { Write-Host ""; Write-Host "[$n/$Total] $texto" -ForegroundColor Cyan }
function Ok($texto)    { Write-Host "  ok: $texto" -ForegroundColor Green }
function Falha($texto) { Write-Host ""; Write-Host "  PROBLEMA: $texto" -ForegroundColor Red; exit 1 }

function Atualizar-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
              [Environment]::GetEnvironmentVariable("Path", "User")
}

function Tem($comando) { [bool](Get-Command $comando -ErrorAction SilentlyContinue) }

# 1. Programas basicos ---------------------------------------------------------
Etapa 1 "Instalando os programas basicos (Git, Node, FFmpeg, Python)"
if (-not (Tem "winget")) {
  Falha "O Windows nao tem o 'Instalador de Aplicativo'. Abra a Microsoft Store, procure 'Instalador de Aplicativo', clique em Atualizar e rode de novo."
}
$programas = @(
  @{ nome = "Git";    comando = "git";    id = "Git.Git" },
  @{ nome = "Node";   comando = "node";   id = "OpenJS.NodeJS.LTS" },
  @{ nome = "FFmpeg"; comando = "ffmpeg"; id = "Gyan.FFmpeg" },
  @{ nome = "Python"; comando = "python"; id = "Python.Python.3.12" }
)
foreach ($p in $programas) {
  if (Tem $p.comando) { Ok "$($p.nome) ja estava instalado"; continue }
  Write-Host "  instalando $($p.nome)... (se o Windows perguntar, clique em Sim)"
  winget install --id $p.id -e --silent --accept-package-agreements --accept-source-agreements | Out-Null
  Atualizar-Path
  if (-not (Tem $p.comando)) { Falha "$($p.nome) nao instalou. Feche esta janela, abra de novo e rode o instalador outra vez." }
  Ok "$($p.nome) instalado"
}

# 2. Pasta de trabalho ---------------------------------------------------------
Etapa 2 "Criando a pasta Editai na sua pasta de usuario"
New-Item -ItemType Directory -Force $Editai | Out-Null
# Copia o kit sem apagar videos e projetos que o aluno ja tenha
robocopy (Join-Path $Pacote "kit") $Editai /E /XC /XN /XO /NFL /NDL /NJH /NJS /NP | Out-Null
Ok "pasta pronta em $Editai"

# 3. Ferramenta de montagem ----------------------------------------------------
Etapa 3 "Instalando a ferramenta de montagem (Hyperframes) - leva alguns minutos"
Push-Location $Editai
try {
  npm install --no-audit --no-fund --loglevel=error
  npx hyperframes browser ensure
} finally { Pop-Location }
Ok "ferramenta de montagem pronta"

# 4. Transcritor ---------------------------------------------------------------
Etapa 4 "Instalando o transcritor de voz (Whisper)"
$PyVenv = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $PyVenv)) { python -m venv $Venv }
& $PyVenv -m pip install --quiet --upgrade pip
& $PyVenv -m pip install --quiet faster-whisper
Ok "transcritor instalado"

# 5. Modelo de voz -------------------------------------------------------------
Etapa 5 "Baixando o modelo que reconhece a voz (cerca de 2 GB, so na primeira vez)"
& $PyVenv (Join-Path $Editai "ferramentas\baixar-modelo.py")
if ($LASTEXITCODE -ne 0) { Falha "O download do modelo parou. Confira a internet e rode de novo: ele continua de onde parou." }
Ok "modelo de voz pronto"

# 6. Skills --------------------------------------------------------------------
Etapa 6 "Ensinando o Claude a editar (instalando as skills do Editai)"
New-Item -ItemType Directory -Force $Skills | Out-Null
Copy-Item -Recurse -Force (Join-Path $Pacote "skills\*") $Skills
Ok "skills instaladas"

# Teste final ------------------------------------------------------------------
Write-Host ""
Write-Host "Testando tudo..." -ForegroundColor Cyan
& $PyVenv (Join-Path $Editai "ferramentas\testar.py")
if ($LASTEXITCODE -ne 0) { Falha "O teste encontrou um problema (veja acima). Peca ao Claude: 'Deu erro, continua a instalacao de onde parou.'" }

Write-Host ""
Write-Host "EDITAI PRONTO!" -ForegroundColor Green
Write-Host "1. Feche e abra o app do Claude."
Write-Host "2. Aba Code > escolha a pasta $Editai"
Write-Host "3. Coloque seu video em meus-videos e escreva: edita meu video"
