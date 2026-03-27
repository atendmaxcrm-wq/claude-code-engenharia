---
name: commit
description: Commits convencionais. Formato feat/fix/ref/perf/docs. Use ao commitar mudancas.
---

# Conventional Commits

## Formato
```
tipo(escopo): descricao curta

[corpo opcional - detalhes]

[footer opcional - breaking changes]
```

## Tipos
| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correcao de bug |
| `ref` | Refatoracao (sem mudar comportamento) |
| `perf` | Melhoria de performance |
| `docs` | Documentacao |
| `style` | Formatacao, espacamento (sem mudar logica) |
| `test` | Testes |
| `chore` | Manutencao, configs, dependencias |
| `ci` | CI/CD |

## Escopo (opcional)
- Modulo ou area afetada: `feat(blog)`, `fix(auth)`, `ref(api)`
- Arquivo se relevante: `fix(evolution-service)`

## Regras
- Descricao em minusculas, sem ponto final
- Imperativo: "adiciona filtro" (nao "adicionado" ou "adicionando")
- Max 72 caracteres na primeira linha
- Corpo separado por linha em branco
- Breaking changes: `BREAKING CHANGE:` no footer

## Exemplos
```
feat(blog): adiciona filtro por categoria no endpoint

fix(cron): corrige horario do blog slot 2 de 12:00 para 13:00

ref(api): extrai validacao de input para middleware

perf(queries): adiciona indice em posts.created_at

chore: atualiza dependencias do projeto
```

## Anti-padroes
- "update" sem contexto
- "fix bug" sem dizer qual
- "changes" generico
- Commit gigante com mudancas nao relacionadas
- Commitar .env ou credenciais
