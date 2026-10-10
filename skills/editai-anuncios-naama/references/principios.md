# Os 12 princípios da animação — como usar no Editai

Para **cada** animação (texto, elemento, transição), escolha o princípio que mais ajuda a fala daquele momento e
anote no plano (`"principio": "..."` em `beats.json`/`scenes.json`). Uma animação pode combinar dois, mas sempre com um principal.

| Princípio | Quando escolher | Como aplicar (GSAP) |
|---|---|---|
| **Squash and Stretch** (comprimir e esticar) | Algo que "chega" com peso: um número, um ✓, um chip | Ao parar: `scaleY .92 / scaleX 1.06` e volta a 1 em 0,18 s (`power2.out`) |
| **Anticipation** (antecipação) | Antes de uma revelação ou número grande | Recua um pouco (`scale .96` ou `y +8`) por 0,12 s antes do movimento principal |
| **Staging** (encenação) | Sempre que houver mais de um elemento | Só um foco por vez: o resto escurece (`opacity .4`) ou espera para entrar |
| **Straight Ahead / Pose to Pose** | Pose to pose em quase tudo (keyframes claros); straight ahead em contadores e barras que "crescem" | Defina poses-chave (início, pico, repouso) e deixe o easing ligar |
| **Follow Through / Overlapping Action** | Grupos e textos com várias partes | Partes param em tempos diferentes: `stagger` 0,04–0,1 s; o rótulo chega depois do card |
| **Slow In and Slow Out** (desacelerar e acelerar) | Em todo movimento | `power2/3.inOut` em deslocamentos, `expo.out` em entradas, `power2.in` em saídas. Nunca linear |
| **Arcs** (arcos) | Elementos que viajam pela tela | Anime `x` e `y` com eases diferentes (ex.: `x power2.inOut`, `y power3.out`) para a trajetória curvar |
| **Secondary Action** (ação secundária) | Para dar vida sem roubar o foco | Deriva lenta, leve rotação de 1–2°, sombra que acompanha |
| **Timing** | Sempre — define o peso | Leve e rápido 0,25–0,4 s; importante e pesado 0,5–0,8 s; segura o texto ≥ 0,8 s |
| **Exaggeration** (exagero) | Só na palavra/ideia principal do vídeo | Escala maior (1,15→1), deslocamento maior; no resto, sutil |
| **Solid Drawing** (volume) | Painéis e cards | Sombra coerente com a luz, vidro com borda clara em cima, profundidade com parallax |
| **Appeal** (carisma) | Sempre — o resultado tem que ser elegante | Poucos elementos, alinhamento limpo, curvas suaves, estilo Apple: nada exagerado fora da exceção acima |

**Regra:** o Claude decide o princípio pensando no que a fala precisa — peso (squash), surpresa (anticipation),
clareza (staging), fluidez (slow in/out, arcs, follow through). Nunca aplique um princípio só por enfeite.
