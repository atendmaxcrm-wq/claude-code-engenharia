#!/usr/bin/env python3
# Motor do /video-motion: transforma um roteiro.json (cenas de tipos prontos, contadas em batidas) em
#   <projeto>/index.html      composicao HyperFrames (HTML + GSAP) com tempos e dados injetados
#   <projeto>/assets/trilha.wav  musica + efeitos sonoros ja mixados, musica abaixando sob os efeitos, -14 LUFS
# Imagem e som saem dos MESMOS tempos calculados aqui, entao nunca dessincronizam.
#
# uso: python3 montar.py <pasta-do-projeto>        (a pasta precisa ter roteiro.json)
# requer: ffmpeg >= 5 (o instalar.sh deixa um em ~/.video-motion/bin) e Pillow
import json, os, random, shutil, subprocess, sys
from datetime import date

MOTOR = os.path.dirname(os.path.abspath(__file__))
HOME_VM = os.path.expanduser(os.environ.get("VIDEO_MOTION_HOME", "~/.video-motion"))
FF = os.environ.get("VM_FFMPEG") or (os.path.join(HOME_VM, "bin", "ffmpeg") if os.path.exists(os.path.join(HOME_VM, "bin", "ffmpeg")) else "ffmpeg")
TECLA = 0.034                                   # segundos por letra digitada (JS usa o mesmo valor)
FORMATOS = {"9:16": (1080, 1920)}               # v1 da skill: vertical (Reels/Shorts/Stories)

PROJ = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
R = json.load(open(os.path.join(PROJ, "roteiro.json"), encoding="utf-8"))
A = os.path.join(PROJ, "assets"); os.makedirs(A, exist_ok=True)
SFX = os.path.join(A, "sfx"); os.makedirs(SFX, exist_ok=True)

def run(args): subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)
def rel(p): return p if not p or p.startswith(("http", "assets/")) else os.path.relpath(os.path.join(PROJ, p), PROJ)

# ------------------------------------------------------------------ grade de batidas
mus = R["musica"]
BPM = mus.get("bpm")
if not BPM:                                     # detecta com o hyperframes beats e subdivide (padrao: 2x)
    raise SystemExit("roteiro.musica.bpm ausente: rode `hyperframes beats` (o renderizar.sh mostra como) e preencha bpm; use subdivisao 2 pra trilhas trap/hip-hop")
B = 60 / (BPM * mus.get("subdivisao", 1))
W, H = FORMATOS.get(R.get("formato", "9:16"), FORMATOS["9:16"])
FPS = R.get("fps", 30)

# ------------------------------------------------------------------ cor (do logo, se pedido)
def cor_do_logo(caminho):
    from PIL import Image
    im = Image.open(caminho).convert("RGBA").resize((80, 80)); cont = {}
    for r, g, b, a in list(im.getdata()):
        mx, mn = max(r, g, b), min(r, g, b)
        if a < 200 or mx < 70 or (mx - mn) / (mx or 1) < .45: continue
        k = (r // 24, g // 24, b // 24); cont[k] = cont.get(k, 0) + 1
    if not cont: return "#2a7fff"
    k = max(cont, key=cont.get)
    return "#%02x%02x%02x" % tuple(min(255, int((c * 24 + 12) * 1.15)) for c in k)
COR = R.get("cor") or (cor_do_logo(os.path.join(PROJ, R["logo_cor"])) if R.get("logo_cor") else "#2a7fff")

# ------------------------------------------------------------------ agenda: tempos de cada cena e eventos de som
sfx = []                                         # (tempo, arquivo, volume)
random.seed(7)
def ev(t, f, v=1.0): sfx.append((round(t, 3), f, v))
def digitar(t0, texto):
    for i, ch in enumerate(texto):
        if ch != " ": ev(t0 + i * TECLA, f"tecla{random.randint(1, 4)}.wav", 0.55 + random.random() * .25)
def dia(s): d, m, y = map(int, s.split("/")); return date(y, m, d)

cenas, t = [], 0.0
for i, c in enumerate(R["cenas"]):
    c = dict(c)
    if c["tipo"] == "video_palavras": c["batidas"] = sum(x["batidas"] for x in c["clipes"])
    c["t"], c["dur"] = round(t, 3), round(c["batidas"] * B, 3)
    c.setdefault("transicao", "lamina" if i else "nenhuma")
    t += c["batidas"] * B
    cenas.append(c)
TOTAL = round(t, 3)

for i, c in enumerate(cenas):
    s, tp = c["t"], c["tipo"]
    if c["transicao"] == "lamina":
        ev(s - 1.25, "riser.wav", .55); ev(s - .28, "whoosh_lr.wav", .8); ev(s, "subdrop.wav", .9)
    elif c["transicao"] == "flash":
        ev(s, "hit.wav", .9)
    if tp == "titulo":
        c["tLinhas"] = [round(s + B * (1 + 2 * k), 3) for k in range(len(c["linhas"]))]
        for k, tl in enumerate(c["tLinhas"]): ev(tl, "whoosh_rl.wav" if k < len(c["linhas"]) - 1 else "hit.wav", .6 if k < len(c["linhas"]) - 1 else .9)
    elif tp == "destaque":
        c["tImagem"] = round(s + 2 * B, 3); ev(c["tImagem"] + .35, "hit.wav", 1.0)
        c["tNumero"] = round(s + 4 * B, 3)
        if c.get("numero"):
            for k in range(8): ev(c["tNumero"] + k * .14, "tick.wav", .35)
        c["tEtiquetas"] = [round(s + B * (6 + 2 * k), 3) for k in range(len(c.get("etiquetas", [])))]
        for k, e in enumerate(c.get("etiquetas", [])): digitar(c["tEtiquetas"][k] + .05, e.upper())
    elif tp == "grafico_linha":
        c["tDesenho"], c["durDesenho"] = round(s + 3 * B, 3), round(9 * B, 3)
        if c.get("legenda"): digitar(s + .2, c["legenda"].upper())
        h0, h1 = dia(c["serie"][0]["data"]), dia(c["serie"][-1]["data"])
        for m in c.get("marcos", []):
            frac = min(1.0, max(0.0, (dia(m["data"]) - h0).days / ((h1 - h0).days or 1)))
            m["t"] = round(c["tDesenho"] + c["durDesenho"] * frac, 3); ev(m["t"], "pop.wav", .7)
        ev(s + 12 * B, "hit.wav", .8)
    elif tp == "linha_tempo":
        c["tItens"] = [round(s + B * (2 + k * 2.2), 3) for k in range(len(c["itens"]))]
        for k, it in enumerate(c["itens"]):
            ev(c["tItens"][k], "pop.wav", .6)
            if it.get("valor"): digitar(c["tItens"][k] + .25, it["valor"].upper())
    elif tp in ("radar", "barras"):
        passo = 1.6 if tp == "radar" else 2
        c["tItens"] = [round(s + B * (3 + k * passo), 3) for k in range(len(c["itens"]))]
        for tt in c["tItens"]: ev(tt, "tick.wav", .5)
        ev(s + 3 * B, "whoosh_rl.wav", .45)
    elif tp == "video_palavras":
        u = s
        for k, cl in enumerate(c["clipes"]):
            cl["t"], cl["dur"] = round(u, 3), round(cl["batidas"] * B, 3)
            ev(u, "hit.wav", .9)
            if cl.get("congelar_em") is not None: ev(u + cl["congelar_em"], "freeze.wav", .8)
            if cl.get("lento_em") is not None: ev(u + cl["lento_em"], "whoosh_rl.wav", .5)
            u += cl["batidas"] * B
    elif tp == "texto_video":
        ev(s, "subdrop.wav", 1.0); ev(s, "hit.wav", .9)
    elif tp == "numeros":
        c["tItens"] = [round(s + B * (2.5 + k * 1.5), 3) for k in range(len(c["itens"]))]
        for tt in c["tItens"]: ev(tt, "tick.wav", .55)
    elif tp == "mockup":
        c["tAparelho"] = round(s + 2 * B, 3); ev(c["tAparelho"], "whoosh_rl.wav", .6); ev(c["tAparelho"] + .45, "hit.wav", .7)
        c["tRolagem"] = round(s + 5 * B, 3)
        from PIL import Image                     # quanto o print rola dentro da tela do aparelho (medido aqui, nao no navegador)
        iw, ih = Image.open(os.path.join(PROJ, c["imagem"])).size
        dw, dh = (980, 620) if c.get("aparelho") == "notebook" else (600, 1220)
        c["rolagem"] = round(max(0, ih * dw / iw - dh), 1)
        c["tEtiquetas"] = [round(s + B * (6 + 1.5 * k), 3) for k in range(len(c.get("etiquetas", [])))]
        for k, e in enumerate(c.get("etiquetas", [])): ev(c["tEtiquetas"][k], "pop.wav", .6); digitar(c["tEtiquetas"][k] + .2, e.upper())
    elif tp == "assinatura":
        c["tMarca"] = round(s + 3 * B, 3); digitar(c["tMarca"], (c.get("marca") or R.get("marca", "")).upper())
        ev(s + 2 * B, "whoosh_rl.wav", .5)
    else:
        raise SystemExit(f"tipo de cena desconhecido: {tp} (veja cenas.md)")

# ------------------------------------------------------------------ efeitos sonoros sintetizados (nada de terceiros)
def gerar_sfx():
    o = lambda n: os.path.join(SFX, n)
    for i, (f, q) in enumerate([(2600, 3400), (3100, 3900), (2200, 3000), (2900, 4200)], 1):
        run(["-f", "lavfi", "-i", "anoisesrc=d=0.035:c=white:a=0.9", "-f", "lavfi", "-i", f"sine=f={q / 4}:d=0.03",
             "-filter_complex", f"[0]bandpass=f={f}:width_type=h:w=1800,afade=t=out:d=0.03:curve=exp[a];[1]afade=t=out:d=0.025:curve=exp,volume=0.5[b];[a][b]amix=inputs=2:normalize=0,volume=1.4",
             "-ac", "2", "-ar", "48000", o(f"tecla{i}.wav")])
    for nome, ex in (("whoosh_lr", "0.5-0.5*cos(PI*t/0.55)"), ("whoosh_rl", "0.5+0.5*cos(PI*t/0.55)")):
        run(["-f", "lavfi", "-i", "anoisesrc=d=0.55:c=pink:a=0.7", "-af",
             f"highpass=f=350,lowpass=f=6000,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.25,pan=stereo|c0=c0|c1=c0,aeval='val(0)*(1-({ex}))|val(1)*({ex})':c=same,volume=1.6",
             "-ar", "48000", o(nome + ".wav")])
    run(["-f", "lavfi", "-i", "anoisesrc=d=1.25:c=pink:a=0.5", "-f", "lavfi", "-i", "aevalsrc='0.35*sin(2*PI*(200*t+300*t*t))':d=1.25",
         "-filter_complex", "[0]highpass=f=800,volume='t/1.25':eval=frame[a];[1]volume='t/1.25':eval=frame[b];[a][b]amix=inputs=2:normalize=0,afade=t=out:st=1.15:d=0.1",
         "-ac", "2", "-ar", "48000", o("riser.wav")])
    run(["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(85*t-28*t*t))*exp(-3.2*t)':d=0.9", "-ac", "2", "-ar", "48000", o("subdrop.wav")])
    run(["-f", "lavfi", "-i", "sine=f=58:d=0.7", "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=white:a=0.5",
         "-filter_complex", "[0]afade=t=out:st=0.05:d=0.65:curve=exp,volume=1.6[a];[1]lowpass=f=2500,afade=t=out:d=0.08[b];[a][b]amix=inputs=2:normalize=0",
         "-ac", "2", "-ar", "48000", o("hit.wav")])
    run(["-f", "lavfi", "-i", "sine=f=2400:d=0.04", "-af", "afade=t=out:d=0.04,volume=0.5", "-ac", "2", "-ar", "48000", o("tick.wav")])
    run(["-f", "lavfi", "-i", "aevalsrc='0.6*sin(2*PI*(520*t+900*t*t))*exp(-18*t)':d=0.16", "-ac", "2", "-ar", "48000", o("pop.wav")])
    run(["-f", "lavfi", "-i", "aevalsrc='0.4*(sin(2*PI*1320*t)+0.6*sin(2*PI*1980*t))*exp(-4*t)':d=0.9", "-ac", "2", "-ar", "48000", o("freeze.wav")])

def gerar_trilha():
    bruta = os.path.join(A, "musica_bruta.wav")
    run(["-ss", str(mus.get("inicio", 0)), "-t", f"{TOTAL + .5:.3f}", "-i", os.path.join(PROJ, mus["arquivo"]), "-vn", "-ac", "2", "-ar", "48000", bruta])
    ins, fil = ["-i", bruta], []
    for k, (t0, f, v) in enumerate(sfx):
        ins += ["-i", os.path.join(SFX, f)]; ms = max(0, int(t0 * 1000))
        fil.append(f"[{k + 1}]adelay={ms}|{ms},volume={v:.2f}[s{k}]")
    n = len(sfx)
    fil.append("".join(f"[s{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL:.3f}[fx]")
    fil.append("[fx]asplit=2[fx1][fxsc]")
    fil.append(f"[0]volume={mus.get('volume', 0.8)},afade=t=out:st={TOTAL - 1.8:.2f}:d=1.8[mu]")
    fil.append("[mu][fxsc]sidechaincompress=threshold=0.04:ratio=5:attack=5:release=280[duck]")
    fil.append(f"[duck][fx1]amix=inputs=2:normalize=0,atrim=0:{TOTAL:.3f},loudnorm=I=-14:TP=-1:LRA=11[out]")
    run(ins + ["-filter_complex", ";".join(fil), "-map", "[out]", "-ar", "48000", "-ac", "2", os.path.join(A, "trilha.wav")])

gerar_sfx(); gerar_trilha()

# ------------------------------------------------------------------ esqueleto HTML (atributos de tempo precisam ser estaticos)
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
cenas_html, midia_html = [], []
for i, c in enumerate(cenas):
    tp, s, d = c["tipo"], c["t"], c["dur"]
    inner = ""
    if tp == "video_palavras":
        for k, cl in enumerate(c["clipes"]):
            inner += f'<div class="h clip" id="c{i}p{k}" data-start="{cl["t"]:.3f}" data-duration="{cl["dur"]:.3f}" style="top:290px;font-size:150px"></div>'
            inner += f'<div class="idx clip" id="c{i}x{k}" data-start="{cl["t"]:.3f}" data-duration="{cl["dur"]:.3f}" style="top:330px;left:auto">{esc(cl.get("indice", ""))}</div>'
        vids = "".join(f'<video id="c{i}v{k}" class="clip" data-start="{cl["t"]:.3f}" data-duration="{cl["dur"]:.3f}" src="{esc(rel(cl["video"]))}" muted playsinline style="object-position:{esc(cl.get("alinhamento", "50% 50%"))}"></video>' for k, cl in enumerate(c["clipes"]))
        midia_html.append(f'<div class="card" id="c{i}card" style="left:66px;top:560px;width:948px;height:1180px">{vids}<div class="spot" id="c{i}spot"></div><div class="anel" id="c{i}anel"></div><div class="anelTag" id="c{i}anelTag"></div><div class="lento" id="c{i}lento">CÂMERA LENTA</div><div class="tagcard" id="c{i}tag"></div></div>')
    elif tp == "texto_video":
        midia_html.append(f'<div class="golbox" id="c{i}box"><video id="c{i}v" class="clip" data-start="{s:.3f}" data-duration="{d:.3f}" src="{esc(rel(c["video"]))}" muted playsinline></video><div class="golt" id="c{i}txt" style="font-size:{c.get("tamanho", 440)}px">{esc(c["texto"])}</div></div>')
    elif tp == "assinatura" and c.get("video"):
        dv = min(d, c.get("video_duracao", 2.4))
        midia_html.append(f'<div class="card" id="c{i}card" style="left:270px;top:330px;width:540px;height:720px"><video id="c{i}v" class="clip" data-start="{s:.3f}" data-duration="{dv:.3f}" src="{esc(rel(c["video"]))}" muted playsinline></video></div>')
        c["videoDur"] = dv
    cenas_html.append(f'<div id="c{i}" class="clip cena cena-{tp}" data-start="{s:.3f}" data-duration="{d:.3f}">{inner}</div>')

fundo_html = ""
if R.get("fundo_video"):
    ate = cenas[min(len(cenas) - 1, R.get("fundo_ate_cena", 1) + 1)]["t"] if len(cenas) > 1 else TOTAL
    fundo_html = f'<video id="fundo" class="clip" data-start="0" data-duration="{ate:.3f}" src="{esc(rel(R["fundo_video"]))}" muted playsinline></video>'
    R["_fundoAte"] = ate

for c in cenas:                                   # caminhos de imagens relativos ao projeto
    for k in ("imagem",):
        if c.get(k): c[k] = rel(c[k])
    for lst in ("marcos", "itens"):
        for it in c.get(lst, []) if isinstance(c.get(lst), list) else []:
            if isinstance(it, dict) and it.get("icone"): it["icone"] = rel(it["icone"])

DADOS = {"cor": COR, "marca": R.get("marca", ""), "rotulo": R.get("rotulo", ""), "cenas": cenas, "total": TOTAL,
         "B": B, "tecla": TECLA, "fundoAte": R.get("_fundoAte")}
html = open(os.path.join(MOTOR, "template.html"), encoding="utf-8").read()
html = (html.replace("{{W}}", str(W)).replace("{{H}}", str(H)).replace("{{FPS}}", str(FPS)).replace("{{TOTAL}}", f"{TOTAL:.3f}")
        .replace("<!--FUNDO-->", fundo_html).replace("<!--CENAS-->", "\n".join(cenas_html)).replace("<!--MIDIA-->", "\n".join(midia_html))
        .replace("/*DADOS*/{}", json.dumps(DADOS, ensure_ascii=False)))
assert "{{" not in html, "marcador sem valor no template"
open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8").write(html)
# dependencias que o instalar.sh deixa em ~/.video-motion (a skill so carrega texto)
gsap = os.path.join(HOME_VM, "hf", "node_modules", "gsap", "dist", "gsap.min.js")
if not os.path.exists(gsap): raise SystemExit("gsap nao encontrado: rode instalar.sh")
shutil.copy(gsap, os.path.join(PROJ, "gsap.min.js"))
fdir = os.path.join(A, "fonts"); os.makedirs(fdir, exist_ok=True)
for f in ("InterTight.ttf", "JetBrainsMono.ttf"):
    src = os.path.join(HOME_VM, "fonts", f)
    if not os.path.exists(src): raise SystemExit(f"fonte {f} ausente: rode instalar.sh")
    shutil.copy(src, os.path.join(fdir, f))
grao = os.path.join(A, "grain.png")
if not os.path.exists(grao):                    # textura de grao de filme (ruido fixo, semente 7)
    from PIL import Image
    rnd = random.Random(7)
    Image.frombytes("L", (512, 512), bytes(rnd.randrange(256) for _ in range(512 * 512))).save(grao)

print(f"ok | {len(cenas)} cenas | {TOTAL:.1f} s | {FPS} fps | cor {COR} | {len(sfx)} efeitos sonoros")
for c in cenas: print(f"  {c['t']:6.2f}s  {c['tipo']:<15} {c['batidas']:>3} batidas")
