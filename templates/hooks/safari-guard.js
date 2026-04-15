#!/usr/bin/env node
'use strict';

/**
 * Hook: Safari Guard (PreToolUse — Edit, Write)
 *
 * Analisa codigo .tsx/.jsx sendo editado/criado e avisa se contem
 * padroes problematicos para Safari iOS/macOS.
 *
 * Exit 0 = permite (com warning no stdout se encontrar issues)
 * Nao bloqueia — apenas avisa.
 *
 * Baseado em 9 fixes reais de producao (Safari iOS):
 *  1. Flex children sem min-h-0 (scroll quebrado)
 *  2. aspect-ratio/aspect-square sem padding-bottom fallback
 *  3. 100vh sem dvh fallback
 *  4. Select sem WebkitAppearance none
 *  5. aspectRatio inline sem minHeight: 0
 *  6. calc(100vh - ...) sem dvh
 *  7. backdrop-filter inline sem -webkit- (se nao Tailwind v4)
 */

const SAFARI_PATTERNS = [
  {
    id: 'flex-no-minh0',
    severity: 'CRITICO',
    // Flex container com filho overflow-y sem min-h-0
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      // Track flex contexts
      let inFlex = false;
      let flexLine = 0;
      let braceDepth = 0;
      let flexBraceDepth = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Count JSX-like nesting (simplified)
        const opens = (line.match(/<[A-Za-z]/g) || []).length;
        const closes = (line.match(/<\//g) || []).length + (line.match(/\/>/g) || []).length;
        braceDepth += opens - closes;

        // Detect flex container
        if (/\bflex\b.*\bflex-col\b|\bflex-col\b.*\bflex\b|\bdisplay:\s*['"]?flex/.test(line)) {
          inFlex = true;
          flexLine = i;
          flexBraceDepth = braceDepth;
        }

        // Inside flex context, check for overflow-y without min-h-0
        if (inFlex && braceDepth > flexBraceDepth) {
          if (/overflow-y-auto|overflow-y-scroll|overflowY:\s*['"]auto|overflowY:\s*['"]scroll/.test(line)) {
            // Check surrounding lines (current and 2 before/after) for min-h-0
            const context = lines.slice(Math.max(0, i - 2), Math.min(lines.length, i + 3)).join(' ');
            if (!/min-h-0|minHeight:\s*0/.test(context)) {
              issues.push({
                line: i + 1,
                msg: 'Flex child com overflow-y scroll sem min-h-0 — Safari nao faz scroll',
                fix: 'Adicionar min-h-0 no elemento ou minHeight: 0 no style',
              });
            }
          }
        }

        // Reset flex context when we exit its depth
        if (inFlex && braceDepth <= flexBraceDepth && i > flexLine) {
          inFlex = false;
        }
      }

      return issues;
    },
  },
  {
    id: 'aspect-ratio-no-fallback',
    severity: 'CRITICO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Tailwind aspect classes
        if (/\baspect-square\b|\baspect-video\b|\baspect-\[/.test(line)) {
          // Check if it's already using padding-bottom trick nearby
          const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 4)).join(' ');
          if (!/paddingBottom|padding-bottom/.test(context)) {
            issues.push({
              line: i + 1,
              msg: 'aspect-ratio CSS sem fallback padding-bottom — Safari < 15 colapsa',
              fix: 'Substituir por padding-bottom trick (100% para square, 56.25% para video)',
            });
          }
        }
      }

      return issues;
    },
  },
  {
    id: 'vh-no-dvh',
    severity: 'ALTO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // 100vh without dvh nearby
        if (/\bh-screen\b|\bmin-h-screen\b|\b100vh\b/.test(line)) {
          const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(' ');
          if (!/dvh|dvw/.test(context)) {
            issues.push({
              line: i + 1,
              msg: '100vh sem fallback dvh — Safari iOS inclui barra de endereco na altura',
              fix: 'Usar style={{ minHeight: "100dvh" }} ou height: "100dvh"',
            });
          }
        }
      }

      return issues;
    },
  },
  {
    id: 'select-no-webkit-appearance',
    severity: 'ALTO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/<select\b/.test(line)) {
          // Look ahead for WebkitAppearance in nearby lines
          const context = lines.slice(i, Math.min(lines.length, i + 8)).join(' ');
          if (/className|rounded|border|bg-/.test(context) && !/WebkitAppearance|webkitAppearance|-webkit-appearance/.test(context)) {
            issues.push({
              line: i + 1,
              msg: '<select> estilizado sem WebkitAppearance: none — Safari ignora estilos',
              fix: 'Adicionar style={{ WebkitAppearance: "none", appearance: "none" }}',
            });
          }
        }
      }

      return issues;
    },
  },
  {
    id: 'inline-aspect-ratio-no-minheight',
    severity: 'ALTO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/aspectRatio:\s*['"]/.test(line)) {
          const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(' ');
          if (!/minHeight:\s*0/.test(context)) {
            issues.push({
              line: i + 1,
              msg: 'aspectRatio inline sem minHeight: 0 — Safari pode colapsar em flex',
              fix: 'Adicionar minHeight: 0 no mesmo style object',
            });
          }
        }
      }

      return issues;
    },
  },
  {
    id: 'calc-vh-no-dvh',
    severity: 'MEDIO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/calc\(\s*100vh/.test(line)) {
          if (!/dvh/.test(line)) {
            issues.push({
              line: i + 1,
              msg: 'calc(100vh - ...) sem dvh — Safari iOS calcula errado com barra dinamica',
              fix: 'Usar max(Xpx, calc(100dvh - ...))',
            });
          }
        }
      }

      return issues;
    },
  },
  {
    id: 'backdrop-filter-no-webkit',
    severity: 'INFO',
    test(content) {
      const issues = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Only flag inline styles, not Tailwind classes (v4 handles it)
        if (/backdropFilter:\s*['"]/.test(line)) {
          const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 3)).join(' ');
          if (!/WebkitBackdropFilter|webkitBackdropFilter/.test(context)) {
            issues.push({
              line: i + 1,
              msg: 'backdropFilter inline sem WebkitBackdropFilter — Safari precisa do prefixo',
              fix: 'Adicionar WebkitBackdropFilter com mesmo valor',
            });
          }
        }
      }

      return issues;
    },
  },
];

async function main() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch {
    process.exit(0);
  }

  // Get file path from tool input
  const filePath = data.tool_input?.file_path || '';

  // Only check .tsx, .jsx files
  if (!/\.(tsx|jsx)$/i.test(filePath)) {
    process.exit(0);
  }

  // Get content being written/edited
  // For Write: tool_input.content
  // For Edit: tool_input.new_string
  const content = data.tool_input?.content || data.tool_input?.new_string || '';

  if (!content || content.length < 20) {
    process.exit(0);
  }

  // Run all pattern checks
  const allIssues = [];
  for (const pattern of SAFARI_PATTERNS) {
    const issues = pattern.test(content);
    for (const issue of issues) {
      allIssues.push({
        severity: pattern.severity,
        id: pattern.id,
        ...issue,
      });
    }
  }

  if (allIssues.length === 0) {
    process.exit(0);
  }

  // Sort by severity
  const severityOrder = { CRITICO: 0, ALTO: 1, MEDIO: 2, INFO: 3 };
  allIssues.sort((a, b) => (severityOrder[a.severity] || 9) - (severityOrder[b.severity] || 9));

  // Format output
  const lines = [];
  lines.push(`[Safari Guard] ${allIssues.length} problema(s) detectado(s) em ${filePath}:`);
  lines.push('');

  for (const issue of allIssues) {
    lines.push(`  [${issue.severity}] Linha ~${issue.line}: ${issue.msg}`);
    lines.push(`    Fix: ${issue.fix}`);
  }

  const criticos = allIssues.filter(i => i.severity === 'CRITICO').length;
  const altos = allIssues.filter(i => i.severity === 'ALTO').length;

  if (criticos > 0) {
    lines.push('');
    lines.push(`  *** ${criticos} CRITICO(S) — corrigir antes de deploy! Use /safari-check para auditoria completa.`);
  } else if (altos > 0) {
    lines.push('');
    lines.push(`  * ${altos} ALTO(S) encontrado(s). Use /safari-check para auditoria completa.`);
  }

  // Output warning (exit 0 = allow, just inform)
  process.stdout.write(lines.join('\n') + '\n');
  process.exit(0);
}

main().catch(() => process.exit(0));
