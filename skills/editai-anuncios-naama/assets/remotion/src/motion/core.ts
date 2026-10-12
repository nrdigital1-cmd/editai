import {Easing, interpolate, spring} from 'remotion';
import {EASE, SPRING, SQUASH, SQUASH_BIG, type Curve} from './tokens';

export type EaseFn = (t: number) => number;
export type Pt = {x: number; y: number};
export type PosFn = (f: number) => Pt;
type SpringCfg = {stiffness: number; damping: number; mass: number};
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** 0→1 (ou from→to) em [start, start+dur] com um easing. Frames (não segundos). */
export const ramp = (f: number, start: number, dur: number, ease: EaseFn = EASE.arrive, from = 0, to = 1) =>
  interpolate(f, [start, start + Math.max(dur, 0.0001)], [from, to], {...CLAMP, easing: ease});

export const keys = (f: number, frames: number[], values: number[], ease: EaseFn = EASE.arrive) =>
  interpolate(f, frames, values, {...CLAMP, easing: ease});

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

export const springAt = (f: number, start: number, fps: number, config: SpringCfg = SPRING.pop) =>
  f < start ? 0 : spring({frame: f - start, fps, config});

/** Squash & stretch no impacto, assentando com mola (big = exagerado). */
export const squashAt = (f: number, impact: number, fps: number, big = false) => {
  if (f < impact) return {sx: 1, sy: 1};
  const q = big ? SQUASH_BIG : SQUASH;
  const k = 1 - spring({frame: f - impact, fps, config: SPRING.blob});
  return {sx: 1 + (q.x - 1) * k, sy: 1 + (q.y - 1) * k};
};

/** Slow-in C1-contínuo: o tempo começa parado e alcança o tempo real após `slowIn` quadros. */
const slowInTime = (t: number, slowIn: number) => (slowIn <= 0 ? t : t < slowIn ? (t * t) / (2 * slowIn) : t - slowIn / 2);

/**
 * travel — progresso com ANTECIPAÇÃO (recua até -anticip nos antDur quadros antes de `start`),
 * SLOW-IN saindo do repouso e FOLLOW-THROUGH de mola (passa do alvo e assenta).
 * Valores fora de 0–1 são intencionais: use com lerp()/spline().
 */
export const travel = (f: number, start: number, fps: number, curve: Curve, opts: {anticip?: number; antDur?: number} = {}) => {
  const a = opts.anticip ?? 0.06;
  const ad = opts.antDur ?? 6;
  if (f < start) return -a * Easing.inOut(Easing.sin)(clamp01((f - (start - ad)) / ad));
  return lerp(-a, 1, spring({frame: slowInTime(f - start, curve.slowIn), fps, config: curve.config}));
};

/** Saída com antecipação: recua um pouco e acelera até 1 (back-in). */
export const leave = (f: number, start: number, dur: number) => ramp(f, start, dur, EASE.backIn);

/** Flutuação ociosa: nada fica 100% parado. */
export const float = (f: number, amp = 6, period = 70, phase = 0): Pt => ({
  x: Math.sin((f / period) * Math.PI * 2 + phase) * amp,
  y: Math.cos((f / (period * 1.3)) * Math.PI * 2 + phase * 1.7) * amp * 0.7,
});

/** Stretch ao longo da velocidade por quadro (máx. 1.6; até 2.2 em smears). */
export const velocityStretch = (pos: PosFn, f: number, k = 0.0045, max = 1.6) => {
  const a = pos(f - 1);
  const b = pos(f);
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const v = Math.hypot(dx, dy);
  return {stretch: Math.min(max, 1 + v * k), angle: v < 0.01 ? 0 : (Math.atan2(dy, dx) * 180) / Math.PI, dx, dy};
};

/**
 * Spline Catmull-Rom parametrizada por comprimento de arco (uma curva de easing para o caminho todo,
 * sem paradas nos pontos intermediários). Fora de 0–1 extrapola pela tangente: a antecipação recua
 * e o overshoot passa do ponto final SEGUINDO o caminho.
 */
export const spline = (pts: Pt[], u: number): Pt => {
  if (pts.length < 2) return pts[0];
  const seg = (i: number, t: number): Pt => {
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    const t2 = t * t;
    const t3 = t2 * t;
    const c = (a: number, b: number, cc: number, d: number) =>
      0.5 * (2 * b + (-a + cc) * t + (2 * a - 5 * b + 4 * cc - d) * t2 + (-a + 3 * b - 3 * cc + d) * t3);
    return {x: c(p0.x, p1.x, p2.x, p3.x), y: c(p0.y, p1.y, p2.y, p3.y)};
  };
  const N = 24;
  const samples: {p: Pt; l: number}[] = [];
  let total = 0;
  let prev = pts[0];
  for (let i = 0; i < pts.length - 1; i++) {
    for (let k = i === 0 ? 0 : 1; k <= N; k++) {
      const p = seg(i, k / N);
      total += Math.hypot(p.x - prev.x, p.y - prev.y);
      samples.push({p, l: total});
      prev = p;
    }
  }
  if (u < 0 || u > 1) {
    const [a, b] = u < 0 ? [samples[1].p, samples[0].p] : [samples[samples.length - 2].p, samples[samples.length - 1].p];
    const d = Math.hypot(b.x - a.x, b.y - a.y) || 1;
    const k = (u < 0 ? -u : u - 1) * total;
    return {x: b.x + ((b.x - a.x) / d) * k, y: b.y + ((b.y - a.y) / d) * k};
  }
  const target = u * total;
  for (let i = 1; i < samples.length; i++) {
    if (samples[i].l >= target) {
      const a = samples[i - 1];
      const b = samples[i];
      const r = (target - a.l) / Math.max(1e-6, b.l - a.l);
      return {x: lerp(a.p.x, b.p.x, r), y: lerp(a.p.y, b.p.y, r)};
    }
  }
  return samples[samples.length - 1].p;
};

/** Hermite com tangentes Catmull-Rom: valores-chave com velocidade contínua (câmera, sem para-e-anda). */
export const smoothKeys = (f: number, frames: number[], values: number[]) => {
  const n = frames.length;
  if (f <= frames[0]) return values[0];
  if (f >= frames[n - 1]) return values[n - 1];
  let i = 0;
  while (f > frames[i + 1]) i++;
  const tan = (k: number) => (k === 0 || k === n - 1 ? 0 : (values[k + 1] - values[k - 1]) / (frames[k + 1] - frames[k - 1]));
  const h = frames[i + 1] - frames[i];
  const s = (f - frames[i]) / h;
  const s2 = s * s;
  const s3 = s2 * s;
  return (2 * s3 - 3 * s2 + 1) * values[i] + (s3 - 2 * s2 + s) * h * tan(i) + (-2 * s3 + 3 * s2) * values[i + 1] + (s3 - s2) * h * tan(i + 1);
};
