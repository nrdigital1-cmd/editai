# Guia de motion — Editai Motion

## 1. Planejar as cenas (`assets/scenes.json`)

Leia a transcrição final inteira e divida em cenas de 3–6 s, cortando sempre no início de uma palavra.
Para cada cena pergunte: *o que quem assiste precisa VER para entender esta frase?*

```json
[
  {"layout":"motion","start":0,"end":2.4,"html":"<div class='kt extrude' style='left:90px;top:760px'>2 HORAS</div>","js":"..."},
  {"layout":"split","start":2.4,"end":6.8,"html":"<div class='glass' style='inset:0'>...</div>","js":"..."},
  {"layout":"full","start":6.8,"end":10.2}
]
```

- `layout`: `full`, `split` ou `motion`. Intervalos ordenados, sem sobreposição; buracos viram `full`.
- `html`: conteúdo da cena (escrito por você, local). Em `split` a caixa é 960×700 a partir de (60,150);
  em `motion` é a tela toda 1080×1920 (mantenha texto entre y 270 e 1250 para não cair sob a interface do Reels).
- `js`: keyframes da cena. Recebe `tl` (timeline GSAP), `t0` (início da cena em segundos) e `el` (elemento da cena).
  Sempre posicione no tempo com `t0 + x`. Nada de `Math.random`, timers ou CSS infinito.

## 2. Vocabulário de motion (use estes termos ao planejar)

| Termo | O que é | Como aplicar aqui |
|---|---|---|
| **Keyframe** | Ponto no tempo com um valor definido | Cada `tl.to/fromTo(..., t0 + x)` é um par de keyframes |
| **Curva de animação / easing** | Como a velocidade muda entre keyframes | Nunca `linear` em movimento; só em barras de progresso constantes |
| **Ease out** (desacelera no fim) | Entrada natural: chega rápido e assenta | Entradas: `power3.out`, `expo.out` |
| **Ease in** (acelera no fim) | Saída: começa devagar e sai rápido | Saídas: `power2.in`, 0,2–0,3 s |
| **Ease in-out** | Acelera e desacelera | Deslocamentos dentro da cena: `power2.inOut`, `expo.inOut` |
| **Overshoot / back** | Passa do ponto e volta | Só em selos e ✓: `back.out(1.6)` |
| **Stagger** | Atraso em cascata entre elementos | Letras 0,02–0,04 s; itens de lista 0,08–0,12 s |
| **Anticipation** | Pequeno movimento contrário antes da ação | Escala 1 → 0,96 → 1,08 antes de um número estourar |
| **Follow-through / settle** | O elemento se acomoda depois de parar | Leve `y` de 6 px voltando a 0 com `power2.out` |
| **Motion blur aparente** | Sensação de velocidade | `filter: blur(8px) → 0` na entrada de elementos rápidos |
| **Timing** | Duração dos movimentos | Entradas 0,35–0,6 s; texto cinético 0,5–0,8 s; saídas 0,2–0,3 s |
| **Hold** | Tempo parado para leitura | Todo texto fica parado no mínimo 0,8 s antes de sair |
| **Mask reveal** | Revelar por dentro de uma máscara | `clipPath: inset(0 100% 0 0) → inset(0 0 0 0)` |
| **Parallax** | Camadas em velocidades diferentes | Fundo/grade 20 px, painel 40 px, texto 60 px no mesmo intervalo |

## 3. Técnicas para cenas `motion`

- **Tipografia cinética:** `E.chars(el)` quebra em letras; anime `y:120, rotateX:-90, opacity:0 → 0` com `stagger:0.03, ease:'expo.out'`.
  Mude escala e posição a cada palavra dita.
- **Liquid typography:** classe `liquid` no texto + `E.liquid(tl, t0)` — a distorção assenta em 0,9 s com `expo.out`.
- **Glitch / texto digital:** `<div class="glitch kt"><span class="g1">TEXTO</span><span class="g2">TEXTO</span></div>`
  + `E.glitch(tl, el.querySelector('.glitch'), t0)`. Use em palavras como "erro", "corte", "gagueira". Curto: ≤ 0,4 s.
- **Texto 3D / extrudado:** classe `extrude`; entre com `rotateY:-35 → 0` e `scale:.8 → 1`, `expo.out`, com `transformPerspective:1200`.
- **Elementos:** barras (`.bar > b` com `scaleX`), contadores (objeto `{v:0}` animado e `onUpdate` escrevendo o número),
  linhas desenhadas (SVG `strokeDashoffset`), cards de vidro entrando em `stagger`.

## 4. Cenas `split` (painel de vidro + apresentador)

Exemplos que ilustram falas comuns:
- "tirou as pausas / cortou os erros" → forma de onda com trechos marcados que encolhem e somem.
- "2 horas → 10 minutos" → duas barras: a longa enche devagar, a curta enche rápido; contador do tempo.
- "eu só gravo e mando" → fluxo: card "vídeo bruto" → seta desenhada → card "Claude" → card "pronto ✓".
- "legenda, prints, animações" → três chips de vidro entrando em stagger, cada um na palavra dita.

## 5. Conferir

Snapshots em todas as trocas de cena e no meio de cada animação (`npx hyperframes snapshot --at ...`).
Confira: legenda legível, rosto livre, texto dentro da área segura, vidro visível sobre o fundo, nenhum glow.
