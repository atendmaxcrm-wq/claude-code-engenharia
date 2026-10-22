#!/usr/bin/env bash
# Video de REFERENCIA (estilo a seguir): baixa (YouTube via Apify; a VPS e barrada pelo YouTube) ou usa arquivo local,
# mede o ritmo (cortes por segundo) e gera folhas de quadros para destilar a LINGUAGEM DE MOVIMENTO em referencia.md.
# Copiar o movimento, o ritmo e a hierarquia; NUNCA o conteudo, a marca ou os textos da referencia.
# uso: bash referencia.sh <url-youtube | arquivo.mp4> <pasta-do-projeto> [--de 00:10 --ate 00:40]
# custo Apify: ~US$0,006/MB (720p); token em ~/.config/apify/token
set -euo pipefail
SRC="${1:?url ou arquivo}"; mkdir -p "${2:?pasta do projeto}"; P="$(cd "$2" && pwd)"; shift 2
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"; source "$VM/env.sh"
DE=""; ATE=""
while [ $# -gt 0 ]; do case "$1" in --de) DE="$2"; shift 2 ;; --ate) ATE="$2"; shift 2 ;; *) echo "opcao desconhecida: $1"; exit 1 ;; esac; done
D="$P/referencia"; mkdir -p "$D"

if [ -f "$SRC" ]; then cp "$SRC" "$D/ref.mp4"
elif [ ! -s "$D/ref.mp4" ]; then
  T=$(cat "${APIFY_TOKEN_FILE:-$HOME/.config/apify/token}" 2>/dev/null) || { echo "sem token Apify em ~/.config/apify/token"; exit 1; }
  echo "== baixando pela Apify (streamers/youtube-video-downloader)"
  RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/streamers~youtube-video-downloader/runs?token=$T" -H 'Content-Type: application/json' \
    -d "{\"videos\":[{\"url\":\"$SRC\"}],\"storeInKVStore\":true,\"preferredQuality\":\"720p\",\"preferredFormat\":\"mp4\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['id'])")
  for _ in $(seq 1 90); do
    ST=$(curl -s "https://api.apify.com/v2/actor-runs/$RUN?token=$T" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['status'])")
    case "$ST" in SUCCEEDED) break ;; FAILED|ABORTED|TIMED-OUT) echo "apify: $ST"; exit 1 ;; esac; sleep 10
  done
  U=$(curl -s "https://api.apify.com/v2/actor-runs/$RUN/dataset/items?token=$T" | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['downloadedFileUrl'])")
  curl -sL "$U?token=$T" -o "$D/ref.mp4"
fi
[ -s "$D/ref.mp4" ] || { echo "sem video"; exit 1; }

IN=(-i "$D/ref.mp4"); [ -n "$DE" ] && IN=(-ss "$DE" "${IN[@]}"); [ -n "$ATE" ] && IN+=(-to "$ATE")
[ -n "$DE" ] && [ -n "$ATE" ] && IN=(-ss "$DE" -to "$ATE" -i "$D/ref.mp4")
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$D/ref.mp4")
echo "== cortes (mudanca de cena > 0.3)"
ffmpeg -hide_banner -nostats "${IN[@]}" -vf "select='gt(scene,0.3)',showinfo" -an -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$D/cortes.txt" || true
python3 - "$D/cortes.txt" "$DUR" "$DE" "$ATE" <<'PY' | tee "$D/ritmo.txt"
import sys
def seg(x):
    if not x: return None
    p = [float(v) for v in x.split(":")]; return sum(v * 60 ** i for i, v in enumerate(reversed(p)))
c = [float(x) for x in open(sys.argv[1]) if x.strip()]
de, ate = seg(sys.argv[3]) or 0, seg(sys.argv[4]) or float(sys.argv[2]); dur = ate - de
gaps = [b - a for a, b in zip([0] + c, c + [dur])]
print(f"duracao analisada {dur:.1f} s | {len(c)} cortes | {len(c) / dur:.2f} cortes/s | plano medio {dur / (len(c) + 1):.2f} s | mais curto {min(gaps):.2f} s | mais longo {max(gaps):.2f} s")
PY
echo "== folhas de quadros"
ffmpeg -hide_banner -loglevel error -y "${IN[@]}" -vf "fps=2,scale=240:-2,tile=8x6" -q:v 4 "$D/folha-%02d.jpg"
ffmpeg -hide_banner -loglevel error -y "${IN[@]}" -vf "select='gt(scene,0.3)',scale=320:-2,tile=6x5" -vsync vfr -frames:v 1 -q:v 4 "$D/cortes.jpg" || true
ls "$D"
cat <<TXT
PROXIMO PASSO: olhar as folhas (Read) e escrever $P/referencia.md com:
  ritmo (cortes/s acima, onde acelera), transicoes, tipo de movimento e easing (mola, linear, freio forte),
  composicao e hierarquia de tipo, uso de cor, como a interface aparece, o que o som marca.
  Depois: o que ADOTAR no nosso video e o que NAO copiar (conteudo, marca, textos da referencia).
TXT
