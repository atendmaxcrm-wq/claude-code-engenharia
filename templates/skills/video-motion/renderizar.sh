#!/usr/bin/env bash
# Monta e renderiza um projeto do /video-motion e confere o resultado.
#   1) montar.py (index.html + assets/trilha.wav)   2) lint do hyperframes (para se houver ERRO)
#   3) render MP4 com prioridade baixa               4) folha de quadros (out/folha.jpg) + volume (LUFS)
#   5) versao comprimida pra web/artifact (out/<nome>-web.mp4, ~2,4 Mbps)
# uso: bash renderizar.sh <pasta-do-projeto> [--rascunho]     (--rascunho = qualidade draft, mais rapido)
set -euo pipefail
SK="$(cd "$(dirname "$0")" && pwd)"
P="$(cd "${1:?informe a pasta do projeto}" && pwd)"
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"
[ -f "$VM/env.sh" ] || { echo "rode antes: bash $SK/instalar.sh"; exit 1; }
source "$VM/env.sh"
NOME=$(basename "$P"); mkdir -p "$P/out"

echo "== 1. montar"
python3 "$SK/motor/montar.py" "$P"

echo "== 2. lint"
LINT=$(hf lint "$P" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' || true)
echo "$LINT" | grep -E '✗|◇' || true
if echo "$LINT" | grep -q '✗'; then echo "PARADO: corrija os erros do lint acima antes de renderizar"; exit 1; fi

echo "== 3. render"
Q=(); [ "${2:-}" = "--rascunho" ] && Q=(-q draft)
time (nice -n 10 bash -c "source '$VM/env.sh'; cd '$VM/hf' && npx hyperframes render '$P' -o '$P/out/$NOME.mp4' -w ${VM_WORKERS:-$(nproc)} ${Q[*]:-}" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E 'ERROR|✗|Failed' || true)
[ -s "$P/out/$NOME.mp4" ] || { echo "render falhou (rode: hf render $P -o $P/out/x.mp4 para ver o log completo)"; exit 1; }

echo "== 4. conferencia"
ffmpeg -hide_banner -loglevel error -y -i "$P/out/$NOME.mp4" -vf "fps=1,scale=150:-1,tile=12x5" -frames:v 1 "$P/out/folha.jpg"
ffmpeg -hide_banner -nostats -i "$P/out/$NOME.mp4" -af ebur128 -f null - 2>&1 | grep -E ' I:' | tail -1
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of compact=p=0 "$P/out/$NOME.mp4"

echo "== 5. versao web"
ffmpeg -hide_banner -loglevel error -y -i "$P/out/$NOME.mp4" -c:v libx264 -preset slow -b:v 2350k -maxrate 3200k -bufsize 6000k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$P/out/$NOME-web.mp4"
ls -la "$P/out"
echo "pronto: olhe $P/out/folha.jpg ANTES de entregar"
