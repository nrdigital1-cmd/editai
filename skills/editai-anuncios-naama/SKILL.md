---
name: editai-anuncios-naama
description: Editar vídeo vertical de vendas em Remotion com legendas, destaques pontuais em gradiente verde limão com glow leve e ilustrações que explicam a fala na identidade Editai de Naamã, com motion fluido (antecipação, overshoot de mola, arcos, motion blur). Use para anúncios, oferta, produto ou criativo publicitário; para conteúdo orgânico discreto use editai-natural-naama.
---

# Editai — Anúncios e Criativos · Naamã

Crie um vídeo vertical final em MP4 (renderizado em **Remotion**) com até 120 segundos por padrão, mantendo a identidade do aluno e a identidade gráfica Editai. Esta skill funciona com ferramentas locais de Claude e Codex; não presuma acesso ao terminal em todas as interfaces.

Antes de executar, leia [fluxo local](references/fluxo.md) (perfil, dependências, cortes, transcrição, build, preview, exportação), [identidade visual](references/identidade.md), [linguagem de motion](references/motion-remotion.md) e [princípios](references/principios.md). Use o preset **anuncios** em `init --style anuncios`.

## Escolha visual
Ilustre mecanismos e benefícios com formas, SVG, ícones, imagens e comparações curtas acima da cabeça (`beats.json`: imagens ou componentes TSX). Cards arredondados. Poucas animações, cada uma explicando o que está sendo dito, todas no motion fluido do Editai. Legenda branca sem contorno; palavras de impacto em Scholar Italic com **gradiente verde limão + glow leve** (`<KeyWord>`), bem maiores. Produto, oferta, preço e CTA vêm do usuário: não use dados demonstrativos como fatos.

## Critérios de entrega
- **Antes de gerar CADA vídeo (obrigatório, primeiro passo):** pergunte ao usuário se mantém a identidade visual do Editai — elementos, cores e fontes — ou se ele prefere usar a da marca dele e vai enviar as fontes, os elementos (logo, ícones, grafismos) e as cores. Não gere nada antes da resposta (se já houver escolha salva no `perfil.json`, mostre-a e confirme). Nome e @ só quando uma cena for mostrar o perfil.
- Remover pausas, respiros audíveis e retomadas sem perder palavras; manter a última versão de falas regravadas.
- Whisper local: transcrição rápida para planejar e nova transcrição do corte final. Escutar emendas; o texto sozinho não valida o corte.
- Helvetica regular com tracking −0,05 em; Scholar Italic nos destaques. Legendas um pouco abaixo do queixo, elementos acima da cabeça, rosto livre.
- Conferir quadros (`editai.py still`) de todas as trocas; avisar antes das etapas demoradas; não repetir processamento sem necessidade.
- **Preview = Remotion Studio** aberto no painel do navegador da conversa — nunca o MP4. **MP4 final só após aprovação** (`editai.py render PROJETO --aprovado`).
- Entregar caminho, cortes feitos, fontes e pendências. Publicação não faz parte da edição.

## Regra das animações
Cada animação precisa ter um motivo: mostrar o que a pessoa está falando naquele momento e ajudar quem assiste a entender. Se for só enfeite, não entra. Na dúvida, menos. Roxo e limão só em detalhes pequenos, como uma palavra destacada; glow só leve, na palavra de destaque.
- **Motion fluido e contínuo (padrão aprovado):** cada elemento com a sua curva de velocidade; antecipação antes de partir; slow in; overshoot com mola na entrada e na saída; arcos; squash & stretch e exagero nos impactos; smears e motion blur nos movimentos rápidos; follow-through e overlapping; ação secundária; nada parado, nada sumindo seco. Ver [linguagem de motion](references/motion-remotion.md).
- **Ênfase na legenda:** a palavra de impacto é SEMPRE bem maior (≈2× a legenda), em gradiente limão com glow leve. Fica na linha de BAIXO quando continua a frase ("frase anterior / *impacto*"); EM CIMA quando a frase começa nela ("*impacto* / frase anterior"). Entra com pop de mola (antecipação + overshoot).
- **Legenda corrida:** cada palavra entra subindo com mola (~18 px, overshoot leve) e sai recuando com blur, encadeada com a próxima.
- **Zoom no rosto:** em alguns momentos dê **zoom no rosto** de quem fala para enfatizar uma palavra ou uma animação (punch-in com antecipação e mola; automático nas palavras de destaque, com intervalo mínimo de 3 s, e manual em `assets/zooms.json`), e mantenha um **leve zoom in/zoom out contínuo e discreto** (respiração de ~2,5% a cada ~7 s). O zoom acontece dentro da moldura, centrado no rosto, em camada composta (sem tremor). Ajuste em `face_zoom` do `editai.json`. **Sem jittery text.**
- **Rosto sempre centralizado (face tracking):** a câmera acompanha o movimento do rosto e o mantém no centro da tela (horizontal) e estável na altura natural em que a pessoa foi filmada, como um operador de câmera: segue os movimentos reais, ignora tremidinhas, sem saltos. O rastreamento é local (OpenCV) e roda sozinho no `cut`; refaça com `editai.py track`. O zoom usado para deslocar é o mínimo necessário (até `max_zoom` 1.25) e soma com o zoom de ênfase e a respiração. Ajustes em `face_track` do `editai.json`.
- **Cor (suave, natural):** toda edição corrige balanço de branco (delicado, preserva o calor da pele), abre os meios-tons e as sombras sem esmagar o preto nem estourar as altas luzes, com **pouco contraste** e saturação natural (automático no `cut`; `editai.py grade` refaz; `"grade": false` desliga; ajustes em `"grade": {"wb_strength", "saturation", "contrast", "vibrance"}`). Nunca deixe o vídeo mais contrastado que o original. Confira o rosto: pele natural e quente, sombras com detalhe.
- **Efeitos sonoros:** **whoosh só em transições de tela e em elementos grandes se movendo** (o build só põe whoosh em beats grandes — área ≥ 300 mil px² — ou com `"whoosh": true`); pop nas palavras de impacto; volume baixo e confortável sob a voz (automático no build; `"sfx": false` desliga, `"sfx_volume"` ajusta). Nada de whoosh em ícones, legendas ou elementos pequenos.
- **12 princípios da animação:** para cada animação, escolha o principal que serve à fala e anote no plano (ver [princípios](references/principios.md)).
