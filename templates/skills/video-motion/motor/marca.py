#!/usr/bin/env python3
# Transforma a captura do site (hyperframes capture) no kit de marca do video:
#   <projeto>/assets/marca/  fontes (baixadas do Google Fonts pelo nome), prints da captura, candidatos a logo (svg/og)
#   <projeto>/marca.json     campos prontos pro roteiro: marca, cor, paleta, fontes
#   <projeto>/marca.md       o que foi achado e de onde veio (mostrar ao usuario ANTES de animar) + o que falta
# uso: python3 marca.py <pasta-da-captura> <projeto> [url]
import json, os, re, shutil, sys, urllib.request

CAP, PROJ = sys.argv[1], os.path.abspath(sys.argv[2]); URL = sys.argv[3] if len(sys.argv) > 3 else ""
X = os.path.join(CAP, "extracted")
tok = json.load(open(os.path.join(X, "tokens.json"), encoding="utf-8"))
est = json.load(open(os.path.join(X, "design-styles.json"), encoding="utf-8")) if os.path.exists(os.path.join(X, "design-styles.json")) else {}
M = os.path.join(PROJ, "assets", "marca"); os.makedirs(os.path.join(M, "fontes"), exist_ok=True); os.makedirs(os.path.join(M, "prints"), exist_ok=True)
falta = []

def rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if re.fullmatch(r"[0-9a-fA-F]{6}", h) else None
def lum(c): return (.299 * c[0] + .587 * c[1] + .114 * c[2]) / 255
def sat(c): mx, mn = max(c), min(c); return (mx - mn) / (mx or 1)

# ---------- cores: variaveis CSS com nome de papel primeiro, depois as cores da pagina
cv = {k.lower(): v for k, v in (tok.get("cssVariables") or {}).items()}
def var(*nomes):
    for n in nomes:
        for k, v in cv.items():
            if re.search(n, k) and rgb(v): return "#" + "".join(f"{x:02x}" for x in rgb(v)), k
    return None, None
cores = [c for c in (tok.get("colors") or []) if rgb(c)]
acc, acc_de = var(r"accent$|--accent|primary$|--primary|brand$|--brand")
if not acc:
    cand = sorted((c for c in cores if sat(rgb(c)) > .45 and .25 < lum(rgb(c)) < .85), key=lambda c: -sat(rgb(c)))
    acc, acc_de = (cand[0].lower(), "cor mais saturada da pagina") if cand else (None, None)
fundo, fundo_de = var(r"canvas|--bg$|background$|--background|--base")
if not fundo and cores: fundo, fundo_de = cores[0].lower() if lum(rgb(cores[0])) < .2 or lum(rgb(cores[0])) > .9 else "#09090b", "1a cor da pagina"
tinta, tinta_de = var(r"--ink$|foreground|--text$|--fg$")
if not tinta and fundo: tinta, tinta_de = ("#f4f4f3" if lum(rgb(fundo)) < .5 else "#111113"), "derivada do fundo"
mudo, _ = var(r"mut|secondary-text|--subtle|--gray")
linha, _ = var(r"--line$|border$|--border")
if not acc: falta.append("cor de destaque (nao achei variavel nem cor saturada; defina `cor` no roteiro)")

# ---------- fontes: papel heading = titulo; rotulo/link/botao com outra familia = interface
tip = est.get("typography") or []
fam = lambda papeis: next((t["fontFamily"].split(",")[0].strip(" '\"") for t in tip if t.get("role") in papeis and t.get("fontFamily")), None)
f_tit = fam({"heading", "display", "h1"}) or (tok.get("fonts") or [{}])[0].get("family")
f_ui = next((t["fontFamily"].split(",")[0].strip(" '\"") for t in tip if t.get("role") in ("label", "link", "button", "caption") and t.get("fontFamily") and not t["fontFamily"].startswith(f_tit or "~")), None) or fam({"body"})
pesos = {f["family"]: f.get("weights") or [400] for f in tok.get("fonts") or []}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def baixa_fonte(familia, alvo, papel):
    if not familia: return None
    q = familia.replace(" ", "+")
    for spec in ("wght@100..900", "wght@200..800", "wght@300..700", "wght@400..800", "wght@400..700", "wght@300..800", None):
        ws = pesos.get(familia, [alvo]); peso = min(ws, key=lambda w: abs(int(w) - alvo))
        url = f"https://fonts.googleapis.com/css2?family={q}:{spec or f'wght@{peso}'}&display=swap"
        try: css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20).read().decode()
        except Exception: continue
        blocos = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}", css)
        latin = next((b for s, b in blocos if s == "latin"), blocos[-1][1] if blocos else css)
        m = re.search(r"url\((https://[^)]+\.woff2)\)", latin)
        if not m: continue
        dst = os.path.join(M, "fontes", f"{papel}-{familia.replace(' ', '')}.woff2")
        urllib.request.urlretrieve(m.group(1), dst)
        return os.path.relpath(dst, PROJ), ("variavel" if spec else f"peso {peso} fixo")
    falta.append(f"fonte '{familia}' ({papel}) nao esta no Google Fonts: copie o .woff2/.ttf do site pra assets/marca/fontes e aponte em `fontes.{papel}`")
    return None
ft = baixa_fonte(f_tit, 650, "titulo"); fu = baixa_fonte(f_ui, 500, "ui") if f_ui and f_ui != f_tit else None

# ---------- prints e candidatos a logo
prints = []
for f in sorted(os.listdir(os.path.join(CAP, "screenshots"))) if os.path.isdir(os.path.join(CAP, "screenshots")) else []:
    if f.endswith((".png", ".jpg")) and "contact" not in f:
        shutil.copy(os.path.join(CAP, "screenshots", f), os.path.join(M, "prints", f)); prints.append(f)
logos = []
sv = os.path.join(CAP, "assets", "svgs")
for f in sorted(os.listdir(sv)) if os.path.isdir(sv) else []:
    if f.endswith(".svg"): shutil.copy(os.path.join(sv, f), os.path.join(M, f)); logos.append(f)
og = tok.get("ogImage")
if og:
    try: urllib.request.urlretrieve(og, os.path.join(M, "og" + (os.path.splitext(og.split("?")[0])[1] or ".jpg"))); logos.append("og" + (os.path.splitext(og.split("?")[0])[1] or ".jpg") + " (imagem de compartilhamento)")
    except Exception: pass
if not [l for l in logos if l.endswith(".svg")]: falta.append("logo vetorial (nenhum SVG na captura): pegar do repo/site e salvar em assets/marca/logo.svg ou .png transparente")

nome = re.split(r"\s+[·|\-–]\s+", tok.get("title") or "")[0].strip() or os.path.basename(PROJ)
kit = {"marca": nome.upper(), "cor": acc, "paleta": {k: v for k, v in {"fundo": fundo, "tinta": tinta, "mudo": mudo, "linha": linha}.items() if v},
       "fontes": {k: v[0] for k, v in {"titulo": ft, "ui": fu}.items() if v}}
json.dump(kit, open(os.path.join(PROJ, "marca.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

h = [t for t in tok.get("headings") or []][:6]
btn = (est.get("buttons") or [{}])[0]
md = f"""# Marca: {nome}

Fonte: {URL} (captura automática; confira antes de animar)
Frase do produto (título do site): **{tok.get('title', '')}**
Descrição: {tok.get('description', '')}

## Cores
| Papel | Cor | De onde veio |
|---|---|---|
| Destaque (a ÚNICA cor de destaque do vídeo) | `{acc}` | {acc_de} |
| Fundo | `{fundo}` | {fundo_de} |
| Texto | `{tinta}` | {tinta_de} |
| Mudo | `{mudo}` | variável CSS |
| Linha | `{linha}` | variável CSS |

Outras cores da página: {', '.join(cores[:12])}

## Fontes
- Título: **{f_tit}** -> `{ft[0] if ft else 'NÃO BAIXADA'}` ({ft[1] if ft else '-'})
- Interface: **{f_ui or '(a mesma do título)'}** -> `{fu[0] if fu else '-'}` ({fu[1] if fu else '-'})

## Botão principal (CTA)
"{btn.get('label', '')}" · raio {btn.get('borderRadius', '?')} · fundo {btn.get('backgroundImage') or btn.get('background', '?')} · texto {btn.get('color', '?')}

## Títulos reais do site (use estes textos, não invente)
""" + "\n".join(f"- {x.get('text')}" for x in h) + f"""

## Prints (assets/marca/prints/)
{chr(10).join('- ' + p for p in prints) or '- nenhum'}

## Logo (candidatos em assets/marca/)
{chr(10).join('- ' + l for l in logos) or '- nenhum'}

## Falta / conferir
{chr(10).join('- ' + f for f in falta) or '- nada'}
- Telas do PRODUTO (área logada): a captura só vê a página pública. Tirar prints reais das telas com Playwright (1440x900 e 390x844) e salvar em assets/marca/prints/. Nunca redesenhar a interface de imaginação.
"""
open(os.path.join(PROJ, "marca.md"), "w", encoding="utf-8").write(md)
print(md)
