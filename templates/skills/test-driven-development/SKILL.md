---
name: test-driven-development
description: RED-GREEN-REFACTOR. Teste falhando primeiro, codigo minimo depois, refatorar por ultimo. Use ao implementar logica critica.
---

# Test-Driven Development (TDD)

## Ciclo RED-GREEN-REFACTOR

### 1. RED — Escrever teste que FALHA
- Escrever teste para o comportamento desejado
- Rodar o teste — DEVE falhar
- Se nao falhar, o teste esta errado ou a feature ja existe

### 2. GREEN — Codigo MINIMO para passar
- Escrever o codigo mais simples que faz o teste passar
- Nao otimizar, nao generalizar, nao embelezar
- So fazer o teste ficar verde

### 3. REFACTOR — Melhorar sem mudar comportamento
- Testes continuam verdes
- Remover duplicacao
- Melhorar nomes
- Simplificar logica
- Extrair funcoes se necessario

## Quando Usar TDD
- Logica de negocios complexa
- Parsing/transformacao de dados
- Validacao com regras multiplas
- Integracao com servicos externos (mocks)
- Correcao de bugs (teste reproduz o bug primeiro)

## Quando NAO Usar TDD
- Componentes visuais (prefira visual testing)
- CRUD simples (boilerplate > valor)
- Prototipacao rapida (explorar primeiro)
- Configuracao/setup (nao ha logica)

## Dicas
- Testes pequenos e focados (1 assert por teste)
- Nomes descritivos: "deve retornar erro quando email invalido"
- Arrange-Act-Assert (setup, execute, verify)
- Mocks para dependencias externas
- Nao testar implementacao, testar comportamento
