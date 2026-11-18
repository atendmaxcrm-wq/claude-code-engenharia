#!/usr/bin/env python3
# Gemini ouve a MIXAGEM final (voz + trilha + efeitos) e aponta onde algo cobre a voz ou incomoda.
# Uso: GEMINI_API_KEY=... python3 -I ouvir_mix.py out/mix.wav "descrição curta dos sons (ex.: viola, cigarras, chocalho)"
# Chave: a do projeto do cliente; em vídeo pessoal do dono, a do .mcp.json (liberada SÓ para ouvir/transcrever áudio).
import json, os, sys, base64, subprocess, urllib.request
src = sys.argv[1]; desc = sys.argv[2] if len(sys.argv) > 2 else "trilha e efeitos"
mp3 = src.rsplit('.', 1)[0] + '-ouvir.mp3'
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-b:a", "96k", mp3], check=True)
b = base64.b64encode(open(mp3, 'rb').read()).decode()
q = (f"Ouça esta mixagem de um vídeo curto narrado (voz + {desc}). Seja breve e crítico: 1) a voz fica clara acima de tudo? "
     "cite segundos onde algo cobre a voz. 2) algum efeito alto demais, agudo, estalo ou chiado? com segundos. 3) nota 0-10.")
body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mpeg", "data": b}}, {"text": q}]}]}
r = urllib.request.urlopen(urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=" + os.environ["GEMINI_API_KEY"],
                           data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=180)
print(json.load(r)["candidates"][0]["content"]["parts"][0]["text"])
