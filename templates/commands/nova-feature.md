---
description: Planejar implementacao de uma nova feature com analise de impacto
argument-hint: "[descricao da feature]"
user-invocable: true
---

Planeje a implementacao da seguinte feature: $ARGUMENTS

Siga estes passos:

1. **Consultar memoria**: Leia os arquivos de memoria relevantes para entender o contexto
   - Database schema: `/memoria/sistema/database-schema.md`
   - API endpoints: `/memoria/sistema/api-endpoints.md`
   - Permissoes: `/memoria/sistema/permissoes.md`

2. **Analisar impacto**: Identifique quais partes do sistema serao afetadas:
   - Novas tabelas no banco?
   - Novos endpoints na API?
   - Novos componentes no frontend?
   - Mudancas em componentes existentes?

3. **Criar plano**: Apresente um plano detalhado com:
   - Alteracoes no banco de dados (migrations SQL)
   - Endpoints da API necessarios
   - Componentes frontend necessarios
   - Permissoes requeridas (quais roles tem acesso)

4. **Listar arquivos**: Indique quais arquivos serao criados/modificados

NAO implemente ainda. Apresente o plano e aguarde aprovacao antes de comecar.
