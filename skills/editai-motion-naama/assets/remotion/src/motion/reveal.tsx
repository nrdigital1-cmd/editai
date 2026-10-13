import React from 'react';
import {CURVE, EASE, FPS, STAGGER, type Curve} from './tokens';
import {clamp01, lerp, leave, ramp, travel} from './core';

/**
 * REVEAL — a palavra nunca aparece inteira e seca. Cinco entradas de texto:
 *
 * - fade          Ease Fade Together: todas as letras juntas, fade com ease + desfoque que some + subida curta.
 * - posRotScale   Overshoot Position & Rotate & Scale: letra a letra, sobe girando e crescendo, passa do ponto e assenta (mola).
 * - scaleTracking Overshoot Scale & Tracking: a palavra encolhe de grande e as letras se juntam; a mola faz a escala e o
 *                 espaçamento passarem um pouco do ponto antes de assentar.
 * - maskY         Overshoot Position & Mask Y: cada letra sobe de dentro de uma máscara (de baixo para cima), com overshoot.
 * - maskX         Overshoot Position & Mask X: a palavra desliza da esquerda para a direita de dentro de uma máscara, com overshoot.
 *
 * Todas usam o motor de motion do Editai: antecipação antes de partir, slow-in saindo do repouso, mola (overshoot) ao chegar,
 * curva de velocidade diferente por letra (nada em sincronia robótica), motion blur proporcional à velocidade e
 * saída com antecipação (recua e acelera). `at`/`out` são quadros.
 */
export type RevealPreset = 'fade' | 'posRotScale' | 'scaleTracking' | 'maskY' | 'maskX';
export const REVEAL_PRESETS: RevealPreset[] = ['maskY', 'posRotScale', 'scaleTracking', 'maskX', 'fade'];

/** Escolha estável (sempre a mesma para o mesmo texto/posição): varia o efeito sem ficar aleatório a cada quadro. */
export const pickReveal = (seed: string | number, pool: RevealPreset[] = REVEAL_PRESETS): RevealPreset => {
  const s = String(seed);
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return pool[Math.abs(h) % pool.length];
};

// Personalidades alternadas por letra: snappy/bouncy/smooth em rodízio → overlapping action natural.
const GLYPH_CURVES: Curve[] = [CURVE.snappy, CURVE.bouncy, CURVE.snappy, CURVE.smooth];
const ANT = {anticip: 0.05, antDur: 4};

const prog = (f: number, start: number, curve: Curve) => travel(f, start, FPS, curve, ANT);
const speed = (f: number, start: number, curve: Curve) => Math.abs(prog(f, start, curve) - prog(f - 1, start, curve));

/** Desfoque de movimento por velocidade (px), + desfoque da saída. Máx. 7 px para continuar legível. */
const mblur = (v: number, dist: number, out: number) => Math.min(7, v * dist * 0.35) + Math.max(0, out) * 6;
const f2 = (n: number) => n.toFixed(2);

type Props = {
  text: string;
  f: number;
  at: number;
  out?: number;
  preset?: RevealPreset;
  /** 'word' para palavras de impacto (gradiente contínuo) ou textos muito longos. */
  unit?: 'glyph' | 'word';
  /** Quadros entre letras (padrão: STAGGER.glyph, ~1 quadro). */
  stagger?: number;
  style?: React.CSSProperties;
  /** Envolve cada unidade (ex.: <KeyWord>) mantendo a animação por fora. */
  wrap?: (node: React.ReactNode) => React.ReactNode;
};

export const Reveal: React.FC<Props> = ({text, f, at, out, preset = 'maskY', unit = 'glyph', stagger, style, wrap}) => {
  const units = unit === 'word' ? [text] : [...text];
  const step = stagger ?? (preset === 'posRotScale' ? STAGGER.glyph * 1.4 : STAGGER.glyph);
  const ex = out === undefined ? 0 : leave(f, out, 8); // saída: recua e acelera
  const wrapNode = wrap ?? ((n: React.ReactNode) => n);

  // scaleTracking anima a palavra inteira (escala + espaçamento entre letras)
  if (preset === 'scaleTracking') {
    const p = prog(f, at, CURVE.snappy);
    const v = speed(f, at, CURVE.snappy);
    const sc = lerp(1.32, 1, p) * (1 + Math.max(0, ex) * 0.08);
    const track = lerp(0.55, 0, p) + Math.max(0, ex) * 0.25; // em; p>1 → espaçamento passa um pouco do ponto (fica mais justo) e volta
    const b = mblur(v, 40, ex);
    const {letterSpacing: base, ...rest} = style ?? {};
    return (
      <span
        style={{
          ...rest,
          display: 'inline-block',
          whiteSpace: 'pre',
          transform: `scale(${f2(sc)})`,
          letterSpacing: base ? `calc(${f2(track)}em + ${base})` : `${f2(track)}em`,
          opacity: clamp01(p * 2.4) * (1 - clamp01(ex)),
          filter: b > 0.2 ? `blur(${f2(b)}px)` : undefined,
        }}
      >
        {wrapNode(text)}
      </span>
    );
  }

  // fade: tudo junto, ease (sem mola)
  if (preset === 'fade') {
    const p = ramp(f, at, 12, EASE.glide);
    const b = (1 - p) * 8 + Math.max(0, ex) * 6;
    return (
      <span
        style={{
          display: 'inline-block',
          whiteSpace: 'pre',
          opacity: p * (1 - clamp01(ex)),
          transform: `translateY(${f2((1 - p) * 0.12 - Math.max(0, ex) * 0.3)}em)`,
          filter: b > 0.2 ? `blur(${f2(b)}px)` : undefined,
          ...style,
        }}
      >
        {wrapNode(text)}
      </span>
    );
  }

  return (
    <span style={{display: 'inline-block', whiteSpace: 'pre', ...style}}>
      {units.map((u, i) => {
        if (u === ' ') return <span key={i}> </span>;
        const curve = GLYPH_CURVES[i % GLYPH_CURVES.length];
        const s = at + i * step;
        const p = prog(f, s, curve);
        const v = speed(f, s, curve);
        const e = out === undefined ? 0 : leave(f, out + i * 0.5, 8);
        const vis = 1 - clamp01(e);

        if (preset === 'posRotScale') {
          const b = mblur(v, 60, e);
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                transformOrigin: '50% 90%',
                transform: `translateY(${f2((1 - p) * 0.55 - Math.max(0, e) * 0.5)}em) rotate(${f2((1 - p) * 22)}deg) scale(${f2(lerp(0.35, 1, p))})`,
                opacity: clamp01(p * 2.6) * vis,
                filter: b > 0.2 ? `blur(${f2(b)}px)` : undefined,
              }}
            >
              {wrapNode(u)}
            </span>
          );
        }

        // máscaras: a unidade fica dentro de uma janela com folga para itálico/acentos/descendentes
        const isX = preset === 'maskX';
        const b = mblur(v, 50, e);
        const move = isX
          ? `translateX(${f2((p - 1) * 105 + Math.max(0, e) * 105)}%)`
          : `translateY(${f2((1 - p) * 110 - Math.max(0, e) * 110)}%)`;
        return (
          <span
            key={i}
            style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', padding: '0.14em 0.1em 0.18em', margin: '-0.14em -0.1em -0.18em'}}
          >
            <span style={{display: 'inline-block', transform: move, filter: b > 0.2 ? `blur(${f2(b)}px)` : undefined}}>{wrapNode(u)}</span>
          </span>
        );
      })}
    </span>
  );
};
