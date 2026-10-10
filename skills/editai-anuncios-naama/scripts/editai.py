"""Ferramentas locais Editai / Naamã. Python 3.10+, FFmpeg e faster-whisper."""
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
    for name in ["ffmpeg", "ffprobe", "node", "npm"]:
        print(f"{name}: {shutil.which(name) or 'AUSENTE'}")
    import importlib.util
    print("faster-whisper:", "OK" if importlib.util.find_spec("faster_whisper") else "AUSENTE")
    for name in ["Helvetica-Regular.otf", "Scholar-Italic.otf"]:
        print(name, "OK" if (SKILL / "assets" / "fonts" / name).exists() else "AUSENTE")

def init(a):
    src, project = Path(a.video).resolve(), Path(a.project).resolve()
    if project.exists():
        raise ValueError("Projeto já existe; escolha outra pasta para preservar o trabalho.")
    info = probe(src)
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        raise ValueError("O vídeo precisa conter áudio para transcrição.")
    for folder in ["assets/fonts", "assets/prints", "src", "renders", "snapshots"]:
        (project / folder).mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL / "assets" / "fonts", project / "assets" / "fonts", dirs_exist_ok=True)
    shutil.copy(SKILL / "assets" / "composition.html", project / "src" / "composition.html")
    config = read(SKILL / "assets" / "design.json")
    config["style"] = a.style
    write(project / "editai.json", config)
    write(project / "package.json", {"private": True, "name": "editai-video", "dependencies": {"hyperframes": "0.8.143", "gsap": "3.15.0"}})
    write(project / "assets" / "source.json", {"path": str(src), "sha256": fingerprint(src)})
    print("Preparando vídeo — esta etapa pode levar alguns minutos.", flush=True)
    run(["ffmpeg", "-v", "error", "-i", src, "-map", "0:v:0", "-map", "0:a:0", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", *encoder(), "-r", "30", "-c:a", "aac", "-b:a", "192k", project / "assets" / "raw.mp4"])
    print(project)

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

def fixes_text(fixes, i, words):
    for fix in fixes:
        if fix["index"] == i:
            return fix["text"].strip()
    return words[i]["text"].strip()

# Volumes pensados para ficar audivel mas confortavel por baixo da voz (voz = 1)
SFX_VOLUME = {"whoosh": 0.35, "pop": 0.14, "tick": 0.12}
SFX_DUR = {"whoosh": 0.55, "pop": 0.18, "tick": 0.07}

def sfx_tags(project, hits, duration, cfg):
    """hits = [(tempo, tipo)]. Copia os sons da skill para o projeto e devolve as tags <audio>."""
    if not cfg.get("sfx", True):
        return ""
    destino = project / "assets" / "sfx"
    destino.mkdir(parents=True, exist_ok=True)
    for som in SFX_VOLUME:
        if not (destino / f"{som}.wav").exists():
            shutil.copy(SKILL / "assets" / "sfx" / f"{som}.wav", destino / f"{som}.wav")
    ganho = float(cfg.get("sfx_volume", 1.0))
    tags, ultimo = [], {}
    for n, (t, som) in enumerate(sorted(hits)):
        # Um som de cada tipo por vez: evita encavalar e embolar
        if t < 0 or t >= duration or t - ultimo.get(som, -9) < SFX_DUR[som] + 0.05:
            continue
        ultimo[som] = t
        d = min(SFX_DUR[som], duration - t)
        tags.append(f'<audio id="sfx-{n}" src="assets/sfx/{som}.wav" data-start="{t:.3f}" data-duration="{d:.3f}" '
                    f'data-track-index="{ {"whoosh": 6, "pop": 7, "tick": 8}[som] }" data-volume="{SFX_VOLUME[som] * ganho:.3f}"></audio>')
    return "\n".join(tags)

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

def build(a):
    project = Path(a.project)
    cfg = read(project / "editai.json")
    transcript = read(project / "assets" / "transcript.json")
    if transcript["source_sha256"] != fingerprint(project / "assets" / "clean.mp4"):
        raise ValueError("Transcrição desatualizada: transcreva clean.mp4 novamente.")
    duration = float(probe(project / "assets" / "clean.mp4")["format"]["duration"])
    if duration > cfg["max_duration"] + 0.1:
        raise ValueError("Vídeo excede o limite configurado.")
    layout = cfg["layout"]
    if layout["caption_top"] < layout["chin_y"] + 12:
        raise ValueError("Legenda precisa ficar abaixo do queixo.")
    if cfg["style"] == "anuncios" and layout["caption_top"] + cfg["impact_size"] * 1.15 > 1248:
        raise ValueError("Legenda do anúncio fora da área conservadora: reenquadre e ajuste caption_top.")
    emphasis = read(project / "assets" / "emphasis.json") if (project / "assets" / "emphasis.json").exists() else []
    fixes = read(project / "assets" / "caption-fixes.json") if (project / "assets" / "caption-fixes.json").exists() else []
    words = transcript["words"]
    captions, motions = [], []
    for i, word in enumerate(words):
        start = float(word["start"])
        end = min(float(words[i + 1]["start"]) if i + 1 < len(words) else duration, start + 1.2)
        text = word["text"]
        for fix in fixes:
            if fix["index"] == i:
                text = fix["text"]
        if not text or end <= start:
            continue
        impact = any(x["index"] == i for x in emphasis)
        if impact:
            # Enfase: a palavra anterior fica em cima e a de impacto entra MAIOR na linha de baixo
            prev = next((fixes_text(fixes, j, words) for j in range(i - 1, -1, -1) if fixes_text(fixes, j, words)), "")
            top = f'<span class="prev">{html.escape(prev)}</span><br>' if prev else ""
            captions.append(f'<div id="word-{i}" class="clip caption" data-start="{start:.3f}" data-duration="{end-start:.3f}" data-track-index="2">'
                            f'{top}<span id="imp-{i}" class="impact">{html.escape(text)}</span></div>')
            # Subida curta (14 px) e rapida, assentando suave
            motions.append({"id": f"imp-{i}", "start": start, "duration": min(0.32, (end - start) * 0.7), "y": 14, "scale": 1, "blur": 4})
        else:
            captions.append(f'<div id="word-{i}" class="clip caption" data-start="{start:.3f}" data-duration="{end-start:.3f}" data-track-index="2">{html.escape(text)}</div>')
            # Legenda corrida: sobe pouco, acelera e desacelera (estilo Apple)
            motions.append({"id": f"word-{i}", "start": start, "duration": min(0.24, (end - start) * 0.8), "y": 12, "scale": 1, "blur": 2, "ease": "power2.inOut"})
    hits = [(m["start"], "pop") for m in motions if m["id"].startswith("imp-")]
    beats = read(project / "assets" / "beats.json") if (project / "assets" / "beats.json").exists() else []
    overlays = []
    for i, beat in enumerate(beats):
        start, end = float(beat["start"]), float(beat["end"])
        x, y, w, h = [float(beat[k]) for k in ["x", "y", "width", "height"]]
        if not (0 <= start < end <= duration + 0.001 and 65 <= x and x+w <= 1015 and y >= layout["top_min"] and y+h <= layout["head_top"]-24):
            raise ValueError(f"Beat {i} fora da duração ou da zona acima da cabeça.")
        if beat.get("kind") == "image":
            relative = Path(beat["src"])
            image = (project / relative).resolve()
            if relative.is_absolute() or project.resolve() not in image.parents or not image.is_file():
                raise ValueError("Imagem deve existir dentro do projeto.")
            content = f'<img src="{html.escape(relative.as_posix(), quote=True)}" alt="{html.escape(beat.get("label", ""), quote=True)}">'
        elif cfg["style"] == "anuncios" and beat.get("kind") == "html":
            # HTML local escrito pelo agente; nunca inserir markup remoto sem inspeção.
            content = beat["html"]
        else:
            raise ValueError("Natural aceita prints/imagens; anúncios aceita imagens e HTML local.")
        overlays.append(f'<div id="beat-{i}" class="clip overlay" data-start="{start}" data-duration="{end-start}" data-track-index="3" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{content}</div>')
        # Entrada longa com desaceleracao, deriva sutil enquanto fica na tela e saida com aceleracao + blur
        motions.append({"id": f"beat-{i}", "start": start, "end": end, "duration": min(0.6, (end - start) * 0.35), "y": 28, "scale": 0.96, "blur": 10, "drift": True})
    gsap = project / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    if not gsap.exists():
        raise ValueError("Execute npm install na pasta do projeto para instalar GSAP e Hyperframes.")
    shutil.copy(gsap, project / "assets" / "gsap.min.js")
    text = (project / "src" / "composition.html").read_text(encoding="utf-8")
    variables = {"DURATION": str(duration), "CAPTIONS": "\n".join(captions), "OVERLAYS": "\n".join(overlays), "MOTIONS": json.dumps(motions), "SFX": sfx_tags(project, hits + [(m["start"] - 0.08, "whoosh") for m in motions if m["id"].startswith("beat-")], duration, cfg), "BLUR": "0.5" if modo_leve(cfg) else "1", "STYLE": cfg["style"], "CAP_TOP": str(layout["caption_top"]), "CAP_SIZE": str(cfg["caption_size"]), "IMPACT_SIZE": str(cfg["impact_size"]), "SHADOW": "0 2px 8px rgba(0,0,0,.35)" if cfg["light_background"] else "none"}
    for key, value in variables.items():
        text = text.replace("__" + key + "__", value)
    for key, value in cfg["palette"].items():
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("Cor inválida na paleta.")
        csskey = {"off_white": "paper"}.get(key, key)
        text = re.sub(r"(--" + csskey + r":)#[0-9a-fA-F]{6}", lambda m: m[1] + value, text)
    text = text.replace("letter-spacing:-.05em", f'letter-spacing:{float(cfg["tracking_em"])}em')
    if re.search(r"__[A-Z_]+__", text):
        raise ValueError("Composição contém variáveis não resolvidas.")
    (project / "index.html").write_text(text, encoding="utf-8")
    print("Composição pronta para lint e snapshots; veja as imagens antes do MP4.")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("doctor"); p.set_defaults(func=doctor)
    p = sub.add_parser("init"); p.add_argument("video"); p.add_argument("project"); p.add_argument("--style", choices=["natural", "anuncios"], required=True); p.set_defaults(func=init)
    p = sub.add_parser("transcribe"); p.add_argument("media"); p.add_argument("output"); p.add_argument("--fast", action="store_true"); p.add_argument("--model"); p.add_argument("--names", default=""); p.set_defaults(func=transcribe)
    p = sub.add_parser("cut"); p.add_argument("project"); p.add_argument("--threshold", type=float, default=-30); p.add_argument("--pause", type=float, default=0.15); p.set_defaults(func=cut)
    p = sub.add_parser("build"); p.add_argument("project"); p.set_defaults(func=build)
    a = parser.parse_args()
    try:
        a.func(a)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
        parser.exit(1, f"Editai: {e}\n")

if __name__ == "__main__":
    main()
