---
name: site-elite-cinema
description: Adiciona camada cinematografica ao /site-elite. Captura visual (Playwright OU foto OU gpt-image-2) -> Veo 3.1 image-to-video -> ffmpeg -g 1 baseline -> hero com scroll-scrub frame-accurate em Next.js 16. Inclui fabrica de assets generativos com validacao por asset (prompts tecnicos + relatorio PASSA/ARTEFATO) e o hero de TRANSFORMACAO (materia A vira materia B: foto que dissolve e remonta no produto, o efeito viral nomadatoast/PeachWeb - que e video scrubado, nao WebGL). Use quando o usuario pedir hero cinematografico, scroll-scrub video, redesign visual de site/sistema existente, landing com produto fisico real, hero de SaaS sem produto pronto, "site com produto", "video hero scrubbed", Veo 3.1, Veo image-to-video, "filme curto na home", "abre um filminho na pagina", "foto que vira produto", "dissolve no scroll", transformacao cinematografica, fabrica de assets, geracao de assets pra site, reuso da estetica /site-elite com camada audiovisual.
---

# /site-elite-cinema - Hero Cinematografico com Scroll-Scrub (Veo 3.1)

> Camada cinematografica sobre /site-elite. Em vez de hero estatico ou WebGL generico, voce captura o produto (UI real, foto, ou imagem gerada), passa por Veo 3.1 image-to-video, pos-processa em ffmpeg com all-keyframes, e integra como `<video>` scroll-scrubbed em Next.js 16. Resultado: pagina que abre como trailer, scroll vira timeline.

---

## STOP: Gate de aderencia

**LEIA ANTES DE COMECAR. Pular qualquer fase = video slop garantido.**

Esta skill existe porque hero cinematografico com video AI em one-shot prompting converge em 3 patologias:

1. **Slop visual Veo** - "epic cinematic" + "stunning" no prompt = camera tremida, lens flare, drift de geometria, texto warped, personagem que muda de cara no meio do clip.
2. **Scroll-scrub quebrado** - H.264 sem `-g 1` (all keyframes) trava em frames-chave a cada 250ms, scroll vira stutter.
3. **Custo descontrolado** - Veo 3.1 Standard 1080p custa $0.40/seg. Um teste de 8s = $3.20. Gerar 5 variacoes em standard sem testar fast antes = $16 jogados fora.

A skill bane explicitamente os prompts ruins, forca um quality gate por fase, e usa Fast 720p ($0.10/seg = $0.80 por 8s) como default ate o roteiro estar travado.

**Se voce vai pular Fase 0 (Vibe + decision tree) ou Fase 4 (ffmpeg -g 1), pare e me avise. Nao prossiga.**

**Antes de comecar:** carregar tools relevantes via ToolSearch:

```
ToolSearch query="select:Bash,Read,Write,Edit,Glob,Grep" max_results=6
ToolSearch query="playwright browser screenshot" max_results=4
```

Se for usar agentes paralelos (caso de site grande com varias secoes cinematograficas), tambem carregar `TeamCreate, TaskCreate, SendMessage` via ToolSearch.

---

## Decision tree (a primeira decisao da skill)

**Antes de tudo, classificar o input do usuario em 1 dos 3 ramos.** A escolha do ramo define toda a Fase 1.

```
O usuario tem o que como "produto" pra estampar no hero?
  |
  |-- (A) Site / app / sistema JA EXISTE com UI navegavel?
  |       (crmax-site, dashboard interno, SaaS web, app com tela)
  |       -> Ramo A: Playwright captura screenshots ricos da UI real
  |       -> Ver reference 01-playwright-capture.md
  |       -> Output: 1-3 frames PNG 1280x720 da UI em estados-chave
  |
  |-- (B) Produto FISICO REAL existe?
  |       (caneta, garrafa, livro, eletronico, peca de marca)
  |       -> Ramo B: usuario fornece foto + composicao em mockup
  |       -> Ver reference 03-compose-mockup.md
  |       -> Output: 1 imagem composta (produto + cenario / mao / fundo)
  |
  |-- (C) Produto ABSTRATO / SaaS sem digital ainda?
  |       (ideia, conceito, marca em fase de pitch, servico intangivel)
  |       -> Ramo C: gerar foto base com gpt-image-2 PRIMEIRO, depois Veo
  |       -> Combo: gpt-image-2 -> Veo image-to-video
  |       -> Output: imagem gerada que serve de frame 0 pra Veo
  |
  |-- (D) Hero de TRANSFORMACAO? (materia A vira materia B)
  |       ("foto que dissolve e vira o produto", "rosto vira perfume",
  |        "ingrediente vira prato", efeito viral nomadatoast/PeachWeb)
  |       -> Ramo D: fabrica gera still ORIGEM + still DESTINO ->
  |          prompt multi-shot 4 beats -> Veo -> scrub
  |       -> Ver references/08-hero-transformacao.md (excecao a regra de
  |          movimento sutil; anti-drift vem dos beats + paleta declarada)
  |       -> NAO tentar esse efeito com particulas WebGL real-time: e o
  |          caminho que ja decepcionou (teto de gl.Points = poeira brilhante)
```

**Se o usuario nao se encaixa em A/B/C/D, pare e pergunte.** Nao chute. Hero cinematografico de SaaS abstrato (C) ja e categoria de fronteira - se ele nao sabe qual ramo, e porque ainda nao definiu o que vai mostrar.

**Fabrica de assets (transversal aos ramos):** sempre que a fase 1 GERAR imagem
(ramo C, ramo D, ou composicao do ramo B) ou o site precisar de mais de 1 asset
visual (stills de secao, fundos, refs), rodar `references/07-fabrica-assets.md`:
lista com orcamento -> prompt tecnico por asset (.txt versionado) -> modo API ou
manual -> validacao com veredito PASSA/ARTEFATO por asset. Foto crua do usuario
direto no Veo so no ramo B com foto JA profissional.

---

## Filosofia

### Por que video AI hero sem workflow vira slop

Mesmo problema do /site-elite original: distributional convergence. Veo 3.1 treinado em milhoes de horas de trailer Hollywood, comercial de carro, B-roll stock. Quando voce pede "cinematic shot of product", o modelo entrega o centroide:

- Camera em movimento constante (push-in + leve dutch)
- Lens flare anamorfico em todo highlight
- Slow-motion ate quando nao faz sentido
- Cor teal-orange grading default
- Texto que aparece na cena warpa porque modelo de video nao trava letras

A virada: **prompt cinematografico tecnico real**, nao prompt de fan de filme. Em vez de "epic cinematic stunning visuals", voce escreve "50mm prime, locked tripod, slow dolly-in 5cm/sec, motivated rim light camera-left, sensor noise grain at ISO 400". Isso e direcao de fotografia. Veo responde a vocabulario de set, nao a hype.

### Constraint > permission (mesma filosofia /site-elite)

Banlist de prompts genericos + uselist de vocabulario tecnico + negative prompt obrigatorio + movimento sutil. Esse e o jogo.

### Por que image-to-video e nao text-to-video

Text-to-video com Veo entrega "alguma coisa cinematografica". Image-to-video entrega "essa imagem especifica em movimento". A imagem-base trava personagem, produto, geometria, paleta. Reduz drift drasticamente. Por isso a skill exige sempre input de imagem (ramo A, B ou C).

### Scroll-scrub e frame-accurate ou nao e nada

Scroll-scrub significa: tempo do video atrelado ao deslocamento de scroll. Se o usuario rola 50% da secao, video esta no frame 50%. Pra isso funcionar fluido, **todo frame precisa ser keyframe** (`-g 1` no x264). Sem isso, browser tem que decodificar para tras a partir do ultimo I-frame, e scroll trava.

---

## Quando usar

Triggers explicitos:

- "Hero cinematografico", "hero com video", "hero scroll-scrubbed"
- "Quero um filminho na home", "abre como trailer"
- "Redesign visual do crmax / makewl / [sistema existente]" - usuario nao falou "video" mas quer impacto visual e tem UI navegavel
- "Landing pra meu produto [fisico real]" - caneta, peca, eletronico
- "Site nivel Aura / Active Theory / Basement com video" - tom WebGL maximalist com camada audiovisual
- "Veo 3.1", "Veo image-to-video"

Sinais implicitos: usuario mostrou um trailer/comercial como referencia, ou disse "tipo aquele site da Apple que tem o iPhone girando", ou "quero algo que se mexe quando role".

---

## Quando NAO usar

- **Site sem produto definido** - se nao da pra encaixar em ramo A/B/C, voltar pro /site-elite normal (Fase 4 com UnicornStudio resolve sem video).
- **Mobile-first puro com data plano baixo** - video scrub pesa. Se o publico-alvo abre o site em 3G, usar /site-elite com background estatico.
- **Performance Lighthouse 95+ obrigatorio sem brechas** - video hero machuca LCP. Possivel salvar com poster + lazy, mas se o gate e 95+, /site-elite e mais seguro.
- **Clone pixel-perfect de site existente** - /clonar-site.
- **Quiz / formulario / wizard** - /criacao-form.
- **Componente isolado** - /component-builder.
- **Apenas animacao SVG/scroll sem video** - /gsap-animations.

---

## Workflow 6 fases

```
[Fase 0] Vibe Questionnaire + Decision tree A/B/C -----+
                                                       |
[Fase 1] Captura visual (Playwright OU foto OU IA) ----+--> frame-base.png (1280x720)
                                                       |
[Fase 2] Preparar input Veo (resize, compor mockup) ---+--> veo-input.png (1280x720 16:9)
                                                       |
[Fase 3] Veo 3.1 image-to-video (fast 720p primeiro) --+--> raw-veo.mp4 (8s, ~$0.80)
                                                       |
[Fase 4] Pos-processar ffmpeg -g 1 baseline -----------+--> hero-scrub.mp4 (all-keyframes)
                                                       |
[Fase 5] Integrar ScrollVideoHero em Next.js 16 -------+--> hero scroll-scrubbed na home
```

**Cada fase tem entregavel concreto + quality gate. Nao avance sem o entregavel da anterior.**

---

### Fase 0 - Vibe Questionnaire + Decision tree

#### Vibe Questionnaire (inline - /site-elite foi ARQUIVADA)

A /site-elite foi aposentada (sessao #86; /replicar-sistema e a autoridade de
acabamento agora). As 4 perguntas Vibe continuam valendo, respondidas AQUI:
Purpose (o que o site vende/comunica), Tone (2-3 adjetivos + 1 referencia real),
Constraints (marca, paleta, prazos, device do publico), Differentiation (a UMA
coisa memoravel). Se ja existe `VIBE.md` de sessao previa, reusar.

**Saida da Fase 0 Vibe:** `VIBE.md` com as 4 respostas. Para o acabamento 2D das
secoes (styleguide, tokens, rubrica visual), a fonte de verdade e /replicar-sistema.

#### Decision tree A/B/C (especifico desta skill)

Apos VIBE.md, pergunta unica:

> Voce tem o que como produto pra estampar no hero?
> (A) Site/app/sistema com UI navegavel - me passa a URL
> (B) Produto fisico real - me passa fotos
> (C) Nao tem visual pronto - vamos gerar com gpt-image-2

Se o usuario hesita entre B e C, perguntar: "Existe o objeto no mundo fisico hoje? Se sim, e B (foto real). Se nao, e C (gerar com IA)."

#### Entregavel Fase 0

- `VIBE.md` preenchido (vem de /site-elite)
- Ramo escolhido (A, B ou C) explicito em uma linha

#### Quality gate Fase 0

- [ ] 4 perguntas Vibe respondidas (purpose, tone, constraints, differentiation)
- [ ] UMA coisa memoravel definida (sem lista de 10)
- [ ] Ramo A/B/C escolhido
- [ ] Usuario confirma orcamento mental: minimo 1 geracao Veo Fast 720p ($0.80) por iteracao

Se algo falta, NAO avancar pra Fase 1.

---

### Fase 1 - Captura visual

Depende do ramo escolhido na Fase 0.

#### Ramo A - Playwright captura UI real

Quando: site/app/sistema ja existe com URL acessivel (ou rodando local).

Output esperado: 1-3 frames PNG 1280x720 capturando a UI em estados-chave (landing carregada, dashboard com dados, modal aberto, etc).

Workflow:

1. Browser navega para URL
2. Aguarda render completo (network idle + selector key)
3. Captura screenshot full viewport 1280x720
4. Para multi-estado: navega + captura + repete

Deep dive em `references/01-playwright-capture.md` (escrito pelo teammate playwright-author).

Anti-padrao Ramo A:
- Capturar com viewport default (geralmente 1366x768) e depois resize - gera ruido
- Capturar em modo dev com badges/toolbars visiveis - limpa antes
- Capturar landing genericamente quando o que importa e o produto em uso - pegar tela com dados reais

#### Ramo B - Produto fisico + composicao em mockup

Quando: usuario tem foto do produto fisico (caneta, livro, peca, eletronico).

Output esperado: 1 imagem 1280x720 com produto composto em cenario (mao segurando, mesa de trabalho, ambiente).

Workflow:

1. Usuario fornece 1-3 fotos do produto em fundo neutro
2. Se a foto ja e usavel direto (produto bem iluminado, fundo limpo), seguir
3. Se precisa composicao (produto sobre cenario), gerar mockup via:
   - **Opcao rapida:** gpt-image-2 com edit mode (mascara + prompt de cenario)
   - **Opcao manual:** Photoshop / equivalente

Deep dive em `references/03-compose-mockup.md` (escrito pelo teammate compose-author).

Anti-padrao Ramo B:
- Foto de produto com flash duro frontal - Veo amplifica em movimento e fica plastico
- Cenario que ja tem movimento implicito (folha ao vento) - Veo entra em conflito com a fisica
- Produto centralizado simetrico - sem espaco pra Veo "mexer" sem cortar

#### Ramo C - gpt-image-2 -> Veo (combo)

Quando: produto abstrato / SaaS sem visual / conceito em pitch.

Output esperado: 1 imagem 1280x720 gerada pela gpt-image-2 que serve de frame-base pro Veo.

Workflow:

1. Definir o que "produto" quer dizer nesse caso (dashboard hipotetico? interface conceitual? metafora visual?)
2. Gerar com gpt-image-2 em alta qualidade (thinking mode se houver texto)
3. Usar essa imagem como input do Veo na Fase 3

Deep dive em `references/02-veo-prompts.md` secao "Combo gpt-image-2 + Veo".

Anti-padrao Ramo C:
- Gerar imagem hipergenerica de "tech abstrato" - vai virar slop ao quadrado quando passar pro Veo
- Texto na imagem gerada - Veo vai distorcer no movimento (negative prompt nao salva 100%)

#### Entregavel Fase 1

`frame-base.png` em qualquer resolucao razoavel (sera tratada na Fase 2).

#### Quality gate Fase 1

- [ ] Imagem nitida (sem JPEG artifacts visiveis)
- [ ] Composicao com espaco lateral pro Veo "mexer" (nao tudo centralizado)
- [ ] Texto na imagem? Se sim, plano pra ele no negative prompt (Fase 3)
- [ ] Iluminacao consistente (sem 2 fontes brigando)

---

### Fase 2 - Preparar input pra Veo

Veo 3.1 image-to-video aceita 16:9 (1280x720) ou 9:16 (720x1280). Para hero web, sempre 16:9.

#### Operacoes obrigatorias

1. **Resize/crop pra 1280x720 exato** - Veo aceita outras resolucoes mas converte internamente e perde fidelidade. Forcar 1280x720 antes.
2. **Verificar bordas** - se a imagem original era 16:9 nativa, ok. Se for outro aspect, NUNCA stretch. Crop centralizado ou letterbox + extensao por IA.
3. **Color check** - paleta neutra/realista funciona. Saturacao exagerada na imagem-base = Veo amplifica e estoura.
4. **Composicao final** - se o ramo B precisava de mockup composto, e aqui que isso fecha.

Deep dive em `references/03-compose-mockup.md`.

#### Entregavel Fase 2

`veo-input.png` em 1280x720, paleta ok, composicao com headroom lateral.

#### Quality gate Fase 2

- [ ] Resolucao exata 1280x720
- [ ] Aspect 16:9 sem stretch
- [ ] Nao tem JPEG artifact, banding ou ruido excessivo
- [ ] Existe espaco pra movimento (assunto nao corta as bordas)

---

### Fase 3 - Veo 3.1 image-to-video

Fase mais cara da skill. Sempre fast 720p primeiro. Standard 1080p so quando o prompt e o frame-base estiverem travados.

#### Modelos disponiveis

| Modelo | Resolucao | Custo (8s) | Tempo geracao | Usar quando |
|--------|-----------|------------|---------------|-------------|
| Veo 3.1 Fast | 720p | ~$0.80 | ~10s | Iteracao, teste de prompt, A/B de movimento |
| Veo 3.1 Standard | 1080p | ~$3.20 | ~30s | Versao final, depois de 2-3 iteracoes fast aprovadas |

**Regra:** nunca pular pra Standard antes de pelo menos 2 iteracoes Fast aprovadas pelo usuario. Custo total por hero termina em ~$5-8 (3-4 fast + 1 standard final).

#### Como rodar

Chamar `scripts/veo-image-to-video.sh` com argumentos: input.png, prompt, negative_prompt, modelo (fast|standard), saida.mp4.

Deep dive em `references/06-veo-api.md` (parametros completos, auth, error handling).

#### Anatomia de prompt cinematografico real

**Estrutura obrigatoria:**

1. **Lens + camera** (ex: "50mm prime lens, locked tripod" ou "85mm, handheld micro-shake")
2. **Movimento** (ex: "slow dolly-in 5cm over 8 seconds" - sutil, nao "epic push-in")
3. **Luz** (ex: "motivated rim light camera-left, soft fill from above")
4. **Grain/textura** (ex: "ISO 400 sensor noise, neutral grade")
5. **Sujeito + acao** (ex: "subject remains static, only camera moves" - trava drift)

**Banlist de prompt Veo:**

- "epic"
- "cinematic" (sozinho - pode usar "cinematic 35mm grain" mas nao "epic cinematic shot")
- "stunning"
- "breathtaking"
- "amazing"
- "perfect"
- "8K hyper-realistic"
- "ultra HD"
- "masterpiece"

Estes adjetivos sinalizam ao Veo "saturar tudo". Resultado: lens flare, motion blur exagerado, cor irreal.

**Uselist de prompt Veo (vocabulario tecnico real):**

- Lentes: "24mm wide", "50mm prime", "85mm portrait", "100mm macro"
- Camera: "locked tripod", "handheld micro-shake", "gimbal slider", "dolly track"
- Movimento: "slow dolly-in 5cm", "subtle parallax", "static camera", "slight tilt-up 3 degrees over 8s"
- Luz: "motivated rim light", "soft key from window", "ambient occlusion", "natural overcast"
- Pos: "neutral grade", "low contrast LUT", "ISO 400 grain", "no color grading effect"
- Otica: "shallow depth of field, f/2.8", "deep focus f/8"

**Negative prompt obrigatorio:**

```
warped text, distorted letters, text drift, geometry drift, morphing objects,
character drift, face change, hand morph, extra fingers, anamorphic flare,
heavy lens flare, motion blur trail, camera shake, dutch angle, teal-orange grade,
oversaturation, plastic skin
```

Negative prompt nao garante 100% mas reduz incidencia. Sempre incluir.

**Movimento sutil > movimento exagerado:**

Veo 3.1 entrega 8 segundos. Em 8s, deslocamento maximo recomendado: **5-10% do frame**. Mais que isso comeca a aparecer drift e morfismo. Hero web nao precisa de movimento ostensivo - precisa de "esta vivo".

Regra de ouro: se voce nao consegue descrever o movimento em uma frase tecnica de direcao de fotografia, ele esta ambiguo demais - Veo vai improvisar e provavelmente fazer slop.

Deep dive em `references/02-veo-prompts.md` (50+ prompts canonicos por categoria).

#### Entregavel Fase 3

`raw-veo.mp4` (8s, 720p ou 1080p, H.264).

#### Quality gate Fase 3

- [ ] Sem warped text na cena (se tinha texto)
- [ ] Geometria do produto estavel (nao morfa)
- [ ] Movimento na faixa 5-10% (nao sobe pra "swoosh trailer")
- [ ] Sem lens flare exagerado
- [ ] Paleta consistente com o frame-base (Veo nao trocou a cor)
- [ ] Custo registrado (fast vs standard) no log da sessao

Se algum item falha: ajustar prompt + negative prompt + rodar de novo (custo $0.80 fast). NAO usar saida slop "porque ja gastei". Custo afundado e armadilha.

---

### Fase 4 - Pos-processamento ffmpeg

**Esta fase e nao-negociavel.** Sem `-g 1` (all keyframes), scroll-scrub trava no browser.

#### O que `-g 1` resolve

H.264 default usa GOP (group of pictures) com 1 keyframe (I-frame) a cada ~30 frames + frames P/B intermediarios que dependem do I anterior. Quando voce faz scroll-scrub e o video precisa ir 50ms pra tras, o browser tem que decodificar de tras pra frente ate o I-frame - o que trava.

Com `-g 1`, cada frame e keyframe. Acesso aleatorio instantaneo. Scroll scrub fica fluido.

Custo: arquivo ~3x maior. Aceita-se. Hero scrub de 8s no destino fica entre 8-15 MB - viavel se for o UNICO hero da pagina.

#### Comando baseline obrigatorio

```bash
ffmpeg -i raw-veo.mp4 \
  -c:v libx264 \
  -profile:v baseline \
  -level 3.0 \
  -pix_fmt yuv420p \
  -g 1 \
  -keyint_min 1 \
  -sc_threshold 0 \
  -movflags +faststart \
  -an \
  hero-scrub.mp4
```

**Por que cada flag:**

- `-profile:v baseline` - maxima compatibilidade Safari iOS (que e onde scrub mais quebra)
- `-level 3.0` - compativel com iPhone antigo
- `-pix_fmt yuv420p` - exigido por Safari pra `<video>` inline
- `-g 1 -keyint_min 1 -sc_threshold 0` - TODOS frames sao keyframes (scrub fluido)
- `-movflags +faststart` - moov atom no inicio do arquivo (video comeca a tocar antes de baixar tudo)
- `-an` - sem audio (hero scrub nao deve ter audio)

Deep dive em `references/04-ffmpeg-scrub.md`.

#### Variantes opcionais

- **Mobile fallback** - gerar segunda versao em 540p com mesmo `-g 1`, servir via `<source media="(max-width: 768px)">` pra economizar banda.
- **WebM AV1** - qualidade superior em arquivo menor, mas browser support ainda irregular pra scrub. Por enquanto stick com H.264.

#### Entregavel Fase 4

`hero-scrub.mp4` (all-keyframes, faststart, baseline H.264).

#### Quality gate Fase 4

- [ ] `ffprobe` mostra todos os frames como `pict_type=I` (todos keyframes)
- [ ] Arquivo abre no QuickTime / VLC / Chrome direct sem problema
- [ ] Tamanho razoavel pra hero (8-15 MB em 720p, 15-25 MB em 1080p)
- [ ] Faststart confirmado (`mediainfo` ou `ffprobe` deve mostrar moov atom antes de mdat)

Comando de verificacao all-keyframes:

```bash
ffprobe -v error -select_streams v:0 -show_entries frame=pict_type \
  -of csv=print_section=0 hero-scrub.mp4 | sort | uniq -c
```

Esperado: apenas `I` na saida. Se aparecer `P` ou `B`, refaz com `-g 1`.

---

### Fase 5 - Integrar ScrollVideoHero em Next.js 16

Componente React que liga `currentTime` do `<video>` a posicao de scroll.

#### Arquitetura minima

- `<video>` sem `autoplay`, sem `controls`, com `playsInline muted preload="metadata" poster="..."`
- ScrollTrigger (GSAP) ou IntersectionObserver pra calcular progresso 0..1
- A cada frame de scroll, setar `video.currentTime = progress * video.duration`
- Throttle via `requestAnimationFrame` (nao throttle por timer - RAF da fluidez frame-accurate)

#### Particularidades teste-aios

- **Inline style pra spacing/sizing** - classes Tailwind v4 + Turbopack nao refletem confiavelmente
- **next build + next start** - next dev nao hidrata via IP externo
- Poster image obrigatorio (frame extraido do video) - evita flash de container vazio enquanto video baixa
- `preload="metadata"` (nao "auto") - baixa so o moov atom inicialmente, scrub funciona, banda economizada

Deep dive em `references/05-scroll-hero-component.md` (componente completo + integracao com /site-elite).

#### Entregavel Fase 5

Componente `ScrollVideoHero.tsx` rodando na home, scrub fluido em desktop e mobile.

#### Quality gate Fase 5

- [ ] Scrub funciona em Chrome desktop a 60fps (DevTools Performance painel)
- [ ] Scrub funciona em Safari iOS real (NAO simulador - testar no aparelho)
- [ ] Sem flash de container vazio (poster image carregada)
- [ ] LCP nao destruido (poster e leve, video preload metadata)
- [ ] prefers-reduced-motion respeitado (fallback pra poster estatico)

---

## Quality gates globais da skill

Antes de declarar a skill completa:

- [ ] **Lighthouse Performance 90+** no hero (com poster + preload metadata, e viavel)
- [ ] **Safari iOS real** testado em aparelho fisico (nao simulador)
- [ ] **Drift visual <5%** - frame 0 do video bate com frame-base original (sem morfismo perceptivel)
- [ ] **Custo total registrado** - soma de todas as geracoes Veo (fast + standard) no log da sessao
- [ ] **Scrub fluido 60fps** desktop e mobile (Chrome DevTools Performance + Safari Web Inspector)
- [ ] **All-keyframes confirmado** via ffprobe
- [ ] **prefers-reduced-motion** respeitado (fallback poster)
- [ ] **Sem warped text** no video final
- [ ] **Anti-slop /site-elite** ainda passa (display nao e Inter, paleta nao e roxo-azul, etc)

Se algo falha: voltar 1-2 fases. NAO entregar com gate aberto.

---

## Pricing transparency (custo Veo 3.1)

| Modelo | Resolucao | Custo por segundo | Custo 8s (1 geracao) | Usar quando |
|--------|-----------|-------------------|----------------------|-------------|
| Veo 3.1 Fast | 720p | $0.10 | $0.80 | Iteracao, teste de prompt, A/B de movimento, hero pra mobile-first |
| Veo 3.1 Standard | 1080p | $0.40 | $3.20 | Versao final apos prompt travado, hero desktop premium |

**Politica de custo recomendada por sessao:**

- 3-4 iteracoes Fast 720p ($0.80 cada = $2.40-$3.20) ate prompt + frame-base estarem travados
- 1 geracao Standard 1080p final ($3.20)
- Total por hero: **$5.60-$6.40**

Se o usuario quer 3 heros pra mesma pagina (hero principal + section break + footer ambient): orcamento ~$18-20.

**Custo afundado e armadilha.** Se a geracao saiu slop, NAO usar so porque ja gastou. Refazer com prompt ajustado.

---

## Exemplos de uso

### Exemplo 1 - Hero do crmax-site (Ramo A: Playwright UI)

**Usuario:** "Quero refazer o hero do crmax-site nivel premium. Tem que mostrar o produto em acao."

**Fluxo:**

1. **Fase 0:** /site-elite Vibe (Purpose: B2B SaaS dashboard, Tone: dark technical, Differentiation: scroll que abre o dashboard frame a frame). Ramo: **A** (UI navegavel existe).
2. **Fase 1:** Playwright navega para crmax-site, captura dashboard com dados reais em 1280x720. Output: `frame-base.png` mostrando widget hero do dashboard.
3. **Fase 2:** Imagem ja em 1280x720, paleta dark consistente. Nada a fazer.
4. **Fase 3:** Veo Fast 720p, prompt: "50mm prime, locked tripod, subtle parallax 3% over 8 seconds on dashboard UI, motivated soft light from above, ISO 400 grain, neutral grade, subject remains static, only camera micro-drifts". Negative prompt completo. Custo: $0.80. Iterar 2x se necessario. Versao final: Standard 1080p, $3.20. Total: $4.80-$5.60.
5. **Fase 4:** ffmpeg `-g 1 baseline +faststart`. Output: `hero-scrub.mp4` 12MB.
6. **Fase 5:** ScrollVideoHero.tsx integrado. Scrub revela dashboard "se montando" conforme usuario rola. Poster: frame 0 do video.

### Exemplo 2 - Hero site Makewl (Ramo B: foto + composicao)

**Usuario:** "Hero novo pro site Makewl. Quero mostrar a Sarah (CEO) com o logo Makewl atras."

**Fluxo:**

1. **Fase 0:** Vibe (Purpose: agencia, Tone: editorial luxury). Ramo: **B** (Sarah existe, logo existe - foto fornecida).
2. **Fase 1:** Usuario fornece 3 fotos da Sarah. Composicao: foto da Sarah em primeiro plano + logo Makewl em painel atras (composto via gpt-image-2 edit mode com mascara). Output: `veo-input.png` 1280x720.
3. **Fase 2:** Resize confirmado, paleta Makewl (consultar /docs/makewl/cores.md). Headroom lateral garantido pro Veo mexer.
4. **Fase 3:** Veo Fast, prompt: "85mm portrait lens, locked tripod, subject (woman) remains static, slow camera dolly-in 4cm over 8s, soft natural key light from window, motivated rim camera-left, neutral grade, low contrast LUT, sensor grain ISO 400, no facial morphing". Negative prompt + "face change, character drift, hand morph". Iterar 3x Fast = $2.40, Standard final = $3.20. Total: $5.60.
5. **Fase 4:** ffmpeg `-g 1` baseline.
6. **Fase 5:** ScrollVideoHero. Scrub revela dolly sutil - pagina abre como cena de documentario.

### Exemplo 3 - Hero produto fisico (Ramo B: caneta exemplo)

**Usuario:** "Landing pra minha marca de caneta artesanal. Tenho fotos."

**Fluxo:**

1. **Fase 0:** Vibe (Purpose: e-commerce premium, Tone: editorial luxury / minimalist Japanese). Ramo: **B**.
2. **Fase 1:** Foto fornecida: caneta sobre mesa de madeira clara, luz natural lateral. Output direto sem composicao (foto ja boa).
3. **Fase 2:** Crop pra 1280x720 mantendo headroom direita pra movimento.
4. **Fase 3:** Veo Fast, prompt: "100mm macro lens, locked tripod, slow pan right 5cm over 8s revealing pen on wood desk, soft window light camera-left, shallow depth of field f/2.8, sensor grain ISO 400, neutral grade, pen remains static". Iterar 2x Fast = $1.60, Standard final = $3.20. Total: $4.80.
5. **Fase 4:** ffmpeg.
6. **Fase 5:** ScrollVideoHero. Scroll abre o objeto na frente do usuario como produto fotografado em catalogo de luxo.

### Exemplo 4 - Hero SaaS abstrato sem produto (Ramo C: gpt-image-2 -> Veo)

**Usuario:** "Pitch deck pra meu novo SaaS de orquestracao de agentes IA. Nao tem produto pronto, so a ideia."

**Fluxo:**

1. **Fase 0:** Vibe (Purpose: pitch / captacao seed, Tone: WebGL maximalist com toque editorial, Differentiation: visualizacao abstrata de "agentes conversando"). Ramo: **C**.
2. **Fase 1:** Gerar imagem base com gpt-image-2 thinking mode: "abstract 3D visualization of interconnected nodes in dark space, glowing soft cyan and warm amber, depth of field, render style: realistic CGI, 16:9 framing". Output: `frame-base.png` 1280x720 gerada.
3. **Fase 2:** Imagem ja em 1280x720 nativo da gpt-image-2. Conferir paleta e composicao.
4. **Fase 3:** Veo Fast: "wide angle 24mm, locked tripod, subtle camera tilt-up 2 degrees over 8s on abstract 3D node graph, deep focus, neutral grade, no warping of geometry, nodes remain in fixed positions, only light pulse and camera micro-move". Negative prompt + "morphing nodes, geometry drift". Iterar 3x Fast = $2.40, Standard final = $3.20. Total: $5.60.
5. **Fase 4:** ffmpeg.
6. **Fase 5:** ScrollVideoHero. Scrub revela a "rede" se animando - abstrato mas controlado, sem slop.

---

## Anti-slop especifico de video AI

### BANLIST de prompts (NUNCA usar nestas combinacoes)

- "epic cinematic"
- "stunning visuals"
- "breathtaking"
- "amazing shot"
- "Hollywood blockbuster style"
- "8K ultra HD masterpiece"
- "perfect lighting"
- "incredible detail"
- "next-level"
- Adjetivos sem ancora tecnica (qualquer "muito X" sem mm de lente, sem ISO, sem direcao de luz)

### USELIST (vocabulario tecnico real que Veo entende)

**Lentes:** 24mm wide, 35mm normal, 50mm prime, 85mm portrait, 100mm macro, 200mm telephoto.

**Movimento de camera:** locked tripod, slow dolly-in [X cm], subtle parallax, gimbal slider, tilt-up [X degrees], pan right [X cm], micro-shake handheld.

**Luz:** motivated rim light camera-left, soft key from window, ambient occlusion, natural overcast, golden hour warm fill, hard noon shadow.

**Cor / grade:** neutral grade, low contrast LUT, no color grading effect, slight desaturation, naturalistic.

**Otica:** shallow depth of field f/2.8, deep focus f/8, bokeh background, in-focus subject foreground.

**Grain / textura:** ISO 400 sensor noise, 35mm film grain, digital clean, slight chromatic aberration only at edges.

**Ancoragem de drift:** subject remains static, only camera moves, geometry remains fixed, no morphing, no warping.

### Negative prompt obrigatorio (copiar tal qual)

```
warped text, distorted letters, text drift, geometry drift, morphing objects,
character drift, face change, hand morph, extra fingers, extra limbs,
anamorphic lens flare, heavy lens flare, motion blur trail, camera shake,
dutch angle, teal-orange grade, oversaturation, plastic skin, doll skin,
extra teeth, melting features, broken anatomy
```

### Movimento sutil > exagerado

Em 8 segundos, deslocamento maximo recomendado: **5-10% do frame**.

| Movimento | Aceitavel | Slop |
|-----------|-----------|------|
| Dolly-in | 3-8 cm em 8s | Push-in trailer (40% do frame) |
| Pan | 4-10 cm em 8s | Whip pan |
| Tilt | 2-5 graus em 8s | Tilt drastico |
| Zoom | Nao use zoom in Veo | Zoom rapido + lens flare |

Regra: se voce tem que pedir "lento" no prompt, ja e sinal que tava planejando rapido demais. Default: sutil.

---

## Decision tree: qual reference consultar quando

```
Estou na Fase 0 (Vibe)
  -> /site-elite skill referencia 02-vibe-questionnaire.md

Estou na Fase 1, Ramo A (Playwright UI)
  -> references/01-playwright-capture.md

Estou na Fase 1, Ramo B (foto + composicao)
  -> references/03-compose-mockup.md

Estou na Fase 1, Ramo C (gpt-image-2 -> Veo)
  -> references/02-veo-prompts.md secao "Combo gpt-image-2 + Veo"
  -> /site-elite references/06-gpt-image-2-prompts.md (prompts canonicos)

Estou na Fase 1, Ramo D (transformacao A->B) ou o site precisa de varios assets
  -> references/07-fabrica-assets.md (lista + orcamento + prompts .txt + validacao)
  -> references/08-hero-transformacao.md (prompt multi-shot 4 beats + gates do ramo)

Estou na Fase 2 (preparar input Veo)
  -> references/03-compose-mockup.md secao "resize 1280x720"

Estou na Fase 3 (Veo image-to-video)
  -> references/02-veo-prompts.md (50+ prompts canonicos)
  -> references/06-veo-api.md (parametros, auth, error handling)

Estou na Fase 4 (ffmpeg pos-processamento)
  -> references/04-ffmpeg-scrub.md

Estou na Fase 5 (ScrollVideoHero em Next.js 16)
  -> references/05-scroll-hero-component.md

Custo Veo descontrolando
  -> tabela "Pricing transparency" desta SKILL.md (volta uma fase, refaz com fast)

Geracao Veo saindo slop
  -> ANTI-SLOP desta SKILL.md (banlist + uselist + negative prompt)
  -> references/02-veo-prompts.md

Scrub trava no browser
  -> references/04-ffmpeg-scrub.md secao "all-keyframes troubleshooting"

Quero o /site-elite normal (sem video)
  -> /site-elite skill (esta skill e camada cinematografica sobre ela)

Cliente nao tem produto definido nem ideia de visual
  -> volta pra /site-elite Fase 4 com UnicornStudio (sem video)
```

---

## Skills auxiliares relacionadas

- `/site-elite` - skill irma. Esta skill e camada cinematografica SOBRE /site-elite, nao substituta. VIBE.md vem de la.
- `/gsap-animations` - deep dive em motion (ScrollTrigger pra Fase 5)
- `/clonar-site` - engenharia reversa pixel-perfect (NAO usar para sites novos)
- `/safari-check` - validacao Safari iOS (gate Fase 5)
- `/text-humanizer` - humanizar copy adjacente

---

## Particularidades teste-aios

### Stack confirmada

- Next.js 16 + Tailwind v4 + Turbopack
- ffmpeg disponivel no host
- Playwright disponivel via mcp__playwright__*
- Veo 3.1 via API (auth + script em scripts/veo-image-to-video.sh)
- gpt-image-2 disponivel (combo Ramo C)

### Regras criticas (CLAUDE.md)

- **USAR INLINE STYLE pra spacing/sizing** em Next.js 16 + Turbopack
- **next dev NAO hidrata via IP externo**: sempre `next build` + `next start`
- **Heredocs em Bash**: NUNCA `cat <<EOF` via Bash tool. Sempre Write tool.
- **gpt-image-2 sem PNG transparente nativo**: gerar fundo solido + mascarar via CSS

### Portas livres pra dev

3107-3199. Verificar `ss -tlnp` antes de subir servidor (ver MEMORY.md do projeto).

### Onde vivem os arquivos cinema da sessao

Convencao: `/root/teste-aios/output/cinema-{projeto}/{data}/` contendo `frame-base.png`, `veo-input.png`, `raw-veo.mp4`, `hero-scrub.mp4`, `prompts.log`, `cost.log`. Log de prompts + custos ajuda a iterar e justificar gasto pro usuario.

---

## Final note

Esta skill NAO entrega um hero cinematografico em 1 prompt. Entrega um workflow em 6 fases que produz um hero scroll-scrubbed memoravel a custo controlado (~$5-8 por hero).

Se o usuario pedir "rapido, em 1 shot", explique que vai sair slop Veo padrao (camera tremida, lens flare, drift) e oferece o trade-off. Se ele insistir, oferecer /site-elite normal (Fase 4 com UnicornStudio resolve sem video, sem custo Veo).

Constraint > permission. Frame-base antes de prompt. Fast antes de Standard. `-g 1` sempre. UMA coisa memoravel.
