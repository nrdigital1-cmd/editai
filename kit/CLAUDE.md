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
