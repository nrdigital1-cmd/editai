---
name: editai-motion-naama
description: Editar vídeo vertical no estilo motion do Editai de Naamã — cortes secos, uma cena nova a cada 3 a 6 segundos, três composições (tela dividida com painel de vidro em cima, apresentador em tela cheia com legenda de 2 a 3 palavras no peito, e cena de motion em tela cheia sem o apresentador, com tipografia cinética, liquid, glitch ou texto 3D), fundo em gradiente com grade fina e painéis de vidro na paleta laranja, marrom e preto. Use quando o usuário pedir estilo motion, vídeo com animações que explicam, tipografia cinética, ou /editai-motion-naama.
---

# Editai — Motion · Naamã

Vídeo vertical 1080×1920 em que **cada animação mostra o que está sendo dito**. Antes de executar, leia
[fluxo local](references/fluxo.md) (perfil, corte, transcrição, validação) e
[guia de motion](references/motion.md) (composições, cenas, curvas, keyframes). Use `init --style motion`.

## As três composições (troca sempre com corte seco)

| Composição | Quando | Como |
|---|---|---|
| `split` — tela dividida | A fala explica algo que dá para mostrar: um processo, um antes e depois, um número | Painel de vidro na faixa de cima (y 150–850); apresentador num card com cantoneiras embaixo |
| `full` — tela cheia | Fala pessoal, opinião, confissão, ponte entre ideias | Apresentador ocupando a tela; legenda no peito |
| `motion` — sem apresentador | A ideia-chave do vídeo, o gancho visual, uma frase que precisa de impacto | Só fundo + tipografia cinética, liquid, glitch, texto 3D ou elementos animados. A voz continua |

## Regras
- **Ritmo:** uma cena nova a cada 3–6 s. Alterne composições; nunca duas `motion` seguidas; `motion` dura 1,5–4 s.
- **Cada animação tem um motivo:** ilustrar a frase daquele momento para quem assiste entender. Enfeite não entra.
- **Legenda:** 2–3 palavras por vez no peito, Helvetica branca; palavra-chave em laranja Scholar Italic (`emphasis.json`, ~1 por frase). Sem legenda nas cenas `motion` (o texto animado é a fala) nem no `split` (o queixo cai sob a interface do Reels; o painel explica a fala).
- **Visual:** fundo sempre em gradiente com grade fina. Formas de preferência em **vidro** (`.glass`), senão gradiente. Paleta: laranja `#FF6D29`, marrom `#453027`, preto `#161316`, off-white `#F5F2EB`. Sem glow, sem neon, sem brilho.
- **Movimento fluido:** entradas com ease-out, saídas com ease-in, nada linear; detalhes no guia de motion.
- Nunca inventar números, prints ou resultados; números nos painéis vêm da fala ou do usuário.
- Remover pausas, gagueiras e frases repetidas, mantendo a última versão; ≤ 120 s por padrão.
- Conferir snapshots de todas as trocas de cena antes de exportar. Entregar caminho do MP4, cortes feitos e pendências.
