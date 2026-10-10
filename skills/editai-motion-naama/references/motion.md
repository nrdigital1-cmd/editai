# Guia de motion — Editai Motion

## 1. Planejar as cenas (`assets/scenes.json`)

Leia a transcrição final inteira e divida em cenas de 3–6 s, cortando sempre no início de uma palavra.
Para cada cena pergunte: *o que quem assiste precisa VER para entender esta frase?*

```json
[
  {"layout":"motion","start":0,"end":2.4,"js":"..."},
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

## 3. Ajudantes prontos (use sempre — já têm curva, blur e deriva)
- `E.enter(tl, alvo, t, {y, x, scale, d, blur, stagger})` — entrada com desaceleração e motion blur.
- `E.exit(tl, alvo, t, {...})` — saída acelerando com blur, terminando no tempo `t`.
- `E.drift(tl, alvo, t, duração)` — movimento lento contínuo enquanto o elemento está na tela.
- `E.wordScene(tl, el, palavras, fim)` — **a palavra vira a cena** (abaixo).
Todo elemento de painel segue: `E.enter` → `E.drift` → `E.exit`. Nada entra seco, nada fica congelado.

### Regras de movimento
- **Entrada:** chega rápido e desacelera ao assentar (`expo.out` / `power3.out`), 0,45–0,7 s. Nunca linear.
- **Motion blur:** todo movimento de entrada e saída leva desfoque proporcional à velocidade (≈10 px em elementos,
  ≈4 px na legenda), que some quando o elemento para. Nada fica desfocado parado.
- **Deriva contínua:** depois de entrar, o elemento continua se movendo devagar (`sine.inOut`, 6–10 px ou escala +1,5%). Nada congela.
- **Saída:** acelera ao sair (`power2.in`), 0,25–0,3 s, com blur; encadeada com a entrada seguinte.
- **Stagger** em grupos (0,06–0,12 s), **anticipation** antes de números estourarem, **follow-through** leve ao parar.
- **Modo leve:** em PC mais simples o builder reduz o blur pela metade sozinho (`"modo_leve"` no `editai.json` força ligado/desligado).

## 4. Cenas só de texto: a palavra vira a cena
Em toda cena `motion` sem elementos, use `E.wordScene`. Cada palavra (ou bloco curto) ocupa a tela no instante
em que é dita e se transforma na próxima: entra subindo com blur, cresce devagar enquanto é falada e sai acelerando
para cima. Palavra de impacto (`key:true`) entra **maior, em laranja Scholar Italic** e um pouco mais lenta.
Varie tamanho e posição entre palavras para dar ritmo (não deixe todas no mesmo lugar).

```js
E.wordScene(tl, el, [
  {t:0.00, text:"se você", size:120, y:700},
  {t:0.92, text:"passa", size:150, y:820},
  {t:1.34, text:"HORAS", key:true, size:230, y:760},
  {t:1.78, text:"editando", size:140, y:900}
], T);
```

## 5. Tipografia cinética: como deixar profissional
- Varie **tamanho, posição e peso** a cada palavra; nunca todas no mesmo lugar.
- Palavra de impacto: maior, laranja Scholar Italic, entra um pouco mais lenta.
- Ritmo acompanha a fala: a palavra entra no instante em que é dita.
- Proibido nesta skill: texto 3D/extrudado, liquid, glitch, distorções e efeitos de "IA".

## 6. Cenas `split` (painel de vidro + apresentador)

Exemplos que ilustram falas comuns:
- "tirou as pausas / cortou os erros" → forma de onda com trechos marcados que encolhem e somem.
- "2 horas → 10 minutos" → duas barras: a longa enche devagar, a curta enche rápido; contador do tempo.
- "eu só gravo e mando" → fluxo: card "vídeo bruto" → seta desenhada → card "Claude" → card "pronto ✓".
- "legenda, prints, animações" → três chips de vidro entrando em stagger, cada um na palavra dita.

## 7. Conferir

Snapshots em todas as trocas de cena e no meio de cada animação (`npx hyperframes snapshot --at ...`).
Confira: legenda legível, rosto livre, texto dentro da área segura, vidro visível sobre o fundo, nenhum glow.
