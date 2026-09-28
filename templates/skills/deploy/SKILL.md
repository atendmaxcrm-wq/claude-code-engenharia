---
name: deploy
description: Deploy completo (restart PM2 + verificacao). Use ao fazer deploy de mudancas.
---

## Pre-requisitos (OBRIGATORIO)

1. Ja testou as mudancas? Feature/fix DEVE ter sido testada antes
2. Aprovacao do usuario: Deploy so com aprovacao explicita
3. Ler no CLAUDE.md do projeto: nome do processo PM2, porta, rota de health e receita
   de build. Esta skill NAO crava nenhum desses valores; se o CLAUDE.md nao tiver, perguntar.

## Passos

Abaixo, `<processo>`, `<porta>` e `<health>` vem do CLAUDE.md do projeto.

### 1. Verificar estado atual
```bash
pm2 status
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<porta><health>
```

### 2. Build (se o projeto tiver etapa de build)
Seguir a receita do CLAUDE.md (ex.: parar, arquivar o build antigo, buildar, subir).
Se o build falhar, NAO reiniciar o processo com o build quebrado.

### 3. Restart do servico
```bash
pm2 restart <processo>
```

### 4. Verificar saude pos-restart
```bash
sleep 5
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<porta><health>
pm2 logs <processo> --lines 20 --nostream
```

### 5. Validacao
- [ ] Health check retorna 200
- [ ] Logs sem erros de startup
- [ ] Crons registrados corretamente (se houver)
- [ ] Endpoints alterados respondendo

Se algum passo falhar, NAO continue. Reporte o erro.

### Rollback (se necessario)
```bash
# Reverter ultimo commit
git revert HEAD

# Rebuild (se houver) e restart com codigo anterior
pm2 restart <processo>
```
