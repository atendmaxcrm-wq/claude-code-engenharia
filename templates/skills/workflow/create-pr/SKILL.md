---
name: create-pr
description: Pull requests com descricoes claras. Formato padronizado com summary, changes, test plan. Use ao criar PRs.
---

# Create Pull Request

## Formato
```markdown
## Summary
[1-3 frases descrevendo O QUE muda e POR QUE]

## Changes
- [lista de mudancas significativas]
- [agrupar por arquivo ou area se muitos]

## Test Plan
- [ ] Build sem erros (`npm run build`)
- [ ] [teste especifico 1]
- [ ] [teste especifico 2]
- [ ] Sem regressoes em funcionalidades existentes

## Screenshots (se UI)
[antes/depois se mudou visual]

## Notes
[qualquer contexto adicional, riscos, decisoes]
```

## Regras
- Titulo curto (< 70 chars), formato: `tipo: descricao`
- Descricao no body (nao no titulo)
- Sempre incluir Test Plan
- Screenshots para mudancas visuais
- Referenciar issue se existir: `Fixes #123`
- Um PR = uma feature/fix (nao misturar)

## Tamanho Ideal
| Tamanho | Linhas | Expectativa |
|---------|--------|-------------|
| Pequeno | < 100 | Review rapido |
| Medio | 100-400 | Review detalhado |
| Grande | 400+ | Considerar dividir |

## Checklist Pre-PR
- [ ] Codigo compila sem erros
- [ ] Testes passam
- [ ] Sem console.log de debug
- [ ] Sem codigo comentado
- [ ] Sem credenciais hardcoded
- [ ] Commit messages claras
- [ ] Branch atualizada com main/dev
