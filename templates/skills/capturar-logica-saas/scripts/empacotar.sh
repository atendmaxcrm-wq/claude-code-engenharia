#!/usr/bin/env bash
# Empacota o blueprint num zip pronto pra levar por SFTP. Inclui SO o que e seguro:
# BLUEPRINT + LEIA-ME + screens (ja revisados) + manifest SANITIZADO + scripts.
# EXCLUI sessao/logs/storage-state/codigo/senha.
#
# Uso: CAP_ROOT=/root/<slug>-blueprint SLUG=<slug> bash empacotar.sh
#   (opcional) INCLUIR_ACESSO=1  -> inclui um ACESSO.md com a senha (SO se o dono pediu).
set -euo pipefail

ROOT="${CAP_ROOT:-$(pwd)}"
SLUG="${SLUG:-$(basename "$ROOT" | sed 's/-blueprint$//')}"
STAGE="$(mktemp -d)"
ZIP="/root/${SLUG}-blueprint-pacote.zip"

cd "$ROOT"

# 1) usar o manifest sanitizado (falha se nao existir - forca o passo de sanitizacao)
if [ ! -f "_recon/manifest-sanitizado.json" ]; then
  echo "ERRO: _recon/manifest-sanitizado.json ausente. Rode sanitizar-manifest.mjs antes." >&2
  exit 1
fi

mkdir -p "$STAGE/estrutura" "$STAGE/screens" "$STAGE/scripts"
cp _recon/manifest-sanitizado.json "$STAGE/estrutura/manifest.json"
# BLUEPRINT + docs de raiz (o que existir)
for f in BLUEPRINT-*.md LEIA-ME-PRIMEIRO.md README.md; do [ -f "$f" ] && cp "$f" "$STAGE/"; done
# screenshots (ja revisados manualmente; os com PII devem ter sido apagados antes)
[ -d screens ] && cp -r screens/* "$STAGE/screens/" 2>/dev/null || true
# scripts (o motor da captura, pra reproduzir)
[ -d _scripts ] && cp _scripts/*.mjs _scripts/*.py "$STAGE/scripts/" 2>/dev/null || true

# acesso/senha SO com pedido explicito
if [ "${INCLUIR_ACESSO:-0}" = "1" ] && [ -f "ACESSO.md" ]; then
  cp ACESSO.md "$STAGE/"
  echo "AVISO: ACESSO.md (com senha) INCLUIDO a pedido."
fi

# 2) zipar (nunca inclui _recon/ de sessao, _storage-state, _code, logs)
( cd "$STAGE" && zip -r -q "$ZIP" . )
rm -rf "$STAGE"

SHA=$(sha256sum "$ZIP" | cut -d' ' -f1)
SIZE=$(du -h "$ZIP" | cut -f1)
echo "pacote: $ZIP"
echo "tamanho: $SIZE"
echo "sha256:  $SHA"
echo "conteudo:"
unzip -l "$ZIP" | tail -n +2 | head -40
