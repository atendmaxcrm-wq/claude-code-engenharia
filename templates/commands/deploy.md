---
description: Deploy completo (restart servico + verificacao)
user-invocable: true
---

## Pre-requisitos (OBRIGATORIO)

1. Ja testou as mudancas? Feature/fix DEVE ter sido testada antes
2. Aprovacao do usuario: Deploy so com aprovacao explicita

## Passos

### 1. Verificar estado atual
Verificar que o servico esta rodando e saudavel.

### 2. Restart do servico
Usar o process manager do projeto (PM2, systemd, etc.)

### 3. Verificar saude pos-restart
- Aguardar servidor subir
- Health check
- Verificar logs (sem erros)

### 4. Validacao
- [ ] Health check retorna 200
- [ ] Logs sem erros de startup
- [ ] Endpoints respondendo

Se algum passo falhar, NAO continue. Reporte o erro.

### Rollback (se necessario)
- Reverter ultimo commit
- Restart com codigo anterior
