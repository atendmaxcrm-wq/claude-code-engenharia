#!/usr/bin/env bash
# Loop de critica ANTES do render (regra: nunca mostrar nem renderizar o video inteiro sem passar por aqui).
#   1) montar.py (index.html, trilha, out/batidas.md)   2) lint (para no ERRO)
#   3) um quadro por batida SEM renderizar o video (hf snapshot, ~1 s por quadro)
#   4) folhas: out/revisao/rN/folha-batidas.jpg (todas as batidas) e folha-celular.jpg (um por compasso, tamanho de celular)
#   5) abre a rodada N em out/revisao.md com a tabela de notas para preencher
# Depois: olhar as folhas (Read), dar nota 1-10 nos 6 criterios, corrigir os 3 piores, rodar de novo.
# So renderizar quando TODAS as notas forem 8 ou mais.
# uso: bash revisar.sh <pasta-do-projeto> [--cada N] [--formato 16:9]   (--cada 2 = um quadro a cada 2 batidas)
set -euo pipefail
SK="$(cd "$(dirname "$0")" && pwd)"
P="$(cd "${1:?informe a pasta do projeto}" && pwd)"; shift
VM="${VIDEO_MOTION_HOME:-$HOME/.video-motion}"
[ -f "$VM/env.sh" ] || { echo "rode antes: bash $SK/instalar.sh"; exit 1; }
source "$VM/env.sh"
CADA=""
while [ $# -gt 0 ]; do case "$1" in
  --cada) CADA="$2"; shift 2 ;;
  --formato) export VM_FORMATO="$2"; shift 2 ;;
  *) echo "opcao desconhecida: $1"; exit 1 ;;
esac; done

echo "== 1. montar"
LOG=$(mktemp); trap 'rm -f "$LOG"' EXIT
python3 "$SK/motor/montar.py" "$P" | tee "$LOG"

echo "== 2. lint"
LINT=$(hf lint "$P" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' || true)
echo "$LINT" | grep -E '✗' || true
if echo "$LINT" | grep -q '✗'; then echo "PARADO: corrija os erros do lint acima"; exit 1; fi

mkdir -p "$P/out/revisao"; N=$(( $(find "$P/out/revisao" -mindepth 1 -maxdepth 1 -name "r*" -type d | wc -l) + 1 ))
D="$P/out/revisao/r$N"; mkdir -p "$D/quadros"
# instante de cada quadro: 3/4 da batida (o que entrou NA batida ja esta visivel e quase assentado)
read -r TEMPOS KS < <(python3 - "$P/out/batidas.json" "${CADA:-0}" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1])); bs = m["batidas"]; cada = int(sys.argv[2]) or (1 if len(bs) <= 64 else 2)
sel = [b for b in bs if b["k"] % cada == 0]
print(",".join(f"{min(m['total'] - .02, b['t'] + .75 * m['B']):.3f}" for b in sel), ",".join(str(b["k"]) for b in sel))
EOF
)
echo "== 3. quadros ($(echo "$KS" | tr ',' '\n' | wc -l) batidas)"
(cd "$VM/hf" && npx hyperframes snapshot "$P" --at "$TEMPOS" --no-end -o "$D/snap" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -E '✗|rror' || true)
i=0; IFS=',' read -ra AK <<< "$KS"
for f in $(ls "$D"/snap/frame-*.png | sort -V); do mv "$f" "$D/quadros/b$(printf %03d "${AK[$i]}").png"; i=$((i + 1)); done
rm -rf "$D/snap"

echo "== 4. folhas"
python3 "$SK/motor/folha.py" "$D/quadros" "$P/out/batidas.json" "$D"
grep -E '^AVISO' "$LOG" > "$D/avisos.txt" || true

echo "== 5. ficha da rodada"
[ -f "$P/out/revisao.md" ] || printf '# Revisão: %s\n\nRegra: nota 1 a 10 em cada critério olhando as folhas; corrigir os 3 piores; repetir até TUDO ficar 8 ou mais. Só então `renderizar.sh`.\n' "$(basename "$P")" > "$P/out/revisao.md"
cat >> "$P/out/revisao.md" <<EOF

## Rodada $N ($(date '+%d/%m %H:%M'))

Folhas: \`out/revisao/r$N/folha-batidas.jpg\` · \`out/revisao/r$N/folha-celular.jpg\` · tabela \`out/batidas.md\`
$( [ -s "$D/avisos.txt" ] && sed 's/^AVISO /- motor: /' "$D/avisos.txt" )

| Critério | Nota | Por quê (o que se vê em qual batida) |
|---|---|---|
| Gancho nos 2 primeiros segundos | | |
| Leitura no tamanho do celular | | |
| Qualidade do movimento | | |
| Variedade (algo novo a cada 2 a 4 s, sem padrão de IA) | | |
| Fidelidade à marca | | |
| Sincronia com o som | | |

3 piores problemas e a correção:
1.
2.
3.
EOF
echo "rodada $N pronta: olhe $D/folha-batidas.jpg e $D/folha-celular.jpg e preencha out/revisao.md"
