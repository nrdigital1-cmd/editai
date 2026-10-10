# Pasta Editai

Esta pasta é onde o aluno edita vídeos com as skills do Editai.

- Python: use sempre o Python do Editai, que já tem o transcritor instalado.
  Windows: `.python\Scripts\python.exe` · Mac: `.python/bin/python`
- Vídeos brutos ficam em `videos-sem-edicao/`. Crie cada projeto em `projetos/<nome-do-video>/`.
- `perfil.json` fica na raiz desta pasta.
- Quando o aluno disser "edita meu vídeo" sem escolher o estilo, pergunte numa frase qual ele quer:
  **natural** (dia a dia, prints reais), **anúncio** (venda, oferta) ou **motion** (animações que explicam, tipografia animada).
  Depois use a skill `editai-natural-naama`, `editai-anuncios-naama` ou `editai-motion-naama`.
- Fale com o aluno em português simples, sem termos técnicos.

## Voltar e alterar um vídeo já feito
- Quando o aluno pedir mudança em um vídeo antigo ("no vídeo X, troca Y"), liste as pastas em `projetos/` e confirme qual é, numa frase, se houver dúvida.
- Reaproveite tudo o que está no projeto (cortes, transcrição, legenda, cenas). **Não transcreva de novo** se o corte não mudou.
- Mude só o que foi pedido, rode o build, abra o preview para o aluno aprovar e só exporte quando ele pedir.
- Salve o vídeo novo com outro nome (ex.: `final-v2.mp4`) para não apagar o anterior.

## Atualizações
- Quando o aluno disser "atualiza o Editai": rode `python ferramentas/atualizar.py` e conte as novidades em português simples.
  Depois peça para fechar e abrir o Claude, para as skills novas valerem.
- No começo de cada edição, rode `python ferramentas/atualizar.py --verificar`.
  Se aparecer "TEM ATUALIZACAO", pergunte numa frase: "Tem novidade no Editai, quer atualizar antes de editar?"
  Se não houver internet, siga com a edição sem comentar.
- A atualização nunca mexe em `videos-sem-edicao`, `projetos` nem `perfil.json`.
