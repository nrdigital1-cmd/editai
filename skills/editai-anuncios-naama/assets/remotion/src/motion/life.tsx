import React from 'react';
import {useVideoConfig} from 'remotion';
import {CURVE, type Curve} from './tokens';
import {clamp01, float, leave, lerp, travel} from './core';
import {MotionBlur} from './blur';

export type LifeOpts = {
  inAt: number; // quadro de entrada (local da cena)
  outAt?: number; // quadro em que a saída COMEÇA
  curve?: Curve; // personalidade de velocidade da entrada
  anticip?: number; // recuo antes de partir (0.04–0.18)
  from?: {x?: number; y?: number; scale?: number; rot?: number}; // de onde vem
  to?: {x?: number; y?: number; scale?: number; rot?: number}; // para onde vai ao sair
  outDur?: number; // quadros da saída (back-in)
  floatAmp?: number; // flutuação ociosa depois de chegar (px)
  phase?: number;
};

/** Estado de vida de um elemento: entrada (antecipação + mola) → flutua → saída (recua e acelera). */
export const lifeAt = (f: number, fps: number, o: LifeOpts) => {
  const curve = o.curve ?? CURVE.snappy;
  const p = travel(f, o.inAt, fps, curve, {anticip: o.anticip ?? 0.06});
  const out = o.outAt === undefined ? 0 : leave(f, o.outAt, o.outDur ?? 10);
  const fr = o.from ?? {y: 60, scale: 0.92};
  const to = o.to ?? {y: -60, scale: 1.04};
  const idle = float(f, o.floatAmp ?? 5, 80, o.phase ?? 0);
  const settled = clamp01((f - o.inAt) / 20);
  return {
    x: lerp(fr.x ?? 0, 0, p) + (to.x ?? 0) * out + idle.x * settled,
    y: lerp(fr.y ?? 0, 0, p) + (to.y ?? 0) * out + idle.y * settled,
    scale: lerp(fr.scale ?? 1, 1, p) * lerp(1, to.scale ?? 1, clamp01(out)),
    rot: lerp(fr.rot ?? 0, 0, p) + (to.rot ?? 0) * out,
    opacity: clamp01(p * 2.5) * (1 - clamp01(out)),
    moving: f >= o.inAt - 6 && f < o.inAt + 14 ? true : o.outAt !== undefined && f >= o.outAt - 2 && f < o.outAt + (o.outDur ?? 10) + 1,
  };
};

/**
 * <Life>: envolve qualquer elemento com entrada/flutuação/saída e motion blur automático
 * durante os movimentos. `style` posiciona o elemento (left/top/width/height).
 */
export const Life: React.FC<LifeOpts & {f: number; style?: React.CSSProperties; children: React.ReactNode; blurSamples?: number}> = ({
  f,
  style,
  children,
  blurSamples = 7,
  ...o
}) => {
  const {fps} = useVideoConfig();
  const now = lifeAt(f, fps, o);
  return (
    <MotionBlur f={f} active={now.moving} samples={blurSamples} shutter={0.9}>
      {(ff) => {
        const s = lifeAt(ff, fps, o);
        return (
          <div
            style={{
              position: 'absolute',
              ...style,
              opacity: s.opacity * ((style?.opacity as number | undefined) ?? 1),
              transform: `translate(${s.x}px, ${s.y}px) rotate(${s.rot}deg) scale(${s.scale})`,
            }}
          >
            {children}
          </div>
        );
      }}
    </MotionBlur>
  );
};
