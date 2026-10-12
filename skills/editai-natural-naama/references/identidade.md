# Identidade Editai · Naamã

Paleta fornecida: Cyber Black `#0A0A0A`, Neon Purple `#8A2BE2`, Electric Lime `#BFFF00`. Complementos provisórios: cinza `#28282D`, off-white `#F5F2EB`, ajustáveis. Preto/cinza formam a base. Roxo e limão aparecem só em detalhes pequenos (uma palavra destacada, um ✓, uma seta), nunca em fundos, painéis inteiros ou molduras. Não tingir a pele nem o vídeo original.

Legenda regular: Helvetica, peso regular, branco `#FFFFFF`, sem contorno, tracking −50/1000 em = `-.05em`. Padrão 48 px em 1080×1920, ajustável dentro de 44–54 px após olhar no celular. Uma palavra por vez, abaixo do queixo. Nunca diminuir a ponto de perder leitura.

**Palavra de destaque:** Scholar Italic, sempre com `<KeyWord>`: **gradiente da cor de destaque** (do tom claro, passando pela cor, até o tom escuro) recortado no texto + **glow leve** da mesma cor. Configurado em `highlight` no `editai.json`:
- Anúncios: gradiente limão `#EEFFA0 → #BFFF00 → #7FCC00`, glow `rgba(191,255,0,.40)` 16 px.
- Natural: gradiente branco `#FFFFFF → #F5F2EB → #D8CFBF`, glow `rgba(255,255,255,.35)` 14 px.
No máximo algumas palavras com importância semântica. O nome de arquivo Helvetica-Regular.otf contém a Helvetica Neue Roman fornecida pelo usuário; a outra fonte é Scholar-Italic.otf. Não substituir silenciosamente por fontes do sistema. Os arquivos são recursos fornecidos pelo usuário; verificar a permissão de redistribuição antes de distribuir o pacote aos alunos.

Cards e prints: bordas arredondadas de 26 px, imagem com proporção preservada e crop intencional. Sempre acima da cabeça, nunca sobre os olhos. Sombra discreta para separar do vídeo; em fundo claro, reforçar levemente.

Natural: legenda regular branca e destaque em gradiente branco com glow leve. Prints entram com curva calma (`lazy`), antecipação curta e overshoot leve, flutuam e saem recuando. Não usar diagramas densos.

Anúncios: legenda regular branca e destaque em gradiente limão com glow leve. Formas, SVG, ícones e imagens explicam a fala em vez de duplicar a legenda, ancorados nas palavras. Poucos elementos por vez: um esquema só quando ele explica algo que a fala diz. Glow só leve, na palavra de destaque; nada de neon em painéis. Mostrar benefício/processo/oferta sem inventar prova ou preço. Não impor abertura de cinco segundos: o gancho visual acompanha o roteiro real.

Todos os tamanhos são pontos de partida para a escala 1080×1920. Confira os extremos das animações (pico do overshoot, quadro do impacto), não somente o estado parado. A voz deve continuar sendo o foco.

## Regra das animações
Cada animação precisa ter um motivo: mostrar o que a pessoa está falando naquele momento e ajudar quem assiste a entender. Se for só enfeite, não entra. Na dúvida, menos.

## Motion profissional (vale para todo elemento e texto)
O padrão é o motion aprovado pelo Naamã — fluido, contínuo, com ritmo. Detalhes, curvas e código em [linguagem de motion](motion-remotion.md).
- **Curva própria por elemento** (`CURVE.lazy/smooth/snappy/bouncy/heavy/long`): nada se move em sincronia robótica.
- **Antecipação** antes de partir e **slow in** ao sair do repouso.
- **Overshoot com mola na entrada e na saída**: passa do alvo e assenta; ao sair recua e acelera (back-in) com blur.
- **Arcos** em tudo que viaja; **squash & stretch** e **exagero** nos impactos; **smears** + **motion blur** em movimentos rápidos.
- **Follow-through, overlapping e ação secundária**: partes atrasam 2–3 quadros; nada fica parado (flutuação ociosa).
- **Keyframes espaçados** (10–30 quadros, sobrepostos): se parecer acelerado, espaçe.
- **Sem jittery text.** **Zoom no rosto** em momentos de ênfase (punch-in com mola) e leve zoom in/out contínuo e discreto, dentro da moldura e centrado no rosto.
- **Rosto sempre centralizado:** a câmera acompanha o rosto (face tracking) de forma suave, sem saltos.
- **Modo leve:** em PC mais simples o build reduz as amostras de motion blur pela metade (`"modo_leve"` no `editai.json` força ligado/desligado).
