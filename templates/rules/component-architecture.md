---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---

# Decomposicao de Componentes

## Regra
Componentes > 300 linhas ou com 2+ responsabilidades DEVEM ser decompostos em pasta:

```
components/[feature]/
  ├── [Feature].tsx           # Orquestrador (max ~500 linhas)
  ├── hooks/
  │   ├── use[Feature]Config.ts
  │   ├── use[Feature]Data.ts
  │   └── use[Feature]Actions.ts
  ├── views/
  │   ├── [SubView1].tsx
  │   └── [SubView2].tsx
  ├── modals/
  │   └── [Modal].tsx
  ├── types.ts
  └── index.ts                # Re-exports
```

## Quando Decompor
- > 300 linhas
- > 5 useState
- > 3 useEffect
- Logica misturada com JSX extenso
- Modais > 80 linhas inline
- Mesma JSX em 2+ lugares

## Quando NAO Decompor
- < 200 linhas
- 1 responsabilidade clara
- Componente utilitario (Button, Input)
- Puramente visual

## Processo
1. Mapear responsabilidades atuais
2. Planejar ondas: utils -> modais -> hooks -> views -> consolidar
3. Extrair em ondas (1 por vez, testar cada)
4. Orquestrador final: so inicializa hooks + renderiza subcomponentes
