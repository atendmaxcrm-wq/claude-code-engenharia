---
name: auditar-fidelidade
description: Auditoria EXAUSTIVA de fidelidade e completude entre uma REFERENCIA (mockup HTML/SPA, print, video ou site) e um app JA IMPLEMENTADO, para achar o que ainda falta, esta parcial ou divergente. Cobre features/recursos (nao so o visual), conteudo tela a tela, modais e campos, configuracoes, design e motion, nos dois temas e no mobile. Saida = lista de gaps priorizada (alta/media/baixa), separando divergencias INTENCIONAIS. Use quando o usuario disser "o que falta?", "verifica TUDO vs o mockup", "compara o que foi feito com a referencia", "auditar completude/fidelidade da replica", "o que do design/HTML nao foi implementado", "ele falou que faltou X", ou apos uma replicacao para garantir que nada passou. NAO e clonar nem construir (isso e replicar-sistema/clonar-site); aqui a entrada e REFERENCIA + APP e a saida e um RELATORIO DE GAPS. E o quality gate de completude que a replicar-sistema chama na fase final.
---

# Auditar Fidelidade (referencia vs app)

Auditar o que falta entre a referencia e o app: $ARGUMENTS

FILOSOFIA (aprendida doendo no My Zap Money v10): **fidelidade visual != completude**.
Da pra reproduzir as telas que se VE e ainda assim faltar metade dos RECURSOS, porque o
grosso do comportamento de um mockup HTML/SPA mora no JAVASCRIPT, nao no markup estatico.
Replicar o que se ve no print deixa passar: features geradas por JS, telas montadas em
runtime, o segundo tema, o mobile, modais com campos, e settings. Esta skill e o checklist
sistematico que pega tudo isso ANTES do dono apontar.

REGRA DE OURO: **renderize a referencia e leia o JS dela**. Nunca audite lendo so o HTML
estatico nem so olhando o print.

## Fase 0 — Definir referencia e app (sem encher de pergunta)

- Referencia: arquivo HTML/SPA? print/foto? video? URL? Caminho do app implementado?
- Se o usuario ja deu os dois, va direto. No maximo 1 pergunta se faltar o essencial.

## Fase 1 — Capturar a VERDADE da referencia (renderizar, nao ler estatico)

Se a referencia for HTML/SPA: rode o JS num browser e screenshote TODAS as views.

```
# Playwright (cache npx), file:// da referencia, clicar cada nav/[data-view], screenshot full
chromium.launch({ executablePath: '<cache>/chromium*/chrome', args:['--no-sandbox'] })
page.goto('file:///.../referencia.html', { waitUntil:'networkidle' })
# cada view: document.querySelector('[data-view="X"]').click(); screenshot OUT/X.png
```

- Capture nos DOIS temas se houver toggle (ex: `document.body.classList.add('light')`).
- Print/foto/video: use os frames como verdade visual (video -> ffmpeg frames).
- Guarde os renders em /tmp/ref-render/ (e /tmp/ref-render-light/) como GROUND TRUTH.

## Fase 2 — Enumerar a SUPERFICIE da referencia

Antes de comparar, liste TUDO que a referencia tem (nao so o visivel):

```
grep -noE "function [a-zA-Z0-9_]+|on(click|change|submit)=|window\.[a-zA-Z0-9_]+\s*="  ref.html
grep -noE "openModal\('[^']+'\)|data-view=\"[^\"]+\"|id=\"m[A-Z][^\"]*\""  ref.html
```

- Funcoes/handlers = features e comportamentos. Modais (`mX`) e seus campos. Views.
- O objeto de estado (ST/store) = quais dados/recursos existem.
- Bloco `<style>`: tokens, classes, e principalmente MOTION (@keyframes, transitions, hover transforms).

## Fase 3 — Auditar em leque (Agent Teams read-only)

Tarefa grande e paralelizavel -> **Agent Teams** (regra do projeto; nao Workflow solto).
Use auditores READ-ONLY (Explore, ou general-purpose com instrucao explicita de NAO editar).
Um auditor por dimensao, cada um compara referencia vs app e devolve gaps estruturados:

1. **Design / visual / motion** — tokens, sombras, radii, e MOTION (hover-lift, reveal,
   tooltip, blur de overlay, pulsos). Quase sempre o gap aqui e movimento, nao cor.
2. **Features / comportamento** — cada funcao/handler/estado do JS mapeado ao app. Pega
   botoes mortos, inputs decorativos (busca sem handler), simuladores estaticos, fluxos faltando.
3. **Conteudo tela a tela** — para cada view, secoes/cards/KPIs/tabelas vs a tela do app.
4. **Modais e formularios** — cada modal + seus CAMPOS (e o gap mais comum: campo faltando).
5. **Configuracoes / settings** — cada pane/aba e seus controles.

Schema de saida de cada auditor: `{ item, status: faltando|parcial|divergente, detalhe (com onde), prioridade: alta|media|baixa }`.

## Fase 4 — Temas e mobile (o que medicao do documento esconde)

- Screenshot do APP autenticado (forjar cookie de sessao assinando o JWT com o secret do .env).
- DOIS temas (claro + escuro) — compare cada um com o render correspondente da referencia.
- Mobile (390px): meça overflow POR ELEMENTO, nao so do documento (scrollWidth-clientWidth=0
  pode esconder corte). Para cada `main *`, ver se `getBoundingClientRect().right > innerWidth`.

## Fase 5 — Sintetizar e priorizar

- Consolidar (dedup + agrupar correlatos) num relatorio: alta / media / baixa.
- **alta** = recurso/feature importante faltando ou quebrado. **media** = conteudo/secao/
  parcial. **baixa** = polish/motion/detalhe.
- SEPARAR divergencias INTENCIONAIS (decisoes de produto documentadas na memoria) — NAO
  contam como gap. Listar so para completude.
- Apresentar a lista ao usuario.

## Fase 6 — Corrigir (se o usuario mandar)

Os gaps viram trabalho de implementacao -> **Agent Teams** (plano + GO + quality gate),
nunca subagents soltos. Cada teammate recebe os renders da referencia como ground truth.

## Anti-padroes (o que faz a auditoria falhar)

- Auditar lendo o HTML ESTATICO (perde tudo que e gerado por JS). RENDERIZE.
- Auditar so o que se ve na tela (perde features do JS: tema, detalhe, conciliacao...).
- Conferir so um tema, so desktop. Sempre claro+escuro+mobile.
- Medir so overflow do documento (esconde blowout clipado). Meça por elemento.
- Contar divergencia intencional documentada como gap (gera retrabalho besta).
- Workflow solto para auditar quando da pra usar Agent Teams (regra do projeto).

## Notas

- PT-BR com acentuacao correta; sem travessao (em-dash).
- Caso exemplo: My Zap Money v10. Replicacao visual passou, mas a auditoria pegou: galeria
  de temas de cor, detalhe do cartao + conciliacao, modo claro (cards escuros hardcoded),
  grid mobile do WhatsApp, busca global decorativa, dashboard personalizavel orfao, campos
  faltando em ~8 modais. Tudo invisivel no print; visivel ao renderizar + ler o JS + auditar
  em leque. Ver memorias [[v10-mockup-js-rendered]] e [[redesign-v10-onda1]].
