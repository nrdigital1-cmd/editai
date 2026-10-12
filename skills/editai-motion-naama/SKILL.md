---
name: editai-motion-naama
description: Editar vídeo vertical no estilo motion do Editai de Naamã, renderizado em Remotion — cortes secos, uma cena nova a cada 3 a 6 segundos, três composições (tela dividida com painel de vidro em cima, apresentador em tela cheia com legenda de 2 a 3 palavras no peito, e tipografia cinética em tela cheia sem o apresentador), fundo em gradiente com grade fina, painéis de vidro na paleta laranja, marrom e preto, palavra de destaque em gradiente laranja com glow leve e motion fluido com antecipação, overshoot de mola, arcos e motion blur. Use quando o usuário pedir estilo motion, vídeo com animações que explicam, tipografia cinética, ou /editai-motion-naama.
---

# Editai — Motion · Naamã

Vídeo vertical 1080×1920 em **Remotion** em que **cada animação mostra o que está sendo dito**. Antes de executar, leia
[fluxo local](references/fluxo.md) (perfil, corte, transcrição, build, preview, exportação),
[linguagem de motion](references/motion-remotion.md) (como mover: curvas, antecipação, mola, arcos, smears, continuidade),
[guia de cenas](references/motion.md) (o que colocar em cada cena) e [princípios](references/principios.md).
Use `init --style motion`.

## As três composições (troca sempre com corte seco)

| Composição | Quando | Como |
|---|---|---|
| `split` — tela dividida | A fala explica algo que dá para mostrar: um processo, um antes e depois, um número | Painel de vidro na faixa de cima (y 150–840); apresentador num card com cantoneiras embaixo |
| `full` — tela cheia | Fala pessoal, opinião, confissão, ponte entre ideias | Apresentador ocupando a tela; legenda no peito; badges de vidro ao lado da cabeça |
| `motion` — sem apresentador | A ideia-chave do vídeo, o gancho, uma frase que precisa de impacto | Só fundo + **tipografia cinética** (`WordScene`): cada bloco dito ocupa a tela e se transforma no próximo. A voz continua |

## Regras
- **Ritmo:** uma cena nova a cada 3–6 s. Alterne composições; nunca duas `motion` seguidas; `motion` dura 1,5–4 s.
- **SEMPRE ilustrar a fala:** toda cena insere elementos, ícones ou objetos que mostram o que está sendo dito, no instante em que é dito. Use os ícones de traço que se desenham (`<Icon>`). Elemento genérico que não ilustra a fala não entra.
- **Motion fluido e contínuo (padrão aprovado):** cada elemento com a sua curva de velocidade (`CURVE.lazy/smooth/snappy/bouncy/heavy/long`); **antecipação** antes de partir; **slow in**; **overshoot com mola na entrada e na saída**; trajetórias em **arco**; **squash & stretch** e **exagero** nos impactos; **smears** + **motion blur** nos movimentos rápidos; **follow-through/overlapping** (partes atrasam 2–3 quadros); **ação secundária** (halo que arrasta, traços no impacto). Keyframes espaçados — se parecer acelerado, espaçe. Nada fica parado (flutuação ociosa) e nada some seco: um elemento passa o bastão ao próximo. Detalhes e números em [linguagem de motion](references/motion-remotion.md).
- **Nada aparece pronto:** todo elemento nasce pela animação de entrada (`<Life>`, `riseStyle`, `popStyle`, `travel`).
- **Zoom no rosto:** em alguns momentos dê **zoom no rosto** de quem fala para enfatizar uma palavra ou uma animação (punch-in com antecipação e mola; automático nas palavras de destaque, com intervalo mínimo de 3 s, e manual em `assets/zooms.json`), e mantenha um **leve zoom in/zoom out contínuo e discreto** (respiração de ~2,5% a cada ~7 s). O zoom acontece dentro da moldura, centrado no rosto, em camada composta (sem tremor). Ajuste em `face_zoom` do `editai.json`.
- **Rosto sempre centralizado (face tracking):** a câmera acompanha o movimento do rosto e o mantém no centro da tela (horizontal) e estável na altura natural em que a pessoa foi filmada, como um operador de câmera: segue os movimentos reais, ignora tremidinhas, sem saltos. O rastreamento é local (OpenCV) e roda sozinho no `cut`; refaça com `editai.py track`. O zoom usado para deslocar é o mínimo necessário (até `max_zoom` 1.25) e soma com o zoom de ênfase e a respiração. Ajustes em `face_track` do `editai.json`.
- **Sem jittery text:** texto/imagem tremendo é erro. Escala animada só em camada composta (`translateZ(0)` + `willChange`).
- **Legenda:** 2–3 palavras por vez no peito, Helvetica branca, entrando com mola (sobe ~18 px, overshoot leve) e saindo com recuo + blur, encadeada com a próxima. Sem legenda nas cenas `motion` (o texto animado é a fala) nem no `split` (o painel explica a fala).
- **Palavra de destaque (legenda, tipografia, painéis):** Scholar Italic em **gradiente laranja** (`#FFB37A → #FF6D29 → #E04A12`) com **glow leve** — sempre com `<KeyWord>` (vem do `highlight` do `editai.json`). Sempre bem maior (≈2× a legenda). Fica na linha de BAIXO quando continua a frase ("frase anterior / *impacto*"); EM CIMA quando a frase começa nela ("*impacto* / frase anterior"). Entra com pop de mola (antecipação + overshoot bouncy). ~1 por frase (`emphasis.json`).
- **Visual:** fundo sempre em gradiente com grade fina. Formas de preferência em **vidro** (`<Glass>`), senão gradiente. Paleta: laranja `#FF6D29`, marrom `#453027`, preto `#161316`, off-white `#F5F2EB`. Glow só leve, na palavra de destaque e em pequenos acentos luminosos; nada de neon em painéis.
- **Só tipografia cinética** nas cenas sem apresentador: nada de texto 3D, liquid, glitch ou distorções.
- **12 princípios da animação:** para cada animação, escolha o principal que serve à fala e anote no plano (`"principio"`).
- Nunca inventar números, prints ou resultados; números nos painéis vêm da fala ou do usuário.
- Remover pausas, gagueiras e frases repetidas, mantendo a última versão; ≤ 120 s por padrão.
- **Cor (suave, natural):** toda edição corrige balanço de branco (delicado, preserva o calor da pele), abre os meios-tons e as sombras sem esmagar o preto nem estourar as altas luzes, com **pouco contraste** e saturação natural (automático no `cut`; `editai.py grade` refaz; `"grade": false` desliga; ajustes em `"grade": {"wb_strength", "saturation", "contrast", "vibrance"}`). Nunca deixe o vídeo mais contrastado que o original. Confira o rosto: pele natural e quente, sombras com detalhe.
- **Efeitos sonoros:** **whoosh só em transições de tela e em elementos grandes se movendo** (trocas de cena e painéis grandes; o build já põe nas trocas de cena); pop nas palavras de impacto; volume baixo e confortável sob a voz (automático no build; `"sfx": false` desliga, `"sfx_volume"` ajusta). Nada de whoosh em ícones, legendas ou elementos pequenos.
- **Antes de gerar CADA vídeo (obrigatório, primeiro passo):** pergunte ao usuário se mantém a identidade visual do Editai — elementos, cores e fontes — ou se ele prefere usar a da marca dele e vai enviar as fontes, os elementos (logo, ícones, grafismos) e as cores. Não gere nada antes da resposta (se já houver escolha salva no `perfil.json`, mostre-a e confirme). Nome e @ só quando uma cena for mostrar o perfil.

## Preview e exportação
- **Preview = Remotion Studio**, sempre: rode `npx remotion studio --no-open` na pasta do projeto e abra a URL no painel do navegador da conversa. **Nunca** exporte ou mostre o MP4 final como preview.
- Conferência interna por quadros com `editai.py still` (todas as trocas de cena e os quadros vizinhos de cada passagem).
- **O MP4 final só é exportado depois da aprovação do aluno** (`editai.py render PROJETO --aprovado`). Entregar caminho do MP4, cortes feitos e pendências.
