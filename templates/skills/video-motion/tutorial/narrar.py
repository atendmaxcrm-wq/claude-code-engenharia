#!/usr/bin/env python3
# Narração com tempo de cada palavra (ElevenLabs /with-timestamps).
# Uso: export ELEVENLABS_API_KEY=... (ou set -a; . <arquivo .env>; set +a); python3 narrar.py narracao.txt [voz] [modelo]
#   narracao.txt = um bloco (frase/passo) por linha. Números por extenso, siglas como se falam ("Évo" em vez de "EVO").
# Saída: assets/narracao.mp3, assets/palavras.json e assets/palavras.js (window.PAL=[[palavra,inicio,fim],...]).
# Plano free: só vozes "premade" (George JBFqnCBsd6RMkjVDRZzb, Sarah EXAVITQu4vr4xnSDxMaL); vozes brasileiras = plano pago.
import json, os, sys, base64, urllib.request
K = os.environ["ELEVENLABS_API_KEY"]
blocos = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
voz = sys.argv[2] if len(sys.argv) > 2 else "JBFqnCBsd6RMkjVDRZzb"
modelo = sys.argv[3] if len(sys.argv) > 3 else "eleven_v4"
txt = " ... ".join(blocos)   # " ... " = respiro entre blocos (vira o corte de cena)
body = {"text": txt, "model_id": modelo, "language_code": "pt",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3}}
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128",
                             json.dumps(body).encode(), {"xi-api-key": K, "Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=300))
os.makedirs("assets", exist_ok=True)
open("assets/narracao.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
a = d.get("alignment") or d.get("normalized_alignment")
pal, w, s, e = [], "", None, None
for c, x, y in zip(a["characters"], a["character_start_times_seconds"], a["character_end_times_seconds"]):
    if c.strip() and c not in ".,?!…:;":
        if not w: s = x
        w += c; e = y
    elif w:
        pal.append((w, round(s, 2), round(e, 2))); w = ""
if w: pal.append((w, round(s, 2), round(e, 2)))
json.dump(pal, open("assets/palavras.json", "w"), ensure_ascii=False)
open("assets/palavras.js", "w").write("window.PAL=" + json.dumps(pal, ensure_ascii=False) + ";")
print(len(txt), "caracteres;", " ".join(f"{p}@{s}" for p, s, _ in pal))
