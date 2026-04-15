#!/bin/bash
# Hook SessionStart (compact): re-injeta contexto apos compactacao
# Injeta apenas insights + progresso (essenciais). Roadmaps e conhecimento sao sob demanda.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORIA_DIR="$PROJECT_ROOT/memoria"

if [ ! -d "$MEMORIA_DIR" ]; then
  exit 0
fi

echo "---"
echo "## [MEMORIA REINJETADA]"
echo ""

# Progresso (mais importante: onde paramos)
if [ -f "$MEMORIA_DIR/progresso.md" ]; then
  echo "### Progresso Atual"
  echo ""
  cat "$MEMORIA_DIR/progresso.md"
  echo ""
  echo "---"
  echo ""
fi

# Insights (decisoes e gotchas)
if [ -f "$MEMORIA_DIR/insights.md" ]; then
  echo "### Insights do Projeto"
  echo ""
  cat "$MEMORIA_DIR/insights.md"
  echo ""
  echo "---"
  echo ""
fi

# Lista roadmaps disponiveis (nao injeta conteudo, so nomes)
if [ -d "$MEMORIA_DIR/roadmaps" ]; then
  ROADMAPS=$(ls "$MEMORIA_DIR/roadmaps/"*.md 2>/dev/null)
  if [ -n "$ROADMAPS" ]; then
    echo "### Roadmaps Disponiveis (leia sob demanda)"
    echo ""
    for f in $ROADMAPS; do
      echo "- \`memoria/roadmaps/$(basename "$f")\`"
    done
    echo ""
  fi
fi

# Lista sistema/ e conhecimento/ (so nomes, nao conteudo)
for SUBDIR in sistema conhecimento; do
  if [ -d "$MEMORIA_DIR/$SUBDIR" ]; then
    FILES=$(ls "$MEMORIA_DIR/$SUBDIR/"*.md 2>/dev/null)
    if [ -n "$FILES" ]; then
      echo "### Memoria/$SUBDIR (leia sob demanda)"
      for f in $FILES; do
        echo "  - $(basename "$f") ($(wc -l < "$f") linhas)"
      done
      echo ""
    fi
  fi
done

echo "---"
echo "[Memoria reinjetada automaticamente. Use \`/atualizar-memoria\` ao final da sessao.]"
