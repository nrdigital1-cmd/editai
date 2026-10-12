import React from 'react';
import {Composition} from 'remotion';
import {Editai} from './Editai';
import data from './data/edit.json';

// Um único vídeo: "Editai". Duração, fps e tamanho vêm do edit.json gerado por `editai.py build`.
export const RemotionRoot: React.FC = () => (
  <Composition
    id="Editai"
    component={Editai}
    durationInFrames={Math.max(1, data.durationInFrames)}
    fps={data.fps}
    width={data.width}
    height={data.height}
  />
);
