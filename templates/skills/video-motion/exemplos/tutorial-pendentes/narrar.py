#!/usr/bin/env python3
# Narração do tutorial do Pendentes (George, eleven_v4) com tempo de cada palavra -> assets/narracao.mp3 + assets/palavras.json
# Rodar: export ELEVENLABS_API_KEY=... (ou set -a; . <arquivo .env>; set +a); python3 narrar.py
import json, os, base64, urllib.request

K = os.environ["ELEVENLABS_API_KEY"]
BLOCOS = [
    "Sabe aquela lista de ligações do EVO? Agora ela está dentro do Chatwoot.",
    "No menu da esquerda, logo abaixo de Não atendidas, fica o Pendentes. O número amarelo é quanta gente você tem pra chamar hoje.",
    "Lá dentro tem três abas: Hoje, Atrasados e Amanhã.",
    "Cada linha é uma ligação agendada no EVO: o nome, se é aluno ou oportunidade, e o assunto.",
    "Se a pessoa já conversa com você, toque em Abrir conversa e você cai direto no chat.",
    "Se ainda não tem conversa, toque em Chamar. A conversa abre no número oficial, já no seu nome. Aí é só escolher o template e enviar.",
    "Na aba Pipeline você vê de quem é o aluno na carteira, quem atendeu por último e o histórico do EVO.",
    "Depois de falar com a pessoa, registre o relacionamento com a data do próximo contato.",
    "Pronto. O registro entra no EVO no seu nome, e a pessoa sai da sua lista. Ela só volta no dia que você marcou.",
    "Lista zerada, dia ganho. Bora chamar!",
]
TXT = " ... ".join(BLOCOS)
body = {"text": TXT, "model_id": "eleven_v4", "language_code": "pt",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3}}
req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb/with-timestamps?output_format=mp3_44100_128",
    json.dumps(body).encode(), {"xi-api-key": K, "Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=300))
os.makedirs("assets", exist_ok=True)
open("assets/narracao.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
a = d.get("alignment") or d.get("normalized_alignment")
pal, w, s, e = [], "", None, None
for c, x, y in zip(a["characters"], a["character_start_times_seconds"], a["character_end_times_seconds"]):
    if c.strip() and c not in ".,?!…:":
        if not w:
            s = x
        w += c
        e = y
    elif w:
        pal.append((w, round(s, 2), round(e, 2)))
        w = ""
if w:
    pal.append((w, round(s, 2), round(e, 2)))
json.dump(pal, open("assets/palavras.json", "w"), ensure_ascii=False)
print(len(TXT), "caracteres;", " ".join(f"{p}@{s}" for p, s, _ in pal))
