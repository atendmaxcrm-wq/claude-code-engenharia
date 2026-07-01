# Prompt-Spec com Assets Embutidos (formato MotionSites)

> Origem: metodo do MotionSites (motionsites.ai), dissecado em 01/07/2026 via video
> "I Built an Award-Winning Website in 19 Minutes" + prompt free "Lithos" + frames
> verificados (analise completa: docs/analise-motionsites-metodo.md). E o formato de
> EMPACOTAMENTO e REUSO de uma secao/mecanica: um prompt autocontido que carrega os
> proprios assets e a implementacao exata. Cola em qualquer AI coder e sai igual.

## Quando usar

- Reuso interno: uma mecanica que deu certo num projeto (ex: hero de transformacao do
  Tino) vira prompt-spec e replica em outro projeto em minutos.
- Distribuicao: prompt-spec e um PRODUTO (MotionSites vende ~130 deles a $149-199/ano,
  free como topo de funil). Se um dia empacotarmos os nossos, o formato e este.
- NAO usar para trabalho interno normal da skill (as fases 0-5 + fabrica ja cobrem);
  isto e formato de SAIDA/empacotamento, nao de processo.

## Anatomia (7 blocos, na ordem)

1. **Stack declarada na primeira linha.** "React 18 + TypeScript + Vite + Tailwind +
   lucide-react". Trava o alvo antes de qualquer detalhe.
2. **Fontes prontas pra colar:** bloco `@import` do Google Fonts + regra de papel
   ("Inter = UI; Playfair Display italic = display"). O usuario do prompt nao decide
   fonte, ele COLA.
3. **ASSETS COM URL PUBLICA + PAPEL.** Cada imagem/video com a URL completa e o nome
   do papel (`BG_IMAGE_1` base, `BG_IMAGE_2` reveal). Sem "adicione uma imagem bonita".
   - Imagens: CDN com params de otimizacao (o MotionSites usa proxy com w/q/output=webp).
   - Video: STREAMING, nao arquivo (ele usa Mux `.m3u8`). Para scroll-scrub frame-accurate
     nosso, continua valendo o mp4 `-g 1` (04-ffmpeg-scrub) - o .m3u8 dele e pra video
     de fundo tocando, nao scrub.
   - Nossos assets da fabrica (07) ficam em output/ local; ao empacotar um prompt-spec
     REUTILIZAVEL, subir os assets pra URL publica estavel (R2/Mux) primeiro.
4. **Layout com precisao de classe:** camadas com z-index explicito, classes Tailwind
   exatas, textos LITERAIS, inline styles pontuais (letterSpacing por linha), `100dvh`
   no hero (nao 100vh - browser chrome mobile corta).
5. **A mecanica-assinatura como IMPLEMENTACAO, nao desejo.** Nao "um efeito legal de
   spotlight": o algoritmo (ver exemplo canonico abaixo). E o que separa prompt-spec
   de prompt comum.
6. **Animacoes de entrada NOMEADAS:** keyframes com nome (heroReveal/heroFadeUp/heroZoom),
   easing declarado (cubic-bezier(0.16,1,0.3,1)), delays escalonados explicitos
   (0.25/0.42/0.7/0.85s) e `prefers-reduced-motion` zerando tudo.
7. **Responsividade explicita:** o que some abaixo de md, escalas de texto por
   breakpoint, ancoragem mobile (left-5 right-5) vs desktop (right-anchored).

Propriedade util do formato: os blocos sao INDEPENDENTES. O criador do video cola so o
bloco 2 (fontes) e avisa "the prompt is broken, do your best" - e funciona. Escrever
cada bloco pra sobreviver sozinho.

## Sistema junto, nao so hero

O prompt-spec bom especifica o SISTEMA da secao: no exemplo real verificado, alem do
hero vem a nav inteira (CSS completo da pill nav, hamburger responsivo, ate os
`gsap.to(window,{scrollTo})` dos cliques) e a montagem final:

```
APP COMPONENT ASSEMBLY
<ScrollVideo src="https://stream.mux.com/....m3u8" />
<PillNav />
<div style={{position:'relative', height:'500vh'}}>
  <ScrollFloat>`Headline`</ScrollFloat>
</div>
<GlassPanel />
```

Container de scroll alto (500vh) + componentes nomeados = a IA monta sem inventar.

## Exemplo canonico de mecanica-assinatura: spotlight cursor-reveal (Lithos)

Duas imagens da MESMA cena (base + reveal); um holofote circular suave segue o cursor
e revela a segunda imagem por mascara:

- Estado: `SPOTLIGHT_R = 260`; refs `mouse` (cru) e `smooth` (suavizado); rAF com lerp
  `smooth += (mouse - smooth) * 0.1` (nunca snap).
- `RevealLayer`: canvas ESCONDIDO do tamanho da janela; a cada frame, radial gradient
  em (cursorX, cursorY) com 6 stops (1 / 1 @0.4 / 0.75 @0.6 / 0.4 @0.75 / 0.12 @0.88 /
  0 @1) preenchendo um arco de raio R; `canvas.toDataURL()` vira `maskImage` +
  `webkitMaskImage` do div de reveal (`maskSize: '100% 100%'`).
- Par de imagens coerente: gerar a base e pedir variacao da MESMA cena (ou zoom-out,
  ver 08). Na nossa fabrica: asset 2 com o asset 1 como ref multimodal.

Outras mecanicas do catalogo dele pra inspirar specs nossos: Ken Burns zoom-out no
load (heroZoom 1.12 -> 1), blur-rise escalonado (heroReveal com filter blur 12px -> 0),
texto que "nasce" da pagina por mascara-gradiente (ver 08), scroll-float, glass panel.

## Checklist antes de dar um prompt-spec por pronto

- [ ] Cola num AI coder LIMPO (sem contexto) e sai a secao certa? (teste real)
- [ ] Assets acessiveis por URL publica (curl -I 200) e com papel nomeado?
- [ ] Mecanica descrita como algoritmo (da pra implementar sem ver a demo)?
- [ ] reduced-motion coberto? Mobile coberto?
- [ ] Textos literais (zero lorem ipsum)?
- [ ] Demo em video gravada (scroll completo) - e a prova social do spec.
