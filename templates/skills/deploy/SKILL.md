---
name: deploy
description: Deploy completo (restart PM2 + verificacao). Use ao fazer deploy de mudancas.
---

## Pre-requisitos (OBRIGATORIO)

1. Ja testou as mudancas? Feature/fix DEVE ter sido testada antes
2. Aprovacao do usuario: Deploy so com aprovacao explicita

## Passos

### 1. Verificar estado atual
```bash
pm2 status
curl http://localhost:4001/health
```

### 2. Restart do servico
```bash
pm2 restart monitor-server
```

### 3. Verificar saude pos-restart
```bash
# Aguardar 5 segundos para o servidor subir
sleep 5

# Health check
curl http://localhost:4001/health

# Verificar logs (sem erros)
pm2 logs monitor-server --lines 20 --nostream

# Status do blog
curl http://localhost:4001/api/blog/status
```

### 4. Validacao
- [ ] Health check retorna 200
- [ ] Logs sem erros de startup
- [ ] Crons registrados corretamente
- [ ] Endpoints respondendo

Se algum passo falhar, NAO continue. Reporte o erro.

### Rollback (se necessario)
```bash
# Reverter ultimo commit
git revert HEAD

# Restart com codigo anterior
pm2 restart monitor-server
```
