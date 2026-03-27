---
description: Migrar lib ou refatorar implementacao de componente
argument-hint: "[ex: drag and drop para dnd-kit, form validation para react-hook-form]"
user-invocable: true
---

Execute migracao: $ARGUMENTS

### Fase 1: Mapear Estado Atual
- Identificar TODOS os usos (Grep imports, referencias)
- Listar features que DEVEM ser preservadas
- Identificar integracoes (callbacks, estados compartilhados)
- Documentar comportamento atual

### Fase 2: Pesquisar Alternativa
Se ainda nao decidiu -> /pesquisar-tech
Se ja decidiu -> ler documentacao completa, migration guides, issues abertas

### Fase 3: Plano de Migracao
ANTES -> DEPOIS com lista de passos
IMPORTANTE: Migrar LADO A LADO. Nunca deletar antigo antes do novo funcionar.

### Fase 4: Implementacao
1. Instalar nova dependencia
2. Criar componente novo (sem tocar no antigo)
3. Migrar feature por feature — testar cada uma
4. Testar integracao
5. Remover codigo antigo
6. Remover dependencia antiga (npm uninstall)
7. Verificar que o servico funciona corretamente

### Fase 5: Validacao
- [ ] Servico respondendo sem erros
- [ ] Todas features preservadas funcionam
- [ ] Nenhuma regressao
- [ ] Sem imports orfaos da lib antiga
- [ ] Sem codigo morto/comentado
- [ ] Logs limpos

NUNCA deletar antes de criar. NUNCA migrar tudo de uma vez.
