import React from 'react';
import {Audio, Video} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import {AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import data from './data/edit.json';
import type {Caption, EditData, Layout} from './types';
import {SCENES} from './scenes';
import {BEATS} from './beats';
import {BlurScale} from './motion/blur';
import {CURVE, EASE} from './motion/tokens';
import {ramp, travel} from './motion/core';
import {HighlightCtx, KeyWord} from './motion/text';
import {Reveal} from './motion/reveal';
import {leave} from './motion/core';
import {Life} from './motion/life';

loadFont({family: 'EditaiHelvetica', url: staticFile('fonts/Helvetica-Regular.otf'), weight: '400'});
loadFont({family: 'EditaiScholar', url: staticFile('fonts/Scholar-Italic.otf'), style: 'italic'});

const D = data as unknown as EditData;

/** Composições da câmera (corte seco). O zoom no rosto é aplicado DENTRO da moldura (faceZoomAt). */
const CAMERA: Record<Layout, React.CSSProperties> = {
  full: {left: 0, top: 0, width: 1080, height: 1920, borderRadius: 0, opacity: 1},
  split: {left: 60, top: 880, width: 960, height: 900, borderRadius: 36, opacity: 1},
  motion: {left: 0, top: 0, width: 1080, height: 1920, opacity: 0},
};

/**
 * Zoom no rosto: respiração contínua e discreta (zoom in/out lento) + punches de ênfase (zooms.json e
 * palavras de destaque) com antecipação (recua um pouco), mola na chegada e saída suave.
 * Base mínima > 1 para a antecipação nunca revelar a borda do vídeo.
 */
const faceZoomAt = (f: number, fps: number) => {
  const z = D.faceZoom;
  const period = Math.max(1, z.breathingPeriod);
  let s = z.base + (z.breathing ? z.breathingAmp * (0.5 - 0.5 * Math.cos((2 * Math.PI * f) / period)) : 0);
  for (const p of D.zooms) {
    if (f < p.from - 8 || f > p.to + 40) continue;
    const curve = CURVE[(p.curve ?? 'smooth') as keyof typeof CURVE] ?? CURVE.smooth;
    const inP = travel(f, p.from, fps, curve, {anticip: 0.12, antDur: 6});
    const outP = ramp(f, p.to, 18, EASE.camera);
    s *= 1 + (p.scale - 1) * inP * (1 - outP);
  }
  return Math.max(1, s);
};

/**
 * FACE TRACKING: a câmera acompanha o rosto e o mantém centralizado (x no centro, y na altura planejada).
 * Usa o zoom MÍNIMO para deslocar sem mostrar a borda do vídeo, somado ao zoom de ênfase/respiração.
 * O rastro vem suavizado do `editai.py track` (sem saltos, zona morta contra tremidinhas).
 */
const SRC_W = 1080;
const SRC_H = 1920;
const cameraAt = (f: number, fps: number, box: {w: number; h: number}, targetY: number) => {
  const zoom = faceZoomAt(f, fps);
  const k = Math.max(box.w / SRC_W, box.h / SRC_H); // cover
  const dw = SRC_W * k;
  const dh = SRC_H * k;
  const offX = (box.w - dw) * 0.5;
  const offY = (box.h - dh) * (D.faceYPercent / 100);
  const tr = D.faceTrack;
  const i = Math.max(0, Math.min((tr?.x.length ?? 1) - 1, Math.round(f)));
  const fx = offX + (tr && tr.x.length ? tr.x[i] : D.faceOrigin.x / 100) * dw;
  const fy = offY + (tr && tr.y.length ? tr.y[i] : D.faceOrigin.y / 100) * dh;
  const tx = box.w * (D.faceTracking.targetX / 100);
  const ty = box.h * targetY;
  // zoom mínimo para centralizar sem revelar bordas
  const need = Math.max(
    zoom,
    fx > 1 ? tx / fx : 1,
    box.w - fx > 1 ? (box.w - tx) / (box.w - fx) : 1,
    fy > 1 ? ty / fy : 1,
    box.h - fy > 1 ? (box.h - ty) / (box.h - fy) : 1,
  );
  const S = Math.min(Math.max(1, need), Math.max(zoom, D.faceTracking.maxZoom));
  const Tx = Math.min(0, Math.max(box.w - S * box.w, tx - S * fx));
  const Ty = Math.min(0, Math.max(box.h - S * box.h, ty - S * fy));
  return {S, Tx, Ty, fy, dw, dh, offY, i};
};
const trackedCamera = (f: number, fps: number, box: {w: number; h: number}, targetY: number) => {
  const c = cameraAt(f, fps, box, targetY);
  return `translate(${c.Tx}px, ${c.Ty}px) scale(${c.S}) translateZ(0)`;
};

/** Onde está o topo da cabeça NA TELA neste quadro (segue o rastreio e o zoom da câmera). */
const headTopOnScreen = (f: number, headTop: number) => {
  const c = cameraAt(f, D.fps, {w: 1080, h: 1920}, D.faceTracking.targetY / 100);
  const faceBase = c.offY + (D.faceOrigin.y / 100) * c.dh; // centro do rosto no enquadramento de referência
  const s = D.faceTrack?.s;
  const ref = D.faceTrack?.sRef ?? 0;
  // distância centro→topo da cabeça medida no vídeo (head_top), escalada pelo tamanho do rosto neste quadro
  const k = s && s.length && ref > 0 ? s[Math.min(s.length - 1, c.i)] / ref : 1;
  return c.Ty + c.S * (c.fy - (faceBase - headTop) * k);
};

const layoutAt = (frame: number): Layout => D.scenes.find((s) => frame >= s.from && frame < s.to)?.layout ?? 'full';

const MotionBackground: React.FC = () => {
  const p = D.palette;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(70% 45% at 12% 30%, ${p.orange ?? '#FF6D29'}8C, transparent 70%),
          radial-gradient(60% 40% at 95% 85%, ${p.brown ?? '#453027'}E6, transparent 70%),
          linear-gradient(180deg, #1d1513 0%, ${p.ink ?? '#161316'} 60%)`,
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage: 'linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px)',
          backgroundSize: '72px 72px',
          WebkitMaskImage: 'radial-gradient(85% 70% at 50% 45%, #000 40%, transparent 100%)',
        }}
      />
    </AbsoluteFill>
  );
};

const CaptionBlock: React.FC<{c: Caption; f: number}> = ({c, f}) => {
  // Cada palavra entra com Reveal (padrão maskY, limpo); a de impacto com posRotScale (overshoot de posição, giro e escala).
  // O bloco só cuida da saída: recua, acelera para cima e desfoca.
  const ex = Math.max(0, leave(f, c.to - 6, 6));
  const enter = {transform: `translateY(${-ex * 24}px)`, opacity: 1 - ex, filter: ex > 0.02 ? `blur(${ex * 6}px)` : undefined};
  let w = 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        width: 960,
        top: c.top,
        textAlign: 'center',
        color: '#fff',
        fontFamily: 'EditaiHelvetica, Helvetica, sans-serif',
        fontSize: D.captionSize,
        lineHeight: 1.05,
        letterSpacing: `${D.trackingEm}em`,
        textShadow: D.lightBackground ? '0 2px 10px rgba(0,0,0,.45)' : D.style === 'motion' ? '0 2px 10px rgba(0,0,0,.45)' : 'none',
        ...enter,
      }}
    >
      {c.lines.map((line, i) => (
        <div key={i}>
          {line.map((part, j) => {
            const at = c.from + w++ * 2; // palavras em cascata (2 quadros)
            return part.key ? (
              <Reveal
                key={j}
                text={part.text}
                f={f}
                at={at + 1}
                preset="posRotScale"
                unit="word"
                wrap={(n) => <KeyWord style={{fontSize: D.impactSize, lineHeight: 0.95}}>{n}</KeyWord>}
              />
            ) : (
              <React.Fragment key={j}>
                {j > 0 ? ' ' : ''}
                <Reveal text={part.text} f={f} at={at} preset={c.anim ?? 'maskY'} />
              </React.Fragment>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/**
 * TÍTULO DO GANCHO: nos primeiros segundos a pessoa está na tela e o título entra ACIMA DA CABEÇA,
 * palavra a palavra (maskY; impacto em posRotScale com gradiente). Sai recuando, subindo e desfocando no fim do gancho.
 */
const HookTitle: React.FC<{f: number}> = ({f}) => {
  const h = D.hook;
  if (!h || f > h.to + 12) return null;
  const ex = Math.max(0, leave(f, h.to - 8, 8));
  let w = 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        width: 960,
        // acompanha a cabeça quadro a quadro (zoom/rastreio), sempre 30 px acima dela
        // nunca acima da área segura (o título inteiro cabe abaixo de safeTop)
        bottom: D.height - Math.max(h.safeTop + h.height, Math.min(h.bottom, headTopOnScreen(f, h.bottom + 30) - 30)),
        textAlign: 'center',
        color: '#fff',
        fontFamily: 'EditaiHelvetica, Helvetica, sans-serif',
        fontSize: D.hookSize,
        lineHeight: 1.02,
        letterSpacing: `${D.trackingEm}em`,
        transform: `translateY(${-ex * 40}px)`,
        opacity: 1 - ex,
        filter: ex > 0.02 ? `blur(${ex * 8}px)` : undefined,
      }}
    >
      {h.lines.map((line, i) => (
        <div key={i}>
          {line.map((part, j) => {
            const at = h.from + 4 + w++ * 4; // entra logo depois do primeiro quadro, palavra a palavra
            return part.key ? (
              <Reveal
                key={j}
                text={part.text}
                f={f}
                at={at + 2}
                preset="posRotScale"
                unit="word"
                wrap={(n) => <KeyWord style={{fontSize: D.hookSize * 1.3, lineHeight: 0.95}}>{n}</KeyWord>}
              />
            ) : (
              <span key={j} style={{textShadow: '0 4px 18px rgba(0,0,0,.45)'}}>
                {j > 0 ? ' ' : ''}
                <Reveal text={part.text} f={f} at={at} preset="maskY" />
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export const Editai: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const lay = D.style === 'motion' ? layoutAt(f) : 'full';
  return (
    <BlurScale.Provider value={D.blurScale}>
      <HighlightCtx.Provider value={D.highlight}>
        <AbsoluteFill style={{backgroundColor: D.palette.ink ?? D.palette.black ?? '#0A0A0A', fontFamily: 'EditaiHelvetica, Helvetica, sans-serif', letterSpacing: `${D.trackingEm}em`, color: D.palette.off_white ?? '#F5F2EB'}}>
          {D.style === 'motion' ? <MotionBackground /> : null}

          {/* Câmera: moldura (corte seco) + zoom no rosto em camada composta (sem tremor) */}
          <div style={{position: 'absolute', overflow: 'hidden', ...CAMERA[lay]}}>
            <div
              style={{
                position: 'absolute',
                inset: 0,
                transform:
                  lay === 'split'
                    ? trackedCamera(f, fps, {w: 960, h: 900}, 0.45)
                    : trackedCamera(f, fps, {w: 1080, h: 1920}, D.faceTracking.targetY / 100),
                transformOrigin: '0 0',
                willChange: 'transform',
              }}
            >
              <Video src={staticFile(D.cameraSrc)} muted objectFit="cover" style={{width: '100%', height: '100%', objectPosition: `50% ${D.faceYPercent}%`}} />
            </div>
          </div>
          {lay === 'split'
            ? [0, 1, 2, 3].map((k) => (
                <div
                  key={k}
                  style={{
                    position: 'absolute',
                    width: 44,
                    height: 44,
                    border: '2px solid rgba(245,242,235,.85)',
                    left: k % 2 === 0 ? 58 : undefined,
                    right: k % 2 === 1 ? 58 : undefined,
                    top: k < 2 ? 878 : undefined,
                    bottom: k >= 2 ? 1920 - 1782 : undefined,
                    borderRight: k % 2 === 0 ? 0 : undefined,
                    borderLeft: k % 2 === 1 ? 0 : undefined,
                    borderBottom: k < 2 ? 0 : undefined,
                    borderTop: k >= 2 ? 0 : undefined,
                    borderTopLeftRadius: k === 0 ? 36 : 0,
                    borderTopRightRadius: k === 1 ? 36 : 0,
                    borderBottomLeftRadius: k === 2 ? 36 : 0,
                    borderBottomRightRadius: k === 3 ? 36 : 0,
                  }}
                />
              ))
            : null}
          <Audio src={staticFile(D.voiceSrc)} />

          {/* Cenas em TSX (skill motion): cada uma numa Sequence com o quadro local começando em 0 */}
          {D.scenes.map((s, i) => {
            const Comp = s.component ? SCENES[s.component] : undefined;
            if (!Comp) return null;
            const box: React.CSSProperties = s.layout === 'split' ? {left: 60, top: 150, width: 960, height: 690} : {left: 0, top: 0, width: 1080, height: 1920};
            return (
              <Sequence key={i} name={s.component} from={s.from} durationInFrames={s.to - s.from} layout="none">
                <div style={{position: 'absolute', ...box}}>
                  <Comp durationInFrames={s.to - s.from} layout={s.layout} palette={D.palette} />
                </div>
              </Sequence>
            );
          })}

          {/* Beats (anúncios/natural): prints acima da cabeça ou componentes TSX */}
          {D.beats.map((b, i) => {
            if (f < b.from - 8 || f > b.to + 2) return null;
            const Comp = b.component ? BEATS[b.component] : undefined;
            return (
              <Life
                key={i}
                f={f}
                inAt={b.from}
                outAt={b.to - 10}
                curve={CURVE.lazy}
                anticip={0.05}
                from={{y: 70, scale: 0.9, rot: -2}}
                to={{y: -70, scale: 1.04}}
                floatAmp={4}
                phase={i}
                style={{left: b.x, top: b.y, width: b.w, height: b.h}}
              >
                {b.kind === 'image' && b.src ? (
                  <Img src={staticFile(b.src)} alt={b.label ?? ''} style={{width: '100%', height: '100%', objectFit: 'contain', borderRadius: 26, boxShadow: '0 3px 14px rgba(0,0,0,.18)'}} />
                ) : Comp ? (
                  <Sequence from={b.from} layout="none">
                    <Comp durationInFrames={b.to - b.from} layout="full" palette={D.palette} />
                  </Sequence>
                ) : null}
              </Life>
            );
          })}

          <HookTitle f={f} />

          {D.captions.map((c, i) => (f >= c.from - 4 && f < c.to + 2 ? <CaptionBlock key={i} c={c} f={f} /> : null))}

          {D.sfx.map((s, i) => (
            <Sequence key={`sfx-${i}`} name={`sfx ${s.type}`} from={s.from} durationInFrames={s.dur} layout="none">
              <Audio src={staticFile(`sfx/${s.type}.wav`)} volume={s.volume} />
            </Sequence>
          ))}
        </AbsoluteFill>
      </HighlightCtx.Provider>
    </BlurScale.Provider>
  );
};
