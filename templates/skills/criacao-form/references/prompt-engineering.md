# Prompt Engineering — Diagnostico com IA

Como estruturar o system prompt e a knowledge base para gerar analises de qualidade.

---

## Arquitetura: Prompt + Knowledge Base

Sempre separar em 2 arquivos:

| Arquivo | Conteudo | Quando muda |
|---------|----------|-------------|
| `prompt-[tema].md` | Comportamento, tom, regras, fluxo | Quando quer mudar como a IA se comporta |
| `kb-[tema].md` | Dados, frameworks, recomendacoes | Quando atualiza informacoes do dominio |

**Regra**: Se muda quando o negocio atualiza, e KB. Se muda quando voce quer comportamento diferente, e prompt.

---

## Estrutura do System Prompt

### 1. Identidade e Objetivo
```markdown
# Identidade e Objetivo
Voce e um [CARGO] com [EXPERIENCIA] em [AREA].
Personalidade: [ADJETIVOS].
Objetivo: [O QUE FAZ COM OS DADOS].
```

### 2. Tom de Voz
```markdown
## Tom de Voz
- Profissional mas acessivel
- Sem jargoes ([LISTA DE PALAVRAS PROIBIDAS])
- Proibido: travessoes (—), cliches, promessas vazias
```

### 3. Regras Criticas
```markdown
## Regras Criticas
1. Base sua analise EXCLUSIVAMENTE nos dados fornecidos
2. Analise INTERDEPENDENCIAS entre areas
3. Priorize areas urgentes (notas 1-2) sobre atencao (nota 3)
4. Cada recomendacao deve ser ACIONAVEL
5. Formate em HTML: h2, h3, p, ul, li, strong, em. Sem h1, sem Markdown
6. Entre 600-900 palavras
7. Acentuacao correta em PT-BR
```

### 4. Fluxo de Analise
```markdown
## Fluxo de Analise
Etapa 1: DIAGNOSTICAR - Quadro geral, media, clusters
Etapa 2: PRIORIZAR - Ordenar por criticidade + interdependencia
Etapa 3: RECOMENDAR - Diagnostico + impacto + acao concreta
Etapa 4: PLANEJAR - Acoes em 30/60/90 dias
```

### 5. Mapa de Interdependencias
```markdown
## Mapa de Interdependencias
- **[Categoria A]** impacta: B, C, D
- **[Categoria B]** impacta: A, E
...
```

### 6. Calibracao de Severidade
```markdown
## Calibracao de Severidade
- Nota 1: Critico. Acao imediata.
- Nota 2: Urgente. Corrigir em 30 dias.
- Nota 3: Atencao. Ajustar em 60 dias.
- Nota 4: Ponto forte. Alavancar.
```

### 7. Estrutura da Saida
```markdown
## Estrutura da Saida
1. Visao Geral (h2)
2. Areas Criticas (h2 + h3 por area)
3. Areas de Atencao (h2)
4. Pontos Fortes (h2)
5. Plano de Acao 30/60/90 (h2)
```

---

## Estrutura da Knowledge Base

### Framework por Categoria
```markdown
## FRAMEWORK: [Nome da Categoria]
Tags: [palavras-chave para busca]

### Sinais por Nota
- **Nota 1**: [descricao do que nota 1 significa nesta categoria]
- **Nota 2**: ...
- **Nota 3**: ...
- **Nota 4**: ...

### Recomendacoes Acionaveis
- **Urgente**: [3 acoes concretas para notas 1-2]
- **Atencao**: [3 acoes para nota 3]
- **Otimizacao**: [3 acoes para potencializar nota 4]

### Interdependencias
[Como esta categoria afeta e e afetada por outras]
```

### Analise de Clusters
```markdown
## TECNICA: Analise de Clusters

### Cluster [Nome]
Areas: A + B + C
Se as 3 estao baixas: [consequencia + acao]
```

### Escala
```markdown
## INFO: Escala de Avaliacao
| Nota | Classificacao | Significado |
|------|--------------|-------------|
| 1 | Critico | Acao de emergencia em 15 dias |
| 2 | Urgente | Corrigir em 30 dias |
| 3 | Atencao | Melhorar em 60 dias |
| 4 | Excelente | Potencializar |
```

---

## Montagem do User Prompt (API Route)

O user prompt e montado dinamicamente com os dados do formulario:

```typescript
const userPrompt = `Analise o seguinte diagnostico.

AVALIACOES (escala 1-4, ordenadas por criticidade):
${ratingsText}
// ex: - Financeiro: 1/4 (CRITICO)
//     - Processos: 2/4 (URGENTE)

RESUMO ESTATISTICO:
- Media geral: ${avg.toFixed(1)}/4.0
- Areas criticas/urgentes (nota 1-2): ${urgent || "Nenhuma"}
- Areas de atencao (nota 3): ${attention || "Nenhuma"}
- Areas excelentes (nota 4): ${excellent || "Nenhuma"}

ANALISE DE CLUSTERS:
${clustersAnalysis}

Pense passo a passo. Analise o quadro geral primeiro, depois detalhe cada area prioritaria.`;
```

---

## Classificacao de Ratings (Servidor)

```typescript
function classifyRating(value: number) {
  if (value === 1) return { label: "CRITICO", severity: "critico" };
  if (value === 2) return { label: "URGENTE", severity: "urgente" };
  if (value === 3) return { label: "ATENCAO", severity: "atencao" };
  return { label: "EXCELENTE", severity: "excelente" };
}
```

## Identificacao de Clusters (Servidor)

```typescript
function identifyClusters(entries: [string, number][]): string {
  const ratings = Object.fromEntries(entries);
  const clusters: string[] = [];

  // Definir clusters por tema
  const clusterDefs = [
    { name: "OPERACIONAL", keys: ["processos", "tecnologia", "eficiencia_operacional"] },
    { name: "PESSOAS", keys: ["pessoas", "cultura", "comunicacao"] },
    // ...
  ];

  for (const cluster of clusterDefs) {
    const avg = cluster.keys.reduce((sum, k) => sum + (ratings[k] || 0), 0) / cluster.keys.length;
    if (avg <= 2) {
      clusters.push(`CLUSTER ${cluster.name} EM RISCO: media ${avg.toFixed(1)}`);
    }
  }

  return clusters.length > 0 ? clusters.join("\n") : "Nenhum cluster em risco critico.";
}
```

---

## Boas Praticas de Prompt

1. **Instrua raciocinio**: "Pense passo a passo" (GPT nao raciocina por padrao)
2. **Proiba comportamentos**: Liste explicitamente o que a IA NAO deve fazer
3. **De exemplos de tom**: "Como um consultor que conversa olho no olho"
4. **Limite escopo**: "Base sua analise EXCLUSIVAMENTE nos dados fornecidos"
5. **Defina formato**: Especifique tags HTML permitidas
6. **Calibre tamanho**: "Entre 600-900 palavras"
7. **Mapeie interdependencias**: A IA precisa saber que areas se conectam
8. **Varie output**: "Varie a linguagem. Nao use a mesma estrutura para cada area"

## Parametros OpenAI

| Parametro | Valor | Razao |
|-----------|-------|-------|
| model | gpt-5.2 | Melhor qualidade (ou gpt-4o para custo menor) |
| max_completion_tokens | 3000 | 600-900 palavras em HTML |
| temperature | 0.7 | Variacao sem ser aleatorio |
| stream | true | Feedback real-time |
