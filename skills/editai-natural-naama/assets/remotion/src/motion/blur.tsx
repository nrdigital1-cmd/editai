import React, {createContext, useContext} from 'react';

/** Escala global do motion blur (modo leve = 0.5 → metade das amostras). */
export const BlurScale = createContext(1);

/**
 * Motion blur por amostragem de sub-quadros: desenha a camada em `samples` instantes dentro do
 * obturador e faz a média (camada k com opacidade 1/k). Funciona no preview do Studio e no render.
 * - blur suave: samples 8–18, shutter 0.5–1
 * - smear "multiples" (estilo cartoon): samples 3–4, shutter 2–2.5
 * `children` precisa ser função pura do quadro (fracionário).
 */
export const MotionBlur: React.FC<{
  f: number;
  children: (ff: number) => React.ReactNode;
  samples?: number;
  shutter?: number;
  active?: boolean;
}> = ({f, children, samples = 8, shutter = 0.75, active = true}) => {
  const scale = useContext(BlurScale);
  const n = Math.max(2, Math.round(samples * scale));
  if (!active) return <>{children(f)}</>;
  const layers: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const ff = f - shutter * (1 - i / (n - 1));
    layers.push(
      <div key={i} style={{position: 'absolute', inset: 0, opacity: 1 / (i + 1)}}>
        {children(ff)}
      </div>,
    );
  }
  return <>{layers}</>;
};
