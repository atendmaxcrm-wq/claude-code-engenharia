---
name: yt-search
description: Busca videos no YouTube pelo terminal e devolve lista estruturada (titulo, canal, views, duracao, data, URL), com filtro de recencia. Usa yt-dlp quando instalado e cai para scraping HTTP da pagina de busca sem ele, sem API key. Use quando o usuario pedir "busca no YouTube", "acha videos sobre X", "quais videos recentes falam de Y", ou para levantar fontes antes de jogar no NotebookLM (skill notebooklm).
---

# yt-search - busca no YouTube sem API key

## Como rodar

O script mora DENTRO desta skill. Rode a partir da raiz do projeto:

```bash
python3 .claude/skills/yt-search/scripts/search.py <consulta> [--count N] [--months N] [--no-date-filter]
```

| Flag | Default | Efeito |
|------|---------|--------|
| `--count N` | 20 | quantos resultados mostrar |
| `--months N` | 6 | descarta video mais velho que N meses |
| `--no-date-filter` | - | nao filtra por data |

Exemplo: `python3 .claude/skills/yt-search/scripts/search.py marketing para clinicas --count 5 --months 3`

## Backends

1. **yt-dlp** (preferido, metadado mais rico). Instalar com `pip install yt-dlp` se quiser.
2. **Scraping HTTP** (fallback automatico): le o `ytInitialData` da pagina de resultados. Funciona sem
   nada instalado alem do Python 3, mas quebra se o YouTube mudar o HTML; nesse caso instale o yt-dlp.

## Saida

Lista numerada com titulo, canal, visualizacoes, duracao, data e URL. Apresente o resultado direto ao
usuario. Se o script der erro, explique a mensagem e sugira o conserto (instalar yt-dlp, afrouxar
`--months`, trocar a consulta).

## Combina com

- **notebooklm**: pegue as URLs dos melhores resultados e use como fontes de um notebook
  (`notebooklm source add <url>`) para gerar resumo, podcast ou quiz.
