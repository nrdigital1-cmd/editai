# Pasta Editai

Esta pasta é onde o aluno edita vídeos com as skills do Editai.

- Python: use sempre o Python do Editai, que já tem o transcritor instalado.
  Windows: `.python\Scripts\python.exe` · Mac: `.python/bin/python`
- Vídeos brutos ficam em `meus-videos/`. Crie cada projeto em `projetos/<nome-do-video>/`.
- `perfil.json` fica na raiz desta pasta.
- Quando o aluno disser "edita meu vídeo" sem escolher o estilo, pergunte numa frase:
  **natural** (conteúdo do dia a dia, prints reais) ou **anúncio** (venda, oferta, criativo).
  Depois use a skill `editai-natural-naama` ou `editai-anuncios-naama`.
- Fale com o aluno em português simples, sem termos técnicos.

## Atualizações
- Quando o aluno disser "atualiza o Editai": rode `python ferramentas/atualizar.py` e conte as novidades em português simples.
  Depois peça para fechar e abrir o Claude, para as skills novas valerem.
- No começo de cada edição, rode `python ferramentas/atualizar.py --verificar`.
  Se aparecer "TEM ATUALIZACAO", pergunte numa frase: "Tem novidade no Editai, quer atualizar antes de editar?"
  Se não houver internet, siga com a edição sem comentar.
- A atualização nunca mexe em `meus-videos`, `projetos` nem `perfil.json`.
