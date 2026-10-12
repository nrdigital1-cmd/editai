# Editai — comece aqui

Bem-vindo! Em uns 20 minutos seu computador vai estar pronto para editar vídeos com o Claude.

## Do que você precisa
- Windows 10/11 ou Mac (macOS 13 ou mais novo)
- Uns 5 GB livres e internet estável
- Assinatura do Claude (Pro ou Max) e o app do Claude instalado: claude.ai/download

## Instalação (uma vez só)
1. Clique no botão **Baixar material** do curso. O arquivo `editai-main.zip` vai para a pasta **Downloads**. Não precisa extrair.
2. Abra o app do Claude → aba **Code** → escolha a pasta **Downloads**.
3. Copie o texto abaixo, cole no Claude e envie:

> Instala o Editai para mim. O arquivo do Editai (editai-main.zip) está na pasta Downloads. Extraia, leia o COMECE-AQUI.md e rode o instalador do meu sistema (instalar-windows.ps1 no Windows ou instalar-mac.sh no Mac). Explique cada etapa em uma frase simples, sem termos técnicos. Se algo der erro, tente resolver e me diga o que aconteceu. No final, rode o teste do instalador e me confirme se está tudo pronto.

4. Quando aparecer um pedido de permissão, clique em **Permitir**. No Windows, clique em **Sim** se o sistema perguntar. No Mac, digite a senha do computador se pedir (ela não aparece enquanto você digita, é normal).
5. Espere aparecer **EDITAI PRONTO**.

Deu erro ou a internet caiu? Escreva no Claude: **"Deu erro, continua a instalação de onde parou."**

## Para editar um vídeo
1. Feche e abra o Claude de novo.
2. Aba **Code** → escolha a pasta **Editai**, que fica em **Documentos**.
3. Coloque seu vídeo na pasta `videos-sem-edicao`, dentro da pasta Editai:
   - Windows: abra **Documentos** → **Editai** → **videos-sem-edicao**
   - Mac: abra o Finder → **Documentos** → **Editai** → **videos-sem-edicao**
4. Escreva: **"edita meu vídeo"** e responda as perguntas.

## O que o instalador coloca no seu computador
| Programa | Para que serve |
|---|---|
| Git | Usado pelo Claude no computador e para receber as atualizações do Editai |
| Node | Motor que roda a ferramenta de montagem |
| FFmpeg | Corta, junta e converte o vídeo |
| Python | Motor que roda o transcritor |
| Whisper | Escuta o vídeo e escreve o que você falou, palavra por palavra |
| Remotion | Monta a edição (legendas, animações, efeitos), mostra a prévia e exporta o MP4 |
| OpenCV | Encontra o seu rosto no vídeo para a câmera acompanhar você |
| Skills do Editai | O manual que ensina o Claude a editar no estilo certo |

Tudo é gratuito para uso pessoal e para criadores individuais.

## Atualizações
Quando sair uma melhoria, o Claude avisa no começo da edição. Você também pode escrever a qualquer momento:
**"atualiza o Editai"**. Seus vídeos, projetos e perfil continuam intactos.
