# Instalador do Editai para Windows
# Pode rodar quantas vezes quiser: o que ja estiver instalado e pulado.

param([string]$Ferramenta = "claude")   # "claude" (padrao) ou "codex"
$Nome = if ($Ferramenta -eq "codex") { "Codex" } else { "Claude" }
$ErrorActionPreference = "Stop"
$Pacote  = $PSScriptRoot
# Pasta Documentos de verdade do aluno (funciona mesmo se ela tiver sido movida)
$Editai  = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Editai"
$Venv    = Join-Path $Editai ".python"
$Repositorio = "https://github.com/nrdigital1-cmd/editai.git"
$Total   = 5

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

# 2. Editai: baixa do GitHub e monta a pasta de trabalho ------------------------
Etapa 2 "Baixando o Editai e criando a pasta Editai em Documentos"
New-Item -ItemType Directory -Force $Editai | Out-Null
$Fonte = Join-Path $Editai ".fonte"
if (-not (Test-Path (Join-Path $Fonte ".git"))) {
  git clone -q $Repositorio $Fonte
  if ($LASTEXITCODE -ne 0) {
    # Sem internet para o GitHub: usa a copia do zip (atualizacoes ligam depois)
    Write-Host "  nao consegui falar com o GitHub; usando os arquivos do zip"
    robocopy $Pacote $Fonte /E /NFL /NDL /NJH /NJS /NP | Out-Null
  }
}
# Copia kit e skills sem apagar videos, projetos e perfil do aluno
python (Join-Path $Fonte "kit\ferramentas\atualizar.py") --sem-baixar --ferramenta $Ferramenta
if ($LASTEXITCODE -ne 0) { Falha "Nao consegui montar a pasta Editai. Rode o instalador de novo." }
Ok "pasta pronta em $Editai e skills instaladas"

# 3. Ferramenta de montagem ----------------------------------------------------
Etapa 3 "Instalando a ferramenta de montagem (Remotion) - leva alguns minutos"
Push-Location $Editai
try {
  npm install --no-audit --no-fund --loglevel=error
  npx remotion browser ensure
} finally { Pop-Location }
Ok "ferramenta de montagem pronta"

# 4. Transcritor ---------------------------------------------------------------
Etapa 4 "Instalando o transcritor de voz (Whisper) e o rastreador de rosto"
$PyVenv = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $PyVenv)) { python -m venv $Venv }
& $PyVenv -m pip install --quiet --upgrade pip
& $PyVenv -m pip install --quiet "faster-whisper==1.2.1" "av==15.1.0" "opencv-python-headless==4.14.0.94"
Ok "transcritor e rastreador de rosto instalados"

# 5. Modelo de voz -------------------------------------------------------------
Etapa 5 "Baixando o modelo que reconhece a voz (cerca de 2 GB, so na primeira vez)"
& $PyVenv (Join-Path $Editai "ferramentas\baixar-modelo.py")
if ($LASTEXITCODE -ne 0) { Falha "O download do modelo parou. Confira a internet e rode de novo: ele continua de onde parou." }
Ok "modelo de voz pronto"

# Teste final ------------------------------------------------------------------
Write-Host ""
Write-Host "Testando tudo..." -ForegroundColor Cyan
& $PyVenv (Join-Path $Editai "ferramentas\testar.py")
if ($LASTEXITCODE -ne 0) { Falha "O teste encontrou um problema (veja acima). Peca ao $Nome`: 'Deu erro, continua a instalacao de onde parou.'" }

Write-Host ""
Write-Host "EDITAI PRONTO!" -ForegroundColor Green
Write-Host "1. Feche e abra o app do $Nome."
if ($Ferramenta -eq "codex") { Write-Host "2. No Codex, abra a pasta $Editai" } else { Write-Host "2. Aba Code > escolha a pasta $Editai" }
Write-Host "3. Coloque seu video em videos-sem-edicao e escreva: edita meu video"
