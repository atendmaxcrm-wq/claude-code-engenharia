#!/usr/bin/env python3
# Gemini ouve a narração e aponta pronúncia ruim (chave Gemini do projeto do cliente, nunca a do CRMAX).
# Uso: GEMINI_API_KEY=... python3 ouvir.py assets/narracao.mp3
import json, os, sys, base64, urllib.request
b = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
q = ("Ouça esta narração em português brasileiro de um tutorial de software. 1) Transcreva. 2) Liste palavras mal pronunciadas "
     "ou estranhas para um brasileiro (siglas, termos em inglês), com o tempo. 3) Nota 0-10 de clareza e de naturalidade. Seja breve.")
body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/mpeg", "data": b}}, {"text": q}]}]}
r = urllib.request.urlopen(urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=" + os.environ["GEMINI_API_KEY"],
                           data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=120)
print(json.load(r)["candidates"][0]["content"]["parts"][0]["text"])
