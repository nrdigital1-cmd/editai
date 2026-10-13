# Pasta Editai (instruções para o Codex)

Esta pasta é onde o aluno edita vídeos com as skills do Editai.

- Python: use sempre o Python do Editai, que já tem o transcritor instalado.
  Windows: `.python\Scripts\python.exe` · Mac: `.python/bin/python`
- Vídeos brutos ficam em `videos-sem-edicao/`. Crie cada projeto em `projetos/<nome-do-video>/`.
- `perfil.json` fica na raiz desta pasta.
- Quando o aluno disser "edita meu vídeo" sem escolher o estilo, pergunte numa frase qual ele quer:
  **natural** (dia a dia, prints reais), **anúncio** (venda, oferta) ou **motion** (animações que explicam, tipografia animada).
  Depois use a skill `editai-natural-naama`, `editai-anuncios-naama` ou `editai-motion-naama`.
- Antes de gerar cada vídeo, pergunte se o aluno mantém a identidade visual do Editai (elementos, cores e fontes) ou se vai enviar as fontes, os elementos e as cores da marca dele.
- Prévia = **Remotion Studio**: na pasta do projeto rode `npx remotion studio --no-open` em segundo plano e diga o endereço (normalmente http://localhost:3000) para o aluno abrir no navegador do computador. Nunca mostre o MP4 final como prévia. Só exporte (`editai.py render ... --aprovado`) quando o aluno aprovar ou escrever "pode exportar".
- Fale com o aluno em português simples, sem termos técnicos.

## Voltar e alterar um vídeo já feito
- Quando o aluno pedir mudança em um vídeo antigo ("no vídeo X, troca Y"), liste as pastas em `projetos/` e confirme qual é, numa frase, se houver dúvida.
- Reaproveite tudo o que está no projeto (cortes, transcrição, legenda, cenas). **Não transcreva de novo** se o corte não mudou.
- Mude só o que foi pedido, rode o build, abra o preview para o aluno aprovar e só exporte quando ele pedir.
- Salve o vídeo novo com outro nome (ex.: `final-v2.mp4`) para não apagar o anterior.
- Projeto antigo, feito antes da versão Remotion (tem `index.html` e não tem `src/Editai.tsx`): crie um projeto novo com `init` a partir do mesmo vídeo bruto e copie para `assets/` do novo os arquivos `keeps.json`, `emphasis.json` e `caption-fixes.json` do antigo; depois `cut` (refaz a cor e o tracking do rosto), transcreva o `clean.mp4` e siga normalmente.

## Atualizações
- Quando o aluno disser "atualiza o Editai": rode `python ferramentas/atualizar.py` e conte as novidades em português simples.
  Depois peça para fechar e abrir o Codex, para as skills novas valerem.
- No começo de cada edição, rode `python ferramentas/atualizar.py --verificar`.
  Se aparecer "TEM ATUALIZACAO", pergunte numa frase: "Tem novidade no Editai, quer atualizar antes de editar?"
  Se não houver internet, siga com a edição sem comentar.
- A atualização nunca mexe em `videos-sem-edicao`, `projetos` nem `perfil.json`.

## Skills no Codex
- As skills ficam em `~/.codex/skills`, `~/.agents/skills` e `.agents/skills` desta pasta. Para usar uma, escreva `$editai-natural-naama`, `$editai-anuncios-naama` ou `$editai-motion-naama`, ou peça "edita meu vídeo" que você escolhe.
