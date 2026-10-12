# Os 12 princípios da animação — como usar no Editai (Remotion)

Para **cada** animação (texto, elemento, transição), escolha o princípio principal que serve à fala daquele momento e
anote no plano (`"principio": "..."` em `scenes.json`/`beats.json`). Quase todo movimento bom combina vários — o pacote
padrão é: **arco + antecipação + slow in/out + follow-through + overlapping**, e nos impactos **squash & stretch + exagero**.
As funções citadas estão em `src/motion/` do projeto (ver [linguagem de motion](motion-remotion.md)).

| Princípio | Quando escolher | Como aplicar (Remotion, `src/motion`) |
|---|---|---|
| **Squash and Stretch** | Tudo que chega com peso ou bate em algo: gota, blob, chip, card, ponto | `squashAt(f, impacto, fps, big)` no impacto (1.3×0.75; `big` = 1.5×0.6) e `velocityStretch` esticando na direção do movimento (até 1.6×; 2.2× em smears) |
| **Anticipation** | Antes de TODA partida | `travel(..., {anticip: 0.06–0.18})`: recua ao longo do caminho antes de sair; spark recua e se comprime antes de investir |
| **Staging** | Mais de um elemento | Um foco por vez: os anteriores escurecem (`opacity .3`) e encolhem levemente |
| **Straight Ahead / Pose to Pose** | Pose to pose com beat sheet de quadros; straight ahead em contadores/barras | Defina as poses no `B = {...}` da cena e ligue com curvas |
| **Follow Through / Overlapping Action** | Grupos, textos com partes, card + rótulo | Partes chegam em tempos diferentes (2–3 quadros); o rótulo atrasa em relação ao card; molas com overshoot assentam depois de chegar |
| **Slow In and Slow Out** | Em todo movimento | Toda curva `CURVE.*` tem `slowIn` (sai do repouso devagar) e chegada com mola; saídas com `leave()` (back-in). Nunca linear (linear só em deriva ambiente) |
| **Arcs** | Tudo que viaja | `spline(pontos, travel(...))`: trajetória curva, um único easing do início ao fim, sem paradas nos pontos do meio |
| **Secondary Action** | Para dar vida sem roubar o foco | Halo que arrasta atrás do objeto, traços que saltam no impacto, `float()` ocioso, pulso de anel no pouso |
| **Timing** | Sempre | Espaçe os keyframes: movimentos de 10–30 quadros que se sobrepõem; cada elemento com a SUA curva (lazy, smooth, snappy, bouncy, heavy, long) |
| **Exaggeration** | Impactos e ideia principal | Antecipação maior, squash maior, smear 4× na investida, pop bouncy na palavra de destaque |
| **Solid Drawing** | Painéis, cards, vidro | Sombra coerente, vidro com borda clara em cima, profundidade com parallax |
| **Appeal** | Sempre | Poucos elementos, alinhamento limpo, curvas de mola suaves; tudo fluido e contínuo, um movimento vira o próximo |

**Regra:** o Claude decide pensando no que a fala precisa — peso (squash, heavy), surpresa (antecipação), clareza
(staging), fluidez (arcos, slow in/out, follow-through). Overshoot com mola na entrada **e** na saída é o padrão do Editai.
Nada de princípio só por enfeite: todo movimento ilustra a fala.
