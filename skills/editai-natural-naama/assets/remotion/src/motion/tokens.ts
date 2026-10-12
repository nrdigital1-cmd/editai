import {Easing} from 'remotion';

/**
 * Motion tokens — Editai. Every duration/easing/curve comes from here.
 * Linguagem: tudo fluido e contínuo; antecipação antes de partir, mola (overshoot) ao chegar e ao sair,
 * slow-in ao sair do repouso, cada elemento com a SUA curva de velocidade.
 */
export const FPS = 30;

export const EASE = {
  arrive: Easing.bezier(0.16, 1, 0.3, 1), // expo-out: chegadas
  glide: Easing.bezier(0.22, 0.61, 0.36, 1), // deslizes, fades
  camera: Easing.bezier(0.65, 0, 0.35, 1), // in-out de câmera
  exit: Easing.bezier(0.7, 0, 0.84, 0), // saídas aceleradas
  lens: Easing.bezier(0.83, 0, 0.17, 1),
  drift: Easing.linear, // só deriva ambiente
  backIn: Easing.back(1.5), // saída com antecipação: recua e acelera
  backInOut: Easing.inOut(Easing.back(1.2)),
  fall: Easing.bezier(0.55, 0, 1, 0.45), // gravidade
  whip: Easing.bezier(0.9, 0, 0.1, 1), // chicote (momentos de smear)
};

/**
 * CURVE — "personalidades" de velocidade (speed graph). Cada elemento usa uma diferente
 * para nada se mover em sincronia robótica. slowIn = quadros de aceleração suave saindo do repouso.
 * Tempos medidos (30 fps): cruza o alvo / pico do overshoot / assenta.
 */
export const CURVE = {
  lazy: {config: {stiffness: 55, damping: 10, mass: 1.2}, slowIn: 6}, // 13f / +8.6% @18f / 27f — flutuante
  smooth: {config: {stiffness: 75, damping: 14, mass: 1}, slowIn: 5}, // 15f / +1.3% / 21f — deslize calmo
  snappy: {config: {stiffness: 150, damping: 14, mass: 0.8}, slowIn: 2}, // 7f / +7.4% / 14f — rápido e preciso
  bouncy: {config: {stiffness: 100, damping: 8, mass: 1}, slowIn: 3}, // 7f / +25% / 33f — brincalhão
  heavy: {config: {stiffness: 65, damping: 15, mass: 1.6}, slowIn: 8}, // 17f / +3.3% / 31f — carrega peso
  long: {config: {stiffness: 30, damping: 9, mass: 1.3}, slowIn: 8}, // 22f / +3.8% / 41f — travessia longa
};
export type Curve = (typeof CURVE)[keyof typeof CURVE];

export const SPRING = {
  blob: {stiffness: 140, damping: 11, mass: 0.9}, // squash de impacto
  pop: {stiffness: 220, damping: 15, mass: 0.6},
  rise: {stiffness: 110, damping: 12, mass: 0.9}, // legenda subindo
};

export const SQUASH = {x: 1.3, y: 0.75};
export const SQUASH_BIG = {x: 1.5, y: 0.6}; // exagero em impactos principais

export const STAGGER = {glyph: 1, word: 7, line: 8, card: 4, item: 2, badge: 5};
