# Full-Source Recovery — Templates No-Code

Tecnica para recuperar o **codigo-fonte HTML/CSS/JS completo** de sites criados em builders no-code (aura.build, v0.dev, lovable, framer preview, etc).

Funciona porque esses builders armazenam o codigo em tabelas publicas Supabase/Firebase com RLS (Row Level Security) mal configurado OU com policy de leitura publica intencional.

## Quando usar

- Site e SPA vazio (so `<div id="root">`), bundle minificado nao ajuda
- Efeito tem lib propria do builder (tipo `data-us-project` da aura.build)
- Quer o HTML renderizado real, nao a versao JSX que monta ele

## Passo a passo

### 1. Identificar o builder

Pistas no dominio/headers/HTML:

| Builder | Pistas |
|---|---|
| **aura.build** | `.aura.build` no dominio, ou site usa `hoirqrkdgbmvpwutwuwj.supabase.co` |
| **v0.dev** | `.vercel.app` com path especifico ou meta `v0.dev` |
| **lovable** | `.lovable.app`, uso de Supabase proprio |
| **framer** | `.framer.app` ou `.framer.website` |
| **webflow** | `webflow.io` |

### 2. Capturar chamadas de rede

No Playwright MCP:

```javascript
() => performance.getEntriesByType('resource')
  .map(r => r.name)
  .filter(n => /supabase\.co|firebaseio|firestore|shared_code|shared_react|rest\/v1|realtime/i.test(n))
```

Procurar URLs tipo:
- `https://SUPABASE/rest/v1/shared_code?select=*&slug=ilike.NOME-DO-TEMPLATE`
- `https://SUPABASE/rest/v1/rpc/get_public_shared_react_project_by_slug`
- `https://firestore.googleapis.com/v1/projects/PROJETO/databases/(default)/documents/templates/ID`

### 3. Extrair a anon key (Supabase)

Supabase sempre expoe a **anon key** no bundle JS client (e by design). Buscar:

```bash
# Baixar bundle principal do builder
curl -s "https://BUILDER.com/assets/index-XXX.js" -o bundle.js

# Extrair JWTs (formato eyJ.XXX.XXX)
grep -oE 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}' bundle.js | sort -u
```

Decodificar base64 do meio pra confirmar role=anon:

```bash
echo 'eyJhbG...' | cut -d. -f2 | base64 -d 2>/dev/null
# Deve retornar algo tipo: {"iss":"supabase","ref":"XXX","role":"anon",...}
```

### 4. Fazer a query

Com a key:

```bash
ANON="eyJ..."
SLUG="nome-do-template-extraido-da-url"

curl -s "https://SUPABASE/rest/v1/shared_code?select=code&slug=ilike.$SLUG" \
  -H "apikey: $ANON" \
  -H "Authorization: Bearer $ANON" \
  -H "Accept: application/json"
```

Retorno: `[{"code": "<html>...</html>"}]`

### 5. Salvar e grep

```bash
curl ... -o raw.json
python3 -c "import json; d=json.load(open('raw.json')); open('template.html','w').write(d[0]['code'])"
```

Agora grep pra achar o efeito:

```bash
grep -n "shader\|canvas\|spline\|unicorn\|rive\|GSAP\|ScrollTrigger\|three" template.html
```

## Exemplo real: aura.build

- **Anon key** (valida em 2026): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhvaXJxcmtkZ2JtdnB3dXR3dXdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2Nzc2NTAsImV4cCI6MjA1OTI1MzY1MH0._UsCSHsTELn7m54tOhX3ySm67WEhcyHAPbuxEQZsl3c`
- **Supabase host**: `hoirqrkdgbmvpwutwuwj.supabase.co`
- **Tabela principal**: `shared_code`
- **Query**: `?select=code&slug=ilike.NOME-DO-TEMPLATE`
- **Slug**: vem da URL (tipo `https://social-automation-template.aura.build/` → slug `social-automation-template`)

Query direta testada e funcionando:

```bash
curl -s "https://hoirqrkdgbmvpwutwuwj.supabase.co/rest/v1/shared_code?select=code&slug=ilike.social-automation-template" \
  -H "apikey: eyJ...(acima)" \
  -H "Authorization: Bearer eyJ...(acima)"
```

Retorna HTML completo (~116kb) com o template inteiro, incluindo:
- Tags de Tailwind compilado
- Scripts externos (UnicornStudio, Lucide, Tailwind runtime)
- `<div data-us-project="ID">` com o project ID do efeito

## Cuidados eticos/legais

- Codigo **publicamente acessivel** via anon key publica = assumido pelo builder como disponivel
- Usar pra **inspiracao tecnica** (saber QUE ferramenta foi usada, COMO foi estruturado)
- **Nao copiar assets proprietarios** (imagens, logos, copy da empresa dona do template)
- Se o template e pago (ex: templates "Paid" da aura), comprar se for usar em producao
- Skills similares exploram o mesmo vetor: esta documentado em labs de seguranca desde 2022 como "supabase anon key misconfig"

## Outras fontes nao-Supabase

| Padrao | Como extrair |
|---|---|
| Firebase Firestore | `curl https://firestore.googleapis.com/v1/projects/XXX/databases/(default)/documents/YYY` |
| Sanity.io | `https://PROJECT.api.sanity.io/v1/data/query/DATASET?query=*` |
| Contentful | Geralmente requer token, mas aparece em headers |
| Static JSON na CDN | `/api/data.json`, `/static/content.json` |
| GraphQL publico | POST em `/graphql` com introspection query |

## Checklist rapido

- [ ] Site e SPA (HTML so tem `<div id="root">`)?
- [ ] Network mostra chamadas pra Supabase/Firebase/API com slug?
- [ ] Anon key no bundle JS do builder?
- [ ] Query retorna `code` com HTML completo?
- [ ] Grep no HTML revela `data-*-project` ou lib black-box?
