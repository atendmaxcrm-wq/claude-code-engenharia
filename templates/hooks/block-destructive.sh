#!/bin/bash
# Hook PreToolUse para Bash: bloqueia comandos destrutivos
# Exit 0 = permite, Exit 2 = bloqueia com mensagem

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Lista de padroes destrutivos
DESTRUCTIVE_PATTERNS=(
  "rm -rf /"
  "rm -rf /*"
  "rm -rf ~"
  "rm -rf \."
  "DROP TABLE"
  "DROP DATABASE"
  "TRUNCATE"
  "DELETE FROM .* WHERE 1"
  "git reset --hard"
  "git push.*--force"
  "git push.*-f "
  "git clean -fd"
  "git checkout \."
  "git restore \."
  "git branch -D main"
  "git branch -D master"
  "> /dev/sda"
  "mkfs\."
  "dd if=/dev/zero"
  ":(){:|:&};:"
  "chmod -R 777 /"
  "chown -R .* /"
)

for PATTERN in "${DESTRUCTIVE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$PATTERN"; then
    echo "BLOQUEADO: Comando destrutivo detectado ('$PATTERN'). Confirme com o usuario antes de prosseguir." >&2
    exit 2
  fi
done

exit 0
