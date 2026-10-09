---
name: editai-natural-naama
description: Editar vídeo vertical orgânico com legendas discretas, palavras de impacto e prints arredondados animados na identidade Editai de Naamã. Use para conteúdo natural, cotidiano ou educativo; para criativos de vendas use editai-anuncios-naama.
---

# Editai — Reels Naturais · Naamã

Crie um vídeo vertical final em MP4 com até 120 segundos por padrão, mantendo a identidade do aluno e a identidade gráfica Editai. Esta skill funciona com ferramentas locais de Claude e Codex; não presuma acesso ao terminal em todas as interfaces.

Antes de executar, leia [fluxo local](references/fluxo.md) para perfil, dependências, cortes, transcrição, composição e validação, e [identidade visual](references/identidade.md) para tipografia, paleta e motion. Use o preset **natural** em `init --style natural`.

## Escolha visual
Use prints e imagens reais acima da cabeça com bordas arredondadas e motion discreto. Legenda branca sem contorno. Palavras de impacto também brancas, em Scholar Italic, um pouco maiores, entrando de cima para baixo com movimento curto, suave e rápido. O estilo deve continuar natural, sem diagramas densos nem glow constante.

## Critérios de entrega
- Perfil salvo uma vez em `perfil.json`; nunca inventar números, logos, prints ou resultados.
- Remover pausas, respiros audíveis e retomadas sem perder palavras; manter a última versão de falas regravadas.
- Whisper local: transcrição rápida para planejar e nova transcrição do corte final. Escutar emendas; o texto sozinho não valida o corte.
- Helvetica regular com tracking −0,05 em; Scholar Italic nos destaques. Legendas um pouco abaixo do queixo, elementos acima da cabeça, rosto livre.
- Conferir snapshots de todas as trocas antes de exportar o MP4 com Hyperframes. Avisar antes das etapas demoradas; não repetir processamento sem necessidade.
- Entregar caminho, cortes feitos, fontes e pendências. Publicação não faz parte da edição.
