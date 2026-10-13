import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {CURVE, EASE} from './tokens';
import {clamp01, leave, ramp, travel} from './core';
import {MotionBlur} from './blur';
import {KeyWord, popStyle, riseStyle} from './text';
import {Reveal, pickReveal, type RevealPreset} from './reveal';
import {Icon} from './ui';

export type Word = {at: number; text?: string; icon?: string; key?: boolean; size?: number; iconSize?: number; anim?: RevealPreset};

/**
 * A PALAVRA VIRA A CENA (tipografia cinética em fluxo contínuo).
 * Cada bloco entra no quadro em que é dito (`at`, quadro LOCAL da cena), empilha abaixo do anterior e a
 * coluna rola com mola (curva smooth, overshoot leve) para manter a fala atual no centro.
 * Anteriores escurecem e somem; impacto (`key`) entra com pop bouncy e gradiente + glow.
 * `endAt`: quadro em que a coluna inteira sai (recua e acelera para cima com blur).
 */
export const WordScene: React.FC<{words: Word[]; endAt: number; center?: number; gap?: number; color?: string}> = ({
  words,
  endAt,
  center = 880,
  gap = 28,
  color = '#F5F2EB',
}) => {
  const f = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  let y = 0;
  const items = words.map((w) => {
    const size = w.size ?? (w.key ? 260 : 170);
    const lines = (w.text ?? '').split('\n').length;
    const h = w.icon ? (w.iconSize ?? 220) : size * 0.98 * lines;
    const it = {w, top: y, c: y + h / 2, size};
    y += h + gap;
    return it;
  });
  const colY = (ff: number) => {
    let v = center - items[0].c;
    for (let k = 1; k < items.length; k++) {
      v += (items[k - 1].c - items[k].c) * travel(ff, items[k].w.at - 3, fps, CURVE.smooth, {anticip: 0.04, antDur: 5});
    }
    return v;
  };
  const out = leave(f, endAt - 10, 10);
  const scrolling = items.some((it, k) => k > 0 && f >= it.w.at - 6 && f < it.w.at + 16) || out > 0;
  return (
    <MotionBlur f={f} active={scrolling} samples={6} shutter={0.8}>
      {(ff) => (
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width,
            transform: `translateY(${colY(ff) - Math.max(0, leave(ff, endAt - 10, 10)) * 160}px)`,
            opacity: 1 - clamp01(leave(ff, endAt - 10, 10)),
          }}
        >
          {items.map((it, k) => {
            const next = items[k + 1]?.w.at;
            const next2 = items[k + 2]?.w.at;
            const dim = next === undefined ? 0 : ramp(ff, next, 12, EASE.glide);
            const gone = next2 === undefined ? 0 : ramp(ff, next2, 12, EASE.exit);
            // texto: o Reveal faz a entrada; so o icone usa a subida/pop do bloco
            const enter = it.w.icon ? (it.w.key ? popStyle(ff, it.w.at) : riseStyle(ff, it.w.at, undefined, {dist: 70, curve: CURVE.snappy})) : {};
            const anim = it.w.anim ?? (it.w.key ? 'posRotScale' : pickReveal(`${k}-${it.w.text}`, ['maskY', 'scaleTracking', 'maskX', 'fade']));
            return (
              <div
                key={k}
                style={{
                  position: 'absolute',
                  left: 0,
                  top: it.top,
                  width,
                  textAlign: 'center',
                  whiteSpace: 'pre-line',
                  fontSize: it.size,
                  lineHeight: 0.92,
                  color,
                  opacity: (1 - dim * 0.7) * (1 - gone),
                  filter: gone > 0 ? `blur(${gone * 8}px)` : undefined,
                  transform: `scale(${1 - dim * 0.06})`,
                }}
              >
                <div style={enter}>
                  {it.w.icon ? (
                    <Icon name={it.w.icon} f={ff} drawAt={it.w.at + 1} size={it.w.iconSize ?? 220} color={color} />
                  ) : (
                    (it.w.text ?? '').split('\n').map((linha, li) => (
                      <div key={li}>
                        <Reveal
                          text={linha}
                          f={ff}
                          at={it.w.at + li * 3}
                          preset={anim}
                          unit={it.w.key ? 'word' : 'glyph'}
                          wrap={it.w.key ? (n) => <KeyWord>{n}</KeyWord> : undefined}
                        />
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </MotionBlur>
  );
};
