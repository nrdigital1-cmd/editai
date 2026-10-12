import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {smoothKeys} from './core';

/**
 * Câmera contínua para cenas SEM apresentador (motion graphics): uma única câmera atravessa as cenas
 * (sem reiniciar zoom a cada cena), com velocidade contínua entre as chaves e leve flutuação de mão.
 * Ex.: push lento → recua (antecipação) → avança junto com a transição → assenta.
 */
export type CameraKeys = {frames: number[]; scale: number[]; x: number[]; y: number[]};

export const cameraAt = (f: number, k: CameraKeys, handheld = 1) => ({
  scale: smoothKeys(f, k.frames, k.scale),
  x: smoothKeys(f, k.frames, k.x) + (Math.sin(f / 41) * 4 + Math.sin(f / 17) * 1.2) * handheld,
  y: smoothKeys(f, k.frames, k.y) + (Math.cos(f / 53) * 3 + Math.sin(f / 23) * 1) * handheld,
  rot: Math.sin(f / 61) * 0.25 * handheld,
});

/** Aplica a câmera (camada composta: escala sem tremer o texto). depth < 1 = parallax (fundo 0.3, meio 0.6). */
export const CameraRig: React.FC<{keys: CameraKeys; depth?: number; handheld?: number; children: React.ReactNode}> = ({keys, depth = 1, handheld = 1, children}) => {
  const f = useCurrentFrame();
  const c = cameraAt(f, keys, handheld);
  const s = 1 + (c.scale - 1) * depth;
  return (
    <AbsoluteFill style={{transform: `translate(${c.x * depth}px, ${c.y * depth}px) rotate(${c.rot * depth}deg) scale(${s}) translateZ(0)`, willChange: 'transform'}}>
      {children}
    </AbsoluteFill>
  );
};
