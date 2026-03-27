---
name: verification-before-completion
description: Proibe dizer "pronto" sem evidencia. Build, teste, logs devem confirmar. Use sempre ao finalizar qualquer tarefa.
---

# Verification Before Completion

## Regra Absoluta
> NUNCA dizer "pronto", "feito", "implementado" sem EVIDENCIA verificavel.

## O que Conta como Evidencia

### Backend
- [ ] Health check retorna 200
- [ ] Endpoint especifico retorna dados corretos
- [ ] Logs do servico sem erros
- [ ] Consulta SQL retorna resultado esperado

### Frontend
- [ ] `npm run build` sem erros
- [ ] Pagina carrega no browser
- [ ] Funcionalidade testada manualmente
- [ ] Console do browser sem erros

### Geral
- [ ] Codigo compila/transpila sem erros
- [ ] Testes passam (se existem)
- [ ] Nenhum erro novo nos logs
- [ ] Comportamento corresponde ao pedido do usuario

## O que NAO Conta como Evidencia
- "Eu acredito que funciona"
- "Deveria funcionar"
- "O codigo parece correto"
- "Fiz a mudanca conforme pedido"
- Build nao executado

## Processo
1. Implementar a mudanca
2. Executar verificacao apropriada (build, curl, test)
3. Coletar output/evidencia
4. Apresentar evidencia ao usuario
5. SO ENTAO dizer "pronto"

## Se a Verificacao Falhar
- NAO dizer "pronto com ressalvas"
- Investigar o erro
- Corrigir
- Verificar novamente
- Repetir ate evidencia positiva
