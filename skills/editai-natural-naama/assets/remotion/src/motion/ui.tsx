import React, {useContext} from 'react';
import {EASE} from './tokens';
import {ramp} from './core';
import {HighlightCtx} from './text';

/** Biblioteca de ícones de traço (viewBox 24). Classe "a" = traço na cor de destaque. */
export const ICONS: Record<string, string> = {
  clock: '<circle cx="12" cy="12" r="9"/><path class="a" d="M12 12V6.5"/><path d="M12 12l3.5 2"/>',
  bolt: '<path class="a" d="M13 2L4.5 13.5H11L10 22l8.5-11.5H12z"/>',
  spark: '<path class="a" d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 2.5v4M17 4.5h4M5 16.5v3M3.5 18h3"/>',
  video: '<rect x="2.5" y="6" width="13.5" height="12" rx="3"/><path d="M16 10.5l5.5-3v9l-5.5-3"/><circle class="a" cx="6.5" cy="10" r="1"/>',
  rec: '<circle cx="12" cy="12" r="9"/><circle class="a" cx="12" cy="12" r="4"/>',
  play: '<circle cx="12" cy="12" r="9"/><path class="a" d="M10 8.5v7l6-3.5z"/>',
  x: '<circle cx="12" cy="12" r="9"/><path class="a" d="M9 9l6 6M15 9l-6 6"/>',
  pause: '<circle cx="12" cy="12" r="9"/><path class="a" d="M10 9v6M14 9v6"/>',
  stutter: '<path d="M4 4.5h16v11.5H9.5L4 20.5z"/><path class="a" d="M7.5 10.5c.8-1.6 1.6 1.6 2.4 0s1.6 1.6 2.4 0 1.6 1.6 2.4 0 1.6 1.6 1.8.6"/>',
  script: '<path d="M6 2.5h9l4 4v15H6z"/><path d="M15 2.5v4h4"/><path class="a" d="M9 11h7M9 14.5h7M9 18h4.5"/>',
  send: '<path d="M21.5 2.5L10.5 13.5"/><path class="a" d="M21.5 2.5l-7 19-4-8-8-4z"/>',
  cc: '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path class="a" d="M10.5 10a2.2 2.2 0 1 0 0 4M17 10a2.2 2.2 0 1 0 0 4"/>',
  shapes: '<circle cx="7" cy="7" r="3.8"/><rect class="a" x="13.2" y="13.2" width="7.6" height="7.6" rx="1.8"/><path d="M17 2.8l3.8 6.4h-7.6z"/><path class="a" d="M3.5 14.5l6 6"/>',
  eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle class="a" cx="12" cy="12" r="3"/>',
  warn: '<path d="M12 3l9.5 17h-19z"/><path class="a" d="M12 9.5v4.5M12 17.2v.1"/>',
  chat: '<path d="M3.5 4h17v12H8.5l-5 4.5z"/><path class="a" d="M7.5 9h9M7.5 12h6"/>',
  box: '<path d="M3 7.5l9-4.5 9 4.5v9.5L12 21.5 3 17z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9.5"/>',
  question: '<circle cx="12" cy="12" r="9"/><path class="a" d="M9.5 9.5a2.5 2.5 0 1 1 3.4 2.3c-.6.3-.9.8-.9 1.5v.6M12 16.8v.1"/>',
  sliders: '<path d="M4 7h16M4 12h16M4 17h16"/><circle class="a" cx="9" cy="7" r="2"/><circle class="a" cx="15" cy="12" r="2"/><circle class="a" cx="7" cy="17" r="2"/>',
  hourglass: '<path d="M6.5 2.5h11M6.5 21.5h11"/><path d="M7.5 2.5v2.5a4.5 4.5 0 0 0 4.5 4.5 4.5 4.5 0 0 0 4.5-4.5V2.5M7.5 21.5V19a4.5 4.5 0 0 1 4.5-4.5 4.5 4.5 0 0 1 4.5 4.5v2.5"/><path class="a" d="M10 19.5h4"/>',
  cap: '<path d="M2 9.5l10-5 10 5-10 5z"/><path d="M6 11.5v5c3.2 2.6 8.8 2.6 12 0v-5"/><path class="a" d="M22 9.5v5.5"/>',
  scissors: '<circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path class="a" d="M8.2 15.8L19 3.5M15.8 15.8L5 3.5"/>',
  check: '<circle cx="12" cy="12" r="9"/><path class="a" d="M8 12.5l2.8 2.8L16.5 9.5"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle class="a" cx="12" cy="12" r="1.5"/>',
  copy: '<rect class="a" x="8.5" y="8.5" width="12" height="12" rx="2.5"/><path d="M15.5 8.5V5a1.5 1.5 0 0 0-1.5-1.5H5A1.5 1.5 0 0 0 3.5 5v9A1.5 1.5 0 0 0 5 15.5h3.5"/>',
  list: '<path d="M9.5 6h11M9.5 12h11M9.5 18h11"/><path class="a" d="M3.5 6l1.2 1.2L7 4.8M3.5 12l1.2 1.2L7 10.8M3.5 18l1.2 1.2L7 16.8"/>',
  book: '<path d="M4 19.5V5a2 2 0 0 1 2-2h14v15H6a2 2 0 0 0-2 2 2 2 0 0 0 2 2h14"/><path class="a" d="M9 8h6M9 11h4"/>',
  userplus: '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3.1-6.5 7-6.5s7 2.5 7 6.5"/><path class="a" d="M19 8v6M16 11h6"/>',
  link: '<path d="M10 14a4.2 4.2 0 0 0 6 0l3-3a4.2 4.2 0 0 0-6-6l-1 1"/><path class="a" d="M14 10a4.2 4.2 0 0 0-6 0l-3 3a4.2 4.2 0 0 0 6 6l1-1"/>',
  arrowr: '<path class="a" d="M3 12h17M14 6l6 6-6 6"/>',
  down: '<path class="a" d="M12 3.5v16M6 13.5l6 6 6-6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path class="a" d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
  wave: '<path d="M3 12h2M7 8v8M11 5v14M15 9v6M19 7v10"/>',
  folder: '<path d="M3 6.5A1.5 1.5 0 0 1 4.5 5h5l2 2.5h8A1.5 1.5 0 0 1 21 9v9.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/><path class="a" d="M12 10.5v6M9 13.5h6"/>',
};

/** Ícone que se desenha (traço) a partir de `drawAt` (quadro local), em `dur` quadros. */
export const Icon: React.FC<{name: string; f: number; drawAt: number; dur?: number; size?: number; color?: string; style?: React.CSSProperties}> = ({
  name,
  f,
  drawAt,
  dur = 18,
  size = 120,
  color = '#F5F2EB',
  style,
}) => {
  const h = useContext(HighlightCtx);
  const parts = (ICONS[name] ?? '').match(/<(path|circle|rect)[^>]*\/>/g) ?? [];
  const svg = parts
    .map((tag, i) => {
      const p = ramp(f, drawAt + i * 2, dur, EASE.camera);
      const accent = tag.includes('class="a"');
      return tag.replace(
        /\/>$/,
        ` pathLength="1" fill="none" stroke="${accent ? h.via : color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1 1" stroke-dashoffset="${1 - p}" opacity="${p > 0 ? 1 : 0}"/>`,
      );
    })
    .join('');
  return <svg viewBox="0 0 24 24" width={size} height={size} style={{overflow: 'visible', ...style}} dangerouslySetInnerHTML={{__html: svg}} />;
};

/** Painel de vidro (fundo translúcido, borda clara em cima, sombra). */
export const Glass: React.FC<{style?: React.CSSProperties; children?: React.ReactNode; pill?: boolean}> = ({style, children, pill}) => (
  <div
    style={{
      position: 'absolute',
      borderRadius: pill ? 999 : 32,
      background: 'linear-gradient(140deg, rgba(255,255,255,.14), rgba(255,255,255,.03) 55%, rgba(255,255,255,.05))',
      border: '1px solid rgba(255,255,255,.18)',
      backdropFilter: 'blur(26px) saturate(140%)',
      boxShadow: 'inset 0 1px 0 rgba(255,255,255,.28), 0 24px 60px rgba(0,0,0,.35)',
      ...style,
    }}
  >
    {children}
  </div>
);
