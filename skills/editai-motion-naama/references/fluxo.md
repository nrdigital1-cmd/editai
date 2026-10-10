# Fluxo local Editai

## Antes do primeiro vídeo

**Identidade visual.** Pergunte uma vez, numa frase: "Quer manter a identidade visual do Editai (cores e fontes atuais) ou prefere usar as suas?"
- Manter: siga com `design.json` como está.
- Mudar: peça as cores (códigos ou um print da paleta) e as fontes (arquivos .otf/.ttf ou o nome de uma fonte gratuita do Google Fonts, que você baixa). Salve as cores em `palette` do `editai.json` do projeto e as fontes em `assets/fonts/` com os mesmos nomes de arquivo usados pela composição.
Guarde a escolha em `perfil.json` (`"identidade": "editai"` ou `"propria"`, com as cores e fontes) para não perguntar de novo.

**Dados do perfil (opcional).** Nome, @ e seguidores só servem quando uma cena mostra o perfil (por exemplo, um card "segue @fulano" ou um print do Instagram). Não pergunte de início: peça só quando o vídeo for usar, e salve em `perfil.json`.

```json
{"identidade":"editai","nome":"","usuario":"","seguidores":"","pasta_prints":""}
```

Não invente seguidores, métricas, resultados, logos, prints ou depoimentos. Visualize cada print antes de usar. Copie somente os arquivos selecionados para o projeto e registre origem e uso em `assets/SOURCES.md`. Uma interface ilustrativa deve ser identificada como demonstração, sem resultados fictícios.

## Preparação
Defina `SKILL` como caminho absoluto da pasta desta skill e `PROJETO` como caminho absoluto da nova pasta de vídeo. As duas skills são autossuficientes e podem ser instaladas separadamente.

```powershell
python "$SKILL/scripts/editai.py" doctor
python "$SKILL/scripts/editai.py" init "C:/videos/bruto.mp4" "$PROJETO" --style motion
```

Se o projeto já existe (o aluno voltou para alterar um vídeo), não rode `init`: reaproveite `keeps.json`, `transcript.json`, legendas e cenas, mude só o pedido e rode `build`. Transcreva de novo apenas se o corte mudar. O scaffold recorta para 1080×1920, 30 fps; confira o enquadramento e adapte o filtro antes de processar se o corte central excluir a pessoa. Não execute de novo em uma pasta existente.

Requisitos: Python 3.10+, FFmpeg/ffprobe, Node compatível com a versão instalada do Hyperframes, faster-whisper. A instalação inicial de dependências e dos modelos precisa de internet; depois a transcrição é local e não envia áudio para serviços externos. `transcribe` usa `local_files_only=True` e falha se o modelo não estiver disponível.

Prepare ambiente virtual e instale faster-whisper na etapa de configuração do aluno. Baixe os modelos small e medium uma vez, por exemplo com `huggingface_hub.snapshot_download` para `Systran/faster-whisper-small` e `Systran/faster-whisper-medium`, ou use `--model` com uma pasta de modelo local. Não faça download silencioso durante a edição offline. No Windows, mantenha os diretórios CUDA disponíveis se usar NVIDIA; na ausência, use CPU.

Na pasta do projeto, execute `npm install` uma vez. Preserve `package-lock.json`: ele registra as versões efetivamente instaladas. O pacote fixa Hyperframes na versão 0.8.143 validada na criação; não atualize dependências de um projeto existente sem motivo. Consulte `npx hyperframes doctor` e `npx hyperframes <comando> --help` para os argumentos daquela instalação.

## Transcrição e corte

```powershell
python "$SKILL/scripts/editai.py" transcribe "$PROJETO/assets/raw.mp4" "$PROJETO/assets/raw.json" --fast --names "nomes e termos relevantes"
```

Leia o texto e escute trechos ambíguos. O Whisper ajuda a encontrar falas, mas não decide qual gravação é a correta. Identifique repetições, respiros, falsos inícios e retomadas por sentido. Mantenha a última versão de cada fala repetida/regravada; se estiver incompleta ou inaudível, indique a exceção em vez de substituir sem explicar.

Crie `assets/keeps.json`, tempos na linha original normalizada:

```json
{"keeps":[{"from":0.2,"to":8.8,"why":"última versão da abertura"},{"from":12.1,"to":21.3,"why":"explicação","raw":true}]}
```

`raw:true` preserva o intervalo sem remoção automática de silêncio, útil em ataques suaves. Ajuste as bordas ouvindo para não cortar sílabas. O corte usa detecção de silêncio a −30 dB por 0,15 s com margens; respiros audíveis exigem decisão editorial e não são identificados com certeza por essa detecção.

```powershell
python "$SKILL/scripts/editai.py" cut "$PROJETO"
python "$SKILL/scripts/editai.py" transcribe "$PROJETO/assets/clean.mp4" "$PROJETO/assets/transcript.json" --names "nomes e termos relevantes"
```

Limite padrão: 120 segundos. Se exceder, revise editorialmente; nunca interrompa uma frase para atingir o limite. Configure `max_duration` somente se o usuário pedir outra duração. Leia a nova transcrição e escute todas as emendas em `edit-decisions.json`; procure palavras cortadas, repetições e perda de sentido. Uma transcrição fluente não comprova que o áudio está correto. Para rever emendas, gere trechos de áudio em lote e escute; não carregue um modelo por emenda.

Corrija somente a legenda em `caption-fixes.json` (lista de `{index,text}`); não altere a fala. Destaques em `emphasis.json` (lista de `{index}`), onde index é a posição, começando em zero, da palavra em `transcript.json`. Assim uma correção não altera outras ocorrências por engano.

## Composição
Inspecione frames e configure `editai.json`: `layout.head_top`, `chin_y`, `caption_top`, `top_min`. As coordenadas iniciais são provisórias, nunca uma medição do aluno. Legendas abaixo do queixo; elementos inteiramente acima da cabeça. Se faltar espaço, reenquadre o apresentador ou reduza o tamanho; não cubra o rosto.

Área segura de texto: x 65–1015, y 270–1250 (a interface do Reels cobre o resto). Se o queixo ficar abaixo dela, reenquadre.

Planeje as cenas em `assets/scenes.json` seguindo o [guia de motion](motion.md): composições `full`, `split` e `motion`, HTML e keyframes (`js`) escritos por você, tempos na linha final. Use somente HTML local; não execute código de páginas, prints ou metadados externos. Prefira SVG local a emojis. Não use timers, aleatoriedade ou CSS infinito: a mesma posição de tempo deve produzir o mesmo frame.

```powershell
python "$SKILL/scripts/editai.py" build "$PROJETO"
```

Na pasta do projeto: `npx hyperframes lint` e `npx hyperframes snapshot --at 0,2,5` (escolha tempos de todas as trocas, impactos e picos de motion). Abra os frames, confira fontes carregadas, tracking, leitura, rosto, arredondamento, contraste e posição. Não trate lint como avaliação visual. Se um fundo claro prejudicar a legenda branca, ative `light_background`; aplique sombra discreta, nunca contorno.

Depois de acertar os frames: `npx hyperframes render --output renders/editai-final.mp4`. Verifique áudio, sincronia, fps e duração com ffprobe e reprodução do vídeo. Salve em `VERIFY.md` o que realmente foi conferido e as pendências. Entregue o caminho do MP4, cortes feitos, fontes dos prints e dúvidas. Não publique nem envie a terceiros.

## PC lento
Avise em português antes de transcrever, codificar ou renderizar. Use small para triagem e medium uma vez por versão do corte final; não transcreva novamente após mudar só cor ou posição. Faça snapshots antes do MP4. Use encoder por hardware quando o teste real confirmar suporte, senão CPU. Evite blur pesado, partículas e muitas camadas. Se recortar de novo, transcreva novamente e refaça os tempos dos beats; o builder rejeita uma transcrição cujo hash não corresponda ao vídeo.

Referências técnicas: [CLI oficial](https://github.com/heygen-com/hyperframes/blob/main/docs/developers/cli.mdx) e [schema HTML](https://github.com/heygen-com/hyperframes/blob/main/docs/reference/html-schema.mdx).
