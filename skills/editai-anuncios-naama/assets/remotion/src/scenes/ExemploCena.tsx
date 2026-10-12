/**
 * EXEMPLO de cena (copie e renomeie). Cena = componente TSX em src/scenes/<Nome>.tsx citado em
 * assets/scenes.json ({"layout","start","end","component":"Nome"}). useCurrentFrame() é LOCAL (0 = início).
 *
 * Linguagem obrigatória: cada elemento com a SUA curva (CURVE), antecipação antes de partir,
 * mola ao chegar, flutuação ociosa, saída com recuo (back-in) e motion blur nos movimentos.
 */
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import type {SceneProps} from '../types';
import {CURVE} from '../motion/tokens';
import {Life} from '../motion/life';
import {Glass, Icon} from '../motion/ui';
import {KeyWord, popStyle, riseStyle} from '../motion/text';
import {WordScene} from '../motion/wordScene';

export const ExemploCena: React.FC<SceneProps> = ({durationInFrames, layout}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const end = durationInFrames;

  if (layout === 'motion') {
    // Tipografia cinética: blocos entram no quadro em que são ditos.
    return (
      <WordScene
        endAt={end}
        words={[
          {at: 0, icon: 'play', iconSize: 190},
          {at: Math.round(0.5 * fps), text: 'testei tudo isso', size: 150},
          {at: Math.round(1.6 * fps), text: 'errado', key: true, size: 290},
        ]}
      />
    );
  }

  // Painel de vidro (split): card entra com curva lazy; ícone com snappy; rótulo chega depois (overlapping).
  return (
    <>
      <Life f={f} inAt={2} outAt={end - 12} curve={CURVE.lazy} anticip={0.08} from={{y: 90, scale: 0.88, rot: -3}} style={{left: 0, top: 0, width: 960, height: 690}}>
        <Glass style={{inset: 0}} />
      </Life>
      <Life f={f} inAt={8} outAt={end - 14} curve={CURVE.snappy} from={{x: -80, scale: 0.6}} style={{left: 90, top: 180, width: 220, height: 220}}>
        <Icon name="clock" f={f} drawAt={10} size={220} />
      </Life>
      <div style={{position: 'absolute', left: 360, top: 230, fontSize: 96, color: '#F5F2EB', ...riseStyle(f, 14, end - 10, {curve: CURVE.smooth, dist: 40})}}>
        2 horas →
      </div>
      <div style={{position: 'absolute', left: 360, top: 350, fontSize: 130, ...popStyle(f, 26, end - 10)}}>
        <KeyWord>10 min</KeyWord>
      </div>
    </>
  );
};
