"""Confere se tudo que o Editai precisa esta funcionando. Mostra OK ou o que falta."""
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
problemas = []


def checar(nome, condicao, dica):
    if condicao:
        print(f"  OK  {nome}")
    else:
        print(f"  --  {nome}: {dica}")
        problemas.append(nome)


checar("Git", shutil.which("git"), "nao encontrado; rode o instalador de novo")
checar("FFmpeg",shutil.which("ffmpeg"), "nao encontrado; rode o instalador de novo")
checar("Node", shutil.which("node"), "nao encontrado; rode o instalador de novo")
checar("Remotion", (KIT / "node_modules" / "remotion").exists() and (KIT / "node_modules" / "@remotion" / "cli").exists(),
       "rode 'npm install' na pasta Editai")

try:
    import faster_whisper  # noqa: F401
    checar("Whisper", True, "")
except ImportError:
    checar("Whisper", False, "transcritor nao instalado")

try:
    import cv2  # noqa: F401
    checar("Rastreador de rosto", True, "")
except ImportError:
    checar("Rastreador de rosto", False, "OpenCV nao instalado; rode o instalador de novo")

skills = Path.home() / ".claude" / "skills"
checar("Skills do Editai", any(skills.glob("editai*")), "skills nao encontradas")

if shutil.which("ffmpeg"):
    teste = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=d=1:s=320x240", "-f", "null", "-"],
        capture_output=True,
    )
    checar("FFmpeg processando video", teste.returncode == 0, "FFmpeg instalado, mas com erro")

sys.exit(1 if problemas else 0)
