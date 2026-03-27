---
name: component-builder
description: Como criar componentes neste projeto. Estrutura, contexts, API calls, padroes. Use ao criar novos componentes.
---

# Component Builder

## Estrutura de Componente
```
components/[Feature]/
  ├── [Feature].tsx           # Orquestrador principal
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
- Componente > 300 linhas
- > 5 useState no mesmo componente
- > 3 useEffect
- Logica misturada com JSX extenso
- Modais > 80 linhas inline

## Quando NAO Decompor
- < 200 linhas com 1 responsabilidade
- Componente utilitario (Button, Input, Badge)
- Puramente visual sem logica

## Padroes
- Componentes funcionais com hooks
- TypeScript com tipagem estrita (sem `any`)
- Props tipadas com interface (nao type)
- Exportar como default no arquivo, named no index.ts
- Estados de loading, error e empty SEMPRE tratados

## Hooks Customizados
```typescript
// useFeatureData.ts - busca e estado
export function useFeatureData(id: string) {
  const [data, setData] = useState<Feature | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { /* fetch */ }, [id]);

  return { data, loading, error, refetch };
}
```

## API Calls
- fetch com try/catch
- Loading state durante request
- Error handling com mensagem ao usuario
- Otimistic updates quando possivel
- Debounce para search/filter (300ms)

## Styling
- Tailwind CSS (utility-first)
- Responsivo: mobile-first (sm: md: lg:)
- Dark mode: classes hardcoded (sem toggle)
- Animacoes: Framer Motion ou GSAP (ver interaction-patterns)
