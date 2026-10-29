#!/usr/bin/env python3
# Recorta a pessoa/objeto principal de uma foto ou de um quadro de video, LOCALMENTE (rembg, CPU, sem custo).
# Gera PNG transparente aparado (bbox). Testa varios instantes de um video e salva todos pra voce escolher.
#
# uso: recortar.py foto.jpg saida.png [--modelo u2net_human_seg|isnet-general-use]
#      recortar.py video.mp4 saida.png --tempos 229.0,229.2,230.0
# Licao: quadros com movimento (bracos borrados) saem cortados; prefira um quadro parado e de frente.
# Truque do "fundo verde" com IA de imagem NAO funciona com fundo poluido (torcida, multidao).
import os, subprocess, sys
VM = os.path.expanduser(os.environ.get("VIDEO_MOTION_HOME", "~/.video-motion"))
args = sys.argv[1:]
if len(args) < 2: raise SystemExit(__doc__ if __doc__ else "uso: recortar.py entrada saida.png [--tempos a,b] [--modelo m]")
ent, sai = args[0], args[1]
modelo = args[args.index("--modelo") + 1] if "--modelo" in args else "u2net_human_seg"
tempos = [float(x) for x in args[args.index("--tempos") + 1].split(",")] if "--tempos" in args else [None]
py = os.path.join(VM, "venv", "bin", "python")
if not os.path.exists(py): raise SystemExit("rode: bash instalar.sh --com-recorte")
ff = os.path.join(VM, "bin", "ffmpeg")
for k, t in enumerate(tempos):
    src = ent
    if t is not None:
        src = f"/tmp/vm_quadro_{k}.png"
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", ent, "-frames:v", "1", src], check=True)
    out = sai if len(tempos) == 1 else sai.replace(".png", f"_{t}.png")
    code = ("from rembg import remove, new_session\nfrom PIL import Image\n"
            f"im=Image.open({src!r}).convert('RGB'); r=remove(im, session=new_session({modelo!r}), post_process_mask=True)\n"
            f"r=r.crop(r.getbbox()); r.save({out!r}); print('ok', {out!r}, r.size)")
    subprocess.run([py, "-c", code], check=True, env={**os.environ, "U2NET_HOME": os.path.join(VM, "modelos")})
