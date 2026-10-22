#!/usr/bin/env bash
# Monta e renderiza um projeto do /video-motion e confere o resultado.
#   1) montar.py (index.html + assets/trilha.wav)   2) lint do hyperframes (para se houver ERRO)
#   3) render MP4 com prioridade baixa               4) folha de quadros (out/folha.jpg) + volume (LUFS)
#   5) versao comprimida pra web/artifact (out/<nome>-web.mp4, ~2,4 Mbps)
# uso: bash renderizar.sh <pasta-do-projeto> [--rascunho] [--formato 16:9|1:1|9:16|todos] [--motion-blur [N]]
#   --rascunho      qualidade draft, mais rapido
#   --formato       outro formato a partir do mesmo roteiro (todos = cada item de roteiro.formatos)
#   --motion-blur   renderiza N subquadros por quadro (padrao 4) e mistura: movimento rapido fica liso como camera.
#                   Custa N vezes o tempo de render; use so no final, depois do revisar.sh
set -euo pipefail
SK="$(cd "$(dirname "$0")" && pwd)"
P="$(cd "${1:?informe a pasta do projeto}" && pwd)"
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"
[ -f "$VM/env.sh" ] || { echo "rode antes: bash $SK/instalar.sh"; exit 1; }
source "$VM/env.sh"
NOME0=$(basename "$P"); mkdir -p "$P/out"; shift
Q=(); MB=0; FORMATOS=("")
while [ $# -gt 0 ]; do case "$1" in
  --rascunho) Q=(-q draft); shift ;;
  --formato) if [ "$2" = todos ]; then mapfile -t FORMATOS < <(python3 -c "import json,sys;r=json.load(open(sys.argv[1]));print('\n'.join(r.get('formatos') or [r.get('formato','9:16')]))" "$P/roteiro.json"); else FORMATOS=("$2"); fi; shift 2 ;;
  --motion-blur) MB=4; if [[ "${2:-}" =~ ^[0-9]+$ ]]; then MB=$2; shift; fi; shift ;;
  *) echo "opcao desconhecida: $1"; exit 1 ;;
esac; done
[ -f "$P/out/revisao.md" ] || echo "AVISO: sem out/revisao.md. O loop de critica (revisar.sh) vem ANTES do render."

for F in "${FORMATOS[@]}"; do
NOME="$NOME0${F:+-${F/:/x}}"
[ -n "$F" ] && export VM_FORMATO="$F"
echo "== 1. montar ${F:-}"
python3 "$SK/motor/montar.py" "$P" | grep -v '^ '

echo "== 2. lint"
LINT=$(hf lint "$P" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' || true)
echo "$LINT" | grep -E '✗|◇' || true
if echo "$LINT" | grep -q '✗'; then echo "PARADO: corrija os erros do lint acima antes de renderizar"; exit 1; fi

echo "== 3. render$( [ "$MB" -gt 0 ] && echo " (motion blur x$MB)")"
FPS=$(grep -o 'data-fps="[0-9]*"' "$P/index.html" | head -1 | grep -o '[0-9]*')
SAIDA="$P/out/$NOME.mp4"; [ "$MB" -gt 0 ] && SAIDA="$P/out/$NOME-sub.mp4"
EXTRA=""; [ "$MB" -gt 0 ] && EXTRA="-f $((FPS * MB))"
[ "$MB" -gt 0 ] && [ $((FPS * MB)) -gt 240 ] && { echo "motion blur: $FPS fps x $MB passa de 240 (limite do hyperframes); use --motion-blur 4 com 60 fps ou 8 com 30"; exit 1; }
time (nice -n 10 bash -c "source '$VM/env.sh'; cd '$VM/hf' && npx hyperframes render '$P' -o '$SAIDA' -w ${VM_WORKERS:-$(nproc)} $EXTRA ${Q[*]:-}" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E 'ERROR|✗|Failed' || true)
[ -s "$SAIDA" ] || { echo "render falhou (rode: hf render $P -o $P/out/x.mp4 para ver o log completo)"; exit 1; }
if [ "$MB" -gt 0 ]; then
  # cada quadro final = media dos N subquadros do seu intervalo (obturador de 360 graus); audio copiado
  ffmpeg -hide_banner -loglevel error -y -i "$SAIDA" -vf "tmix=frames=$MB,fps=$FPS" -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a copy "$P/out/$NOME.mp4"
  rm -f "$SAIDA"
fi

# o mixer do hyperframes tira ~1,5 dB da trilha; o audio do video e so a nossa trilha (videos das cenas sao mudos), entao recoloca a original
ffmpeg -hide_banner -loglevel error -y -i "$P/out/$NOME.mp4" -i "$P/assets/trilha.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$P/out/$NOME-a.mp4" && mv "$P/out/$NOME-a.mp4" "$P/out/$NOME.mp4"

echo "== 4. conferencia"
ffmpeg -hide_banner -loglevel error -y -i "$P/out/$NOME.mp4" -vf "fps=1,scale=150:-1,tile=12x5" -frames:v 1 "$P/out/folha${F:+-${F/:/x}}.jpg"
ffmpeg -hide_banner -nostats -i "$P/out/$NOME.mp4" -af ebur128 -f null - 2>&1 | grep -E ' I:' | tail -1
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of compact=p=0 "$P/out/$NOME.mp4"

echo "== 5. versao web"
ffmpeg -hide_banner -loglevel error -y -i "$P/out/$NOME.mp4" -c:v libx264 -preset slow -b:v 2350k -maxrate 3200k -bufsize 6000k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$P/out/$NOME-web.mp4"
done
unset VM_FORMATO
python3 "$SK/motor/montar.py" "$P" >/dev/null       # deixa o index.html no formato principal
ls -la "$P/out" | grep -E 'mp4|jpg'
echo "pronto: olhe as folhas em $P/out ANTES de entregar"
