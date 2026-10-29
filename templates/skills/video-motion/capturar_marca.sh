#!/usr/bin/env bash
# Marca REAL do site no projeto: captura (hyperframes capture) -> fontes, cores, prints, logo -> marca.json + marca.md.
# Guarda o kit na biblioteca ~/.video-motion/marcas/<slug> (uma marca, um kit): no proximo video da mesma marca,
# reaproveita sem capturar de novo (use --atualizar para recapturar).
# uso: bash capturar_marca.sh <url> <pasta-do-projeto> [--slug nome] [--atualizar]
set -euo pipefail
SK="$(cd "$(dirname "$0")" && pwd)"
URL="${1:?informe a url}"; mkdir -p "${2:?informe a pasta do projeto}"; P="$(cd "$2" && pwd)"; shift 2
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"
source "$VM/env.sh"
SLUG=$(echo "$URL" | sed -E 's#https?://(www\.)?##; s#[/?].*##; s#\.[a-z.]+$##'); ATU=0
while [ $# -gt 0 ]; do case "$1" in --slug) SLUG="$2"; shift 2 ;; --atualizar) ATU=1; shift ;; *) echo "opcao desconhecida: $1"; exit 1 ;; esac; done
BIB="$VM/marcas/$SLUG"

if [ -f "$BIB/marca.json" ] && [ $ATU = 0 ]; then
  echo "== marca '$SLUG' ja esta na biblioteca: copiando (use --atualizar para recapturar)"
  mkdir -p "$P/assets"; cp -r "$BIB/assets/marca" "$P/assets/"; cp "$BIB/marca.json" "$BIB/marca.md" "$P/"
  cat "$P/marca.md"; exit 0
fi

echo "== captura de $URL"
CAP="$P/marca-captura"; rm -rf "$CAP"
(cd "$VM/hf" && npx hyperframes capture "$URL" -o "$CAP" --skip-vision --max-screenshots 12 --capture-budget 150000 --json > "$P/marca-captura.json" 2>/dev/null) || true
[ -f "$CAP/extracted/tokens.json" ] || { echo "captura falhou: veja $P/marca-captura.json"; exit 1; }

echo "== kit de marca"
python3 "$SK/motor/marca.py" "$CAP" "$P" "$URL"
mkdir -p "$BIB/assets"; rm -rf "$BIB/assets/marca"; cp -r "$P/assets/marca" "$BIB/assets/"; cp "$P/marca.json" "$P/marca.md" "$BIB/"
echo "kit salvo em $BIB (reaproveitado no proximo video desta marca)"
echo "PROXIMO PASSO: mostrar marca.md ao usuario e listar o que foi achado ANTES de animar; completar o que estiver em 'Falta'."
