"""Ferramentas locais Editai Motion / Naamã. Python 3.10+, FFmpeg e faster-whisper."""
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

LAYOUTS = {"full", "split", "motion"}


def caption_chunks(words, duration, emphasis, fixes, max_words=3, max_chars=18):
    """Agrupa palavras em blocos de 2-3 palavras, quebrando em pausas e pontuacao."""
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
            chars = sum(len(t) + 1 for _, t in current) + len(text)
            if gap > 0.25 or len(current) >= max_words or chars > max_chars:
                close()
        current.append((i, text))
        if re.search(r"[.!?,;:]$", text):
            close()
    close()

    out = []
    for n, chunk in enumerate(chunks):
        start = float(words[chunk[0][0]]["start"])
        nxt = float(words[chunks[n + 1][0][0]]["start"]) if n + 1 < len(chunks) else duration
        end = min(nxt, float(words[chunk[-1][0]]["end"]) + 0.6)
        if end <= start:
            continue
        parts = []
        for i, text in chunk:
            safe = html.escape(text)
            parts.append(f'<span class="key">{safe}</span>' if i in marked else safe)
        out.append((start, end, " ".join(parts)))
    return out


def build(a):
    project = Path(a.project)
    cfg = read(project / "editai.json")
    clean = project / "assets" / "clean.mp4"
    transcript = read(project / "assets" / "transcript.json")
    if transcript["source_sha256"] != fingerprint(clean):
        raise ValueError("Transcrição desatualizada: transcreva clean.mp4 novamente.")
    duration = float(probe(clean)["format"]["duration"])
    if duration > cfg["max_duration"] + 0.1:
        raise ValueError("Vídeo excede o limite configurado.")
    assets = project / "assets"
    emphasis = read(assets / "emphasis.json") if (assets / "emphasis.json").exists() else []
    fixes = read(assets / "caption-fixes.json") if (assets / "caption-fixes.json").exists() else []
    scenes = read(assets / "scenes.json")

    # Cenas: ordenadas, sem sobreposicao; buracos viram tela cheia
    previous = 0.0
    for n, s in enumerate(scenes):
        if s.get("layout") not in LAYOUTS:
            raise ValueError(f"Cena {n}: layout deve ser full, split ou motion.")
        if not (previous - 0.001 <= float(s["start"]) < float(s["end"]) <= duration + 0.001):
            raise ValueError(f"Cena {n}: tempos fora de ordem, sobrepostos ou além do vídeo.")
        previous = float(s["end"])

    def layout_at(t):
        for s in scenes:
            if float(s["start"]) <= t < float(s["end"]):
                return s["layout"]
        return "full"

    lay = cfg["layout"]
    captions = []
    for n, (start, end, text) in enumerate(caption_chunks(transcript["words"], duration, emphasis, fixes)):
        where = layout_at(start)
        if where == "motion":
            continue  # sem apresentador: a tipografia cinetica da cena fala por ele
        if where == "split" and not lay.get("split_captions", False):
            continue  # no split o queixo fica sob a interface do Reels; o painel explica a fala
        top = lay["caption_top"] if where == "full" else lay["split_caption_top"]
        captions.append(f'<div id="cap-{n}" class="clip caption" data-start="{start:.3f}" '
                        f'data-duration="{end - start:.3f}" data-track-index="4" style="top:{top}px">{text}</div>')

    panels, scripts, camera = [], [], []
    for n, s in enumerate(scenes):
        start, end = float(s["start"]), float(s["end"])
        camera.append({"t": start, "layout": s["layout"]})
        if s.get("html"):
            # HTML escrito localmente pelo agente para esta cena; nunca markup remoto
            panels.append(f'<div id="scene-{n}" class="clip scene {s["layout"]}" data-start="{start:.3f}" '
                          f'data-duration="{end - start:.3f}" data-track-index="3">{s["html"]}</div>')
        if s.get("js"):
            # Keyframes da cena: recebe a timeline (tl), o inicio (t0) e o elemento da cena (el)
            scripts.append(f"(function(tl,t0,el){{{s['js']}}})(timeline,{start},document.getElementById('scene-{n}'));")

    gsap = project / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    if not gsap.exists():
        raise ValueError("Execute npm install na pasta do projeto para instalar GSAP e Hyperframes.")
    shutil.copy(gsap, assets / "gsap.min.js")
    text = (project / "src" / "composition.html").read_text(encoding="utf-8")
    pal = cfg["palette"]
    for key, value in pal.items():
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("Cor inválida na paleta.")
    variables = {
        "DURATION": f"{duration:.3f}", "CAPTIONS": "\n".join(captions), "PANELS": "\n".join(panels),
        "SCENE_SCRIPTS": "\n".join(scripts), "CAMERA": json.dumps(camera),
        "CAP_SIZE": str(cfg["caption_size"]), "IMPACT_SIZE": str(cfg["impact_size"]),
        "FACE_Y": str(lay.get("face_y_percent", 30)),
        "ORANGE": pal["orange"], "BROWN": pal["brown"], "INK": pal["ink"], "PAPER": pal["off_white"],
    }
    for key, value in variables.items():
        text = text.replace("__" + key + "__", value)
    if re.search(r"__[A-Z_]+__", text):
        raise ValueError("Composição contém variáveis não resolvidas.")
    (project / "index.html").write_text(text, encoding="utf-8")
    print(f"Composição pronta: {len(scenes)} cenas, {len(captions)} blocos de legenda. Veja os snapshots antes do MP4.")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("doctor"); p.set_defaults(func=doctor)
    p = sub.add_parser("init"); p.add_argument("video"); p.add_argument("project"); p.add_argument("--style", choices=["motion"], required=True); p.set_defaults(func=init)
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
