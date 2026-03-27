---
name: code-review
description: Checklist de revisao de codigo. Seguranca, padroes, performance. Use ao revisar codigo ou antes de deploy.
---

# Code Review Checklist

## Seguranca (CRITICO)
- [ ] Queries SQL parametrizadas (nunca concatenacao)
- [ ] Input do usuario sanitizado
- [ ] Endpoints protegidos com autenticacao
- [ ] Nenhuma credencial hardcoded (API keys, tokens, senhas)
- [ ] Nenhum .env commitado
- [ ] CORS configurado corretamente
- [ ] Rate limiting em endpoints publicos
- [ ] Sem eval(), innerHTML ou equivalentes perigosos

## Codigo
- [ ] Sem codigo morto ou comentado
- [ ] Sem console.log de debug em producao
- [ ] Tratamento de erros adequado (try/catch)
- [ ] TypeScript types corretos (sem `any`)
- [ ] Funcoes com responsabilidade unica
- [ ] Nomes descritivos (variaveis, funcoes, componentes)
- [ ] Sem duplicacao (DRY, mas sem over-abstraction)

## Performance
- [ ] Sem re-renders desnecessarios (React.memo, useCallback)
- [ ] Queries com indices adequados
- [ ] Cache aplicado onde faz sentido
- [ ] Sem loops N+1 (fetch em loop)
- [ ] Bundle size razoavel (lazy loading se grande)
- [ ] Imagens otimizadas (next/image, webp)

## Padroes do Projeto
- [ ] Segue convencoes do CLAUDE.md
- [ ] Consistente com codigo ao redor
- [ ] Reutiliza componentes/funcoes existentes
- [ ] Nao introduz dependencias desnecessarias
- [ ] Conteudo PT-BR com acentuacao correta
- [ ] Sem travessoes (em-dash) no conteudo

## Resultado
- APROVADO: Sem issues criticos, poucos medios
- APROVADO COM RESSALVAS: Issues medios listados
- REPROVADO: Issues criticos que devem ser corrigidos
