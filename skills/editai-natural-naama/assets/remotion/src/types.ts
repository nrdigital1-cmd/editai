import type {Highlight} from './motion/text';

export type Layout = 'full' | 'split' | 'motion';
export type CaptionPart = {text: string; key: boolean};
export type Caption = {from: number; to: number; top: number; lines: CaptionPart[][]};
export type SceneEntry = {from: number; to: number; layout: Layout; component?: string};
export type Beat = {from: number; to: number; x: number; y: number; w: number; h: number; kind: 'image' | 'component'; src?: string; component?: string; label?: string};
export type Zoom = {from: number; to: number; scale: number; curve?: string};
export type Sfx = {from: number; type: 'whoosh' | 'pop' | 'tick'; volume: number; dur: number};

/** Gerado por `editai.py build` em src/data/edit.json — não editar à mão. */
export type EditData = {
  style: 'motion' | 'anuncios' | 'natural';
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  cameraSrc: string;
  voiceSrc: string;
  faceYPercent: number;
  palette: Record<string, string>;
  highlight: Highlight;
  captionSize: number;
  impactSize: number;
  trackingEm: number;
  lightBackground: boolean;
  blurScale: number;
  captions: Caption[];
  scenes: SceneEntry[];
  beats: Beat[];
  sfx: Sfx[];
  faceOrigin: {x: number; y: number}; // centro do rosto em % do quadro (origem do zoom)
  faceZoom: {base: number; breathing: boolean; breathingAmp: number; breathingPeriod: number};
  zooms: Zoom[]; // punches de ênfase (quadros)
  faceTrack: {x: number[]; y: number[]} | null; // centro do rosto por quadro (0–1), de `editai.py track`
  faceTracking: {targetX: number; targetY: number; maxZoom: number}; // onde manter o rosto (%) e zoom máximo
};

/** Props que toda cena/beat em TSX recebe. Use useCurrentFrame() (quadro LOCAL, 0 = início da cena). */
export type SceneProps = {durationInFrames: number; layout: Layout; palette: Record<string, string>};
