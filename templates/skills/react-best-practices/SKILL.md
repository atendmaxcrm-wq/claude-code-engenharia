---
name: react-best-practices
description: 57 regras de performance React. Re-renders, bundle, virtualizacao, patterns. Use ao otimizar componentes React.
---

# React Best Practices

## Renderizacao
1. Componentes funcionais (nao class components)
2. React.memo para componentes que recebem mesmas props frequentemente
3. useCallback para callbacks passados como props
4. useMemo para calculos caros
5. Keys unicas e estaveis em listas (NUNCA index como key)
6. Evitar criar objetos/arrays inline em JSX (nova referencia cada render)
7. Lazy loading com React.lazy + Suspense para rotas/componentes pesados

## Estado
8. Estado o mais local possivel (nao levantar sem necessidade)
9. useState para estado simples, useReducer para estado complexo
10. Evitar estado derivado (calcular em render, nao duplicar em state)
11. Context para estado global leve (theme, auth, locale)
12. Nao usar Context para estado que muda frequentemente (re-render cascade)
13. Separar contexts por dominio (nao 1 context gigante)
14. Valores default em useState devem ser constantes (nao funcoes que rodam todo render)

## Efeitos
15. useEffect so para side effects (nao para derivar estado)
16. Dependencias do useEffect devem ser completas (ESLint react-hooks/exhaustive-deps)
17. Cleanup em useEffect para subscriptions, timers, listeners
18. Evitar useEffect para sincronizar estado (use derivacao direta)
19. Nao fazer fetch em useEffect sem controle de race condition (AbortController)

## Componentes
20. Componente = 1 responsabilidade
21. Componentes pequenos e compostos (< 300 linhas)
22. Props tipadas com TypeScript interface
23. Destructure props no parametro da funcao
24. Nao passar props desnecessarias (prop drilling → Context ou composition)
25. Children como composicao (nao render props quando possivel)

## Formularios
26. Controlled inputs para validacao em tempo real
27. Uncontrolled inputs para forms simples (useRef)
28. Validacao com feedback inline (nao so no submit)
29. Debounce em inputs de busca (300ms)
30. Desabilitar submit durante processamento

## Performance
31. Virtualizar listas longas (> 100 itens)
32. Paginar dados do backend (nao carregar tudo)
33. Skeleton loading (nao spinner) durante carregamento
34. Imagens com next/image (lazy loading + otimizacao)
35. Code splitting por rota
36. Prefetch de rotas provaveis (next/link prefetch)

## Patterns
37. Custom hooks para logica reutilizavel
38. Compound components para UI flexivel
39. Render props so quando necessario (prefira hooks)
40. HOCs: evitar (prefira hooks)
41. Error boundaries para capturar erros de render
42. Suspense boundaries para loading states

## TypeScript
43. Interface para props (nao type)
44. Sem `any` — usar `unknown` e narrow com type guards
45. Discriminated unions para variantes de estado
46. Generics para componentes reutilizaveis
47. Tipagem estrita de eventos: React.ChangeEvent<HTMLInputElement>

## Testes
48. Testar comportamento, nao implementacao
49. React Testing Library > Enzyme
50. Screen queries por role > por testId > por text
51. User events > fireEvent
52. Mock de API com MSW (nao mock de fetch)

## Acessibilidade
53. Semantica HTML (button, nav, main, article)
54. ARIA labels em elementos interativos
55. Focus management em modais
56. Keyboard navigation (Tab, Enter, Escape)
57. Contraste de cores acessivel (WCAG AA)
