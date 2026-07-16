---
name: migrar-componente
description: "Migrar lib ou refatorar implementacao de componente. Suporta Agent Teams para migracoes que afetam muitos arquivos. Use ao trocar libs ou abordagem tecnica."
---

# Migrar Componente — Troca de Lib ou Refatoracao

Migracao solicitada: $ARGUMENTS

---

## Workflow Padrao (Migracao Simples)

### Fase 1: Mapear Estado Atual
- Identificar TODOS os usos (Grep imports, referencias)
- Listar features que DEVEM ser preservadas
- Identificar integracoes (callbacks, estados compartilhados)
- Documentar comportamento atual

### Fase 2: Pesquisar Alternativa
Se ainda nao decidiu → /pesquisar-tech
Se ja decidiu → ler documentacao, migration guides, issues abertas

### Fase 3: Plano de Migracao
ANTES → DEPOIS com lista de passos
IMPORTANTE: Migrar LADO A LADO. Nunca deletar antigo antes do novo funcionar.

### Fase 4: Implementacao
1. Instalar nova dependencia
2. Criar componente novo (sem tocar no antigo)
3. Migrar feature por feature — testar cada uma
4. Testar integracao
5. Remover codigo antigo
6. Remover dependencia antiga (npm uninstall)

### Fase 5: Validacao
- [ ] Build sem erros
- [ ] Todas features preservadas funcionam
- [ ] Nenhuma regressao
- [ ] Sem imports orfaos da lib antiga
- [ ] Sem codigo morto/comentado

NUNCA deletar antes de criar. NUNCA migrar tudo de uma vez.

---

## Modo Agent Teams (Migracao Grande)

Usar quando: migracao afeta 10+ arquivos, lib usada em multiplos dominios (componentes + hooks + utils + testes).

### Time de Migracao

| Teammate | Tipo | Responsabilidade |
|----------|------|-----------------|
| **researcher** | Explore (sonnet) | Mapeia todos os usos da lib antiga, documenta API surface |
| **migrator-core** | general-purpose (sonnet) | Migra componentes core e hooks |
| **migrator-pages** | general-purpose (sonnet) | Migra paginas e integracoes |
| **validator** | general-purpose (haiku) | Roda build, verifica imports orfaos, testa |

### Execucao

```
TeamCreate: { team_name: "migration-[lib]", description: "Migrate [old] to [new]" }

Wave 0: researcher (Explore) — mapeia todos os usos, gera relatorio
Wave 1: migrator-core — migra componentes base e hooks (outros dependem)
Wave 2 (apos Wave 1): migrator-pages (migra consumidores dos componentes core)
Wave 3: validator — build + verificacao de imports orfaos + testes
TeamDelete
```

### Regras
- **Cada migrator recebe lista explicita** de arquivos do researcher
- **Migrators NAO deletam lib antiga** — so criam novo lado a lado
- **Validator confirma** que tudo funciona antes de remover antigo
- **Remocao final** (npm uninstall, delete old files) feita pelo lead apos quality gate

### Quando NAO usar Agent Teams
- Lib usada em menos de 5 arquivos → migrar direto
- Migracao e so renomear imports (drop-in replacement) → fazer direto
