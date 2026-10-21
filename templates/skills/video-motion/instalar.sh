#!/usr/bin/env bash
# Instala o ferramental do /video-motion em ~/.video-motion, SEM tocar no sistema:
#   node 22 portatil, ffmpeg 7 estatico, hyperframes (versao fixa) + gsap, e (opcional) rembg num venv.
# Idempotente: pode rodar de novo. Gera ~/.video-motion/env.sh para dar `source` antes de renderizar.
# uso: bash instalar.sh [--com-recorte]
set -euo pipefail
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"
HF_VERSAO="0.8.185"                       # versao testada; o hyperframes sai quase todo dia, fixe e teste antes de subir
NODE_VERSAO="v22.20.0"
mkdir -p "$VM/bin" "$VM/hf"
cd "$VM"

if [ ! -x "$VM/node/bin/node" ]; then
  echo "> node $NODE_VERSAO"
  curl -sL "https://nodejs.org/dist/$NODE_VERSAO/node-$NODE_VERSAO-linux-x64.tar.xz" -o node.tar.xz
  tar -xf node.tar.xz && rm node.tar.xz && mv "node-$NODE_VERSAO-linux-x64" node
fi
if [ ! -x "$VM/bin/ffmpeg" ]; then
  echo "> ffmpeg estatico (o do Ubuntu 22.04 e 4.4 e quebra a mixagem de audio do hyperframes)"
  curl -sL https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ff.tar.xz
  tar -xf ff.tar.xz && d=$(ls -d ffmpeg-*-amd64-static | head -1) && cp "$d/ffmpeg" "$d/ffprobe" bin/ && rm -rf ff.tar.xz "$d"
fi
export PATH="$VM/bin:$VM/node/bin:$PATH"
if [ ! -d "$VM/hf/node_modules/hyperframes" ]; then
  echo "> hyperframes $HF_VERSAO"
  (cd "$VM/hf" && npm init -y >/dev/null && npm install --silent "hyperframes@$HF_VERSAO" gsap@3.13.0 >/dev/null)
fi

# fontes (OFL, Google Fonts): a skill nao carrega binarios
mkdir -p "$VM/fonts"
for f in "intertight/InterTight%5Bwght%5D.ttf:InterTight.ttf" "jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf:JetBrainsMono.ttf"; do
  [ -s "$VM/fonts/${f#*:}" ] || curl -sL -o "$VM/fonts/${f#*:}" "https://raw.githubusercontent.com/google/fonts/main/ofl/${f%%:*}"
done

# navegador: o hyperframes baixa o proprio Chrome com `unzip`; se o sistema nao tiver unzip, usa o headless shell do Playwright
SHELL_PW=$(ls -d "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | tail -1 || true)

if [ "${1:-}" = "--com-recorte" ] && [ ! -x "$VM/venv/bin/python" ]; then
  echo "> rembg (recorte local de pessoas/objetos, CPU)"
  python3 -m venv "$VM/venv" && "$VM/venv/bin/pip" install -q "rembg[cpu]"
fi

cat > "$VM/env.sh" <<EOF
# gerado pelo instalar.sh do /video-motion
export VIDEO_MOTION_HOME="$VM"
export PATH="$VM/bin:$VM/node/bin:\$PATH"
export HYPERFRAMES_NO_TELEMETRY=1
export U2NET_HOME="$VM/modelos"
${SHELL_PW:+export PRODUCER_HEADLESS_SHELL_PATH="$SHELL_PW"}
hf() { (cd "$VM/hf" && npx hyperframes "\$@"); }
EOF
echo "ok: source $VM/env.sh"
"$VM/bin/ffmpeg" -version | head -1
"$VM/node/bin/node" -v
[ -z "$SHELL_PW" ] && echo "AVISO: sem headless shell do Playwright; instale 'unzip' (apt) ou rode: npx playwright install chromium-headless-shell"
exit 0
