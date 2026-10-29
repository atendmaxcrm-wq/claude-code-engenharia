#!/usr/bin/env bash
# Sobe um Chrome headless com CDP SO em 127.0.0.1, perfil isolado, abrindo uma URL.
# O REA inspeciona a pagina viva por essa porta (rea list-browser-targets / inspect-web-page).
# Uso: cdp.sh <porta> <url>        CHROME=/caminho/do/chrome para escolher o binario
# Parar: pgrep -f "port=<porta>" | xargs -r kill   (NUNCA pkill -f com o mesmo padrao:
#        ele casa com a linha de comando do proprio shell e mata o shell junto)
set -euo pipefail
PORTA="${1:?uso: cdp.sh <porta> <url>}"; URL="${2:?uso: cdp.sh <porta> <url>}"
CHROME="${CHROME:-$(ls -d ~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome 2>/dev/null | tail -1)}"
[ -x "$CHROME" ] || { echo "Chrome nao encontrado: defina CHROME=... ou rode npx playwright install chromium" >&2; exit 1; }
PERFIL="${REA_PERFIL_DIR:-$PWD/.rea/perfil-$PORTA}"; mkdir -p "$PERFIL"
exec "$CHROME" --headless=new --no-sandbox --disable-dev-shm-usage \
  --remote-debugging-address=127.0.0.1 --remote-debugging-port="$PORTA" \
  --user-data-dir="$PERFIL" "$URL"
