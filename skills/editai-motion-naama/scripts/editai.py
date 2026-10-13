"""Ferramentas locais Editai / Naamã (motor: Remotion). Python 3.10+, FFmpeg, Node e faster-whisper.

Fluxo: doctor → init → transcribe → cut (+grade) → transcribe → build → preview no Remotion Studio
→ still (conferência) → aprovação do aluno → render (só então o MP4 final).
"""
import argparse
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SKILL = Path(__file__).resolve().parents[1]
FPS = 30

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)

def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path], capture_output=True, text=True).stdout)

def fingerprint(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def encoder():
    for name, options in [("h264_nvenc", ["-preset", "p4", "-cq", "20"]), ("h264_qsv", ["-global_quality", "22"]), ("h264_amf", ["-quality", "balanced"]), ("h264_videotoolbox", ["-b:v", "12M"])]:
        p = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=320x320:d=0.1", "-c:v", name, *options, "-f", "null", "-"], capture_output=True)
        if p.returncode == 0:
            return ["-c:v", name, *options]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]

def doctor(_):
    for name in ["ffmpeg", "ffprobe", "node", "npm", "npx"]:
        print(f"{name}: {shutil.which(name) or 'AUSENTE'}")
    import importlib.util
    print("faster-whisper:", "OK" if importlib.util.find_spec("faster_whisper") else "AUSENTE")
    print("opencv (face tracking):", "OK" if importlib.util.find_spec("cv2") else "AUSENTE — pip install \"opencv-python-headless<5\"")
    for name in ["Helvetica-Regular.otf", "Scholar-Italic.otf"]:
        print(name, "OK" if (SKILL / "assets" / "fonts" / name).exists() else "AUSENTE")
    print("template Remotion:", "OK" if (SKILL / "assets" / "remotion" / "package.json").exists() else "AUSENTE")

def styles():
    return ["motion"] if read(SKILL / "assets" / "design.json")["style"] == "motion" else ["natural", "anuncios"]

def init(a):
    src, project = Path(a.video).resolve(), Path(a.project).resolve()
    if project.exists():
        raise ValueError("Projeto já existe; escolha outra pasta para preservar o trabalho.")
    info = probe(src)
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        raise ValueError("O vídeo precisa conter áudio para transcrição.")
    # Projeto Remotion (template da skill) + pastas de trabalho
    shutil.copytree(SKILL / "assets" / "remotion", project, ignore=shutil.ignore_patterns("node_modules", "out", "*.log"))
    for folder in ["assets/prints", "public/fonts", "public/media", "public/sfx", "renders", "snapshots"]:
        (project / folder).mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL / "assets" / "fonts", project / "public" / "fonts", dirs_exist_ok=True)
    shutil.copytree(SKILL / "assets" / "sfx", project / "public" / "sfx", dirs_exist_ok=True)
    config = read(SKILL / "assets" / "design.json")
    config["style"] = a.style
    write(project / "editai.json", config)
    write(project / "assets" / "source.json", {"path": str(src), "sha256": fingerprint(src)})
    print("Preparando vídeo — esta etapa pode levar alguns minutos.", flush=True)
    run(["ffmpeg", "-v", "error", "-i", src, "-map", "0:v:0", "-map", "0:a:0", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", *encoder(), "-r", "30", "-c:a", "aac", "-b:a", "192k", project / "assets" / "raw.mp4"])
    print(project)
    if link_deps(project):
        print("Dependências do Remotion ligadas à pasta Editai (não precisa npm install).")
    else:
        print("Próximo: npm install dentro da pasta do projeto (uma vez).")

def link_deps(project):
    """Liga node_modules do projeto ao de uma pasta acima que já tenha o Remotion (ex.: Documentos/Editai),
    para não baixar as dependências de novo a cada vídeo."""
    for parent in project.resolve().parents:
        mods = parent / "node_modules"
        if (mods / "remotion").exists() and (mods / "@remotion" / "cli").exists():
            target = project / "node_modules"
            if target.exists():
                return True
            try:
                if sys.platform == "win32":
                    subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(mods)], check=True, capture_output=True)
                else:
                    os.symlink(mods, target, target_is_directory=True)
                return True
            except (OSError, subprocess.CalledProcessError):
                return False
    return False

def transcribe(a):
    from faster_whisper import WhisperModel
    media, out = Path(a.media), Path(a.output)
    print("Transcrevendo localmente — esta etapa pode levar alguns minutos.", flush=True)
    name = a.model or ("small" if a.fast else "medium")
    # Exige modelo já armazenado; instalação/download é uma etapa separada.
    def run_model(device, compute_type, **extra):
        model = WhisperModel(name, device=device, compute_type=compute_type, local_files_only=True, **extra)
        segments, info = model.transcribe(str(media), language="pt", word_timestamps=True, condition_on_previous_text=False, beam_size=1 if a.fast else 3, initial_prompt=a.names or None)
        # A placa de video so falha de verdade ao processar: consome tudo aqui dentro
        words = [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segments for w in (s.words or [])]
        return words, info

    try:
        words, info = run_model("cuda", "float16")
    except (RuntimeError, ValueError, OSError):
        print("Placa de vídeo indisponível; transcrevendo pelo processador.", flush=True)
        words, info = run_model("cpu", "int8", cpu_threads=max(1, min(4, os.cpu_count() or 1)))
    write(out, {"source_sha256": fingerprint(media), "duration": info.duration, "words": words})
    out.with_suffix(".txt").write_text("\n".join(f'{w["start"]:.3f}–{w["end"]:.3f} {w["text"]}' for w in words), encoding="utf-8")

def grade_filter(media, cfg=None):
    """Correcao automatica: balanco de branco (parcial, preserva a pele), brilho nos meios-tons, contraste e saturacao."""
    opts = (cfg or {}).get("grade", {})
    opts = opts if isinstance(opts, dict) else {}
    duration = float(probe(media)["format"]["duration"])
    total = [0.0, 0.0, 0.0]
    count = 0
    luma = []
    for k in range(8):
        t = duration * (k + 0.5) / 8
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(media), "-frames:v", "1", "-vf", "scale=108:192",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        for i in range(0, len(raw) - 2, 3):
            r, g, b = raw[i], raw[i + 1], raw[i + 2]
            y = (r + g + b) / 3
            luma.append(y)
            if 40 < y < 200:
                total[0] += r
                total[1] += g
                total[2] += b
                count += 1
    r, g, b = (c / max(count, 1) for c in total)
    strength = float(opts.get("wb_strength", 0.15))  # 0 = sem correcao; 1 = cinza total (deixa a pele sem vida)
    clamp = lambda v: max(0.94, min(1.06, v))  # correcao delicada: preserva o calor natural da pele
    gr, gb = clamp((g / max(r, 1)) ** strength), clamp((g / max(b, 1)) ** strength)
    mean = sum(luma) / max(len(luma), 1)
    # Curvas SUAVES: levantam os meios-tons sem esmagar as sombras nem estourar as altas luzes
    # (resultado natural, pouco contraste). Sombras levemente abertas; altas luzes contidas.
    if mean < 50:    # video escuro: abre os meios-tons com delicadeza
        curve = "0/0.012 0.1/0.115 0.3/0.36 0.7/0.75 1/0.985"
    elif mean < 90:
        curve = "0/0.01 0.1/0.11 0.3/0.33 0.7/0.72 1/0.99"
    else:
        curve = "0/0.005 0.5/0.505 1/0.995"
    sat = float(opts.get("saturation", 1.06))
    con = float(opts.get("contrast", 0.98))  # < 1 = um pouco menos contraste que o original
    vib = float(opts.get("vibrance", 0.1))
    flt = (f"colorchannelmixer=rr={gr:.3f}:gg=1:bb={gb:.3f},curves=all='{curve}',"
           f"eq=contrast={con}:saturation={sat},vibrance=intensity={vib}")
    return flt, {"rgb_medio": [round(r), round(g), round(b)], "luma_media": round(mean, 1), "filtro": flt}

def grade(a):
    project = Path(a.project)
    cfg = read(project / "editai.json")
    clean = project / "assets" / "clean.mp4"
    if cfg.get("grade") is False:
        print("Correcao de cor desligada no editai.json.")
        return
    flt, info = grade_filter(clean, cfg)
    print("Corrigindo cor (balanco de branco, brilho, contraste, saturacao) - pode levar alguns minutos.", flush=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", clean, "-map", "0:v:0", "-vf", flt, *encoder(), "-r", "30", "-an", project / "assets" / "graded.mp4"])
    info["clean_sha256"] = fingerprint(clean)
    write(project / "assets" / "grade.json", info)
    print("Cor corrigida:", info["filtro"])

def camera_source(project, clean):
    """Video corrigido para a camera (o audio continua vindo de clean.mp4)."""
    assets = project / "assets"
    if (assets / "graded.mp4").exists() and (assets / "grade.json").exists():
        if read(assets / "grade.json").get("clean_sha256") != fingerprint(clean):
            raise ValueError("Correção de cor desatualizada: rode grade novamente.")
        return "assets/graded.mp4"
    return "assets/clean.mp4"

def plan_segments(keeps, silences, duration, fps=30):
    pieces = []
    previous = 0
    for k in keeps:
        start, end = float(k["from"]), float(k["to"])
        if not (0 <= start < end <= duration + 0.001) or start < previous:
            raise ValueError("Intervalos devem ser ordenados, sem sobreposição e dentro do vídeo.")
        previous = end
        cursor = start
        for sa, sb in ([] if k.get("raw") else silences):
            # Margens preservam ataques suaves e finais de palavras.
            sa, sb = max(start, sa + 0.06), min(end, sb - 0.09)
            if sb <= cursor or sa >= end or sb - sa < 0.07:
                continue
            if sa > cursor:
                pieces.append((cursor, sa, k.get("why", "")))
            cursor = max(cursor, sb)
        if cursor < end:
            pieces.append((cursor, end, k.get("why", "")))
    return [(round(s * fps) / fps, round(e * fps) / fps, why) for s, e, why in pieces if round(e * fps) - round(s * fps) >= 2]

def cut(a):
    project = Path(a.project)
    assets = project / "assets"
    media = assets / "raw.mp4"
    duration = float(probe(media)["format"]["duration"])
    decision = read(assets / "keeps.json")
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(media), "-af", f"silencedetect=noise={a.threshold}dB:d={a.pause}", "-f", "null", "-"], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    silences = [(float(s), float(e)) for s, e in re.findall(r"silence_start: ([\d.]+).*?silence_end: ([\d.]+)", p.stderr, re.S)]
    segments = plan_segments(decision["keeps"], silences, duration)
    total = sum(e - s for s, e, _ in segments)
    maximum = read(project / "editai.json")["max_duration"]
    if not segments or total > maximum + 0.001:
        raise ValueError(f"Corte vazio ou duração {total:.2f}s acima do limite de {maximum}s. Revise keeps.json; nenhuma fala foi truncada automaticamente.")
    filters, pairs, records, offset = [], [], [], 0
    for i, (s, e, why) in enumerate(segments):
        filters += [f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]", f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0,e-s-0.008)}:d=0.008[a{i}]"]
        pairs.append(f"[v{i}][a{i}]")
        records.append({"source_start": s, "source_end": e, "output_start": offset, "output_end": offset + e - s, "why": why})
        offset += e - s
    filters.append("".join(pairs) + f"concat=n={len(segments)}:v=1:a=1[v][a]")
    filterfile = assets / "cut-filter.txt"
    filterfile.write_text(";".join(filters), encoding="utf-8")
    print("Aplicando cortes — esta etapa pode levar alguns minutos.", flush=True)
    version = run(["ffmpeg", "-version"], capture_output=True, text=True).stdout
    match = re.search(r"ffmpeg version (\d+)", version)
    option = "-/filter_complex" if match and int(match.group(1)) >= 7 else "-filter_complex_script"
    run(["ffmpeg", "-y", "-v", "error", "-i", media, option, filterfile, "-map", "[v]", "-map", "[a]", *encoder(), "-r", "30", "-c:a", "aac", "-b:a", "192k", assets / "clean.mp4"])
    write(assets / "edit-decisions.json", {"duration": total, "segments": records, "source_sha256": fingerprint(media), "clean_sha256": fingerprint(assets / "clean.mp4")})
    grade(argparse.Namespace(project=str(project)))
    try:
        track(argparse.Namespace(project=str(project)))
    except ValueError as e:
        print(f"Aviso: {e}")

def caption_chunks(words, duration, emphasis, fixes, max_words=3, max_chars=18):
    """Blocos de 2-3 palavras. Palavra de impacto: EMBAIXO quando continua a frase (fecha o bloco),
    EM CIMA quando a frase comeca nela (o resto vem na linha de baixo). Sempre bem maior."""
    fixed = {f["index"]: f["text"] for f in fixes}
    marked = {e["index"] for e in emphasis}
    chunks, current = [], []

    def close():
        if current:
            chunks.append(list(current))
            current.clear()

    for i, w in enumerate(words):
        text = fixed.get(i, w["text"]).strip()
        if not text:
            continue
        if current:
            gap = float(w["start"]) - float(words[current[-1][0]]["end"])
            chars = sum(len(t) + 1 for j, t in current if j not in marked) + (0 if i in marked else len(text))
            has_key = any(j in marked for j, _ in current)
            if gap > 0.25 or (len(current) >= max_words and (i not in marked or len(current) > max_words)) or chars > max_chars or (has_key and i in marked):
                close()
        current.append((i, text))
        # impacto que continua a frase fecha o bloco: fica embaixo, no fim
        if (i in marked and len(current) > 1) or re.search(r"[.!?,;:]$", text):
            close()
    close()

    out = []
    for n, chunk in enumerate(chunks):
        start = float(words[chunk[0][0]]["start"])
        nxt = float(words[chunks[n + 1][0][0]]["start"]) if n + 1 < len(chunks) else duration
        end = min(nxt, float(words[chunk[-1][0]]["end"]) + 0.6)
        if end <= start:
            continue
        keys = [k for k, (i, _) in enumerate(chunk) if i in marked]
        plain = lambda part: [{"text": t, "key": False} for _, t in part]
        if not keys:
            lines = [plain(chunk)]
        else:
            k = keys[0]
            key = {"text": chunk[k][1], "key": True}
            before, after = chunk[:k], chunk[k + 1:]
            if before:   # continuacao da frase: impacto embaixo
                lines = [plain(before), [key] + plain(after)]
            else:        # a frase comeca no impacto: impacto em cima, resto embaixo
                lines = [[key]] + ([plain(after)] if after else [])
        out.append((start, end, lines))
    return out


def modo_leve(cfg):
    """PC fraco (poucos nucleos ou pouca memoria) exporta com menos blur. editai.json pode forcar: "modo_leve": true/false."""
    escolha = cfg.get("modo_leve", "auto")
    if isinstance(escolha, bool):
        return escolha
    nucleos = os.cpu_count() or 2
    memoria_gb = 8.0
    try:
        if sys.platform == "win32":
            import ctypes
            class M(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("c", ctypes.c_ulong), ("total", ctypes.c_ulonglong)] + [(f"x{k}", ctypes.c_ulonglong) for k in range(6)]
            m = M(); m.l = ctypes.sizeof(M)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            memoria_gb = m.total / 2**30
        elif sys.platform == "darwin":
            memoria_gb = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) / 2**30
        else:
            memoria_gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30
    except Exception:
        pass
    leve = nucleos <= 4 or memoria_gb < 8
    if leve:
        print("Modo leve: PC mais simples detectado, usando menos desfoque de movimento para exportar mais rápido.", flush=True)
    return leve

def fixes_text(fixes, i, words):
    for fix in fixes:
        if fix["index"] == i:
            return fix["text"].strip()
    return words[i]["text"].strip()

def word_captions(words, duration, emphasis, fixes):
    """Anúncios/natural: uma palavra por vez. Impacto SEMPRE maior: embaixo quando continua a frase
    (anterior em cima), em cima quando a frase começa nele (a próxima embaixo)."""
    out = []
    marked = {e["index"] for e in emphasis}
    for i, word in enumerate(words):
        start = float(word["start"])
        end = min(float(words[i + 1]["start"]) if i + 1 < len(words) else duration, start + 1.2)
        text = fixes_text(fixes, i, words)
        if not text or end <= start:
            continue
        if i in marked:
            j = next((j for j in range(i - 1, -1, -1) if fixes_text(fixes, j, words)), None)
            prev = fixes_text(fixes, j, words) if j is not None else ""
            continua = bool(prev) and start - float(words[j]["end"]) < 0.3 and not re.search(r"[.!?;:]$", prev)
            key = [{"text": text, "key": True}]
            if continua:
                lines = [[{"text": prev, "key": False}], key]
            else:
                k = next((k for k in range(i + 1, len(words)) if fixes_text(fixes, k, words)), None)
                nxt = fixes_text(fixes, k, words) if k is not None and float(words[k]["start"]) - float(word["end"]) < 0.3 else ""
                lines = [key] + ([[{"text": nxt, "key": False}]] if nxt else [])
        else:
            lines = [[{"text": text, "key": False}]]
        out.append((start, end, lines))
    return out

# Volumes pensados para ficar audível mas confortável por baixo da voz (voz = 1)
SFX_VOLUME = {"whoosh": 0.35, "pop": 0.14, "tick": 0.12}
SFX_DUR = {"whoosh": 0.55, "pop": 0.18, "tick": 0.07}
# Whoosh é só para transições de tela e elementos grandes em movimento (área mínima em px² de 1080×1920)
WHOOSH_MIN_AREA = 300_000

def sfx_list(hits, duration, cfg):
    """hits = [(segundos, tipo)] → lista para o Remotion (um som de cada tipo por vez, sem embolar)."""
    if not cfg.get("sfx", True):
        return []
    ganho = float(cfg.get("sfx_volume", 1.0))
    out, ultimo = [], {}
    for t, som in sorted(hits):
        if t < 0 or t >= duration or t - ultimo.get(som, -9) < SFX_DUR[som] + 0.05:
            continue
        ultimo[som] = t
        out.append({"from": round(t * FPS), "type": som, "volume": round(SFX_VOLUME[som] * ganho, 3), "dur": max(1, round(min(SFX_DUR[som], duration - t) * FPS))})
    return out

def sync_media(src, dst):
    """Copia mídia para public/ só quando mudou (o Remotion serve arquivos de public/)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size == src.stat().st_size and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    shutil.copy2(src, dst)

def track(a):
    """Face tracking local (OpenCV, sem internet): centro do rosto a cada quadro, suavizado como um operador
    de câmera (sem saltos, ignora tremidinhas, segue movimentos reais). Salva assets/face-track.json."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ValueError("Face tracking precisa do OpenCV: pip install \"opencv-python-headless<5\" (versão 4.x, com os detectores embutidos).")
    project = Path(a.project)
    assets = project / "assets"
    clean = assets / "clean.mp4"
    src = project / camera_source(project, clean)
    SFPS, W, H = 10, 270, 480
    print("Rastreando o rosto — esta etapa pode levar alguns minutos.", flush=True)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"fps={SFPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                            stdout=subprocess.PIPE)
    front = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    raw, prev = [], None
    while True:
        buf = proc.stdout.read(W * H)
        if len(buf) < W * H:
            break
        img = cv2.equalizeHist(np.frombuffer(buf, np.uint8).reshape(H, W))
        faces = list(front.detectMultiScale(img, 1.1, 5, minSize=(28, 28)))
        if not faces:  # rosto de perfil (os dois lados)
            faces = list(profile.detectMultiScale(img, 1.1, 4, minSize=(28, 28)))
            faces += [(W - x - w, y, w, h) for x, y, w, h in profile.detectMultiScale(cv2.flip(img, 1), 1.1, 4, minSize=(28, 28))]
        if faces:
            def score(fc):
                x, y, w, h = fc
                c = ((x + w / 2) / W, (y + h / 2) / H)
                return w * h * (1.0 if prev is None else 1 / (1 + 25 * math.hypot(c[0] - prev[0], c[1] - prev[1])))
            x, y, w, h = max(faces, key=score)
            prev = ((x + w / 2) / W, (y + h / 2) / H)
            raw.append((prev[0], prev[1], w / W))
        else:
            raw.append(None)
    proc.wait()
    found = [i for i, r in enumerate(raw) if r]
    if len(found) < max(3, 0.2 * len(raw)):
        write(assets / "face-track.json", {"clean_sha256": fingerprint(clean), "fps": FPS, "x": [], "y": [], "detected": round(len(found) / max(1, len(raw)), 3)})
        print("Rosto pouco detectado: tracking desligado para este vídeo (enquadramento fixo). Confira a luz/enquadramento.")
        return
    t = np.arange(len(raw))
    cols = [np.interp(t, found, [raw[i][k] for i in found]) for k in range(3)]
    # mediana (remove detecções erradas isoladas)
    med = [np.array([np.median(c[max(0, i - 2):i + 3]) for i in range(len(c))]) for c in cols]
    # zona morta: o alvo só muda quando o rosto anda de verdade (câmera calma, sem tremer)
    dead = float(read(project / "editai.json").get("face_track", {}).get("dead_zone", 0.025))
    held = [med[0].copy(), med[1].copy()]
    for k in range(2):
        cur = med[k][0]
        for i in range(len(t)):
            if abs(med[k][i] - cur) > dead:
                cur = med[k][i] - math.copysign(dead, med[k][i] - cur)
            held[k][i] = cur
    # suavização ida e volta (sem atraso), constante de tempo ~0,45 s
    alpha = 1 - math.exp(-1 / (0.45 * SFPS))
    def smooth(v):
        out = v.copy()
        for i in range(1, len(v)):
            out[i] = out[i - 1] + alpha * (v[i] - out[i - 1])
        for i in range(len(v) - 2, -1, -1):
            out[i] = out[i + 1] + alpha * (out[i] - out[i + 1])
        return out
    sx, sy = smooth(held[0]), smooth(held[1])
    ss = smooth(med[2])  # tamanho do rosto (fração da largura): mostra onde fica o topo da cabeça
    duration = float(probe(src)["format"]["duration"])
    tt = np.arange(0, duration, 1 / FPS)
    ts = t / SFPS
    data = {"clean_sha256": fingerprint(clean), "fps": FPS, "detected": round(len(found) / len(raw), 3),
            "x": [round(float(v), 4) for v in np.interp(tt, ts, sx)], "y": [round(float(v), 4) for v in np.interp(tt, ts, sy)],
            "s": [round(float(v), 4) for v in np.interp(tt, ts, ss)]}
    write(assets / "face-track.json", data)
    print(f"Rosto rastreado em {data['detected']*100:.0f}% das amostras; câmera vai acompanhar o rosto.")

NAME = re.compile(r"[A-Z][A-Za-z0-9]*")

def registry(folder, names, export):
    """Gera src/<folder>/index.ts importando os componentes TSX citados nos planos."""
    lines = ["// GERADO por `editai.py build` — não editar à mão.", "import type React from 'react';", "import type {SceneProps} from '../types';"]
    for n in sorted(names):
        lines.append(f"import {{{n}}} from './{n}';")
    lines.append(f"\nexport const {export}: Record<string, React.FC<SceneProps>> = {{{', '.join(sorted(names))}}};\n")
    (folder / "index.ts").write_text("\n".join(lines), encoding="utf-8")

def build(a):
    project = Path(a.project)
    cfg = read(project / "editai.json")
    style = cfg["style"]
    assets = project / "assets"
    clean = assets / "clean.mp4"
    transcript = read(assets / "transcript.json")
    if transcript["source_sha256"] != fingerprint(clean):
        raise ValueError("Transcrição desatualizada: transcreva clean.mp4 novamente.")
    duration = float(probe(clean)["format"]["duration"])
    if duration > cfg["max_duration"] + 0.1:
        raise ValueError("Vídeo excede o limite configurado.")
    emphasis = read(assets / "emphasis.json") if (assets / "emphasis.json").exists() else []
    fixes = read(assets / "caption-fixes.json") if (assets / "caption-fixes.json").exists() else []
    lay = cfg["layout"]
    fr = lambda t: round(float(t) * FPS)
    for key, value in cfg["palette"].items():
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("Cor inválida na paleta.")

    scenes, beats, captions, hits = [], [], [], []
    scene_names, beat_names = set(), set()

    # GANCHO (obrigatorio): nos primeiros segundos a pessoa aparece e um titulo entra acima da cabeca
    hook_file = assets / "hook.json"
    if not hook_file.exists():
        raise ValueError('Falta o título do gancho: crie assets/hook.json, ex.: {"linhas": [[{"text": "Eu gastava"}], '
                         '[{"text": "2 horas", "key": true}]], "fim": 4.8}')
    hook_cfg = read(hook_file)
    hook_lines = hook_cfg.get("linhas") or []
    if not hook_lines or not all(isinstance(l, list) and l and all(isinstance(p, dict) and str(p.get("text", "")).strip() for p in l) for l in hook_lines):
        raise ValueError("hook.json: 'linhas' precisa ser uma lista de linhas, cada uma com partes {\"text\": ..., \"key\": true/false}.")
    if len(hook_lines) > 3 or sum(len(str(p["text"])) for l in hook_lines for p in l) > 42:
        raise ValueError("hook.json: título longo demais. Use até 3 linhas curtas (cerca de 6 palavras).")
    hook_end = float(hook_cfg.get("fim", min(5.0, duration)))
    if not (2.0 <= hook_end <= min(6.0, duration)):
        raise ValueError("hook.json: 'fim' deve ficar entre 2 e 6 segundos (o gancho dura cerca de 5 s).")
    hook_bottom = int(lay.get("head_top", 700)) - 30
    safe_top = 270 if style == "anuncios" else int(lay.get("top_min", 150))  # anúncios: área segura da Meta
    linhas_alt = sum(1.35 if any(p.get("key") for p in l) else 1.05 for l in hook_lines)
    # o título diminui sozinho até caber acima da cabeça; abaixo de 56 px fica pequeno demais para ler
    hook_size = int(min(int(cfg.get("hook_size", 92)), (hook_bottom - safe_top) / linhas_alt))
    if hook_size < 56:
        raise ValueError("O título do gancho não cabe acima da cabeça: encurte para 1 linha ou reenquadre "
                         "(deixe mais espaço acima da cabeça na gravação).")
    hook = {"from": 0, "to": fr(hook_end), "bottom": hook_bottom, "safeTop": safe_top, "height": round(hook_size * linhas_alt),
            "lines": [[{"text": str(p["text"]).strip(), "key": bool(p.get("key"))} for p in l] for l in hook_lines]}
    hits.append((0.12, "whoosh"))
    if any(p["key"] for l in hook["lines"] for p in l):
        hits.append((0.45, "pop"))
    if style == "motion":
        plan = read(assets / "scenes.json")
        previous = 0.0
        for n, s in enumerate(plan):
            if s.get("layout") not in {"full", "split", "motion"}:
                raise ValueError(f"Cena {n}: layout deve ser full, split ou motion.")
            if not (previous - 0.001 <= float(s["start"]) < float(s["end"]) <= duration + 0.001):
                raise ValueError(f"Cena {n}: tempos fora de ordem, sobrepostos ou além do vídeo.")
            previous = float(s["end"])
            comp = s.get("component")
            if comp:
                if not NAME.fullmatch(comp) or not (project / "src" / "scenes" / f"{comp}.tsx").exists():
                    raise ValueError(f"Cena {n}: componente {comp} não existe em src/scenes/{comp}.tsx (nome em PascalCase).")
                scene_names.add(comp)
                code = (project / "src" / "scenes" / f"{comp}.tsx").read_text(encoding="utf-8")
                # pops nas palavras de impacto da tipografia cinética (WordScene: {at: N, ..., key: true})
                hits += [(float(s["start"]) + float(t) / FPS, "pop") for t in re.findall(r"at:\s*([\d.]+)[^}]*key:\s*true", code)]
            scenes.append({"from": fr(s["start"]), "to": fr(s["end"]), "layout": s["layout"], "component": comp})
        hits += [(float(s["start"]) - 0.1, "whoosh") for s in plan[1:]]
        if not plan or plan[0]["layout"] != "full" or float(plan[0]["start"]) > 0.001 or float(plan[0]["end"]) < hook_end - 0.05:
            raise ValueError(f"Cena 0 é o gancho: precisa ser layout 'full' (pessoa na tela) de 0 até pelo menos {hook_end:.1f} s.")
        if plan[0].get("component"):
            raise ValueError("Cena 0 é o gancho: sem componente. O título acima da cabeça vem de assets/hook.json.")

        def layout_at(t):
            return next((s["layout"] for s in plan if float(s["start"]) <= t < float(s["end"])), "full")

        for start, end, lines in caption_chunks(transcript["words"], duration, emphasis, fixes):
            where = layout_at(start)
            if where == "motion" or (where == "split" and not lay.get("split_captions", False)):
                continue  # sem apresentador a tipografia fala por ele; no split o painel explica a fala
            top = lay["caption_top"] if where == "full" else lay["split_caption_top"]
            captions.append({"from": fr(start), "to": max(fr(start) + 2, fr(end)), "top": top, "lines": lines})
            if any(p["key"] for line in lines for p in line):
                hits.append((start, "pop"))
    else:
        if lay["caption_top"] < lay["chin_y"] + 12:
            raise ValueError("Legenda precisa ficar abaixo do queixo.")
        if style == "anuncios" and lay["caption_top"] + cfg["impact_size"] * 1.15 > 1248:
            raise ValueError("Legenda do anúncio fora da área conservadora: reenquadre e ajuste caption_top.")
        for start, end, lines in word_captions(transcript["words"], duration, emphasis, fixes):
            captions.append({"from": fr(start), "to": max(fr(start) + 2, fr(end)), "top": lay["caption_top"], "lines": lines})
            if any(p["key"] for line in lines for p in line):
                hits.append((start, "pop"))
        plan = read(assets / "beats.json") if (assets / "beats.json").exists() else []
        for i, beat in enumerate(plan):
            start, end = float(beat["start"]), float(beat["end"])
            x, y, w, h = [float(beat[k]) for k in ["x", "y", "width", "height"]]
            if start < hook_end:
                raise ValueError(f"Beat {i}: começa no gancho (antes de {hook_end:.1f} s). Nos primeiros segundos, acima da cabeça fica só o título do gancho.")
            if not (0 <= start < end <= duration + 0.001 and 65 <= x and x + w <= 1015 and y >= lay["top_min"] and y + h <= lay["head_top"] - 24):
                raise ValueError(f"Beat {i} fora da duração ou da zona acima da cabeça.")
            item = {"from": fr(start), "to": fr(end), "x": x, "y": y, "w": w, "h": h, "label": beat.get("label", "")}
            if beat.get("kind") == "image":
                relative = Path(beat["src"])
                image = (project / relative).resolve()
                if relative.is_absolute() or project.resolve() not in image.parents or not image.is_file():
                    raise ValueError("Imagem deve existir dentro do projeto.")
                sync_media(image, project / "public" / relative)
                item.update(kind="image", src=relative.as_posix())
            elif style == "anuncios" and beat.get("kind") == "component":
                comp = beat.get("component", "")
                if not NAME.fullmatch(comp) or not (project / "src" / "beats" / f"{comp}.tsx").exists():
                    raise ValueError(f"Beat {i}: componente {comp} não existe em src/beats/{comp}.tsx.")
                beat_names.add(comp)
                item.update(kind="component", component=comp)
            else:
                raise ValueError("Natural aceita prints/imagens; anúncios aceita imagens e componentes TSX locais.")
            beats.append(item)
            # whoosh só para elementos GRANDES se movendo (ou se o plano pedir "whoosh": true)
            if beat.get("whoosh", w * h >= WHOOSH_MIN_AREA):
                hits.append((start - 0.08, "whoosh"))

    # Zoom no rosto: punches de ênfase (zooms.json + palavras de destaque) e respiração contínua discreta
    fz = {"base": 1.02, "breathing": True, "breathing_amp": 0.025, "breathing_period_s": 7, "punch_scale": 1.12,
          "auto_on_emphasis": True, "min_gap_s": 3.0, **cfg.get("face_zoom", {})}
    zooms = []
    manual = read(assets / "zooms.json") if (assets / "zooms.json").exists() else []
    for i, z in enumerate(manual):
        if not (0 <= float(z["start"]) < float(z["end"]) <= duration + 0.001) or not (1.0 < float(z.get("scale", fz["punch_scale"])) <= 1.4):
            raise ValueError(f"Zoom {i}: tempos fora do vídeo ou escala fora de 1.0–1.4.")
        zooms.append({"from": fr(z["start"]), "to": fr(z["end"]), "scale": float(z.get("scale", fz["punch_scale"])), "curve": z.get("curve", "smooth")})
    if fz["auto_on_emphasis"]:
        last = -99.0
        taken = [(z["from"] / FPS, z["to"] / FPS) for z in zooms]
        for c in captions:
            t0, t1 = c["from"] / FPS, c["to"] / FPS
            if not any(p["key"] for line in c["lines"] for p in line) or t0 - last < fz["min_gap_s"]:
                continue
            if any(a - 1 < t0 < b + 1 for a, b in taken):
                continue
            zooms.append({"from": c["from"], "to": c["to"] + 9, "scale": fz["punch_scale"], "curve": "snappy"})
            last = t0
    zooms.sort(key=lambda z: z["from"])
    top, chin = lay.get("head_top", 700), lay.get("chin_y", 1100)
    face_origin = {"x": lay.get("face_x_percent", 50), "y": round((top + chin) / 2 / 1920 * 100, 1)}

    ftc = {"enabled": True, "target_x": 50, "target_y": None, "max_zoom": 1.25, **cfg.get("face_track", {})}
    face_track = None
    ft_path = assets / "face-track.json"
    if ftc["enabled"]:
        if not ft_path.exists():
            print("Aviso: sem assets/face-track.json — rode `editai.py track` para a câmera acompanhar o rosto.")
        else:
            ft = read(ft_path)
            if ft.get("clean_sha256") != fingerprint(clean):
                raise ValueError("Face tracking desatualizado: rode `editai.py track` novamente.")
            if ft["x"]:
                sz = ft.get("s", [])
                face_track = {"x": ft["x"], "y": ft["y"], "s": sz, "sRef": float(sorted(sz)[len(sz) // 2]) if sz else 0}
                if ftc["target_y"] is None:
                    # altura natural do rosto neste vídeo (mediana): centraliza na horizontal e só estabiliza na vertical
                    ys = sorted(ft["y"])
                    ftc["target_y"] = round(ys[len(ys) // 2] * 100, 1)

    registry(project / "src" / "scenes", scene_names, "SCENES")
    registry(project / "src" / "beats", beat_names, "BEATS")
    cam = camera_source(project, clean)
    sync_media(project / cam, project / "public" / "media" / Path(cam).name)
    sync_media(clean, project / "public" / "media" / "clean.mp4")
    for som in SFX_VOLUME:
        if not (project / "public" / "sfx" / f"{som}.wav").exists():
            shutil.copy(SKILL / "assets" / "sfx" / f"{som}.wav", project / "public" / "sfx" / f"{som}.wav")
    highlight = cfg.get("highlight", {})
    data = {
        "style": style, "fps": FPS, "width": 1080, "height": 1920, "durationInFrames": max(1, math.floor(duration * FPS)),
        "cameraSrc": f"media/{Path(cam).name}", "voiceSrc": "media/clean.mp4", "faceYPercent": lay.get("face_y_percent", 30),
        "palette": cfg["palette"],
        "highlight": {"from": highlight.get("from", "#FFB37A"), "via": highlight.get("via", "#FF6D29"), "to": highlight.get("to", "#E04A12"),
                      "glow": highlight.get("glow", "rgba(255,109,41,0.45)"), "glowPx": highlight.get("glow_px", 18)},
        "captionSize": cfg["caption_size"], "impactSize": cfg["impact_size"], "trackingEm": float(cfg["tracking_em"]),
        "lightBackground": bool(cfg.get("light_background", False)), "blurScale": 0.5 if modo_leve(cfg) else 1,
        "captions": captions, "scenes": scenes, "beats": beats, "sfx": sfx_list(hits, duration, cfg),
        "hook": hook, "hookSize": hook_size,
        "faceOrigin": face_origin, "zooms": zooms, "faceTrack": face_track,
        "faceTracking": {"targetX": float(ftc["target_x"]), "targetY": float(ftc["target_y"]) if ftc["target_y"] is not None else face_origin["y"],
                         "maxZoom": float(ftc["max_zoom"])},
        "faceZoom": {"base": float(fz["base"]), "breathing": bool(fz["breathing"]), "breathingAmp": float(fz["breathing_amp"]),
                     "breathingPeriod": max(1, round(float(fz["breathing_period_s"]) * FPS))},
    }
    (project / "src" / "data").mkdir(parents=True, exist_ok=True)
    write(project / "src" / "data" / "edit.json", data)
    print(f"Pronto para o preview: {len(scenes)} cenas, {len(beats)} beats, {len(captions)} legendas, {len(zooms)} zooms no rosto.")
    print("Abra o Remotion Studio (npx remotion studio) e mostre ao aluno. NÃO exporte o MP4 sem aprovação.")

def npx(project, *args):
    return run(["npx.cmd" if sys.platform == "win32" else "npx", *args], cwd=project)

def still(a):
    """Snapshots para conferência (não é o vídeo final): frames em segundos → snapshots/*.png."""
    project = Path(a.project)
    for t in [float(x) for x in a.at.split(",") if x.strip()]:
        npx(project, "remotion", "still", "Editai", str(project / "snapshots" / f"t{t:07.2f}.png"), f"--frame={round(t * FPS)}")

def render(a):
    """MP4 FINAL — só depois de o aluno aprovar o preview no Remotion Studio."""
    if not a.aprovado:
        raise ValueError("Exportação bloqueada: o MP4 final só sai depois da aprovação do aluno no preview do Remotion Studio. Rode com --aprovado quando ele pedir.")
    project = Path(a.project)
    renders = project / "renders"
    renders.mkdir(exist_ok=True)
    out = renders / "final.mp4"
    n = 2
    while out.exists():  # alterações viram final-v2, final-v3... sem apagar o anterior
        out = renders / f"final-v{n}.mp4"
        n += 1
    print("Exportando o MP4 final — esta etapa pode levar alguns minutos.", flush=True)
    npx(project, "remotion", "render", "Editai", str(out), "--codec=h264", "--pixel-format=yuv420p")
    print(out)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("doctor"); p.set_defaults(func=doctor)
    p = sub.add_parser("init"); p.add_argument("video"); p.add_argument("project"); p.add_argument("--style", choices=styles(), required=True); p.set_defaults(func=init)
    p = sub.add_parser("transcribe"); p.add_argument("media"); p.add_argument("output"); p.add_argument("--fast", action="store_true"); p.add_argument("--model"); p.add_argument("--names", default=""); p.set_defaults(func=transcribe)
    p = sub.add_parser("cut"); p.add_argument("project"); p.add_argument("--threshold", type=float, default=-30); p.add_argument("--pause", type=float, default=0.15); p.set_defaults(func=cut)
    p = sub.add_parser("grade"); p.add_argument("project"); p.set_defaults(func=grade)
    p = sub.add_parser("track"); p.add_argument("project"); p.set_defaults(func=track)
    p = sub.add_parser("build"); p.add_argument("project"); p.set_defaults(func=build)
    p = sub.add_parser("still"); p.add_argument("project"); p.add_argument("--at", required=True, help="segundos separados por vírgula"); p.set_defaults(func=still)
    p = sub.add_parser("render"); p.add_argument("project"); p.add_argument("--aprovado", action="store_true"); p.set_defaults(func=render)
    a = parser.parse_args()
    try:
        a.func(a)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
        parser.exit(1, f"Editai: {e}\n")

if __name__ == "__main__":
    main()
