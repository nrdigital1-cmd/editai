"""Instala e atualiza o Editai a partir do GitHub.

Uso:
  python atualizar.py              baixa a versao nova e instala
  python atualizar.py --verificar  so diz se existe versao nova
  python atualizar.py --sem-baixar instala a copia que ja esta no computador (usado pelo instalador)
  python atualizar.py --ferramenta codex   (so no instalador do Codex)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORIO = "https://github.com/nrdigital1-cmd/editai.git"
def documentos():
    """Pasta Documentos de verdade (no Windows ela pode ter sido movida para outro disco)."""
    if sys.platform == "win32":
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf) == 0:  # 5 = Documentos
            return Path(buf.value)
    return Path.home() / "Documents"


EDITAI = documentos() / "Editai"
FONTE = EDITAI / ".fonte"          # copia do GitHub, o aluno nao mexe aqui
MARCADOR = EDITAI / ".ferramenta"   # "claude" ou "codex": guarda onde o aluno instalou


def pastas_de_skills(ferramenta):
    """Onde cada ferramenta procura skills."""
    if ferramenta == "codex":
        return [Path.home() / ".codex" / "skills", Path.home() / ".agents" / "skills", EDITAI / ".agents" / "skills"]
    return [Path.home() / ".claude" / "skills"]


def ferramenta_atual(escolhida=None):
    if escolhida:
        MARCADOR.parent.mkdir(parents=True, exist_ok=True)
        MARCADOR.write_text(escolhida, encoding="utf-8")
        return escolhida
    try:
        valor = MARCADOR.read_text(encoding="utf-8").strip()
    except OSError:
        valor = "claude"
    return valor if valor in ("claude", "codex") else "claude"
PASTAS_DO_ALUNO = {"videos-sem-edicao", "projetos", "perfil.json", ".python", "node_modules", ".fonte"}


def git(*args, capturar=True):
    resultado = subprocess.run(["git", "-C", str(FONTE), *args], capture_output=capturar, text=True)
    if resultado.returncode != 0:
        raise RuntimeError((resultado.stderr or "").strip() or f"git {' '.join(args)} falhou")
    return (resultado.stdout or "").strip()


def baixar():
    """Traz a versao mais nova do GitHub. Devolve (versao_antiga, versao_nova)."""
    if not (FONTE / ".git").exists():
        if FONTE.exists():
            shutil.rmtree(FONTE)
        subprocess.run(["git", "clone", "-q", REPOSITORIO, str(FONTE)], check=True)
        return None, git("rev-parse", "HEAD")
    antiga = git("rev-parse", "HEAD")
    git("fetch", "-q", "origin", "main")
    # O aluno nao edita .fonte, entao alinhar com o GitHub e seguro
    git("reset", "-q", "--hard", "origin/main")
    return antiga, git("rev-parse", "HEAD")


def copiar_kit():
    """Atualiza as ferramentas da pasta Editai sem tocar nos videos, projetos e perfil do aluno."""
    # Versoes antigas usavam "meus-videos": renomeia mantendo os videos do aluno
    antiga, nova = EDITAI / "meus-videos", EDITAI / "videos-sem-edicao"
    if antiga.exists() and not nova.exists():
        antiga.rename(nova)
    for item in (FONTE / "kit").iterdir():
        if item.name in PASTAS_DO_ALUNO:
            (EDITAI / item.name).mkdir(parents=True, exist_ok=True) if item.is_dir() else None
            continue
        destino = EDITAI / item.name
        if item.is_dir():
            shutil.copytree(item, destino, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destino)


def copiar_skills(ferramenta):
    for pasta in pastas_de_skills(ferramenta):
        pasta.mkdir(parents=True, exist_ok=True)
        for skill in (FONTE / "skills").iterdir():
            if not skill.is_dir():
                continue
            destino = pasta / skill.name
            if destino.exists():
                shutil.rmtree(destino)  # tira arquivos que sairam da versao nova
            shutil.copytree(skill, destino)


def atualizar_montagem(antiga, nova):
    """Reinstala a ferramenta de montagem so se as versoes mudaram."""
    if not (EDITAI / "node_modules").exists() or antiga is None:
        return
    mudou = git("diff", "--name-only", antiga, nova, "--", "kit/package.json")
    if mudou:
        print("  atualizando a ferramenta de montagem...", flush=True)
        subprocess.run([shutil.which("npm") or "npm", "install", "--no-audit", "--no-fund", "--loglevel=error"],
                       cwd=EDITAI, check=True)
        # navegador usado pelo Remotion para gerar o video (baixa so uma vez)
        subprocess.run([shutil.which("npx") or "npx", "remotion", "browser", "ensure"], cwd=EDITAI, check=True)


def atualizar_python():
    """Garante o rastreador de rosto (OpenCV 4.x) no Python do Editai."""
    py = EDITAI / ".python" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not py.exists():
        return
    tem = subprocess.run([str(py), "-c", "import cv2"], capture_output=True).returncode == 0
    if not tem:
        print("  instalando o rastreador de rosto...", flush=True)
        subprocess.run([str(py), "-m", "pip", "install", "--quiet", "opencv-python-headless==4.14.0.94"], check=True)


def novidades(antiga, nova):
    if antiga is None or antiga == nova:
        return []
    texto = git("log", "--format=%s", f"{antiga}..{nova}")
    return [linha for linha in texto.splitlines() if linha]


def verificar():
    if not (FONTE / ".git").exists():
        print("Editai instalado sem ligacao com o GitHub. Escreva 'atualiza o Editai' para ligar.")
        return
    git("fetch", "-q", "origin", "main")
    faltam = int(git("rev-list", "--count", "HEAD..origin/main"))
    if faltam:
        print(f"TEM ATUALIZACAO: {faltam} novidade(s) disponivel(is).")
        for linha in git("log", "--format=%s", "HEAD..origin/main").splitlines():
            print(f"  - {linha}")
    else:
        print("Voce ja tem a versao mais nova do Editai.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verificar", action="store_true")
    parser.add_argument("--sem-baixar", action="store_true")
    parser.add_argument("--ferramenta", choices=["claude", "codex"], help="usado pelo instalador; depois fica salvo")
    a = parser.parse_args()
    try:
        if a.verificar:
            verificar()
            return
        EDITAI.mkdir(parents=True, exist_ok=True)
        if a.sem_baixar:
            antiga = nova = None
        else:
            print("Baixando a versao mais nova do Editai...", flush=True)
            antiga, nova = baixar()
        copiar_kit()
        copiar_skills(ferramenta_atual(a.ferramenta))
        if not a.sem_baixar:
            atualizar_montagem(antiga, nova)
            atualizar_python()
        lista = novidades(antiga, nova)
        if antiga is not None and not lista:
            print("Voce ja tinha a versao mais nova. Nada mudou.")
        elif lista:
            print("Editai atualizado! Novidades:")
            for linha in lista:
                print(f"  - {linha}")
        else:
            print("Editai instalado.")
    except (RuntimeError, OSError, subprocess.CalledProcessError) as erro:
        print(f"Nao consegui atualizar: {erro}")
        print("Confira a internet e tente de novo. Seus videos e projetos nao foram alterados.")
        sys.exit(1)


if __name__ == "__main__":
    main()
