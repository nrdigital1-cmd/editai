---
name: editai-anuncios-naama
description: Editar vídeo vertical de vendas com legendas, destaques em verde limão, ilustrações, ícones, formas e motions na identidade Editai de Naamã. Use para anúncios, oferta, produto ou criativo publicitário; para conteúdo orgânico discreto use editai-natural-naama.
---

# Editai — Anúncios e Criativos · Naamã

Crie um vídeo vertical final em MP4 com até 120 segundos por padrão, mantendo a identidade do aluno e a identidade gráfica Editai. Esta skill funciona com ferramentas locais de Claude e Codex; não presuma acesso ao terminal em todas as interfaces.

Antes de executar, leia [fluxo local](references/fluxo.md) para perfil, dependências, cortes, transcrição, composição e validação, e [identidade visual](references/identidade.md) para tipografia, paleta e motion. Use o preset **anuncios** em `init --style anuncios`.

## Escolha visual
Ilustre mecanismos e benefícios com formas, SVG, ícones, imagens e comparações curtas acima da cabeça. Cards arredondados, motion suave e glow discreto. Legenda branca sem contorno; palavras de impacto em Scholar Italic verde limão, um pouco maiores. Produto, oferta, preço e CTA vêm do usuário: não use dados demonstrativos como fatos.

## Critérios de entrega
- Perfil salvo uma vez em `perfil.json`; nunca inventar números, logos, prints ou resultados.
- Remover pausas, respiros audíveis e retomadas sem perder palavras; manter a última versão de falas regravadas.
- Whisper local: transcrição rápida para planejar e nova transcrição do corte final. Escutar emendas; o texto sozinho não valida o corte.
- Helvetica regular com tracking −0,05 em; Scholar Italic nos destaques. Legendas um pouco abaixo do queixo, elementos acima da cabeça, rosto livre.
- Conferir snapshots de todas as trocas antes de exportar o MP4 com Hyperframes. Avisar antes das etapas demoradas; não repetir processamento sem necessidade.
- Entregar caminho, cortes feitos, fontes e pendências. Publicação não faz parte da edição.
