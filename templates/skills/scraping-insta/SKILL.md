---
name: scraping-insta
description: Baixa posts/reels de um perfil Instagram, transcreve com Whisper, analisa hooks/estrutura/CTAs e destila um padrao viral replicavel. Usa a REST API interna do Instagram (sem Apify, custo zero de scraping). Use quando o usuario quer analisar um perfil IG, replicar o estilo de um criador, extrair formula de sucesso, ou gerar dataset pra treinar IA com o tom de alguem.
---

Analise o perfil Instagram e destile o padrao de sucesso: $ARGUMENTS

## O que essa skill faz

Pega um perfil Instagram publico e entrega:

1. **Metadados** dos top N reels/posts (views, likes, comments, shares, saves, captions, thumbs)
2. **Videos baixados** dos top virais
3. **Transcricoes** (audio -> texto via Whisper)
4. **Analise individual** de cada post (hook, estrutura, CTA, tema, gatilhos)
5. **Padrao destilado** em markdown: formula replicavel + hooks testados com numbers reais
6. **Dataset JSONL** (opcional) pronto pra fine-tuning na OpenAI

Output final igual ao `garbers-viral-formulas.md` do projeto original: formula de N blocos + biblioteca de hooks rankeada por engagement.

## Passo 1: Perguntar ao usuario

ANTES de qualquer acao, use AskUserQuestion:

1. **Qual perfil?** (username sem @, ex: `dr.luizgarbers`)

2. **Quantos posts analisar?**
   - Top 20 (rapido, ~$0.30)
   - Top 50 (padrao, ~$0.65)
   - Top 100 (profundo, ~$1.30)

3. **O que priorizar?**
   - So reels (melhor pra padrao de hook/audio)
   - So carrosseis/posts (melhor pra padrao de copy/caption)
   - Ambos (padrao completo)

4. **Gerar JSONL pra fine-tuning?**
   - Sim (gera dataset no formato da OpenAI, pronto pra `fine_tuning.jobs.create`)
   - Nao (so o markdown de padrao)

5. **Nicho do perfil?** (opcional, melhora a analise)
   - Ex: saude/odontologia/estetica, marketing, fitness, etc. Se nao souber, deixa vazio.

## Passo 2: Scrape do perfil

Use o scraper nativo do monitor-server (REST API interna do IG, sem Apify, $0):

```bash
node -e "
const scraper = require('/root/teste-aios/aios-core/apps/monitor-server/src/instagram-scraper-native.js');
(async () => {
  const data = await scraper.scrapeProfile('USERNAME', { maxPosts: N });
  require('fs').writeFileSync('/tmp/ig-raw.json', JSON.stringify(data, null, 2));
})();
"
```

Endpoints que o scraper usa internamente:
- `/api/v1/users/web_profile_info/` - metadata + primeiros 12 posts
- `/api/v1/feed/user/{id}/` - paginacao (12 por pagina, delay 2s)

Rate limit: ~200 req/h por IP. Se der 429, esperar 30min e retomar.

**Se o scraper nativo nao existir no projeto de destino**, implementar seguindo:
- Base URL: `https://www.instagram.com`
- Headers: `X-IG-App-ID: 936619743392459`, `User-Agent: Mozilla/5.0 (Chrome 131)`
- POSTS_PER_PAGE: 12, DELAY_BETWEEN_PAGES_MS: 2000

## Passo 3: Ranquear e filtrar top virais

Ordenar posts por engagement rate:
```
score = (likes + comments*3 + shares*5 + saves*4) / views
```

Pegar os top N definidos no Passo 1.

## Passo 4: Download dos videos

Usar `yt-dlp` pra cada reel:

```bash
yt-dlp -o "/tmp/ig-analysis/%(id)s.mp4" \
  --max-filesize 50M \
  "https://www.instagram.com/reel/CODIGO/"
```

Limites: 50MB por video. Se estourar, pular.

## Passo 5: Extrair audio

Pra cada video baixado:

```bash
ffmpeg -i /tmp/ig-analysis/ID.mp4 \
  -vn -acodec mp3 -ar 16000 -ac 1 -b:a 64k \
  /tmp/ig-analysis/ID.mp3
```

MP3 16kHz mono 64k = fica abaixo dos 25MB do limite do Whisper.

## Passo 6: Transcrever

**Modelo: `gpt-4o-mini-transcribe`** (custo ~$0.003/min, qualidade otima em PT-BR)

```javascript
const { OpenAI } = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const transcription = await openai.audio.transcriptions.create({
  file: fs.createReadStream('/tmp/ig-analysis/ID.mp3'),
  model: 'gpt-4o-mini-transcribe',
  language: 'pt',
});
```

Salvar cada transcricao em `/tmp/ig-analysis/ID.txt`.

## Passo 7: Analise individual por post

**Modelo: `gpt-4o-mini`** (tarefa repetitiva estruturada, nao precisa modelo premium)

Pra cada post, enviar: caption + transcricao + metricas. Pedir JSON:

```json
{
  "hook_falado": "primeira frase do audio",
  "hook_escrito": "primeira linha do caption",
  "hook_categoria": "curiosidade|provocacao|storytelling|quebra-mito|problema-solucao|valor|desafio",
  "estrutura_blocos": ["hook", "dor", "validacao", "quebra", "solucao", "resultado", "cta"],
  "cta_tipo": "comentar|salvar|compartilhar|seguir|dm|link-bio|nenhum",
  "cta_frase": "texto exato do CTA",
  "tema": "tema central do conteudo",
  "gatilhos": ["autoridade", "escassez", "prova-social", "urgencia", "reciprocidade"],
  "tom": "provocativo|educativo|inspirador|humor|serio",
  "duracao_estimada_seg": 45,
  "por_que_bombou": "hipotese em 1 frase"
}
```

Sistema prompt deve enfatizar PT-BR, sem travessao (em-dash), acentuacao correta.

## Passo 8: Destilacao do padrao

**Modelo: `gpt-5.2`** (etapa criativa/sintese, vale pagar mais). Lembrete: GPT-5.2 usa `max_completion_tokens`, NAO `max_tokens`.

Enviar todos os JSONs do Passo 7 + metricas dos posts e pedir:

1. **Formula de N blocos** (identificar quantos blocos recorrentes, nomear cada um, descrever funcao)
2. **Biblioteca de hooks** rankeada por tier S/A/B baseado em views reais
   - Tier S: top 10% em views
   - Tier A: 10-30%
   - Tier B: 30-60%
3. **Categorias de hook** ordenadas por engagement medio
4. **CTAs mais usados** (com frequencia)
5. **Temas recorrentes** (top 5)
6. **Gatilhos dominantes** (top 3)
7. **Voz/tom caracteristico** (descricao em 3-5 bullets)
8. **Vocabulario obrigatorio** (palavras que o criador usa muito)
9. **Vocabulario proibido** (palavras que ele EVITA)
10. **Checklist pre-publicacao** (replicavel)

Salvar em `/root/scraping-insta-output/USERNAME/padrao-viral.md`.

## Passo 9: JSONL (se usuario pediu)

Formato OpenAI fine-tuning (`messages` array por linha):

```jsonl
{"messages":[{"role":"system","content":"Voce escreve reels no estilo de @USERNAME. Tom: [X]. Vocabulario: [Y]."},{"role":"user","content":"Tema: [tema do post]"},{"role":"assistant","content":"[caption + roteiro do post real]"}]}
```

Uma linha por post analisado. Salvar em `/root/scraping-insta-output/USERNAME/dataset.jsonl`.

Treinar depois com:
```bash
openai api fine_tuning.jobs.create -t dataset.jsonl -m gpt-4o-mini-2024-07-18
```

## Passo 10: Apresentar resultado

Mostrar ao usuario:
- Total de posts scrapados / analisados / transcritos
- Custo real estimado (tokens + Whisper minutos)
- Caminho do `padrao-viral.md`
- Caminho do `dataset.jsonl` (se gerado)
- Preview dos 3 top hooks encontrados
- Perguntar se quer ajustar nicho/categorizacao antes de salvar final

## Modelos OpenAI (referencia rapida)

| Etapa | Modelo | Parametro tokens | Por que |
|-------|--------|------------------|---------|
| Transcricao | `gpt-4o-mini-transcribe` | - | Whisper barato PT-BR |
| Analise por post | `gpt-4o-mini` | `max_tokens` | Estruturado, repetitivo |
| Destilacao final | `gpt-5.2` | `max_completion_tokens` | Sintese criativa |
| Embeddings (opcional) | `text-embedding-3-small` | - | 1536D padrao projeto |

**IMPORTANTE sobre GPT-5.2:** usa `max_completion_tokens`, nao `max_tokens`. Passar `max_tokens` retorna 400.

## Dependencias

No sistema de destino precisa ter:
- `node` 18+
- `yt-dlp` (`pip install yt-dlp`)
- `ffmpeg` (`apt install ffmpeg`)
- `openai` npm package
- Variavel `OPENAI_API_KEY` no ambiente

Scraper nativo (se nao existir no projeto):
- Copiar `instagram-scraper-native.js` do projeto teste-aios: `aios-core/apps/monitor-server/src/instagram-scraper-native.js`
- Ou implementar seguindo os endpoints documentados no Passo 2.

## Custos estimados por perfil

| Tamanho | Custo total | Breakdown |
|---------|-------------|-----------|
| Top 20 reels | ~$0.30 | Whisper $0.20 + analise $0.05 + destilacao $0.05 |
| Top 50 reels | ~$0.65 | Whisper $0.50 + analise $0.10 + destilacao $0.05 |
| Top 100 reels | ~$1.30 | Whisper $1.00 + analise $0.20 + destilacao $0.10 |

## Observacoes

- Rate limit IG (~200 req/h): se analisando varios perfis em sequencia, esperar entre eles.
- Perfis privados: nao da, scraper so funciona em perfis publicos.
- Reels com musica copyright: yt-dlp baixa normalmente, Whisper transcreve apenas audio do criador.
- Conteudo PT-BR: acentuacao correta OBRIGATORIA, travessao (em-dash) PROIBIDO no padrao final (parece IA).
- Se o perfil tiver menos posts que N solicitado, usar o que tem e avisar o usuario.
