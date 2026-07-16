---
name: frontend-design
description: Design UI excepcional, nao-generico. Guidelines oficiais Anthropic. Use ao criar interfaces para garantir qualidade visual.
---

# Frontend Design — Exceptional UI

## Principios Core
1. **Intencionalidade**: Cada elemento tem um proposito. Se nao justifica sua existencia, remova.
2. **Hierarquia**: O olho do usuario deve ser guiado naturalmente. Um elemento dominante por viewport.
3. **Restricao**: Menos opcoes = melhor UX. Limitar cores, fontes, tamanhos.
4. **Consistencia**: Mesmas acoes = mesma aparencia. Sempre.

## Anti-generico
- NUNCA usar UI padrao "out of the box" sem customizar
- NUNCA copiar designs genericos de templates
- Cada projeto deve ter personalidade visual propria
- Detalhes fazem a diferenca: micro-interacoes, transicoes, espacamento

## Espacamento (Ritmo Visual)
- Espacamento generoso entre secoes (py-20+)
- Padding interno consistente (p-6 a p-8)
- Whitespace nao e "espaco vazio" — e um elemento de design
- Texto com max-width para legibilidade (65-75 chars)

## Tipografia
- Hierarquia clara: titulo > subtitulo > body > caption
- Peso da fonte para enfase (bold para titulos, medium para subtitulos)
- Tamanhos com escala harmonica (1.25x ou 1.333x)
- Line-height: 1.5 body, 1.1-1.2 headings

## Cores
- Paleta restrita: 1 primaria + 1 accent + escala de neutros
- Usar opacidade para variantes (primary/80, primary/60)
- Cor so para significado ou destaque (nao decoracao)
- Contraste acessivel: 4.5:1 texto, 3:1 elementos UI

## Componentes
- Cards: arredondados, sombra sutil, hover com feedback
- Botoes: hierarquia clara (primary > secondary > ghost)
- Inputs: estados visiveis (focus, error, success)
- Modais: overlay blur, cantos arredondados, escape para fechar

## Responsividade
- Mobile-first: projetar para 375px, expandir para desktop
- Breakpoints consistentes: sm(640) md(768) lg(1024) xl(1280)
- Touch targets: minimo 44x44px
- Conteudo adapta, nao so encolhe

## Performance Visual
- Skeleton loading > spinner (menos intrusivo)
- Transicoes suaves (300ms ease-out padrao)
- Feedback imediato em interacoes (hover, click, submit)
- Progressive disclosure (mostrar detalhes sob demanda)
