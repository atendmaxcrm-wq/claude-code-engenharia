---
name: safari-check
description: Auditoria de compatibilidade Safari iOS/macOS. Detecta 9 padroes problematicos em componentes React. Use ao criar UI ou antes de deploy.
---

# Safari Compatibility Check

Audite o projeto inteiro ou arquivos especificos para padroes que quebram no Safari iOS/macOS.

## Como Usar

```
/safari-check                    # Audita todos os .tsx/.jsx do projeto
/safari-check src/components/    # Audita pasta especifica
/safari-check MyComponent.tsx    # Audita arquivo especifico
```

## Processo

1. **Escanear** todos os arquivos .tsx/.jsx no escopo
2. **Detectar** cada padrao da tabela abaixo
3. **Reportar** com severidade, arquivo, linha e fix sugerido
4. **Resumo** com contagem por severidade

## 9 Padroes Problematicos

### 1. CRITICO — Flex children sem min-h-0 (overflow scroll quebrado)

**Detecta:** Container flex/flex-col com filho que tem `overflow-y-auto` ou `overflow-y-scroll` mas SEM `min-h-0` no filho ou no container.

**Sintoma Safari:** Conteudo nao faz scroll, estoura o container.

**Fix:** Adicionar `min-h-0` no elemento flex child que tem overflow, OU `className="min-h-0"` / `style={{ minHeight: 0 }}` no container flex.

```tsx
// ERRADO
<div className="flex flex-col h-screen">
  <div className="overflow-y-auto">...</div>  // Safari: nao scrolla
</div>

// CORRETO
<div className="flex flex-col h-screen">
  <div className="overflow-y-auto min-h-0">...</div>
</div>
```

### 2. CRITICO — aspect-ratio sem fallback padding-bottom

**Detecta:** Uso de `aspect-square`, `aspect-video`, `aspect-ratio` em elementos que contém imagens ou conteudo visual.

**Sintoma Safari:** Imagem colapsa para 0px de altura em Safari < 15, ou dimensoes erradas em iOS.

**Fix:** Substituir por padding-bottom trick:
```tsx
// ERRADO
<div className="aspect-square">
  <img src="..." className="object-cover" />
</div>

// CORRETO
<div className="relative w-full" style={{ paddingBottom: '100%' }}>
  <img src="..." className="absolute inset-0 w-full h-full object-cover" />
</div>
```

**Variantes:**
- `aspect-square` → `paddingBottom: '100%'`
- `aspect-video` → `paddingBottom: '56.25%'`
- `aspect-[4/3]` → `paddingBottom: '75%'`
- `aspect-[3/4]` → `paddingBottom: '133.33%'`

### 3. CRITICO — Sidebar flex sem min-h-0

**Detecta:** Layout com sidebar (flex horizontal) onde o sidebar tem overflow scroll mas sem min-h-0.

**Sintoma Safari:** Sidebar nao faz scroll, conteudo fica cortado.

**Fix:** Mesmo do padrao 1 — adicionar `min-h-0` no flex child.

### 4. ALTO — 100vh sem fallback dvh

**Detecta:** Uso de `h-screen`, `min-h-screen`, `100vh` sem fallback `100dvh`.

**Sintoma Safari iOS:** 100vh inclui a barra de endereco, conteudo fica cortado embaixo.

**Fix:** Usar dvh com fallback:
```tsx
// ERRADO
<div className="min-h-screen">

// CORRETO (Tailwind v4 — suporta dvh nativo)
<div style={{ minHeight: '100dvh' }}>

// CORRETO (Tailwind v3 — precisa de ambos)
<div className="min-h-screen" style={{ minHeight: '100dvh' }}>
```

### 5. ALTO — Select sem WebkitAppearance none

**Detecta:** Elementos `<select>` com estilizacao custom mas sem `-webkit-appearance: none`.

**Sintoma Safari:** Select ignora border-radius, padding e background customizados.

**Fix:**
```tsx
// ERRADO
<select className="rounded-lg px-4 py-2 bg-gray-800">

// CORRETO
<select
  className="rounded-lg px-4 py-2 bg-gray-800"
  style={{ WebkitAppearance: 'none', appearance: 'none' }}
>
```

### 6. ALTO — Cards com aspectRatio inline sem minHeight

**Detecta:** Elementos com `style={{ aspectRatio: '...' }}` em contexto flex.

**Sintoma Safari:** Card colapsa ou dimensoes inconsistentes.

**Fix:** Adicionar `minHeight: 0` no mesmo style:
```tsx
// ERRADO
<div style={{ aspectRatio: '16/9' }}>

// CORRETO
<div style={{ aspectRatio: '16/9', minHeight: 0 }}>
```

### 7. MEDIO — Fullscreen sem fallback dvh

**Detecta:** Modais ou overlays fullscreen usando `h-screen` / `100vh` sem dvh.

**Sintoma Safari iOS:** Modal nao ocupa tela inteira, barra de endereco cobre conteudo.

**Fix:** Mesmo do padrao 4.

### 8. MEDIO — Container de scroll com altura calculada sem dvh

**Detecta:** `calc(100vh - Xpx)` sem equivalente dvh.

**Sintoma Safari iOS:** Altura calculada errada por causa da barra de endereco dinamica.

**Fix:**
```tsx
// ERRADO
style={{ height: 'calc(100vh - 320px)' }}

// CORRETO
style={{ height: 'max(200px, calc(100dvh - 320px))' }}
```

### 9. INFO — backdrop-blur sem -webkit-backdrop-filter

**Detecta:** Uso de `backdrop-blur` ou `backdrop-filter` sem prefixo webkit.

**Nota:** Tailwind v4 ja gera o prefixo automaticamente. Apenas reportar se estiver usando CSS inline ou Tailwind v3 sem autoprefixer.

**Fix (se necessario):**
```tsx
style={{
  backdropFilter: 'blur(10px)',
  WebkitBackdropFilter: 'blur(10px)',
}}
```

## Formato do Relatorio

```
Safari Compatibility Report
═══════════════════════════

[CRITICO] src/components/Classroom.tsx:45
  Flex child com overflow-y-auto sem min-h-0
  Fix: Adicionar className="min-h-0" no elemento linha 45

[ALTO] src/views/LoginOTP.tsx:12
  100vh sem fallback dvh
  Fix: Adicionar style={{ minHeight: '100dvh' }}

[MEDIO] src/components/TimelineView.tsx:78
  calc(100vh - ...) sem dvh
  Fix: Usar max(200px, calc(100dvh - 320px))

═══════════════════════════
Resumo: 2 criticos | 1 alto | 1 medio | 0 info
```

## Severidades

| Nivel | Significado | Acao |
|-------|-------------|------|
| CRITICO | Quebra funcionalidade (scroll, layout colapsado) | Corrigir antes de deploy |
| ALTO | UX degradada (select bugado, altura errada) | Corrigir antes de deploy |
| MEDIO | Problema visual menor (altura nao ideal) | Corrigir quando possivel |
| INFO | Potencial problema (backdrop-blur) | Verificar se framework ja trata |

## Dicas

- Rodar antes de cada deploy para producao
- Focar nos CRITICOS primeiro (flex + min-h-0 e aspect-ratio)
- Safari iOS e o mais afetado — testar sempre em iPhone real ou Simulator
- 100dvh resolve 80% dos problemas de altura no Safari iOS
- Tailwind v4 ja gera prefixos -webkit- para backdrop-filter
