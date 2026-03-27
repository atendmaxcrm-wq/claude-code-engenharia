---
name: planejar-feature
description: Workflow de 6 fases para planejar features. Use antes de implementar qualquer feature media ou grande.
---

# Planejar Feature — Workflow de 6 Fases

## Fase 1: ENTENDER
- O que o usuario quer? Reformular para confirmar
- Consultar memoria (changelog, insights, troubleshooting)
- Verificar se algo similar ja existe
- Identificar escopo: pequena / media / grande

## Fase 2: PESQUISAR (se necessario)
- Feature envolve lib/tech nova? → pesquisar alternativas
- Componente UI complexo? → buscar referencias
- Multiplas abordagens? → comparar antes de escolher
- Nao pular esta fase — decisoes ruins custam caro

## Fase 3: PLANEJAR

### Banco de Dados
- Novas tabelas? Colunas, tipos, constraints, indices
- Alteracoes em tabelas existentes? Migrations
- Impacto em queries existentes?

### Backend
- Novos endpoints? Metodo, rota, auth, body, resposta
- Cache? TTL? Invalidacao?
- Integracoes externas?

### Frontend
- Novos componentes? Estrutura?
- Novos tipos TypeScript?
- Impacto em componentes existentes?

### Permissoes
- Quais roles tem acesso?
- Novos scopes necessarios?

## Fase 4: DIMENSIONAR
| Tamanho | Arquivos | Abordagem |
|---------|----------|-----------|
| Pequena | 1-3 | Implementar direto |
| Media | 3-5 | Planejar passos, sequencial |
| Grande | 5+ | Agent teams com ondas paralelas |

## Fase 5: LISTAR ARQUIVOS
Todos os arquivos que serao criados ou modificados.
Ordem de implementacao (dependencias primeiro).

## Fase 6: AGUARDAR APROVACAO
- Apresentar plano completo ao usuario
- NAO implementar sem aprovacao
- Ajustar plano se usuario pedir mudancas
- So apos "ok" / "aprovo" → implementar
