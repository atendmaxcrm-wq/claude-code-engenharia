#!/usr/bin/env bash
# Instala as skills de TERCEIROS que usamos junto com o CCE (Felipe Borges e impeccable).
# O codigo delas NAO fica no nosso repo (algumas nao tem licenca publicada): o script baixa cada uma
# do repo oficial, no commit fixado em skills.tsv, e aplica so os nossos ajustes:
#   - modo "manual" ganha `disable-model-invocation: true` (o Claude nao chama sozinho; usuario digita /nome
#     ou o Claude le o SKILL.md e segue), para nao roubar pedido da video-motion/site-elite;
#   - grava ORIGEM.txt com repo, commit e licenca.
# Uso:
#   bash terceiros/instalar.sh [pasta-de-skills]          # padrao: ./.claude/skills (rode na raiz onde o CCE foi instalado)
#   bash terceiros/instalar.sh ~/.claude/skills reel scrollar   # so algumas
#   ATUALIZAR=1 bash terceiros/instalar.sh ...           # usa o HEAD atual de cada repo em vez do commit fixado
# Extra: --com-whisper-gemini instala bin/whisper-cli-gemini como `whisper-cli` em ~/.local/bin (a /reel transcreve
# pelo Gemini em vez do whisper.cpp; precisa de GEMINI_API_KEY no ambiente).
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHISPER=0; ARGS=()
for x in "$@"; do [ "$x" = "--com-whisper-gemini" ] && WHISPER=1 || ARGS+=("$x"); done
set -- "${ARGS[@]+"${ARGS[@]}"}"
DEST="${1:-./.claude/skills}"; shift || true
SO=("$@")
mkdir -p "$DEST"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
command -v curl >/dev/null || { echo "precisa de curl"; exit 1; }

baixar() { # repo commit -> pasta extraida
  local repo="$1" ref="$2" alvo="$TMP/$(echo "$repo@$ref" | tr '/@' '__')"
  if [ ! -d "$alvo" ]; then
    mkdir -p "$alvo"
    curl -fsSL "https://codeload.github.com/$repo/tar.gz/$ref" | tar -xz -C "$alvo" --strip-components=1
  fi
  echo "$alvo"
}

ok=0
while IFS=$'\t' read -r nome repo commit sub modo lic; do
  [ -z "${nome:-}" ] || [ "${nome:0:1}" = "#" ] && continue
  if [ ${#SO[@]} -gt 0 ] && [[ ! " ${SO[*]} " =~ " $nome " ]]; then continue; fi
  ref="$commit"; [ "${ATUALIZAR:-0}" = "1" ] && ref="HEAD"
  src="$(baixar "$repo" "$ref")/$sub"
  [ -f "$src/SKILL.md" ] || { echo "ERRO $nome: SKILL.md nao achado em $repo/$sub"; continue; }
  rm -rf "$DEST/$nome"; mkdir -p "$DEST/$nome"
  cp -a "$src/." "$DEST/$nome/"
  rm -rf "$DEST/$nome/.git" "$DEST/$nome/.github"
  if [ "$modo" = "manual" ] && ! grep -q '^disable-model-invocation:' "$DEST/$nome/SKILL.md"; then
    # insere antes do --- que fecha o frontmatter
    awk 'NR==1 && $0=="---"{print; fm=1; next} fm && $0=="---"{print "disable-model-invocation: true"; print; fm=0; next} {print}' \
      "$DEST/$nome/SKILL.md" > "$DEST/$nome/SKILL.md.tmp" && mv "$DEST/$nome/SKILL.md.tmp" "$DEST/$nome/SKILL.md"
  fi
  printf 'Origem: https://github.com/%s (%s), commit %s, pasta %s\nLicenca: %s\nModo: %s\nInstalada por terceiros/instalar.sh do CCE em %s\n' \
    "$repo" "$sub" "$ref" "$sub" "$lic" "$modo" "$(date +%F)" > "$DEST/$nome/ORIGEM.txt"
  echo "ok  $nome ($modo) <- $repo"
  ok=$((ok+1))
done < "$AQUI/skills.tsv"

if [ "$WHISPER" = "1" ]; then
  mkdir -p "$HOME/.local/bin"
  install -m 755 "$AQUI/bin/whisper-cli-gemini" "$HOME/.local/bin/whisper-cli"
  mkdir -p "$HOME/.cache/whisper-cpp"; : > "$HOME/.cache/whisper-cpp/ggml-large-v3-turbo.bin"  # marcador: a /reel so confere se existe
  echo "ok  whisper-cli (Gemini) em ~/.local/bin; exporte GEMINI_API_KEY"
fi
echo "$ok skill(s) de terceiros em $DEST. Reinicie o Claude Code para carregar."
