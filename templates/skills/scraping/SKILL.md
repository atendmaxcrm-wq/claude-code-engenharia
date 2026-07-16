---
name: scraping
description: Fazer scraping completo de um site (texto + imagens + base de conhecimento). Use ao extrair conteudo de sites.
---

Faca o scraping do seguinte site: $ARGUMENTS

## Passo 1: Perguntar ao usuario o que deseja

ANTES de qualquer acao, use AskUserQuestion para perguntar:

1. **O que extrair?**
   - Tudo (texto + imagens)
   - So textos
   - So imagens

2. **Profundidade do scraping?**
   - So a pagina principal (home)
   - Site inteiro (todas as paginas internas)
   - Paginas especificas (perguntar quais)

3. **Gerar base de conhecimento?**
   - Sim (gerar MD organizado com todo conteudo)
   - Nao (so extrair dados brutos)

4. **Organizar imagens por secao/modelo/produto?**
   - Sim (criar subpastas organizadas e limpar icones/logos)
   - Nao (deixar tudo na pasta images/)

## Passo 2: Executar o scraper

Rode o script Python com Playwright:

```bash
python3 /root/teste-aios/aios-core/apps/monitor-server/src/scripts/site-scraper.py \
  --url "URL_DO_SITE" \
  --output "/root/teste-aios/scraping-output/NOME_DO_SITE" \
  --max-pages 100 \
  --delay 2
```

O script:
- Usa Playwright + Stealth (headless Chromium) para renderizar JS
- Navega por todas as paginas internas automaticamente
- Extrai textos (titulos, headings, paragrafos, meta tags)
- Extrai e baixa todas as imagens
- Salva `content.json` (dados estruturados) + pasta `images/`
- Rate limiting de 2s entre paginas para nao sobrecarregar o servidor

## Passo 3: Se pediu base de conhecimento

Leia o `content.json` completo e gere um arquivo MD seguindo o formato de referencia:
`/root/teste-aios/scraping-output/lavorofoton/base_conhecimento_odontobarra_v2.md`

A base de conhecimento deve conter (adaptar conforme o tipo de negocio):

- Informacoes basicas (nome, endereco, telefone, email, redes sociais, horarios)
- Equipe / Autoridade (fundadores, historia, numeros de autoridade)
- Produtos ou servicos oferecidos (com detalhes tecnicos completos)
- Tecnologia e diferenciais
- Comparativos com concorrentes (se houver)
- Cases de clientes / depoimentos
- Facilidades de pagamento
- Scripts de objecoes (criar baseado no conteudo do site)
- Perguntas frequentes (criar baseado no conteudo do site)
- Biblioteca de gatilhos (autoridade, escassez, prova social, urgencia)
- Frases de impacto (extrair do site)

Salvar como: `base_conhecimento_NOME.md` na pasta de output.

## Passo 4: Se pediu organizar imagens

1. Identificar as categorias/secoes/modelos/produtos do site
2. Criar subpastas em `fotos-por-modelo/` (ou `fotos-por-secao/`)
3. Copiar imagens para as subpastas corretas baseado no prefixo slug
4. **Limpar icones e logos**: Usar MD5 hash para encontrar arquivos repetidos em 3+ pastas (sao icones do template) e remover
5. Remover tambem duplicados menores (<250KB) que aparecem em 2+ pastas
6. Verificar visualmente os arquivos menores restantes e remover icones residuais

## Passo 5: Apresentar resultado

Mostrar ao usuario:
- Quantidade de paginas scrapadas
- Quantidade de imagens baixadas (antes e depois da limpeza)
- Tamanho total do output
- Estrutura de pastas gerada
- Resumo do conteudo da base de conhecimento (se gerada)
- Perguntar se quer ajustar algo

## Notas tecnicas

- O scraper usa `playwright` + `playwright-stealth` (Python, ja instalado)
- Sites renderizados por JS (React, Next.js, etc) sao suportados
- Timeout de 30s por pagina, scroll automatico para lazy loading
- Logs vao para stderr, dados para stdout
- Output fica em `/root/teste-aios/scraping-output/`
- Script: `/root/teste-aios/aios-core/apps/monitor-server/src/scripts/site-scraper.py`
