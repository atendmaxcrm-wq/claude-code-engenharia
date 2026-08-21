---
name: analise-impacto
description: Analise obrigatoria antes de editar arquivos core. Mapeia dependencias e efeitos colaterais. Use antes de modificar arquivos criticos.
---

# Analise de Impacto

## Quando Aplicar
- Editar arquivo core (index.js, config, schema)
- Alterar interface publica de modulo
- Mudar schema do banco
- Alterar fluxo de autenticacao/permissoes
- Remover ou renomear exports

## Passo 1: Mapear Dependencias
```
Arquivo alvo: [path]
  ├── Importado por: [listar todos os arquivos que importam]
  ├── Importa de: [listar dependencias]
  ├── Exports publicos: [listar funcoes/classes exportadas]
  └── Usado em: [endpoints, crons, hooks]
```

## Passo 2: Classificar Risco
| Nivel | Criterio | Acao |
|-------|----------|------|
| BAIXO | Mudanca interna, sem alteracao de interface | Implementar com cuidado |
| MEDIO | Alteracao de interface, poucos consumidores | Planejar, testar cada consumidor |
| ALTO | Alteracao de interface, muitos consumidores | Plano detalhado, aprovacao obrigatoria |
| CRITICO | Schema, auth, config principal | Plano + backup + rollback plan |

## Passo 3: Listar Efeitos Colaterais
- Queries afetadas?
- Cache a invalidar?
- Endpoints que mudam comportamento?
- Componentes frontend que quebram?
- Crons que dependem?
- Integracoes externas afetadas?

## Passo 4: Plano de Mitigacao
- Ordem de aplicacao (dependencias primeiro)
- Testes a executar apos cada mudanca
- Rollback plan se algo der errado
- Comunicar riscos ao usuario ANTES de implementar

## Regra de Ouro
> Nunca editar arquivo core sem antes mapear quem depende dele.
> O custo de 5 minutos de analise e menor que o custo de 2 horas de debug.
