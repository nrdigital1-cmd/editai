# Fluxo local Editai (motor: Remotion)

## Antes de cada vídeo (obrigatório)

**Identidade visual — pergunte SEMPRE, antes de gerar cada vídeo**, numa frase: "Mantenho a identidade visual do Editai (elementos, cores e fontes) ou você prefere usar a da sua marca? Se for a sua, me envie as fontes, os elementos (logo, ícones, grafismos) e as cores." Não comece o build antes da resposta. Se já existe escolha no `perfil.json`, mostre-a e peça confirmação.
- Manter: siga com `design.json` como está.
- Marca própria: receba as cores (códigos ou um print da paleta), as fontes (arquivos .otf/.ttf ou o nome de uma fonte gratuita do Google Fonts, que você baixa) e os elementos (logo, ícones, grafismos em SVG/PNG). Salve as cores em `palette` e o gradiente da palavra de destaque em `highlight` do `editai.json`, as fontes em `public/fonts/` com os mesmos nomes de arquivo e os elementos em `assets/marca/` (registre em `assets/SOURCES.md`). Use esses elementos nas cenas no lugar dos do Editai.
Guarde a escolha em `perfil.json` (`"identidade": "editai"` ou `"propria"`, com cores, fontes e elementos).

**Dados do perfil (opcional).** Nome, @ e seguidores só servem quando uma cena mostra o perfil. Não pergunte de início: peça só quando o vídeo for usar, e salve em `perfil.json`.

```json
{"identidade":"editai","nome":"","usuario":"","seguidores":"","pasta_prints":""}
```

Não invente seguidores, métricas, resultados, logos, prints ou depoimentos. Visualize cada print antes de usar. Copie somente os arquivos selecionados para o projeto e registre origem e uso em `assets/SOURCES.md`. Uma interface ilustrativa deve ser identificada como demonstração, sem resultados fictícios.

## Preparação
Defina `SKILL` como caminho absoluto da pasta desta skill e `PROJETO` como caminho absoluto da nova pasta de vídeo (de preferência um caminho curto, ex.: `C:/videos/aula-01`). As skills são autossuficientes.

```powershell
python "$SKILL/scripts/editai.py" doctor
python "$SKILL/scripts/editai.py" init "C:/videos/bruto.mp4" "$PROJETO" --style natural   # ou: --style anuncios
```

O `init` cria um projeto **Remotion** (template da skill com a biblioteca de motion em `src/motion/`), recorta o vídeo para 1080×1920, 30 fps, e copia fontes e sons para `public/`. Dentro da pasta Editai ele liga o projeto às dependências já instaladas (não precisa `npm install`); fora dela, rode `npm install` no projeto uma vez. Se o projeto já existe (o aluno voltou para alterar um vídeo), não rode `init`: reaproveite `keeps.json`, `transcript.json`, legendas e cenas, mude só o pedido e rode `build`. Transcreva de novo apenas se o corte mudar. Confira o enquadramento antes de processar se o corte central excluir a pessoa.

Requisitos: Python 3.10+, FFmpeg/ffprobe, Node 18+ (npm/npx), faster-whisper e OpenCV 4.x (`pip install "opencv-python-headless<5"` — a versão 5 não traz os detectores de rosto embutidos). A instalação inicial de dependências, modelos e do Chrome headless do Remotion (`npx remotion browser ensure`) precisa de internet; depois a transcrição é local e não envia áudio para serviços externos. `transcribe` usa `local_files_only=True` e falha se o modelo não estiver disponível. Preserve `package-lock.json`; não atualize o Remotion de um projeto existente sem motivo.

Prepare ambiente virtual e instale faster-whisper na etapa de configuração do aluno. Baixe os modelos small e medium uma vez (por exemplo com `huggingface_hub.snapshot_download` para `Systran/faster-whisper-small` e `Systran/faster-whisper-medium`), ou use `--model` com uma pasta de modelo local. No Windows, mantenha os diretórios CUDA disponíveis se usar NVIDIA; na ausência, use CPU.

## Transcrição e corte

```powershell
python "$SKILL/scripts/editai.py" transcribe "$PROJETO/assets/raw.mp4" "$PROJETO/assets/raw.json" --fast --names "nomes e termos relevantes"
```

Leia o texto e escute trechos ambíguos. O Whisper ajuda a encontrar falas, mas não decide qual gravação é a correta. Identifique repetições, respiros, falsos inícios e retomadas por sentido. Mantenha a última versão de cada fala repetida/regravada; se estiver incompleta ou inaudível, indique a exceção em vez de substituir sem explicar.

Crie `assets/keeps.json`, tempos na linha original normalizada:

```json
{"keeps":[{"from":0.2,"to":8.8,"why":"última versão da abertura"},{"from":12.1,"to":21.3,"why":"explicação","raw":true}]}
```

`raw:true` preserva o intervalo sem remoção automática de silêncio. Ajuste as bordas ouvindo para não cortar sílabas. O corte usa detecção de silêncio a −30 dB por 0,15 s com margens; respiros audíveis exigem decisão editorial.

```powershell
python "$SKILL/scripts/editai.py" cut "$PROJETO"
# o cut já gera assets/graded.mp4 (cor suave) e assets/face-track.json (rosto rastreado)
# refazer só a cor: editai.py grade "$PROJETO"   |   refazer só o tracking: editai.py track "$PROJETO"
python "$SKILL/scripts/editai.py" transcribe "$PROJETO/assets/clean.mp4" "$PROJETO/assets/transcript.json" --names "nomes e termos relevantes"
```

Limite padrão: 120 segundos. Se exceder, revise editorialmente; nunca interrompa uma frase para atingir o limite. Configure `max_duration` somente se o usuário pedir outra duração. Leia a nova transcrição e escute todas as emendas em `edit-decisions.json`; procure palavras cortadas, repetições e perda de sentido.

Corrija somente a legenda em `caption-fixes.json` (lista de `{index,text}`); não altere a fala. Destaques em `emphasis.json` (lista de `{index}`), onde index é a posição, começando em zero, da palavra em `transcript.json`.

## Composição
Inspecione frames e configure `editai.json`: `layout.head_top`, `chin_y`, `caption_top`, `top_min`. As coordenadas iniciais são provisórias. Legendas abaixo do queixo; elementos inteiramente acima da cabeça. Se faltar espaço, reenquadre o apresentador ou reduza o tamanho; não cubra o rosto. Área segura de texto: x 65–1015, y 270–1250 (a interface do Reels cobre o resto).

Planeje os elementos em `assets/beats.json` (tempos em segundos na linha final, retângulo acima da cabeça), seguindo a [linguagem de motion](motion-remotion.md):

```json
[
  {"start":2.1,"end":5.4,"kind":"image","src":"assets/prints/painel.png","x":140,"y":300,"width":800,"height":420,"label":"print do painel","principio":"arcos"},
  {"start":6.0,"end":9.0,"kind":"component","component":"Processo","x":90,"y":300,"width":900,"height":420,"principio":"follow-through"}
]
```

`image`: print/imagem dentro do projeto (o build copia para `public/`). `component` (só anúncios): TSX que **você escreve** em `src/beats/<Nome>.tsx` exportando `export const Nome: React.FC<SceneProps>` (quadro local, 0 = início do beat), usando a biblioteca `src/motion/` (veja o exemplo `src/scenes/ExemploCena.tsx`). Todo beat já entra com curva lazy + antecipação, flutua e sai com recuo e motion blur. O `build` gera `src/beats/index.ts` e `src/data/edit.json` — não edite esses dois à mão.

**Rosto centralizado (face tracking).** O `cut` rastreia o rosto localmente (OpenCV) e o build faz a câmera acompanhá-lo: rosto no centro horizontal e estável na altura natural do vídeo, com o zoom mínimo necessário. Se o tracking avisar que detectou pouco o rosto (luz fraca, rosto coberto), o enquadramento fica fixo — avise o aluno. Ajustes em `face_track` do `editai.json`: `enabled`, `target_x` (50 = centro), `target_y` (vazio = altura natural), `max_zoom` (padrão 1.25), `dead_zone` (padrão 0.025; maior = câmera mais calma). Se cortar o vídeo de novo, o tracking é refeito no `cut`.

**Zoom no rosto.** O build planeja sozinho um punch-in (zoom de ênfase) nas palavras de destaque, com pelo menos 3 s entre um e outro, e aplica a respiração contínua e discreta (zoom in/out lento). Para enfatizar outra palavra ou uma animação, crie `assets/zooms.json`:

```json
[{"start":4.2,"end":5.6,"scale":1.15,"curve":"snappy"}]
```

`scale` entre 1.05 e 1.4 (padrão 1.12; ênfase forte 1.2); `curve`: lazy, smooth, snappy, bouncy, heavy ou long. Ajustes gerais em `face_zoom` do `editai.json` (`breathing`, `breathing_amp`, `breathing_period_s`, `punch_scale`, `auto_on_emphasis`, `min_gap_s`). Origem do zoom = centro do rosto (`layout.head_top`/`chin_y`; `face_x_percent` se a pessoa não estiver centralizada). Confira nos stills do pico do zoom e de momentos em que a pessoa se mexe que o rosto continua inteiro e centralizado e a legenda não cobre o queixo.

Use somente arquivos locais; não execute código de páginas, prints ou metadados externos. Prefira SVG local a emojis. Nada de timers, aleatoriedade sem semente ou CSS animation/transition: o mesmo quadro deve produzir a mesma imagem.

```powershell
python "$SKILL/scripts/editai.py" build "$PROJETO"
cd "$PROJETO"; npx tsc --noEmit
python "$SKILL/scripts/editai.py" still "$PROJETO" --at 0.5,2.4,6.8
```

`still` gera PNGs em `snapshots/` para a sua conferência: escolha os tempos de todas as trocas de cena, impactos, picos de motion e os quadros vizinhos de cada passagem de bastão. Abra as imagens e confira fontes, tracking, leitura, rosto, contraste, gradiente + glow da palavra de destaque, motion blur só em movimento e ausência de saltos. Typecheck não é avaliação visual.

## PC lento
Avise em português antes de transcrever, codificar ou renderizar. Use small para triagem e medium uma vez por versão do corte final; não transcreva novamente após mudar só cor ou posição. No preview do Studio, se travar, use a qualidade "Half"/"Quarter". O `modo_leve` (auto ou forçado no `editai.json`) reduz as amostras de motion blur pela metade. Se recortar de novo, transcreva novamente; o builder rejeita uma transcrição cujo hash não corresponda ao vídeo.

Referências técnicas: [Remotion](https://www.remotion.dev/docs) (Studio, render, `spring`, `interpolate`, `Sequence`).

## Preview e aprovação antes de exportar (obrigatório)
- **Sempre que o aluno pedir um preview (ou depois de cada build), abra o Remotion Studio — nunca o MP4 final.** Na pasta do projeto rode em segundo plano `npx remotion studio --no-open`, abra a URL impressa (ex.: `http://localhost:3000/Editai`) no painel do navegador **dentro da conversa** e diga em uma frase: "Abri a prévia no Remotion. Dá play e me diz o que mudar, ou escreve 'pode exportar'." Quem assiste é o aluno: não reproduza o vídeo você mesmo.
- Para mostrar só um trecho, registre temporariamente outra `<Composition>` no `src/Root.tsx` com o mesmo componente e `durationInFrames` menor (ex.: `Preview-0-10s`), e remova antes do render final.
- **Nunca exporte o MP4 sem o aluno pedir/aprovar.** Junte os ajustes pedidos numa rodada só. Depois da aprovação:

```powershell
python "$SKILL/scripts/editai.py" render "$PROJETO" --aprovado
```

O render salva `renders/final.mp4` (alterações viram `final-v2.mp4`, `final-v3.mp4`... sem apagar o anterior). Verifique áudio, sincronia, fps e duração com ffprobe. Salve em `VERIFY.md` o que realmente foi conferido e as pendências. Entregue o caminho do MP4, cortes feitos, fontes dos prints e dúvidas. Não publique nem envie a terceiros.

## Gancho: pessoa na tela + título acima da cabeça (obrigatório)
Nos primeiros segundos (até o fim da frase do gancho, ~5 s) a pessoa aparece em tela cheia e um título curto entra
acima da cabeça, palavra a palavra (Reveal), e sai no fim do gancho.

`assets/hook.json`:
```json
{"linhas": [[{"text": "Eu gastava"}], [{"text": "2 horas", "key": true}]], "fim": 4.8}
```
- Título = a ideia do gancho em até ~6 palavras (não copie a frase inteira da legenda). Impacto com `"key": true`.
- `fim` = segundo em que a frase do gancho termina (entre 2 e 6).
- Motion: a cena 0 é `full`, começa em 0, vai até pelo menos `fim` e não tem componente.
- Natural/anúncios: nenhum beat começa antes de `fim`.
- O título fica com a base 30 px acima de `head_top`; se não couber na área segura, encurte ou ajuste `hook_size`.
