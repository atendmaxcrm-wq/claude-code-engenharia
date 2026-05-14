# 06 - Veo 3.1 API (REST canonico + payloads)

Endpoint REST oficial do Veo 3.1 via Google AI Studio (Gemini API). Cobre text-to-video, image-to-video com `bytesBase64Encoded` (validado nesta VPS em 2026-05-13), parametros aceitos, polling, pricing 2026, rate limits, error handling e script bash pronto para shell.

Fontes oficiais:
- https://ai.google.dev/gemini-api/docs/video
- https://ai.google.dev/api/generate-content#video
- https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos
- https://ai.google.dev/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits

## Endpoint canonico

```
POST https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning
```

Autenticacao:

- Via query string: `?key=$GOOGLE_API_KEY` (testado e funciona neste projeto)
- Via header: `x-goog-api-key: $GOOGLE_API_KEY`

Testar query string primeiro. Se setup recusar (algumas org policies bloqueiam key em URL), trocar para header.

## Modelos disponiveis

| Model id | Velocidade | Preco | Quando usar |
|----------|------------|-------|-------------|
| `veo-3.1-generate-preview` | Standard (~60-120s) | $0.40/s gerado | Hero final do cliente, qualidade max |
| `veo-3.1-fast-generate-preview` | Fast (~30-50s) | $0.10/s gerado | Iteracao, 80% da qualidade por 25% do preco |
| `veo-3.1-lite-preview` | Mais rapido | $0.05/s | Drafts, vibe check |

`fast` e o sweet spot para production de hero: rapido o bastante para iterar, qualidade indistinguivel do standard em 16:9 720p.

## Payload text-to-video

```json
{
  "instances": [
    {
      "prompt": "Slow cinematic push-in on a MacBook Pro on a walnut desk, screen showing a minimal SaaS dashboard. North-facing studio light, 35mm anamorphic lens, subtle film grain, teal-orange grade. Less than 5% scale change."
    }
  ],
  "parameters": {
    "aspectRatio": "16:9",
    "durationSeconds": "8",
    "resolution": "720p",
    "negativePrompt": "no text overlays, no captions, no UI flickering, no warped geometry",
    "seed": 1337,
    "personGeneration": "allow"
  }
}
```

## Payload image-to-video (validado 2026-05-13)

```json
{
  "instances": [
    {
      "prompt": "Very slow push-in, less than 5% scale change. Static screen content. North-facing light, 35mm lens, shallow depth of field, subtle film grain.",
      "image": {
        "bytesBase64Encoded": "<base64 string of JPEG/PNG>",
        "mimeType": "image/jpeg"
      }
    }
  ],
  "parameters": {
    "aspectRatio": "16:9",
    "durationSeconds": "8",
    "resolution": "720p",
    "negativePrompt": "no UI distortion, no fingers, no text changing"
  }
}
```

Notas validadas hoje:

- O campo correto e `image.bytesBase64Encoded` + `image.mimeType`. NAO usar `inlineData` (retorna 400 "isn't supported by this model").
- `durationSeconds` aceita string `"4"`, `"6"` ou `"8"`.
- `aspectRatio`: `"16:9"`, `"9:16"`, `"1:1"`.
- `resolution`: `"720p"`, `"1080p"`. Preview pode aceitar `"4k"` em standard.

## Parametros aceitos (lista completa)

| Campo | Tipo | Valores | Default |
|-------|------|---------|---------|
| `aspectRatio` | string | `16:9`, `9:16`, `1:1` | `16:9` |
| `durationSeconds` | string | `4`, `6`, `8` | `8` |
| `resolution` | string | `720p`, `1080p`, `4k` (standard) | `720p` |
| `negativePrompt` | string | texto | vazio |
| `seed` | integer | qualquer int positivo | random |
| `personGeneration` | string | `allow`, `disallow` | `allow` |
| `enhancePrompt` | bool | true/false | true |

`enhancePrompt: true` deixa Google reescrever seu prompt internamente. Desligar com `false` se voce ja escreveu prompt cuidadoso e nao quer interferencia.

## Polling (operation pattern)

Veo e `predictLongRunning`. POST retorna uma operation, voce faz GET ate `done: true`.

```
POST .../veo-3.1-fast-generate-preview:predictLongRunning?key=$KEY
{ ... payload ... }
```

Resposta inicial:

```json
{
  "name": "models/veo-3.1-fast-generate-preview/operations/abc123xyz"
}
```

Polling:

```
GET https://generativelanguage.googleapis.com/v1beta/<operation-name>?key=$KEY
```

Quando pronto:

```json
{
  "name": "models/.../operations/abc123xyz",
  "done": true,
  "response": {
    "generateVideoResponse": {
      "generatedSamples": [
        {
          "video": {
            "uri": "https://generativelanguage.googleapis.com/v1beta/files/.../download:download"
          }
        }
      ]
    }
  }
}
```

Download do video: appendar `&key=$KEY` na URI:

```
GET <video.uri>?alt=media&key=$KEY
```

Salvar como `.mp4`.

## Loop de polling em JS

```js
async function pollOperation(name, apiKey, intervalMs = 5000, timeoutMs = 600000) {
  const url = `https://generativelanguage.googleapis.com/v1beta/${name}?key=${apiKey}`;
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`poll ${r.status}: ${await r.text()}`);
    const data = await r.json();
    if (data.done) return data;
    await new Promise((res) => setTimeout(res, intervalMs));
  }
  throw new Error('polling timeout');
}
```

## Cliente Node completo (image-to-video)

```js
// scripts/veo/image-to-video.js
const fs = require('fs');
const path = require('path');

const API = 'https://generativelanguage.googleapis.com/v1beta';
const MODEL = 'veo-3.1-fast-generate-preview';
const KEY = process.env.GOOGLE_API_KEY;
if (!KEY) throw new Error('GOOGLE_API_KEY missing');

async function generate({ imagePath, prompt, negativePrompt, seed, out }) {
  const bytes = fs.readFileSync(imagePath).toString('base64');
  const mimeType = imagePath.endsWith('.png') ? 'image/png' : 'image/jpeg';

  const payload = {
    instances: [{ prompt, image: { bytesBase64Encoded: bytes, mimeType } }],
    parameters: {
      aspectRatio: '16:9',
      durationSeconds: '8',
      resolution: '720p',
      negativePrompt: negativePrompt || '',
      ...(seed ? { seed } : {}),
    },
  };

  const start = await fetch(`${API}/models/${MODEL}:predictLongRunning?key=${KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!start.ok) throw new Error(`start ${start.status}: ${await start.text()}`);
  const { name } = await start.json();
  console.log('operation:', name);

  // poll
  let done = null;
  for (let i = 0; i < 120; i++) {
    await new Promise((r) => setTimeout(r, 5000));
    const r = await fetch(`${API}/${name}?key=${KEY}`);
    const data = await r.json();
    if (data.done) {
      done = data;
      break;
    }
    process.stdout.write('.');
  }
  if (!done) throw new Error('polling timeout');
  console.log('\ndone');

  const uri = done.response.generateVideoResponse.generatedSamples[0].video.uri;
  const dl = await fetch(`${uri}&key=${KEY}`);
  if (!dl.ok) throw new Error(`download ${dl.status}`);
  const buf = Buffer.from(await dl.arrayBuffer());
  fs.writeFileSync(out, buf);
  console.log('saved:', out, `(${(buf.length / 1024 / 1024).toFixed(1)} MB)`);
}

generate({
  imagePath: process.argv[2],
  prompt: process.argv[3],
  negativePrompt: 'no text overlays, no UI flickering, no warped geometry',
  out: process.argv[4] || 'out.mp4',
}).catch((e) => {
  console.error(e);
  process.exit(1);
});
```

Uso: `node image-to-video.js hero.jpg "Slow push-in..." out.mp4`.

## Script bash canonico

```bash
#!/usr/bin/env bash
# scripts/veo/image-to-video.sh
set -euo pipefail

: "${GOOGLE_API_KEY:?need GOOGLE_API_KEY}"
IMAGE="${1:?usage: $0 image.jpg \"prompt\" out.mp4}"
PROMPT="${2}"
OUT="${3:-out.mp4}"
MODEL="${MODEL:-veo-3.1-fast-generate-preview}"
API="https://generativelanguage.googleapis.com/v1beta"

BYTES=$(base64 -w0 "$IMAGE")
MIME=$(file --mime-type -b "$IMAGE")

PAYLOAD=$(jq -nc \
  --arg p "$PROMPT" \
  --arg b "$BYTES" \
  --arg m "$MIME" \
  '{
    instances: [{
      prompt: $p,
      image: { bytesBase64Encoded: $b, mimeType: $m }
    }],
    parameters: {
      aspectRatio: "16:9",
      durationSeconds: "8",
      resolution: "720p",
      negativePrompt: "no text overlays, no captions, no warped geometry"
    }
  }')

OP=$(curl -sS -X POST \
  "$API/models/$MODEL:predictLongRunning?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq -r '.name')

echo "operation: $OP"

for i in $(seq 1 120); do
  sleep 5
  RES=$(curl -sS "$API/$OP?key=$GOOGLE_API_KEY")
  DONE=$(echo "$RES" | jq -r '.done // false')
  if [ "$DONE" = "true" ]; then
    URI=$(echo "$RES" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "downloading: $URI"
    curl -sS "$URI&key=$GOOGLE_API_KEY" -o "$OUT"
    echo "saved: $OUT"
    exit 0
  fi
  printf '.'
done
echo "polling timeout"
exit 1
```

Uso: `./image-to-video.sh hero.jpg "Slow push-in..." out.mp4`.

## Pricing (2026)

| Modelo | $/segundo gerado |
|--------|------------------|
| `veo-3.1-lite-preview` | $0.05 |
| `veo-3.1-fast-generate-preview` | $0.10 |
| `veo-3.1-generate-preview` (720p) | $0.40 |
| `veo-3.1-generate-preview` (1080p) | $0.50 |
| `veo-3.1-generate-preview` (4k) | $0.60 |

Hero de 8s em fast: $0.80. Mesmo hero em standard 1080p: $4.00. Para production iterativa, fast paga a conta.

## Rate limits

| Tier | RPM | Notas |
|------|-----|-------|
| Free / preview | 10 | Para POC, validacao |
| Production | 50 | Apos billing ativado |
| Enterprise | 200+ | Pedir aumento via console |

`predictLongRunning` so consome quota no POST inicial. Polling GET nao conta para RPM.

## Error handling

| HTTP | Causa | Acao |
|------|-------|------|
| 400 | `inlineData` em vez de `bytesBase64Encoded` | Trocar campo do payload |
| 400 | `mimeType` invalido | Usar `image/jpeg` ou `image/png` |
| 400 | `durationSeconds` invalido | So 4, 6 ou 8 |
| 401 | API key invalida ou ausente | Checar `$GOOGLE_API_KEY` |
| 403 | Quota da API video desativada | Ativar Generative Language API no console |
| 429 | Rate limit | Backoff exponencial (1s, 2s, 4s, 8s, 16s) |
| 500/503 | Backend transient | Retry com mesmo payload |
| `done: true` + error | Operacao concluida com erro | Ler `error.message` no response |

## Backoff exponencial recomendado

```js
async function withBackoff(fn, max = 5) {
  for (let i = 0; i < max; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === max - 1) throw e;
      const wait = Math.pow(2, i) * 1000;
      console.warn(`retry ${i + 1} after ${wait}ms:`, e.message);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
}
```

## Files API (imagens > 20MB)

Image-to-video inline limita em ~20MB de payload. Acima disso, subir via Files API e referenciar por `fileUri`.

```bash
# upload
curl -sS -X POST \
  "https://generativelanguage.googleapis.com/upload/v1beta/files?key=$GOOGLE_API_KEY" \
  -H "X-Goog-Upload-Protocol: raw" \
  -H "Content-Type: image/jpeg" \
  --data-binary @big.jpg
# resposta tras file.uri

# usar no payload em vez de bytesBase64Encoded
# image: { fileUri: "files/xxx" }
```

Raramente necessario - sharp resize para 1920px ja cabe inline.

## Anti-pattern

```json
SLOP: { "instances": [{ "image": { "inlineData": { "data": "...", "mimeType": "image/jpeg" } } }] }
```

Retorna 400 "isn't supported by this model". Veo 3.1 quer `bytesBase64Encoded`.

```json
SIGNAL: { "instances": [{ "image": { "bytesBase64Encoded": "...", "mimeType": "image/jpeg" } }] }
```
