# Guia de cenas — Editai Motion (Remotion)

Leia junto a [linguagem de motion](motion-remotion.md): ela define curvas, antecipação, overshoot, arcos, smears e
continuidade. Este guia diz **o que** colocar em cada cena; a linguagem diz **como** mover.

## 1. Planejar as cenas (`assets/scenes.json`)
Leia a transcrição final inteira e divida em cenas de 3–6 s, cortando sempre no início de uma palavra.
Para cada cena pergunte: *o que quem assiste precisa VER para entender esta frase?*

```json
[
  {"layout":"motion","start":0,"end":2.4,"component":"Gancho","principio":"exagero"},
  {"layout":"split","start":2.4,"end":6.8,"component":"DuasHoras","principio":"arcos + follow-through"},
  {"layout":"full","start":6.8,"end":10.2,"component":"BadgePausa"}
]
```

- `layout`: `full`, `split` ou `motion`. Intervalos ordenados, sem sobreposição; buracos viram `full` sem elementos.
- `component`: TSX seu em `src/scenes/<Nome>.tsx` (PascalCase). Em `split` a caixa é 960×690 a partir de (60,150);
  em `full`/`motion` é a tela toda 1080×1920 (texto entre y 270 e 1250 para não cair sob a interface do Reels).
- O quadro é LOCAL (`useCurrentFrame()` = 0 no início da cena); `durationInFrames` vem nas props.
  Converta falas para quadros: `Math.round((tempoDaPalavra - startDaCena) * 30)`.

## 2. Estrutura de uma cena
```tsx
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {SceneProps} from '../types';
import {CURVE, EASE} from '../motion/tokens';
import {Life} from '../motion/life';
import {Glass, Icon} from '../motion/ui';
import {KeyWord, popStyle, riseStyle} from '../motion/text';

// Beat sheet: quadros (locais) de cada batida — espaçados, com sobreposição
const B = {card: 2, icone: 8, rotulo: 14, impacto: 26};

export const DuasHoras: React.FC<SceneProps> = ({durationInFrames: end}) => {
  const f = useCurrentFrame();
  return (
    <>
      <Life f={f} inAt={B.card} outAt={end - 12} curve={CURVE.lazy} anticip={0.08}
            from={{y: 90, scale: 0.88, rot: -3}} style={{left: 0, top: 0, width: 960, height: 690}}>
        <Glass style={{inset: 0}} />
      </Life>
      <Life f={f} inAt={B.icone} outAt={end - 14} curve={CURVE.snappy} from={{x: -80, scale: 0.6}}
            style={{left: 90, top: 180, width: 220, height: 220}}>
        <Icon name="clock" f={f} drawAt={B.icone + 2} size={220} />
      </Life>
      <div style={{position: 'absolute', left: 360, top: 230, fontSize: 96, ...riseStyle(f, B.rotulo, end - 10, {curve: CURVE.smooth, dist: 40})}}>2 horas →</div>
      <div style={{position: 'absolute', left: 360, top: 350, fontSize: 130, ...popStyle(f, B.impacto, end - 10)}}><KeyWord>10 min</KeyWord></div>
    </>
  );
};
```
Cada elemento com uma curva diferente (lazy, snappy, smooth, bouncy): é isso que dá ritmo.

## 3. As três composições
| Composição | Quando | Como |
|---|---|---|
| `split` | A fala explica algo que dá para mostrar: processo, antes/depois, número | Painel de vidro na faixa de cima; apresentador no card com cantoneiras embaixo |
| `full` | Fala pessoal, opinião, ponte entre ideias | Apresentador na tela; badges de vidro (`Glass` + `Icon`) ao lado da cabeça (x 60 ou 820, y ≈380) entrando pela borda com mola |
| `motion` | Gancho, ideia-chave, frase de impacto | Só fundo + tipografia cinética `WordScene` (a palavra vira a cena). A voz continua |

## 4. Tipografia cinética (`WordScene`)
```tsx
<WordScene endAt={end} words={[
  {at: 0, icon: 'play', iconSize: 190},
  {at: 14, text: 'testei tudo isso', size: 150},
  {at: 48, text: 'errado', key: true, size: 290},
]} />
```
- Blocos de 2–4 palavras (nunca uma palavra a cada 0,3 s); `\n` quebra linha; `at` como número literal (o build acha os pops).
- Palavras grandes: 150–260 px; impacto 260–340 px com `key: true` (gradiente + glow, pop bouncy).
- Varie tamanho e peso; a coluna rola com mola; anteriores escurecem e somem; a saída recua e sobe com blur.
- Revelações extras: `Scramble`, `TypeOn`, `trackingCollapse` (ver linguagem de motion).

## 5. Ícones que se desenham (ilustram a fala)
`<Icon name="clock" f={f} drawAt={quadro} size={120} />`. Ícones: clock, bolt, spark, video, rec, play, x, pause,
stutter, script, send, cc, shapes, eye, warn, chat, box, question, sliders, hourglass, cap, scissors, check, target,
copy, list, book, userplus, link, arrowr, down, user, wave, folder. O traço "a" usa a cor de destaque.
Escolha pelo que é FALADO naquele instante ("pausas" → pause, "erros" → x, "legendas" → cc, "link na bio" → link).

## 6. Ideias para `split`
- "tirou as pausas / cortou os erros" → forma de onda com trechos que encolhem (squash) e somem (leave).
- "2 horas → 10 minutos" → duas barras: a longa enche devagar (heavy), a curta enche rápido (snappy) com overshoot.
- "eu só gravo e mando" → card "vídeo bruto" → seta que se desenha em arco → card "pronto ✓" (passagem de bastão).
- "legenda, prints, animações" → três chips de vidro entrando com stagger de 4 quadros, cada um na palavra dita.

## 7. Transições entre cenas (continuidade)
A saída de uma cena e a entrada da seguinte são **um movimento só**: mesmo sentido, saída com `leave` (recua e acelera)
começando ~8 quadros antes do corte e entrada com `travel` + mola terminando ~15 quadros depois; o pico de velocidade
fica no corte (whoosh automático). Sempre que possível um elemento da cena atual vira o elemento da próxima.

## 8. Conferir
`editai.py still PROJETO --at ...` em todas as trocas de cena, no meio de cada animação e nos quadros vizinhos de cada
passagem. Confira: legenda legível, rosto livre, texto na área segura, vidro visível, gradiente + glow só na palavra
de destaque, motion blur só em movimento, nada tremendo, nenhum salto. Depois: preview no Remotion Studio para o aluno.
