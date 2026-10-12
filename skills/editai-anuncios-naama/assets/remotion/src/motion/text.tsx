import React, {createContext, useContext} from 'react';
import {random, spring} from 'remotion';
import {CURVE, EASE, FPS, SPRING} from './tokens';
import {clamp01, leave, ramp, springAt, travel} from './core';

export type Highlight = {from: string; via: string; to: string; glow: string; glowPx: number};
export const HighlightCtx = createContext<Highlight>({from: '#FFB37A', via: '#FF6D29', to: '#E04A12', glow: 'rgba(255,109,41,0.45)', glowPx: 18});

/**
 * Palavra de destaque: GRADIENTE da cor de destaque (claro → cor → escuro) recortado no texto
 * + glow leve. Use em toda palavra de impacto (legenda, tipografia cinética, painéis).
 */
export const KeyWord: React.FC<{children: React.ReactNode; style?: React.CSSProperties; glow?: number}> = ({children, style, glow = 1}) => {
  const h = useContext(HighlightCtx);
  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: 'EditaiScholar, serif',
        fontStyle: 'italic',
        letterSpacing: '-0.01em',
        padding: '0 0.08em 0.06em',
        backgroundImage: `linear-gradient(175deg, ${h.from} 0%, ${h.via} 55%, ${h.to} 100%)`,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        color: 'transparent',
        WebkitTextFillColor: 'transparent',
        filter: `drop-shadow(0 0 ${h.glowPx * glow}px ${h.glow})`,
        ...style,
      }}
    >
      {children}
    </span>
  );
};

/**
 * Entrada de texto com mola (Rise): sobe com slow-in e assenta com overshoot leve; sai com antecipação
 * (recua, depois acelera para cima) e desfoque proporcional à velocidade.
 */
export const riseStyle = (f: number, inAt: number, outAt?: number, o: {dist?: number; curve?: typeof CURVE.lazy; outDur?: number} = {}) => {
  const p = travel(f, inAt, FPS, o.curve ?? CURVE.snappy, {anticip: 0.04, antDur: 3});
  const dist = o.dist ?? 22;
  const out = outAt === undefined ? 0 : leave(f, outAt, o.outDur ?? 8);
  const vin = Math.abs(p - travel(f - 1, inAt, FPS, o.curve ?? CURVE.snappy, {anticip: 0.04, antDur: 3}));
  const blur = Math.min(8, vin * dist * 0.5) + Math.max(0, out) * 6;
  return {
    transform: `translateY(${(1 - p) * dist - out * dist * 1.4}px) scale(${0.96 + 0.04 * Math.min(1.05, p)})`,
    opacity: clamp01(p * 2.5) * (1 - clamp01(out)),
    filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
  } as React.CSSProperties;
};

/** Pop de palavra de impacto: antecipação (encolhe), mola bouncy com overshoot, exagero controlado. */
export const popStyle = (f: number, inAt: number, outAt?: number) => {
  const s = springAt(f, inAt, FPS, CURVE.bouncy.config);
  const pre = ramp(f, inAt - 4, 4, EASE.glide) * (1 - ramp(f, inAt, 1, EASE.drift));
  const out = outAt === undefined ? 0 : leave(f, outAt, 8);
  const sc = f < inAt ? 0.7 - pre * 0.05 : 0.7 + 0.3 * s;
  return {
    transform: `translateY(${(1 - Math.min(1, s)) * 26 - out * 30}px) scale(${sc * (1 + Math.max(0, out) * 0.1)})`,
    opacity: clamp01(s * 3) * (1 - clamp01(out)),
    filter: out > 0 ? `blur(${out * 6}px)` : undefined,
  } as React.CSSProperties;
};

/** Spring de subida de legenda (corrido): sobe ~18 px com overshoot leve. */
export const captionRise = (f: number, inAt: number) => {
  const s = f < inAt ? 0 : spring({frame: f - inAt, fps: FPS, config: SPRING.rise});
  return {transform: `translateY(${(1 - s) * 18}px)`, opacity: clamp01(s * 2.2)} as React.CSSProperties;
};

/** blockScramble: bloco/glifos resolvendo nos caracteres reais, da esquerda para a direita. */
export const Scramble: React.FC<{text: string; f: number; start: number; dur?: number; seed: string; blockColor?: string; mode?: 'block' | 'glyph'}> = ({
  text,
  f,
  start,
  dur = 10,
  seed,
  blockColor = 'currentColor',
  mode = 'block',
}) => {
  const chars = [...text];
  const n = chars.length;
  const glyphs = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*+=<>/';
  return (
    <span style={{display: 'inline-block', whiteSpace: 'pre'}}>
      {chars.map((c, i) => {
        const resolveAt = start + (dur * (i + 1)) / n;
        const state = f < start ? 'hidden' : f >= resolveAt ? 'char' : f >= resolveAt - 3 ? 'glyph' : 'pre';
        const showGlyph = state === 'glyph' || (state === 'pre' && mode === 'glyph');
        return (
          <span
            key={i}
            style={{
              position: 'relative',
              display: 'inline-block',
              color: state === 'char' ? undefined : 'transparent',
              backgroundColor: state === 'pre' && mode === 'block' ? blockColor : undefined,
            }}
          >
            {c}
            {showGlyph && c !== ' ' ? (
              <span style={{position: 'absolute', left: 0, right: 0, top: 0, textAlign: 'center', color: blockColor, opacity: 0.7}}>
                {glyphs[Math.floor(random(`${seed}-${i}-${Math.floor(f)}`) * glyphs.length)]}
              </span>
            ) : null}
          </span>
        );
      })}
    </span>
  );
};

/** typeOn: um caractere a cada 1,5 quadro, cada um com fade + subida curta. */
export const TypeOn: React.FC<{text: string; f: number; start: number; perChar?: number}> = ({text, f, start, perChar = 1.5}) => (
  <span style={{whiteSpace: 'pre'}}>
    {[...text].map((c, i) => {
      const p = ramp(f, start + i * perChar, 4, EASE.arrive);
      return (
        <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 0.12}em)`}}>
          {c}
        </span>
      );
    })}
  </span>
);

/** trackingCollapse: letter-spacing 1.2em → 0 (letras espalhadas que se juntam). */
export const trackingCollapse = (f: number, start: number, dur = 14) => ramp(f, start, dur, EASE.arrive, 1.2, 0);
