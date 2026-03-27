---
name: systematic-debugging
description: Debug sistematico em 4 fases. Proibe quick fixes. Use ao investigar bugs ou comportamento inesperado.
---

# Systematic Debugging

## Principio
> Quick fixes mascaram problemas. Encontre a CAUSA RAIZ, nao o sintoma.

## Fase 1: INVESTIGAR
- Reproduzir o problema (cenario exato)
- Coletar evidencias: logs, estado, console, rede
- Tracar fluxo de dados: input → processamento → output
- Onde exatamente o comportamento desvia do esperado?

## Fase 2: ANALISAR
- Isolar o trecho de codigo responsavel
- Verificar: dados de entrada estao corretos?
- Verificar: logica de processamento esta correta?
- Verificar: output esta sendo usado corretamente?
- Comparar: como funcionava antes? O que mudou?

## Fase 3: HIPOTESE
- Formular ate 3 hipoteses ordenadas por probabilidade
- Para cada hipotese:
  - O que explicaria o comportamento?
  - Como testar/validar?
  - Se confirmada, qual a correcao?
- Testar a hipotese mais provavel primeiro

## Fase 4: IMPLEMENTAR
- Corrigir a causa raiz (nao o sintoma)
- Testar que o problema original foi resolvido
- Testar que nao introduziu regressoes
- Documentar em troubleshooting.md:
  - Sintoma
  - Causa raiz
  - Correcao aplicada
  - Como evitar no futuro

## Anti-padroes (PROIBIDO)
- Adicionar try/catch para esconder erro
- Adicionar setTimeout/retry sem entender por que falha
- Mudar codigo "pra ver se funciona" sem hipotese
- Dizer "funciona agora" sem entender por que
- Corrigir sintoma sem investigar causa
