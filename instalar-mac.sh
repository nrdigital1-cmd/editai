#!/bin/bash
# Instalador do Editai para Mac
# Pode rodar quantas vezes quiser: o que ja estiver instalado e pulado.
set -e

PACOTE="$(cd "$(dirname "$0")" && pwd)"
EDITAI="$HOME/Documents/Editai"
VENV="$EDITAI/.python"
REPOSITORIO="https://github.com/nrdigital1-cmd/editai.git"
TOTAL=5

etapa() { printf "\n\033[36m[%s/%s] %s\033[0m\n" "$1" "$TOTAL" "$2"; }
ok()    { printf "  \033[32mok:\033[0m %s\n" "$1"; }
falha() { printf "\n  \033[31mPROBLEMA:\033[0m %s\n" "$1"; exit 1; }
tem()   { command -v "$1" >/dev/null 2>&1; }

# 1. Programas basicos
etapa 1 "Instalando os programas basicos (Git, Node, FFmpeg, Python)"
if ! tem brew; then
  echo "  instalando o Homebrew (o instalador de programas do Mac). Pode pedir a senha do Mac."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
fi
tem brew || falha "O Homebrew nao instalou. Rode o instalador de novo."
for par in "git:git" "node:node" "ffmpeg:ffmpeg" "python3:python@3.12"; do
  cmd="${par%%:*}"; pkg="${par##*:}"
  if tem "$cmd"; then ok "$cmd ja estava instalado"; else
    echo "  instalando $pkg..."; brew install "$pkg" >/dev/null
    tem "$cmd" || falha "$pkg nao instalou. Rode o instalador de novo."
    ok "$pkg instalado"
  fi
done

# 2. Editai: baixa do GitHub e monta a pasta de trabalho
etapa 2 "Baixando o Editai e criando a pasta Editai em Documentos"
mkdir -p "$EDITAI"
FONTE="$EDITAI/.fonte"
if [ ! -d "$FONTE/.git" ]; then
  if ! git clone -q "$REPOSITORIO" "$FONTE"; then
    # Sem internet para o GitHub: usa a copia do zip (atualizacoes ligam depois)
    echo "  nao consegui falar com o GitHub; usando os arquivos do zip"
    mkdir -p "$FONTE" && rsync -a "$PACOTE/" "$FONTE/"
  fi
fi
# Copia kit e skills sem apagar videos, projetos e perfil do aluno
python3 "$FONTE/kit/ferramentas/atualizar.py" --sem-baixar \
  || falha "Nao consegui montar a pasta Editai. Rode o instalador de novo."
ok "pasta pronta em $EDITAI e skills instaladas"

# 3. Ferramenta de montagem
etapa 3 "Instalando a ferramenta de montagem (Hyperframes) - leva alguns minutos"
( cd "$EDITAI" && npm install --no-audit --no-fund --loglevel=error && npx hyperframes browser ensure )
ok "ferramenta de montagem pronta"

# 4. Transcritor
etapa 4 "Instalando o transcritor de voz (Whisper)"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "faster-whisper==1.2.1" "av==15.1.0"
ok "transcritor instalado"

# 5. Modelo de voz
etapa 5 "Baixando o modelo que reconhece a voz (cerca de 2 GB, so na primeira vez)"
"$VENV/bin/python" "$EDITAI/ferramentas/baixar-modelo.py" \
  || falha "O download do modelo parou. Confira a internet e rode de novo: ele continua de onde parou."
ok "modelo de voz pronto"

# Teste final
printf "\n\033[36mTestando tudo...\033[0m\n"
"$VENV/bin/python" "$EDITAI/ferramentas/testar.py" \
  || falha "O teste encontrou um problema (veja acima). Peca ao Claude: 'Deu erro, continua a instalacao de onde parou.'"

printf "\n\033[32mEDITAI PRONTO!\033[0m\n"
echo "1. Feche e abra o app do Claude."
echo "2. Aba Code > escolha a pasta $EDITAI"
echo "3. Coloque seu video em videos-sem-edicao e escreva: edita meu video"
