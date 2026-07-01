# Hero de Transformacao (materia A vira materia B) - Ramo D

> A resposta correta ao efeito viral "foto que se desfaz e vira o produto"
> (@nomadatoast, @web.with.ai). Evidencia de 01/07/2026 (frames dos reels): esses
> heros sao VIDEO gerado por IA e scrubado no scroll, NAO particulas WebGL
> real-time. O criador literalmente legenda "I SAID VIDEO" e usa arquivo
> "Scroll Video Hero Prompt". Kling 3.0 multi-shot / Seedance geram a
> transformacao; o site so scruba o mp4.

## Por que rota VIDEO e nao particulas real-time (licao da demo-particulas)

A demo do rosto->perfume (Three.js, 101k particulas additive) provou o TETO da
tecnica real-time: gl.Points com sprite sempre rende "poeira brilhante". Os reels
que impressionam tem fios volumetricos com sombra propria, cubos com iluminacao
global, materiais fotorreais - isso e RENDER offline, impossivel em Points a 60fps.
Nao era execucao ruim; era ferramenta errada pro alvo.

Divisao honesta:
- **Video scrubado (este ramo):** riqueza visual ilimitada, materia fotorreal.
  Fixo: nao reage a mouse. E o default pro "wow cinematografico".
- **Particulas real-time (demo-particulas/):** so quando INTERACAO e o ponto
  (repulsao de mouse, holograma com depth). Pode ser CAMADA leve por cima do video
  (dust ambiente, 5-10k particulas) - o video da o wow, a particula da o "vivo".

## Pipeline (usa as fases da SKILL.md + fabrica 07)

```
[1] Fabrica de assets (07): still ORIGEM + still DESTINO
    - MESMO enquadramento/proporcao/paleta declarada nos dois prompts
    - Gerados com direcao de arte, NUNCA foto crua do usuario direto no Veo
[2] Prompt de transformacao multi-shot (template abaixo)
[3] Veo 3.1 FAST 720p -> validar os 4 beats -> so entao STANDARD
    - **CONFIRMADO em producao (01/07/2026):** `veo-3.1-fast-generate-preview`
      ACEITA `lastFrame` no instance (`{"image":{...},"lastFrame":{...}}`) - a
      interpolacao trava os dois extremos e o frame final sai identico ao still
      DESTINO. Usar sempre. Script validado: output/cinema-tino/2026-07-01/veo-transform.sh
    - GOTCHA confirmado: "35mm film grain" no prompt fez o Veo renderizar
      MOLDURA DE FILME literal (furos de pelicula + texto "35mm 55" nas bordas).
      Usar "subtle digital sensor grain ISO 400" e incluir no negative:
      "film strip border, sprocket holes, film frame edges, frame numbers".
[4] ffmpeg -g 1 baseline (Fase 4 da SKILL.md, inegociavel)
[5] ScrollVideoHero (Fase 5) - o scroll vira a timeline da transformacao
```

## Robustez do scrub (bugs REAIS da primeira entrega, 01/07/2026)

O usuario viu "so a foto parada" na primeira versao. Correcoes obrigatorias:
1. **Video via fetch -> Blob -> objectURL**, com loader de % e scroll travado ate
   bufferizar 100%. `preload="auto"` NAO garante buffer (data-saver/low-power
   ignoram); scrub sem buffer = poster congelado. Blob elimina a classe inteira
   de falha (streaming, range, mobile unlock).
2. **prefers-reduced-motion NAO pode apagar a pagina.** Scrub e movimento
   dirigido 1:1 pelo input do usuario: manter. Reduzir = desligar Lenis/inercia
   (lerp 1.0) e entrance animations, nunca display:none no video.
3. **TODO elemento visivel entra na coreografia de progresso** - eyebrow e lead
   dos panes tambem, nao so as palavras do headline (bug real: pane final
   visivel desde o inicio).
4. A pagina nao e so o video: **camada de scroll completa** (Lenis + GSAP
   ScrollTrigger) - palavras do headline se desfazem junto com a materia (split
   por palavra + janelas de progresso no ticker), caption no HOLD, text-fill no
   manifesto, parallax em stills, reveals, footer gigante outline. Exemplo
   funcionando: output/cinema-tino/2026-07-01/site/index.html (porta 3115).

## Template: prompt de transformacao multi-shot

A disciplina anti-drift (adaptada de Kling/Seedance pro Veo): **4 beats com
timestamp + paleta com % declarada + materialidade da transicao nomeada**.
Densidade tecnica e o que impede o modelo de derivar no meio do clip.

```
Locked tripod, 50mm prime, [luz: ex. single tungsten key camera-left].
START (frame 0): [descricao exata do still ORIGEM].
BEAT 1 (0-2s): a superficie de [sujeito] comeca a se desfazer em [materialidade:
  fibras incandescentes / po fino / cubos de voxel / fumaca densa] a partir de
  [regiao], o resto permanece intacto e nitido.
BEAT 2 (2-4s): a desintegracao varre [direcao], os fragmentos ficam suspensos
  com [comportamento: peso / deriva lenta / brilho proprio].
BEAT 3 (4-6s): HOLD - a nuvem paira quase estatica mantendo a silhueta fantasma
  de [origem], micro-movimento apenas.
BEAT 4 (6-8s): os fragmentos convergem e remontam em [descricao exata do still
  DESTINO], superficie selando por ultimo em [regiao].
PALETTE: [ex. 70% deep black background, 20% warm amber fragments, 10% skin tone].
Camera nao se move. Fundo permanece constante.
NEGATIVE: [negative da SKILL.md + no scene change, no camera movement,
  no new objects, no palette shift]
```

Notas:
- O BEAT 3 (hold) e o beat dramatico que ja validamos na demo-particulas - ele
  continua valendo aqui, so que renderizado pelo modelo de video.
- A materialidade NOMEADA e a decisao estetica central (fibras? po? voxels?
  fumaca?). Escolher UMA e manter nos 4 beats. Trocar de materia no meio = slop.
- **Excecao a regra "movimento 5-10% do frame"** da SKILL.md: transformacao move
  muito por definicao. O que trava o drift aqui NAO e sutileza de movimento, e a
  densidade dos beats + paleta declarada + extremos travados (first/last frame).
  A camera continua LOCKED - o movimento e da materia, nunca da camera.

## Quality gate do ramo D (alem dos gates globais)

- [ ] Frame 0 do video == still ORIGEM (sem re-interpretacao do modelo)
- [ ] Frame final legivel como o still DESTINO (produto reconhecivel, sem morph residual)
- [ ] Os 4 beats acontecem NOS timestamps (scrubbar em 25/50/75% e conferir)
- [ ] Materialidade constante (nao vira fumaca no meio se comecou fibra)
- [ ] Paleta dentro dos % declarados do inicio ao fim
- [ ] Validacao final e do USUARIO vendo o scrub real - nao declarar bonito por ele

## Custo tipico do ramo D

2 stills fabrica (~$0.15) + 2-3 iteracoes Veo fast ($1.60-2.40) + 1 standard final
($3.20) = **~$5-6 por hero de transformacao**. Registrar em cost.log.

## Narrativa (regra anti-slop, herdada da demo-particulas)

Origem e destino precisam de vinculo conceitual ("a fundadora vira o perfume",
"o ingrediente vira o prato", "o rascunho vira o produto"). Transformacao sem
narrativa e efeito bonito e vazio - exigir o vinculo antes de gerar qualquer asset.
