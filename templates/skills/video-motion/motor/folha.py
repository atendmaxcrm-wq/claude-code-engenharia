#!/usr/bin/env python3
# Monta as folhas de conferencia do revisar.sh a partir dos quadros tirados por batida:
#   folha-batidas.jpg  um quadro por batida, com numero, compasso.batida, segundo e cena (olhar ritmo, variedade, sincronia)
#   folha-celular.jpg  um quadro por compasso no TAMANHO DE TELA DE CELULAR (390 px de largura na vertical): se nao da
#                      pra ler aqui, nao da pra ler no telefone
# uso: python3 folha.py <pasta-dos-quadros> <batidas.json> <pasta-de-saida>
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

Q, BJ, OUT = sys.argv[1:4]
meta = json.load(open(BJ, encoding="utf-8"))
VM = os.path.expanduser(os.environ.get("VIDEO_MOTION_HOME", "~/.video-motion"))
try: FONTE = ImageFont.truetype(os.path.join(VM, "fonts", "JetBrainsMono.ttf"), 15)
except OSError: FONTE = ImageFont.load_default()

quadros = []
for b in meta["batidas"]:
    p = os.path.join(Q, f"b{b['k']:03d}.png")
    if os.path.exists(p): quadros.append((b, p))
if not quadros: raise SystemExit(f"nenhum quadro em {Q}")
W, H = meta["W"], meta["H"]
cenas = meta["cenas"]

def folha(itens, larg, colunas, nome):
    alt = round(larg * H / W); lab = 22
    linhas = (len(itens) + colunas - 1) // colunas
    img = Image.new("RGB", (colunas * (larg + 6) + 6, linhas * (alt + lab + 6) + 6), (24, 24, 27))
    d = ImageDraw.Draw(img)
    for j, (b, p) in enumerate(itens):
        x, y = 6 + (j % colunas) * (larg + 6), 6 + (j // colunas) * (alt + lab + 6)
        img.paste(Image.open(p).convert("RGB").resize((larg, alt), Image.LANCZOS), (x, y + lab))
        corte = any(int((c["t"] + .004) // meta["B"]) == b["k"] for c in cenas)          # batida em que entra cena nova
        d.rectangle([x, y, x + larg, y + lab - 2], fill=(255, 122, 26) if corte else (40, 40, 45))
        d.text((x + 5, y + 3), f"{b['k'] + 1} {b['compasso']}.{b['batida']} {b['t']:.1f}s c{b['cena'] + 1}", font=FONTE, fill=(0, 0, 0) if corte else (220, 220, 220))
    img.save(os.path.join(OUT, nome), quality=86)
    return os.path.join(OUT, nome)

vert = H > W
print(folha(quadros, 150 if vert else 240, 12 if vert else 8, "folha-batidas.jpg"))
pc = max(b["batida"] for b in meta["batidas"])
por_compasso = [q for q in quadros if q[0]["batida"] == pc // 2 + 1] or quadros     # meio do compasso: movimento ja assentou
print(folha(por_compasso, 390 if vert else 640, 4 if vert else 3, "folha-celular.jpg"))
