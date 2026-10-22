#!/usr/bin/env python3
# Motor do /video-motion: transforma um roteiro.json (cenas de tipos prontos, contadas em batidas) em
#   <projeto>/index.html      composicao HyperFrames (HTML + GSAP) com tempos e dados injetados
#   <projeto>/assets/trilha.wav  musica + efeitos sonoros ja mixados, musica abaixando sob os efeitos, -14 LUFS
# Imagem e som saem dos MESMOS tempos calculados aqui, entao nunca dessincronizam.
#
# Tambem escreve <projeto>/out/batidas.md (tabela batida a batida: cena, o que acontece, som) e out/batidas.json
# (tempos de cada batida, usados pelo revisar.sh) e avisa tempo morto (mais de 4 s sem nada novo na tela).
#
# uso: python3 montar.py <pasta-do-projeto>        (a pasta precisa ter roteiro.json)
#      VM_FORMATO=16:9 python3 montar.py <pasta>    (outro formato a partir do mesmo roteiro)
# requer: ffmpeg >= 5 (o instalar.sh deixa um em ~/.video-motion/bin), Pillow e numpy
import json, os, random, shutil, subprocess, sys
from datetime import date

MOTOR = os.path.dirname(os.path.abspath(__file__))
HOME_VM = os.path.expanduser(os.environ.get("VIDEO_MOTION_HOME", "~/.video-motion"))
FF = os.environ.get("VM_FFMPEG") or (os.path.join(HOME_VM, "bin", "ffmpeg") if os.path.exists(os.path.join(HOME_VM, "bin", "ffmpeg")) else "ffmpeg")
TECLA = 0.034                                   # segundos por letra digitada (JS usa o mesmo valor)
FORMATOS = {"9:16": (1080, 1920), "1:1": (1080, 1080), "16:9": (1920, 1080)}
SO_VERTICAL = {"destaque", "grafico_linha", "linha_tempo", "radar", "barras", "video_palavras", "texto_video", "numeros", "mockup"}

PROJ = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
R = json.load(open(os.path.join(PROJ, "roteiro.json"), encoding="utf-8"))
KIT = os.path.join(PROJ, R.get("kit_marca", "marca.json"))   # gerado pelo capturar_marca.sh; o roteiro sobrescreve
if os.path.exists(KIT) and R.get("kit_marca", True):
    for k, v in json.load(open(KIT, encoding="utf-8")).items(): R.setdefault(k, v)
A = os.path.join(PROJ, "assets"); os.makedirs(A, exist_ok=True)
OUT = os.path.join(PROJ, "out"); os.makedirs(OUT, exist_ok=True)
SFX = os.path.join(A, "sfx"); os.makedirs(SFX, exist_ok=True)

def run(args): subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)
def rel(p): return p if not p or p.startswith(("http", "assets/")) else os.path.relpath(os.path.join(PROJ, p), PROJ)

# ------------------------------------------------------------------ grade de batidas
mus = R["musica"]
BPM = mus.get("bpm")
SINTETICA = mus.get("sintetizar") or not mus.get("arquivo")   # sem faixa = trilha original em codigo
if SINTETICA and not BPM: BPM = mus["bpm"] = 120
if not BPM:                                     # detecta com o hyperframes beats e subdivide (padrao: 2x)
    raise SystemExit("roteiro.musica.bpm ausente: rode `hyperframes beats` (o renderizar.sh mostra como) e preencha bpm; use subdivisao 2 pra trilhas trap/hip-hop")
B = 60 / (BPM * mus.get("subdivisao", 1))
FORMATO = os.environ.get("VM_FORMATO") or R.get("formato", "9:16")
if FORMATO not in FORMATOS: raise SystemExit(f"formato {FORMATO} invalido: use {', '.join(FORMATOS)}")
W, H = FORMATOS[FORMATO]
if FORMATO != "9:16":
    ruins = sorted({c["tipo"] for c in R["cenas"] if c["tipo"] in SO_VERTICAL} | {"assinatura com video" for c in R["cenas"] if c["tipo"] == "assinatura" and c.get("video")})
    if ruins: raise SystemExit(f"formato {FORMATO}: estas cenas so existem na vertical: {', '.join(ruins)} (use titulo, ui_produto, livre e assinatura)")
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
acoes = []                                       # (tempo, texto) -> tabela de batidas e checagem de tempo morto
random.seed(7)
def ev(t, f, v=1.0): sfx.append((round(t, 3), f, v))
def acao(t, txt): acoes.append((round(t, 3), txt))
def digitar(t0, texto):
    for i, ch in enumerate(texto):
        if ch != " ": ev(t0 + i * TECLA, f"tecla{random.randint(1, 4)}.wav", 0.55 + random.random() * .25)
def dia(s): d, m, y = map(int, s.split("/")); return date(y, m, d)

cenas, t = [], 0.0
for i, c in enumerate(R["cenas"]):
    c = dict(c)
    if c["tipo"] == "video_palavras": c["batidas"] = sum(x["batidas"] for x in c["clipes"])
    if c["tipo"] == "ui_produto": c["batidas"] = sum(x["batidas"] for x in c["estados"])
    c["t"], c["dur"] = round(t, 3), round(c["batidas"] * B, 3)
    c.setdefault("transicao", "lamina" if i else "nenhuma")
    t += c["batidas"] * B
    cenas.append(c)
TOTAL = round(t, 3)

SONS = {"hit": "hit.wav", "pop": "pop.wav", "tick": "tick.wav", "clique": "clique.wav", "sopro": "sopro.wav", "whoosh": "whoosh_rl.wav",
        "whoosh_lr": "whoosh_lr.wav", "riser": "riser.wav", "subdrop": "subdrop.wav", "freeze": "freeze.wav"}
for i, c in enumerate(cenas):
    s, tp = c["t"], c["tipo"]
    acao(s, f"entra {tp}" + (f" ({c['transicao']})" if c["transicao"] != "nenhuma" else ""))
    if c["transicao"] == "lamina":
        ev(s - 1.25, "riser.wav", .55); ev(s - .28, "whoosh_lr.wav", .8); ev(s, "subdrop.wav", .9)
    elif c["transicao"] == "flash":
        ev(s, "hit.wav", .9)
    if tp == "titulo":
        c["tLinhas"] = [round(s + B * (1 + c.get("passo", 2) * k), 3) for k in range(len(c["linhas"]))]
        for k, tl in enumerate(c["tLinhas"]): acao(tl, f'linha "{c["linhas"][k].replace("*", "")}"')
        for k, tl in enumerate(c["tLinhas"]): ev(tl, "whoosh_rl.wav" if k < len(c["linhas"]) - 1 else "hit.wav", .6 if k < len(c["linhas"]) - 1 else .9)
    elif tp == "destaque":
        c["tImagem"] = round(s + 2 * B, 3); ev(c["tImagem"] + .35, "hit.wav", 1.0); acao(c["tImagem"], "imagem sobe na frente da palavra")
        c["tNumero"] = round(s + 4 * B, 3)
        if c.get("numero"): acao(c["tNumero"], "numero conta")
        if c.get("numero"):
            for k in range(8): ev(c["tNumero"] + k * .14, "tick.wav", .35)
        c["tEtiquetas"] = [round(s + B * (6 + 2 * k), 3) for k in range(len(c.get("etiquetas", [])))]
        for k, e in enumerate(c.get("etiquetas", [])): digitar(c["tEtiquetas"][k] + .05, e.upper()); acao(c["tEtiquetas"][k], f"etiqueta {e}")
    elif tp == "grafico_linha":
        c["tDesenho"], c["durDesenho"] = round(s + 3 * B, 3), round(9 * B, 3); acao(c["tDesenho"], "linha comeca a desenhar")
        if c.get("legenda"): digitar(s + .2, c["legenda"].upper())
        h0, h1 = dia(c["serie"][0]["data"]), dia(c["serie"][-1]["data"])
        for m in c.get("marcos", []):
            frac = min(1.0, max(0.0, (dia(m["data"]) - h0).days / ((h1 - h0).days or 1)))
            m["t"] = round(c["tDesenho"] + c["durDesenho"] * frac, 3); ev(m["t"], "pop.wav", .7); acao(m["t"], "marco")
        ev(s + 12 * B, "hit.wav", .8)
    elif tp == "linha_tempo":
        c["tItens"] = [round(s + B * (2 + k * 2.2), 3) for k in range(len(c["itens"]))]
        for k, it in enumerate(c["itens"]):
            ev(c["tItens"][k], "pop.wav", .6); acao(c["tItens"][k], f'etapa {it.get("nome", "")}')
            if it.get("valor"): digitar(c["tItens"][k] + .25, it["valor"].upper())
    elif tp in ("radar", "barras"):
        passo = 1.6 if tp == "radar" else 2
        c["tItens"] = [round(s + B * (3 + k * passo), 3) for k in range(len(c["itens"]))]
        for k, tt in enumerate(c["tItens"]): ev(tt, "tick.wav", .5); acao(tt, f"{c['itens'][k][0]} = {c['itens'][k][1]}")
        ev(s + 3 * B, "whoosh_rl.wav", .45)
    elif tp == "video_palavras":
        u = s
        for k, cl in enumerate(c["clipes"]):
            cl["t"], cl["dur"] = round(u, 3), round(cl["batidas"] * B, 3)
            ev(u, "hit.wav", .9); acao(u, f'clipe "{cl.get("palavra", "").replace("*", "")}"')
            if cl.get("congelar_em") is not None: ev(u + cl["congelar_em"], "freeze.wav", .8)
            if cl.get("lento_em") is not None: ev(u + cl["lento_em"], "whoosh_rl.wav", .5)
            u += cl["batidas"] * B
    elif tp == "texto_video":
        ev(s, "subdrop.wav", 1.0); ev(s, "hit.wav", .9); acao(s + .5, f'video dentro de "{c["texto"]}"')
    elif tp == "numeros":
        c["tItens"] = [round(s + B * (2.5 + k * 1.5), 3) for k in range(len(c["itens"]))]
        for k, tt in enumerate(c["tItens"]): ev(tt, "tick.wav", .55); acao(tt, f"conta {c['itens'][k][0]}")
    elif tp == "mockup":
        c["tAparelho"] = round(s + 2 * B, 3); acao(c["tAparelho"], f'{c.get("aparelho", "celular")} sobe'); acao(s + 5 * B, "tela rola"); ev(c["tAparelho"], "whoosh_rl.wav", .6); ev(c["tAparelho"] + .45, "hit.wav", .7)
        c["tRolagem"] = round(s + 5 * B, 3)
        from PIL import Image                     # quanto o print rola dentro da tela do aparelho (medido aqui, nao no navegador)
        iw, ih = Image.open(os.path.join(PROJ, c["imagem"])).size
        dw, dh = (980, 620) if c.get("aparelho") == "notebook" else (600, 1220)
        c["rolagem"] = round(max(0, ih * dw / iw - dh), 1)
        c["tEtiquetas"] = [round(s + B * (6 + 1.5 * k), 3) for k in range(len(c.get("etiquetas", [])))]
        for k, e in enumerate(c.get("etiquetas", [])): acao(c["tEtiquetas"][k], f"etiqueta {e}"); ev(c["tEtiquetas"][k], "pop.wav", .6); digitar(c["tEtiquetas"][k] + .2, e.upper())
    elif tp == "assinatura":
        c["tMarca"] = round(s + 3 * B, 3); acao(s + 2 * B, "titulo final"); acao(c["tMarca"], "marca digitada"); digitar(c["tMarca"], (c.get("marca") or R.get("marca", "")).upper())
        ev(s + 2 * B, "whoosh_rl.wav", .5)
    elif tp == "ui_produto":
        # um conteiner que nunca corta: cada estado e o mesmo elemento mudando de forma; o cursor provoca a troca
        u = s
        for k, e in enumerate(c["estados"]):
            e["t"], e["dur"] = round(u, 3), round(e["batidas"] * B, 3)
            ct = e.get("conteudo", {})
            if k: ev(u, "sopro.wav", .55); acao(u, f"vira estado {k + 1}: " + (ct.get("titulo") or ct.get("texto") or ct.get("campo") or ct.get("icone") or ("tela" if ct.get("imagem") else "") or "forma"))
            else: acao(u + .2, "conteiner aparece")
            if ct.get("digitar"):
                e["tDigitar"] = round(u + B, 3); digitar(e["tDigitar"], ct["digitar"]); acao(e["tDigitar"], f'digita "{ct["digitar"]}"')
            if ct.get("icone") == "check": ev(u + .25, "pop.wav", .8)
            if ct.get("lista"): e["tLista"] = [round(u + B * (.5 + j * .5), 3) for j in range(len(ct["lista"]))]; [ev(x, "tick.wav", .45) for x in e["tLista"]]
            if e.get("nota"): acao(u + .3, f'legenda "{e["nota"]}"')
            ac = e.get("acao")
            if ac and ac.get("tipo", "clique") != "nenhuma":
                e["tAcao"] = round(u + e["dur"] - .06, 3)          # clique cai colado na batida da troca
                if ac.get("tipo", "clique") == "clique": ev(e["tAcao"], "clique.wav", .9); acao(e["tAcao"], "cursor clica")
                else: acao(e["tAcao"] - .5, "cursor passa por cima")
            u += e["dur"]
    elif tp == "livre":
        # cena escrita na hora (JS proprio), mas com som e tempos daqui: c.tBatidas = inicio de cada batida
        c["tBatidas"] = [round(s + k * B, 3) for k in range(int(c["batidas"]) + 1)]
        for x in c.get("sons", []):
            f = SONS.get(x["som"], x["som"] if str(x["som"]).endswith(".wav") else None)
            if not f: raise SystemExit(f'cena livre: som desconhecido {x["som"]} (use {", ".join(SONS)})')
            ev(s + x["batida"] * B, f, x.get("volume", .8))
        for x in c.get("digitar", []): digitar(s + x["batida"] * B, x["texto"])
        for x in c.get("acontece", []): acao(s + x["batida"] * B, x["texto"])
        js = os.path.join(PROJ, c["arquivo"])
        if not os.path.exists(js): raise SystemExit(f"cena livre: arquivo {c['arquivo']} nao existe")
        c["_js"] = open(js, encoding="utf-8").read().strip().rstrip(";")
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
    run(["-f", "lavfi", "-i", "anoisesrc=d=0.012:c=white:a=0.8", "-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*1800*t)*exp(-90*t)':d=0.03",
         "-filter_complex", "[0]highpass=f=1800,afade=t=out:d=0.012[a];[1]volume=0.6[b];[a][b]amix=inputs=2:normalize=0", "-ac", "2", "-ar", "48000", o("clique.wav")])
    run(["-f", "lavfi", "-i", "anoisesrc=d=0.38:c=pink:a=0.6", "-af", "bandpass=f=1600:width_type=h:w=2400,afade=t=in:d=0.12,afade=t=out:st=0.14:d=0.24,volume=1.3",
         "-ac", "2", "-ar", "48000", o("sopro.wav")])
    run(["-f", "lavfi", "-i", "aevalsrc='0.4*(sin(2*PI*1320*t)+0.6*sin(2*PI*1980*t))*exp(-4*t)':d=0.9", "-ac", "2", "-ar", "48000", o("freeze.wav")])

def gerar_trilha():
    bruta = os.path.join(A, "musica_bruta.wav")
    if SINTETICA:
        sys.path.insert(0, MOTOR); from trilha_sintetica import sintetizar
        sintetizar(bruta, BPM, TOTAL + .5, mus.get("clima", "energico"), mus.get("tom", "A"), mus.get("modo", "menor"))
    else:
        run(["-ss", str(mus.get("inicio", 0)), "-t", f"{TOTAL + .5:.3f}", "-i", os.path.join(PROJ, mus["arquivo"]), "-vn", "-ac", "2", "-ar", "48000", bruta])
    ins, fil = ["-i", bruta], []
    for k, (t0, f, v) in enumerate(sfx):
        ins += ["-i", os.path.join(SFX, f)]; ms = max(0, int(t0 * 1000))
        fil.append(f"[{k + 1}]adelay={ms}|{ms},volume={v:.2f}[s{k}]")
    n = len(sfx)
    fil.append("".join(f"[s{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL:.3f}[fx]")
    fil.append("[fx]asplit=2[fx1][fxsc]")
    fil.append(f"[0]volume={mus.get('volume', 0.55 if SINTETICA else 0.8)},afade=t=out:st={TOTAL - 1.8:.2f}:d=1.8[mu]")
    fil.append("[mu][fxsc]sidechaincompress=threshold=0.04:ratio=5:attack=5:release=280[duck]")
    fil.append(f"[duck][fx1]amix=inputs=2:normalize=0,atrim=0:{TOTAL:.3f},loudnorm=I=-14:TP=-1:LRA=11[out]")
    pre = os.path.join(A, "trilha_pre.wav")
    run(ins + ["-filter_complex", ";".join(fil), "-map", "[out]", "-ar", "48000", "-ac", "2", pre])
    # 2a passada: o loudnorm de uma passada erra 1 a 2 LU em trecho curto; mede e corrige o ganho com limitador no pico
    med = subprocess.run([FF, "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    import re as _re
    I = float(_re.findall(r"I:\s+(-?[\d.]+) LUFS", med)[-1])
    run(["-i", pre, "-af", f"volume={-14 - I:.2f}dB,alimiter=limit=0.84:level=false", "-ar", "48000", "-ac", "2", os.path.join(A, "trilha.wav")])
    os.remove(pre)

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
    for e in c.get("estados", []):                # ui_produto: tamanho real do print, pra recortar sem esticar
        ct = e.get("conteudo", {})
        if ct.get("imagem"):
            from PIL import Image
            ct["iw"], ct["ih"] = Image.open(os.path.join(PROJ, ct["imagem"])).size; ct["imagem"] = rel(ct["imagem"])
    for lst in ("marcos", "itens"):
        for it in c.get(lst, []) if isinstance(c.get(lst), list) else []:
            if isinstance(it, dict) and it.get("icone"): it["icone"] = rel(it["icone"])

# ------------------------------------------------------------------ estilo e marca (uma fonte de titulo, uma de interface, uma cor de destaque)
EST = R.get("estilo", {})
fontes_css, FONTE = [], {"titulo": "Inter Tight", "ui": "JB Mono"}
fdir = os.path.join(A, "fonts"); os.makedirs(fdir, exist_ok=True)
for papel, arq in (R.get("fontes") or {}).items():
    if papel not in FONTE or not arq: continue
    ext = os.path.splitext(arq)[1]; dst = f"Marca-{papel}{ext}"
    shutil.copy(os.path.join(PROJ, arq), os.path.join(fdir, dst))
    fontes_css.append(f'@font-face {{ font-family: "Marca {papel}"; src: url("assets/fonts/{dst}"); font-weight: 100 900; }}')
    FONTE[papel] = f"Marca {papel}"
pal = R.get("paleta", {})                          # fundo, tinta, mudo, cartao, linha (hex); o resto deriva
vars_css = {"--bg": pal.get("fundo"), "--ink": pal.get("tinta"), "--mut": pal.get("mudo"), "--card": pal.get("cartao"), "--line": pal.get("linha")}
estilo_css = "\n".join(fontes_css) + "\n:root { " + " ".join(f"{k}: {v};" for k, v in vars_css.items() if v) + \
    f' --f-tit: "{FONTE["titulo"]}", "Inter Tight", sans-serif; --f-ui: "{FONTE["ui"]}", "JB Mono", monospace; }}'
if EST.get("fundo", "liso") == "liso": estilo_css += "\n.glow { display: none; }"
if not EST.get("brilho", False): estilo_css += "\n.bar.top .fi, .tr.fim .e, .anel { box-shadow: none !important; }"

# ------------------------------------------------------------------ texto que cabe: mede com a FONTE REAL (a da marca e larga ou estreita) e encolhe
from PIL import ImageFont
ARQ_FONTE = {"titulo": os.path.join(PROJ, R["fontes"]["titulo"]) if (R.get("fontes") or {}).get("titulo") else os.path.join(HOME_VM, "fonts", "InterTight.ttf")}
_fc = {}
def largura(txt, px, peso=600, esp=-.05):
    if peso not in _fc:
        f = ImageFont.truetype(ARQ_FONTE["titulo"], 200)
        try: f.set_variation_by_axes([peso])
        except Exception: pass
        _fc[peso] = f
    return _fc[peso].getlength(txt) * px / 200 + esp * px * max(0, len(txt) - 1)
def cabe(textos, px, maxw, peso=600, esp=-.05):
    for t in textos:
        w = largura(t, px, peso, esp)
        if w > maxw: px = int(px * maxw / w)
    return px
MX = 66 if H > W else round(W * .06); LIVRE = W - 2 * MX
TAM_TIT = {"grafico_linha": 120, "linha_tempo": 140, "radar": 140, "barras": 150, "numeros": 150, "mockup": 120, "ui_produto": 120 if H > W else 96}
limpa = lambda t: t.replace("*", "")
for c in cenas:
    tp = c["tipo"]
    if tp == "titulo": c["tamanho"] = cabe([limpa(l) for l in c["linhas"]], c.get("tamanho", 196), LIVRE)
    elif tp == "assinatura":
        c["tamanho"] = cabe([limpa(l) for l in (c.get("titulo") or "").split(" / ")], c.get("tamanho", 170), LIVRE)
        c["tamanho_marca"] = cabe([(c.get("marca") or R.get("marca", "")).upper()], 64, LIVRE, 800, .2)
    elif tp == "destaque" and c.get("palavra"): c["tamanho_palavra"] = cabe([c["palavra"].upper()], c.get("tamanho_palavra") or min(260, 1700 // max(4, len(c["palavra"]))), W * .94, 800, -.06)
    elif c.get("titulo") and tp in TAM_TIT:      # titulo que quebra em linhas: a palavra mais longa tem que caber
        c["tamanho"] = cabe(limpa(c["titulo"]).replace(" / ", " ").split(), c.get("tamanho", TAM_TIT[tp]), LIVRE)
    for e in c.get("estados", []):
        ct, f = e.get("conteudo", {}), e["forma"]
        if ct.get("texto") and not ct.get("titulo"): ct["tamanho"] = cabe([ct["texto"]], ct.get("tamanho", 44), f["w"] - 64, 600, -.02)
        if ct.get("digitar"): ct["tamanho"] = cabe([ct["digitar"]], ct.get("tamanho", 54), f["w"] - 84 - (110 if e.get("acao") else 0), 500, -.02)
        if ct.get("imagem"):                      # recorte na proporcao da forma, sem passar da imagem; rolagem true = ate o fim
            iw, ih = ct["iw"], ct["ih"]; rx, ry, rw, rh = ct.get("recorte") or [0, 0, iw, ih]
            rw = min(rw, iw - rx); rh2 = rw * f["h"] / f["w"]
            if ry + rh2 > ih: rh2 = ih - ry; nw = rh2 * f["w"] / f["h"]; rx += (rw - nw) * {"esquerda": 0, "direita": 1}.get(ct.get("alinhar"), .5); rw = nw
            ct["recorte"] = [round(rx), round(ry), round(rw), round(rh2)]
            if ct.get("rolagem") is True: ct["rolagem"] = max(0, round(ih - ry - rh2))

livres = ",\n".join(f"{i}: ({c['_js']})" for i, c in enumerate(cenas) if c["tipo"] == "livre")
for c in cenas: c.pop("_js", None)
DADOS = {"cor": COR, "marca": R.get("marca", ""), "rotulo": R.get("rotulo", ""), "cenas": cenas, "total": TOTAL,
         "B": B, "tecla": TECLA, "fundoAte": R.get("_fundoAte"), "W": W, "H": H, "formato": FORMATO}
html = open(os.path.join(MOTOR, "template.html"), encoding="utf-8").read()
html = (html.replace("{{W}}", str(W)).replace("{{H}}", str(H)).replace("{{FPS}}", str(FPS)).replace("{{TOTAL}}", f"{TOTAL:.3f}")
        .replace("<!--FUNDO-->", fundo_html).replace("<!--CENAS-->", "\n".join(cenas_html)).replace("<!--MIDIA-->", "\n".join(midia_html))
        .replace("/*DADOS*/{}", json.dumps(DADOS, ensure_ascii=False)).replace("/*ESTILO*/", estilo_css).replace("/*LIVRES*/", livres))
assert "{{" not in html, "marcador sem valor no template"
open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8").write(html)
# dependencias que o instalar.sh deixa em ~/.video-motion (a skill so carrega texto)
gsap = os.path.join(HOME_VM, "hf", "node_modules", "gsap", "dist", "gsap.min.js")
if not os.path.exists(gsap): raise SystemExit("gsap nao encontrado: rode instalar.sh")
shutil.copy(gsap, os.path.join(PROJ, "gsap.min.js"))
for f in ("InterTight.ttf", "JetBrainsMono.ttf"):
    src = os.path.join(HOME_VM, "fonts", f)
    if not os.path.exists(src): raise SystemExit(f"fonte {f} ausente: rode instalar.sh")
    shutil.copy(src, os.path.join(fdir, f))
grao = os.path.join(A, "grain.png")
if not os.path.exists(grao):                    # textura de grao de filme (ruido fixo, semente 7)
    from PIL import Image
    rnd = random.Random(7)
    Image.frombytes("L", (512, 512), bytes(rnd.randrange(256) for _ in range(512 * 512))).save(grao)

# ------------------------------------------------------------------ tabela de batidas (aprovar ANTES de renderizar) + ritmo
NOME_SOM = {v: k for k, v in SONS.items()} | {f"tecla{k}.wav": "teclado" for k in range(1, 5)} | {"whoosh_lr.wav": "whoosh"}
nb = int(round(TOTAL / B)); linhas, beats = [], []
na = lambda t: int((t + .004) // B)               # batida de um evento (tempos ja vem arredondados em 3 casas)
PC = 4 * mus.get("subdivisao", 1)                 # unidades da grade por compasso (subdivisao 2 = meia batida)
for k in range(nb):
    t0 = k * B
    cena = max((j for j, c in enumerate(cenas) if na(c["t"]) <= k), default=0)
    oq = [x for t, x in acoes if na(t) == k]
    sons = sorted({NOME_SOM.get(f, f) for t, f, v in sfx if na(t) == k})
    beats.append({"k": k, "t": round(t0, 3), "compasso": k // PC + 1, "batida": k % PC + 1, "cena": cena, "acontece": oq, "sons": sons})
    linhas.append(f"| {k + 1} | {t0:5.2f} | {k // PC + 1}.{k % PC + 1} | {cena + 1} {cenas[cena]['tipo']} | {'; '.join(oq) or '·'} | {', '.join(sons) or '·'} |")
open(os.path.join(OUT, "batidas.md"), "w", encoding="utf-8").write(
    f"# Batidas: {R.get('titulo', os.path.basename(PROJ))}\n\n{BPM:g} BPM{' x' + str(mus.get('subdivisao')) if mus.get('subdivisao', 1) != 1 else ''} · {B:.3f} s por batida · {TOTAL:.1f} s · {FORMATO} {W}x{H} · {FPS} fps\n\n"
    "| # | s | compasso.batida | cena | o que acontece | som |\n|---|---|---|---|---|---|\n" + "\n".join(linhas) + "\n")
json.dump({"B": B, "total": TOTAL, "W": W, "H": H, "formato": FORMATO, "cenas": [{"t": c["t"], "dur": c["dur"], "tipo": c["tipo"]} for c in cenas], "batidas": beats},
          open(os.path.join(OUT, "batidas.json"), "w", encoding="utf-8"), ensure_ascii=False)

avisos = []
marcos = sorted({t for t, _ in acoes} | {0.0, TOTAL})
for a, b in zip(marcos, marcos[1:]):
    if b - a > 4.0: avisos.append(f"tempo morto: {a:.1f}s a {b:.1f}s sem nada novo ({b - a:.1f} s; a regra e algo novo a cada 2 a 4 s)")
for j in range(1, len(cenas)):
    if cenas[j]["tipo"] == cenas[j - 1]["tipo"] and cenas[j]["tipo"] not in ("livre", "ui_produto"): avisos.append(f"cenas {j} e {j + 1} sao do mesmo tipo ({cenas[j]['tipo']}): falta variedade")
for j, c in enumerate(cenas[1:], 1):
    k = na(c["t"])
    if k % (PC // 2): avisos.append(f"cena {j + 1} ({c['tipo']}) entra em {k // PC + 1}.{k % PC + 1}, fora do tempo forte (1 ou {PC // 2 + 1} do compasso): ajuste as batidas da cena anterior para multiplo de {PC // 2}")
if cenas and cenas[0]["tipo"] == "titulo" and cenas[0].get("tLinhas") and cenas[0]["tLinhas"][-1] > 2.0:
    avisos.append(f"gancho lento: a frase de abertura so termina em {cenas[0]['tLinhas'][-1]:.1f} s (o gancho tem que estar na tela nos 2 primeiros segundos)")

print(f"ok | {FORMATO} {W}x{H} | {len(cenas)} cenas | {TOTAL:.1f} s | {FPS} fps | cor {COR} | {len(sfx)} efeitos sonoros | trilha {'sintetizada' if SINTETICA else 'da faixa'}")
for c in cenas: print(f"  {c['t']:6.2f}s  {c['tipo']:<15} {c['batidas']:>3} batidas")
print(f"tabela batida a batida: {os.path.join(OUT, 'batidas.md')}")
for a in avisos: print("AVISO", a)
