# Fabrica de Assets Generativos (com validacao por asset)

> Origem: fluxo do reel @human___academy (frames verificados em 01/07/2026, skill
> /criar-site deles) adaptado ao nosso stack. E a fase que faltava nas nossas skills:
> geracao de imagem/video era ad-hoc e a validacao era "olhar e achar bom".
> Compartilhada por: /site-elite-cinema (assets do hero), /replicar-sistema (imagens
> de mockup/telas) e qualquer skill que gere mais de 1 asset visual.

## Principio

O asset e metade da qualidade percebida. Os sites virais partem de stills gerados
com direcao de arte (luz, lente, materialidade descritas), nao de foto crua do
usuario. Foto amadora na entrada = resultado amador na saida, por melhor que seja
o pipeline depois. TODA imagem/video que entra num hero premium passa por esta
fabrica: prompt tecnico -> geracao -> validacao com veredito -> so PASSA entra.

## Fase A - Lista de assets + orcamento (aprovar ANTES de gerar)

Montar tabela e mostrar ao usuario:

| id | tipo | papel na pagina | modelo | custo est. |
|----|------|-----------------|--------|------------|
| 01-marca-hero | still 21:9 | hero START | gpt-image-2 | ~$0.07 |
| 02-produto-hero | still 21:9 | hero END | gpt-image-2 | ~$0.07 |
| 07-transicao-rest | video 8s | hero scrub | Veo 3.1 fast | ~$0.80 |

Regras:
- Naming canonico desde a lista: `NN-slug-papel.ext`. O arquivo gerado ja nasce com
  o nome final (rastreabilidade prompt -> asset -> secao da pagina).
- Orcamento total na mesa antes de disparar QUALQUER geracao.
- Estimar 1.3x o custo (assets reprovados na validacao serao regerados).

## Fase B - Prompt tecnico por asset (arquivos versionados)

Um arquivo `prompts/NN-slug.txt` por asset, com 6 blocos:

```
MODELO: gpt-image-2 | gemini image (nano banana) | veo-3.1-fast | veo-3.1-standard
ASPECT/RES: 21:9 2K | 1280x720 | ...
PAPEL: hero START / secao 03 fundo / ...
REFS: refs/NN-*.png (o que anexar como referencia visual, se o modo suportar)
PROMPT: [direcao de fotografia real: lente, luz, materialidade, composicao,
         paleta declarada em %. Vocabulario da USELIST da SKILL.md, nunca da banlist]
NEGATIVE: [catalogo abaixo, adaptado ao asset]
```

Sem prompt "epic cinematic stunning": a anatomia e a mesma da Fase 3 da SKILL.md
(lens + luz + grain + materialidade + ancoragem). Paleta SEMPRE declarada com
percentuais ("70% preto profundo, 20% ambar quente, 10% branco estourado") - e o
que mantem coerencia entre assets de secoes diferentes.

### Catalogo: negative prompt de fotorealismo (stills)

Copiar e adaptar (extraido do fluxo de referencia + nossos gotchas Veo):

```
no plastic skin, no airbrush effect, no beauty filter, no HDR crunchy look,
no over-sharpening halos, no digital noise, no banding, no compression artifacts,
no cartoon stylization, no illustration feel, no 3D render look,
no stock photography cliche, no generic studio glossy,
no floating objects without physics, no broken anatomy, no text artifacts,
no watermarks, no logos, no warped clothing folds,
no fashion-magazine glamour pose, no celebrity recognition,
no digital sky replacement look, no neon signage
```

Se o asset TEM texto proposital (embalagem, letreiro): remover "no text artifacts"
e escrever o texto exato entre aspas no PROMPT (e conferir na validacao - modelos
adoram renderizar o texto do prompt literalmente na imagem).

## Fase C - Geracao: modo A (API) ou modo B (manual)

Perguntar UMA vez, com o orcamento da Fase A na mesa:

**(A) Modo API** - eu disparo tudo:
- Stills: `gpt-image-2` (default do projeto) ou Gemini image/Nano Banana (key ja no
  projeto, shim OpenAI-compat).
- Video: Veo 3.1 via `scripts/veo-image-to-video.sh` (fast antes de standard, sempre).
- Agregador opcional: se o usuario fornecer `FREEPIK_API_KEY` no `.env`, a API da
  Freepik da acesso unificado a Seedance/Kling/Runway alem dos nossos - util quando
  o look pedir um modelo especifico. NAO e dependencia: sem a key, os modelos do
  projeto cobrem tudo.

**(B) Modo Manual** - usuario gera fora (free tiers) e devolve:
- Entregar o pacote `prompts/*.txt` + `refs/` + a instrucao: "gere em [modelo
  sugerido], anexe as refs indicadas, salve com o nome exato do arquivo .txt".
- Vantagem: custo zero de API pro cliente. Desvantagem: ciclo mais lento.
- Ao receber, conferir naming e rodar a Fase D igual.

## Fase D - Validacao por asset (o gate que faltava)

Cada asset gerado e LIDO (tool Read e multimodal) e comparado contra o proprio
prompt. Veredito em `relatorio-assets.md`:

```
## Relatorio de validacao
- [PASSA]    01-marca-hero - bate com prompt. Paleta ok, negative space pro headline ok.
- [PASSA*]   02-produto-hero - PASSA com observacao: pose lateral em vez de 3/4.
             Valido editorialmente, mantido.
- [ARTEFATO] 03-secao-tangente - modelo renderizou literalmente o texto do prompt
             na imagem. REGERAR com negative reforcado.
- [DESVIO]   04-secao-baile - composicao centralizada, pedido era bilateral.
             REGERAR so se a grade da secao exigir; senao aceitar e registrar.
```

Checklist por asset:
- [ ] Artefatos: texto fantasma, anatomia quebrada, objetos flutuando, warp
- [ ] Composicao: bate com o PAPEL (headroom pro texto? espaco pro Veo mexer?)
- [ ] Paleta: dentro dos percentuais declarados (comparar com os outros assets)
- [ ] Materialidade: parece foto/filme, nao render 3D generico
- [ ] Se still vai virar input de video: regras da Fase 2 da SKILL.md (1280x720 etc)

Regras duras:
- So PASSA / PASSA* entram em `public/assets/`. ARTEFATO regenera sempre.
- Custo afundado e armadilha (mesma regra da Fase 3): nao usar asset ruim
  "porque ja gastou".
- Maximo 2 regeracoes por asset; na 3a falha, repensar o prompt (o problema e ele).
- Relatorio SEMPRE mostrado ao usuario com os assets renderizados - a aprovacao
  estetica final e dele, nao minha (licao da demo-particulas: "validado e medido"
  nao e "bonito").

## Artefatos da sessao (versionados junto do projeto)

```
output/assets-{projeto}/{data}/
  briefing.json        # o que foi pedido, paleta global, refs do usuario
  prompts/*.txt        # 1 por asset (Fase B)
  refs/                # referencias visuais renomeadas
  relatorio-assets.md  # vereditos (Fase D)
  cost.log             # custo real por geracao
public/assets/         # SO os aprovados, com naming canonico
```
