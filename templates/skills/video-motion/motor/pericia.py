#!/usr/bin/env python3
# Pericia de MOVIMENTO em numeros (ideia da skill motion-por-referencia do Felipe Borges, reescrita para o nosso motor).
# Estrutura, cor e tipo se pegam no olho; movimento nao. Isto mede:
#   perfil de energia (diferenca media entre quadros, em baldes de 0,5 s), cortes duros,
#   AMPLITUDE = pico / mediana (filme premium alterna rajada e quase-parada; filme morno anda no mesmo volume),
#   fracao do filme em quase-parada, picos, e (com --batidas) % de cortes que caem na grade de batidas.
# uso: pericia.py video.mp4 [--json saida.json] [--batidas out/batidas.json] [--contra referencia.mp4]
#   --contra roda o TESTE DE ACEITE (metas derivadas da referencia); sai com codigo 1 se reprovar.
import argparse, json, re, subprocess, sys, tempfile, os

BALDE = 0.5


def sonda(v):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                                   "-show_entries", "format=duration", "-of", "json", v], capture_output=True, text=True, check=True).stdout)
    s = d["streams"][0]; n, q = s["r_frame_rate"].split("/")
    return float(d["format"]["duration"]), float(n) / float(q), f"{s['width']}x{s['height']}"


def energia(v):
    # escala pequena: mede MOVIMENTO, nao detalhe (tira ruido de compressao e fica rapido)
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "m.txt")
        subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"scale=192:108,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file={f}",
                        "-f", "null", "-"], capture_output=True, check=True)
        return [(float(t), float(y)) for t, y in re.findall(r"pts_time:([\d.]+).*?YAVG=([\d.]+)", open(f).read(), re.S)]


def cortes(v, limiar=0.18):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-filter:v", f"select='gt(scene,{limiar})',metadata=print:file=-", "-f", "null", "-"],
                         capture_output=True, text=True).stdout
    c = []
    for t in (float(x) for x in re.findall(r"pts_time:([\d.]+)", out)):
        if not c or t - c[-1] > 0.25: c.append(t)   # um corte acende varios quadros vizinhos
    return c


def medir(v, batidas=None):
    dur, fps, res = sonda(v)
    b = {}
    for t, y in energia(v): b.setdefault(round(t / BALDE) * BALDE, []).append(y)
    pf = {k: sum(x) / len(x) for k, x in sorted(b.items())}
    vals = sorted(pf.values()) or sys.exit(f"sem energia medida em {v}")
    med, pico = vals[len(vals) // 2], max(vals[-1], 1e-6)
    m = {"arquivo": v, "duracao": dur, "fps": fps, "resolucao": res, "cortes": cortes(v), "perfil": pf, "mediana": med, "pico": pico,
         "amplitude": pico / med if med else 0.0, "vales": [k for k, y in pf.items() if y < pico * .10], "picos": [k for k, y in pf.items() if y > pico * .60]}
    m["parada"] = len(m["vales"]) / len(pf)
    if batidas:
        bt = [x["t"] for x in json.load(open(batidas))["batidas"]]
        tol = 2 / fps + 1e-3                                   # ate 2 quadros da batida
        na = [c for c in m["cortes"] if min(abs(c - t) for t in bt) <= tol]
        m["na_batida"] = len(na) / len(m["cortes"]) if m["cortes"] else None
    return m


def mostra(m):
    print(f"\n  {os.path.basename(m['arquivo'])}  {m['duracao']:.2f} s · {m['resolucao']} · {m['fps']:g} fps")
    print("  cortes duros: " + (", ".join(f"{t:.2f}" for t in m["cortes"]) or "nenhum (todo em transicao suave)"))
    for k, y in m["perfil"].items():
        print(f"  {k:6.1f}s {y:7.2f}  {'#' * int(round(y / m['pico'] * 30)):<30}{'  <- pico' if k in m['picos'] else '  <- parada' if k in m['vales'] else ''}")
    print(f"  mediana {m['mediana']:.2f} | pico {m['pico']:.2f} | AMPLITUDE {m['amplitude']:.1f}x | quase-parada {m['parada'] * 100:.0f}% | picos {len(m['picos'])}"
          + (f" | cortes na batida {m['na_batida'] * 100:.0f}%" if m.get("na_batida") is not None else ""))


def aceite(nosso, ref):
    metas = [("amplitude", nosso["amplitude"], ref["amplitude"], ref["amplitude"] * .7, "x"),
             ("quase-parada", nosso["parada"] * 100, ref["parada"] * 100, max(25, ref["parada"] * 100 - 10), "%"),
             ("picos", len(nosso["picos"]), len(ref["picos"]), max(1, int(len(ref["picos"]) * .7)), "")]
    if nosso.get("na_batida") is not None: metas.append(("cortes na batida", nosso["na_batida"] * 100, None, 70, "%"))
    print(f"\n  TESTE DE ACEITE\n  {'':18}{'nosso':>9}{'ref':>9}{'meta':>9}")
    falhas = []
    for nome, a, r, meta, u in metas:
        ok = a >= meta; falhas += [] if ok else [nome]
        print(f"  {nome:18}{a:8.1f}{u}{'' if r is None else f'{r:8.1f}{u}':>9}{'>=' + format(meta, '.1f'):>9}  {'PASSA' if ok else 'FALHA'}")
    if falhas:
        print(f"  REPROVADO em: {', '.join(falhas)}. Quase sempre o filme esta uniforme demais: escolha UM beat para ser o soco "
              "(corte duro em vez de crossfade, entrada mais rapida, objeto maior) e aprofunde as paradas vizinhas. Nao e 'acelerar tudo'.")
        return 1
    print("  APROVADO: a assinatura de movimento bate com a referencia."); return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--json"); ap.add_argument("--batidas"); ap.add_argument("--contra")
    a = ap.parse_args()
    m = medir(a.video, a.batidas); mostra(m)
    if a.json: json.dump(m, open(a.json, "w"), ensure_ascii=False, indent=1)
    if a.contra:
        r = medir(a.contra); mostra(r); sys.exit(aceite(m, r))
