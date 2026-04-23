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

A skill e auto-contida: o scraper fica em `assets/instagram-scraper-native.js` dentro da propria skill. Nao depende de caminhos externos.

## Passo 0: Verificar dependencias

Antes de rodar, confira se o sistema tem as dependencias. Se faltar algo, informe o usuario e instale:

```bash
# Checar
command -v node && node --version     # >= 18
command -v yt-dlp && yt-dlp --version
command -v ffmpeg && ffmpeg -version | head -1
echo $OPENAI_API_KEY | head -c 10     # deve comecar com sk-

# Instalar o que faltar (Linux)
pip install -U yt-dlp
apt-get install -y ffmpeg
npm install openai    # instala localmente no projeto
```

Depois, **descubra onde a skill esta instalada**. Use o diretorio pra achar o asset:

```bash
SKILL_DIR="$(find . -type d -path '*/.claude/skills/scraping-insta' 2>/dev/null | head -1)"
[ -z "$SKILL_DIR" ] && SKILL_DIR="$HOME/.claude/skills/scraping-insta"
echo "Skill em: $SKILL_DIR"
ls "$SKILL_DIR/assets/instagram-scraper-native.js"  # deve existir
```

Crie um diretorio de trabalho pra essa analise:

```bash
WORK_DIR="/tmp/scraping-insta-$USERNAME-$(date +%s)"
mkdir -p "$WORK_DIR"
```

## Passo 1: Perguntar ao usuario

Use AskUserQuestion:

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
   - Sim (gera dataset no formato da OpenAI)
   - Nao (so o markdown de padrao)

5. **Nicho do perfil?** (opcional, melhora a analise)
   - Ex: saude/odontologia/estetica, marketing, fitness, etc.

## Passo 2: Scrape do perfil

Usa o scraper que vem empacotado com a skill. Crie `$WORK_DIR/scrape.js`:

```javascript
const scraper = require(process.env.SKILL_DIR + '/assets/instagram-scraper-native.js');
const fs = require('fs');

(async () => {
  const username = process.env.IG_USERNAME;
  const maxPosts = parseInt(process.env.MAX_POSTS || '50', 10);
  const data = await scraper.scrapeInstagramProfile(username, { maxPosts });
  fs.writeFileSync(process.env.WORK_DIR + '/raw.json', JSON.stringify(data, null, 2));
  console.log(`Scraped ${data.posts.length} posts from @${username}`);
})().catch(e => { console.error(e); process.exit(1); });
```

Rode:

```bash
SKILL_DIR="$SKILL_DIR" WORK_DIR="$WORK_DIR" \
  IG_USERNAME="perfil_aqui" MAX_POSTS=50 \
  node "$WORK_DIR/scrape.js"
```

**Sobre o scraper:** usa endpoints internos do Instagram (`/api/v1/users/web_profile_info/` e `/api/v1/feed/user/{id}/`) com header `X-IG-App-ID: 936619743392459`. Sem login, sem Apify, custo zero. Rate limit ~200 req/h por IP, delay automatico de 2s entre paginas.

Se voltar 429 (rate limit), espere 30min e retome. Se voltar 404, perfil nao existe ou e privado.

## Passo 3: Ranquear e filtrar top virais

Leia `$WORK_DIR/raw.json` e ordene por engagement:

```
score = (likes + comments*3 + shares*5 + saves*4) / max(views, 1)
```

Filtrar pelo tipo escolhido no Passo 1 (reels/posts/ambos). Pegar top N. Salvar em `$WORK_DIR/top.json`.

## Passo 4: Download dos videos

Pra cada item de `top.json` que seja video/reel:

```bash
yt-dlp -o "$WORK_DIR/videos/%(id)s.mp4" \
  --max-filesize 50M \
  --no-warnings \
  "https://www.instagram.com/reel/CODIGO/"
```

Limites: 50MB. Se estourar, pula e registra.

## Passo 5: Extrair audio

Pra cada video baixado:

```bash
ffmpeg -i "$WORK_DIR/videos/ID.mp4" \
  -vn -acodec mp3 -ar 16000 -ac 1 -b:a 64k \
  -y "$WORK_DIR/audio/ID.mp3" 2>/dev/null
```

MP3 16kHz mono 64k fica abaixo do limite de 25MB do Whisper.

## Passo 6: Transcrever

**Modelo: `gpt-4o-mini-transcribe`** (PT-BR otimo, ~$0.003/min):

```javascript
const { OpenAI } = require('openai');
const fs = require('fs');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const transcription = await openai.audio.transcriptions.create({
  file: fs.createReadStream(audioPath),
  model: 'gpt-4o-mini-transcribe',
  language: 'pt',
});

fs.writeFileSync(`${WORK_DIR}/transcripts/${id}.txt`, transcription.text);
```

## Passo 7: Analise individual por post

**Modelo: `gpt-4o-mini`** (tarefa estruturada, barato). Usa `max_tokens` normal.

Pra cada post, enviar caption + transcricao + metricas. Pedir JSON:

```json
{
  "hook_falado": "primeira frase do audio",
  "hook_escrito": "primeira linha do caption",
  "hook_categoria": "curiosidade|provocacao|storytelling|quebra-mito|problema-solucao|valor|desafio",
  "estrutura_blocos": ["hook", "dor", "validacao", "quebra", "solucao", "resultado", "cta"],
  "cta_tipo": "comentar|salvar|compartilhar|seguir|dm|link-bio|nenhum",
  "cta_frase": "texto exato do CTA",
  "tema": "tema central",
  "gatilhos": ["autoridade", "escassez", "prova-social", "urgencia", "reciprocidade"],
  "tom": "provocativo|educativo|inspirador|humor|serio",
  "duracao_estimada_seg": 45,
  "por_que_bombou": "hipotese em 1 frase"
}
```

System prompt: enfatize PT-BR, sem travessao (em-dash), acentuacao correta.

Salvar cada JSON em `$WORK_DIR/analysis/ID.json`.

## Passo 8: Destilacao do padrao

**Modelo: `gpt-5.2`** (sintese criativa). Usa `max_completion_tokens`, NAO `max_tokens`.

Envie todos os JSONs do Passo 7 + metricas e peca:

1. **Formula de N blocos** recorrentes (nomear cada um, descrever funcao)
2. **Biblioteca de hooks** rankeada por tier baseado em views reais:
   - Tier S: top 10% em views
   - Tier A: 10-30%
   - Tier B: 30-60%
3. **Categorias de hook** ordenadas por engagement medio
4. **CTAs mais usados** (com frequencia)
5. **Temas recorrentes** (top 5)
6. **Gatilhos dominantes** (top 3)
7. **Voz/tom caracteristico** (3-5 bullets)
8. **Vocabulario obrigatorio** (palavras recorrentes do criador)
9. **Vocabulario proibido** (palavras que ele EVITA)
10. **Checklist pre-publicacao** (replicavel)

Salvar em `$WORK_DIR/padrao-viral.md`.

## Passo 9: JSONL (se usuario pediu)

Formato OpenAI fine-tuning (uma linha por post):

```jsonl
{"messages":[{"role":"system","content":"Voce escreve reels no estilo de @USERNAME. Tom: X. Vocabulario: Y."},{"role":"user","content":"Tema: [tema do post]"},{"role":"assistant","content":"[caption + roteiro do post real]"}]}
```

Salvar em `$WORK_DIR/dataset.jsonl`.

Pra treinar depois:
```bash
openai api fine_tuning.jobs.create -t dataset.jsonl -m gpt-4o-mini-2024-07-18
```

## Passo 10: Copiar output e apresentar resultado

Copie `padrao-viral.md` (e `dataset.jsonl` se gerado) de `$WORK_DIR` pra um diretorio estavel no projeto atual:

```bash
OUTPUT_DIR="./scraping-insta-output/$IG_USERNAME"
mkdir -p "$OUTPUT_DIR"
cp "$WORK_DIR/padrao-viral.md" "$OUTPUT_DIR/"
[ -f "$WORK_DIR/dataset.jsonl" ] && cp "$WORK_DIR/dataset.jsonl" "$OUTPUT_DIR/"
```

Mostrar ao usuario:
- Total de posts scrapados / analisados / transcritos
- Custo real (tokens + minutos Whisper)
- Caminho do `padrao-viral.md`
- Caminho do `dataset.jsonl` (se gerado)
- Preview dos 3 top hooks encontrados
- Perguntar se quer ajustar nicho/categorizacao

## Modelos OpenAI (referencia rapida)

| Etapa | Modelo | Param tokens | Por que |
|-------|--------|--------------|---------|
| Transcricao | `gpt-4o-mini-transcribe` | - | Whisper barato PT-BR |
| Analise por post | `gpt-4o-mini` | `max_tokens` | Estruturado, repetitivo |
| Destilacao final | `gpt-5.2` | `max_completion_tokens` | Sintese criativa |
| Embeddings (opcional) | `text-embedding-3-small` | - | 1536D |

**IMPORTANTE GPT-5.2:** usa `max_completion_tokens`. Passar `max_tokens` retorna 400.

## Dependencias do sistema

| Dep | Checar | Instalar |
|-----|--------|----------|
| Node 18+ | `node --version` | nvm ou gerenciador |
| yt-dlp | `yt-dlp --version` | `pip install -U yt-dlp` |
| ffmpeg | `ffmpeg -version` | `apt install ffmpeg` |
| openai (npm) | dentro do projeto | `npm install openai` |
| OPENAI_API_KEY | `echo $OPENAI_API_KEY` | exportar no shell |

## Custos estimados

| Tamanho | Custo total |
|---------|-------------|
| Top 20 reels | ~$0.30 |
| Top 50 reels | ~$0.65 |
| Top 100 reels | ~$1.30 |

## Observacoes

- Rate limit IG (~200 req/h): ao analisar varios perfis em sequencia, aguardar entre eles
- Perfis privados: nao funciona, scraper so pega publicos
- Reels com musica copyright: yt-dlp baixa normal, Whisper transcreve so o audio do criador
- Conteudo PT-BR: acentuacao correta OBRIGATORIA, travessao (em-dash) PROIBIDO no padrao final
- Se o perfil tem menos posts que N, usar o que tem e avisar
