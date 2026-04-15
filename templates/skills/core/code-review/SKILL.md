---
name: code-review
description: "Checklist de revisao de codigo. Seguranca, padroes, performance. Suporta Agent Teams para review multi-perspectiva. Use ao revisar codigo ou antes de deploy."
---

# Code Review

Alvo do review: $ARGUMENTS

---

## Checklist Padrao

### Seguranca (CRITICO)
- [ ] Queries SQL parametrizadas (nunca concatenacao)
- [ ] Input do usuario sanitizado
- [ ] Endpoints protegidos com autenticacao
- [ ] Nenhuma credencial hardcoded (API keys, tokens, senhas)
- [ ] Nenhum .env commitado
- [ ] CORS configurado corretamente
- [ ] Rate limiting em endpoints publicos
- [ ] Sem eval(), innerHTML ou equivalentes perigosos

### Codigo
- [ ] Sem codigo morto ou comentado
- [ ] Sem console.log de debug em producao
- [ ] Tratamento de erros adequado (try/catch)
- [ ] TypeScript types corretos (sem `any`)
- [ ] Funcoes com responsabilidade unica
- [ ] Nomes descritivos (variaveis, funcoes, componentes)
- [ ] Sem duplicacao (DRY, mas sem over-abstraction)

### Performance
- [ ] Sem re-renders desnecessarios (React.memo, useCallback)
- [ ] Queries com indices adequados
- [ ] Cache aplicado onde faz sentido
- [ ] Sem loops N+1 (fetch em loop)
- [ ] Bundle size razoavel (lazy loading se grande)
- [ ] Imagens otimizadas (next/image, webp)

### Padroes do Projeto
- [ ] Segue convencoes do CLAUDE.md
- [ ] Consistente com codigo ao redor
- [ ] Reutiliza componentes/funcoes existentes
- [ ] Nao introduz dependencias desnecessarias
- [ ] Conteudo PT-BR com acentuacao correta
- [ ] Sem travessoes (em-dash) no conteudo

### Resultado
- **APROVADO**: Sem issues criticos, poucos medios
- **APROVADO COM RESSALVAS**: Issues medios listados
- **REPROVADO**: Issues criticos que devem ser corrigidos

---

## Modo Agent Teams (Review Multi-Perspectiva)

Usar quando: PR grande (10+ arquivos), mudanca cross-cutting, ou pre-deploy critico.

### Time de Review

| Teammate | Tipo | Perspectiva |
|----------|------|------------|
| **security-reviewer** | Explore (sonnet) | SQL injection, XSS, auth bypass, credentials, CORS |
| **quality-reviewer** | Explore (sonnet) | Codigo morto, tipos, DRY, nomes, patterns do projeto |
| **perf-reviewer** | Explore (sonnet) | Re-renders, N+1, cache, bundle, queries |

### Execucao

```
TeamCreate: { team_name: "code-review", description: "Review [escopo]" }

Wave 1 (todos paralelos — read-only, sem conflito):
Todos os 3 revisores rodam simultaneamente sobre os mesmos arquivos.
Cada um foca na sua perspectiva e gera lista de issues.

Comunicacao: Se um reviewer encontra algo relevante pra outro, avisa via SendMessage.
Ex: security-reviewer encontra query sem indice → avisa perf-reviewer.

Consolidacao: Lead merge todos os findings:
- Issues duplicados (encontrados por 2+ reviewers) = maior confianca
- Issues unicos = verificar se sao validos

TeamDelete
```

### Formato do Veredicto

```
## Code Review — [escopo]

### Issues Criticos (bloqueia merge)
| # | Issue | Reviewer | Arquivo:Linha |
|---|-------|----------|--------------|

### Issues Medios (corrigir antes de prod)
| # | Issue | Reviewer | Arquivo:Linha |

### Sugestoes (nice-to-have)
| # | Sugestao | Reviewer |

**Veredicto:** APROVADO / APROVADO COM RESSALVAS / REPROVADO
```

### Quando NAO usar Agent Teams
- Review de 1-3 arquivos → checklist manual suficiente
- Mudanca so de texto/CSS → nao precisa de time
- Hotfix urgente → review rapido single-pass
