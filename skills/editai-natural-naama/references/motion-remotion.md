# Linguagem de motion Editai (Remotion)

O padrão de qualidade é a animação aprovada pelo Naamã: **fluida, contínua, com ritmo, cada movimento sendo
continuação do anterior e do próximo**. Toda animação é função pura do quadro (`useCurrentFrame()`), sem CSS
transition/animation, sem `setTimeout`, sem `Math.random` (use `random(seed)` do Remotion).

## 1. As 10 regras (não negociáveis)
1. **Cada elemento tem a sua curva de velocidade** (`CURVE`). Nunca tudo com o mesmo easing.
2. **Antecipação antes de partir**: o elemento recua (ao longo do próprio caminho) antes de ir.
3. **Slow in**: sai do repouso devagar — nada dá tranco no primeiro quadro.
4. **Overshoot com mola na entrada e na saída**: passa do alvo e assenta; ao sair, recua e acelera (back-in).
5. **Keyframes espaçados**: movimentos de 10–30 quadros que se sobrepõem. Se parece acelerado, espaçe — não comprima.
6. **Arcos**: tudo que viaja segue curva (`spline`), com um único easing do início ao fim (sem para-e-anda nos pontos do meio).
7. **Squash & stretch + exagero** nos impactos; **smears** (esticar 2–4× + motion blur) nos movimentos de chicote.
8. **Follow-through, overlapping e ação secundária**: partes atrasam 2–3 quadros; halo arrasta; traços saltam no impacto.
9. **Nada fica parado nem some seco**: depois de chegar, flutua (`float`); toda saída é movimento. Um elemento passa o bastão ao próximo (o ponto vira a palavra, o spark vira o anel...).
10. **Motion blur** em todo movimento rápido (`<MotionBlur>`/`<Life>`), nunca em elemento parado.
11. **Zoom no rosto** para enfatizar palavras/animações e respiração contínua discreta (vídeos com apresentador).

## 2. Curvas de velocidade (`src/motion/tokens.ts`)
| Curva | Sensação | Cruza o alvo / overshoot / assenta (30 fps) | Use em |
|---|---|---|---|
| `CURVE.lazy` | flutuante, overshoot longo | 13f / +8.6% / 27f | cards, anel abrindo, partículas, painéis |
| `CURVE.smooth` | deslize calmo | 15f / +1.3% / 21f | ponteiro, rolagem de coluna, inchar |
| `CURVE.snappy` | rápido e preciso | 7f / +7.4% / 14f | saltos curtos, pouso, legenda |
| `CURVE.bouncy` | brincalhão, rebote duplo | 7f / +25% / 33f | pop de palavra de destaque, chip, badges |
| `CURVE.heavy` | demora a sair, carrega peso | 17f / +3.3% / 31f | giros, objetos grandes |
| `CURVE.long` | travessia sem pressa | 22f / +3.8% / 41f | objeto que cruza a tela inteira |

Easings auxiliares (`EASE`): `arrive` (expo-out), `glide`, `camera` (in-out), `backIn` (saída com recuo),
`backInOut`, `fall` (gravidade), `whip` (chicote). `drift` (linear) só para deriva ambiente.

## 3. Ferramentas (`src/motion/`)
```ts
travel(f, start, fps, CURVE.x, {anticip, antDur})  // progresso: recua (<0), slow-in, mola (>1), assenta em 1
leave(f, start, dur)                                // saída back-in (recua um pouco, acelera até 1)
spline(pontos, u)                                   // caminho em arco; u fora de 0–1 extrapola pela tangente
float(f, amp, period, phase)                        // flutuação ociosa
squashAt(f, impacto, fps, big?)                     // {sx, sy} do impacto
velocityStretch(posFn, f, k, max)                   // {stretch, angle, dx, dy} pela velocidade
smoothKeys(f, frames, values)                       // valores-chave com velocidade contínua (câmera)
<MotionBlur f samples shutter active>{(ff)=>...}</MotionBlur>  // blur por sub-quadros; smear: samples 3–4, shutter 2–2.5
<Life f inAt outAt curve anticip from to floatAmp style>        // entrada→flutua→saída com blur automático
riseStyle(f, inAt, outAt, {dist, curve}) / popStyle(f, inAt, outAt)  // texto: subida com mola / pop bouncy
<KeyWord>                                           // palavra de destaque: gradiente da cor + glow leve
<WordScene words endAt>                             // tipografia cinética em fluxo contínuo
<Icon name f drawAt size> / <Glass> / <Scramble> / <TypeOn> / trackingCollapse
```

Receita padrão de um objeto que viaja e pousa:
```tsx
const u = travel(f, B.hop, fps, CURVE.snappy, {anticip: 0.15, antDur: 7});   // antecipa, sai devagar, passa e volta
const p = spline([inicio, {x: meioX, y: topoDoArco}, alvo], u);               // em arco
const v = velocityStretch((ff) => spline([...], travel(ff, ...)), f, 0.006, 2.2); // estica na velocidade (smear)
const sq = squashAt(f, B.pouso, fps, true);                                    // squash exagerado no pouso
```

## 4. Planejamento: beat sheet
Antes de animar, escreva no topo da cena um `const B = {...}` com o quadro de cada batida (entrada, impacto,
saída). Espaçe as batidas; sobreponha os movimentos (o próximo começa antes do anterior assentar). Para cada batida
defina: curva, antecipação, o que reage ao impacto (ação secundária) e para onde o elemento vai depois (passagem de bastão).

## 5. Continuidade e passagem de bastão
- O fim de um movimento é o começo do próximo: mesma posição, mesma velocidade, mesmo raio. Compartilhe a função de
  posição entre as cenas (exporte-a) em vez de copiar números.
- **Troque o dono do elemento só depois que todas as molas assentaram** (senão há salto visível na troca).
- Quem tem overshoot é o tamanho/escala; o centro de um objeto que muda de dono chega sem overshoot.
- Confira as trocas com `editai.py still` nos quadros vizinhos (ex.: 87, 88, 89): não pode haver salto nem sumiço.
- A cena (Sequence) precisa durar até a passagem terminar — sequência curta faz o elemento sumir por alguns quadros.

## 6. Texto
- Legenda corrida: sobe ~18 px com mola (`riseStyle`, curva snappy) e sai recuando e subindo com blur, encadeada com a próxima.
- **Palavra de destaque**: sempre `<KeyWord>` — **gradiente da cor de destaque** (claro → cor → escuro) + **glow leve**
  (`highlight` no `editai.json`); entra com `popStyle` (encolhe na antecipação, pop bouncy com overshoot).
- Tipografia cinética: `WordScene` (blocos de 2–4 palavras entrando no quadro em que são ditos; a coluna rola com mola).
  Escreva `at` como número de quadros literal (`{at: 48, text: 'errado', key: true}`) para o build achar os pops.
- Revelações: `Scramble` (bloco/glifos resolvendo), `TypeOn` (1,5 quadro por letra), `trackingCollapse` (letras espalhadas se juntam).
- **Sem jittery text**: não anime `scale` em camadas com texto sem compor a camada (`transform: ... translateZ(0)` +
  `willChange: 'transform'`). Texto tremendo = erro.

## 7. Câmera, zoom no rosto e som
- **Zoom no rosto (vídeos com apresentador):** punch-in de ênfase numa palavra ou animação (antecipação: recua ~1%, depois mola até 1.12–1.2 e volta suave) + **respiração contínua e discreta** (zoom in/out de ~2,5% a cada ~7 s). Sempre dentro da moldura, centrado no rosto, em camada composta (`translateZ(0)` + `willChange`) — o template faz isso (`faceZoomAt`).
- **Rosto sempre centralizado (face tracking):** a câmera segue o rosto (rastro local suavizado, zona morta contra tremidinhas) e usa o zoom mínimo para centralizar sem mostrar as bordas (`trackedCamera` no template).
- Em cenas sem apresentador, uma câmera contínua (`CameraRig` com `smoothKeys` + leve flutuação) envolve as camadas, com parallax (fundo 0,3 : meio 0,6 : frente 1). Nunca reinicie o zoom a cada cena.
- **Whoosh só em transições de tela e elementos grandes se movendo**; pop nas palavras de impacto; ticks só em digitação.

## 8. Preview e exportação (obrigatório)
- **"Preview" = Remotion Studio**: `npx remotion studio --no-open` na pasta do projeto (em segundo plano) e abrir a URL
  impressa no painel do navegador da conversa. Nunca renderize o MP4 para mostrar um preview.
- Conferência interna: `editai.py still PROJETO --at 0.5,2.6,...` (PNG em `snapshots/`).
- **MP4 final só depois da aprovação explícita do aluno**: `editai.py render PROJETO --aprovado`.
