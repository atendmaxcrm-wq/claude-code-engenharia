---
name: notebooklm
description: Controla o Google NotebookLM pela linha de comando (biblioteca nao oficial notebooklm-py) - cria notebooks, adiciona fontes (URL, PDF, YouTube, Drive), pergunta ao notebook e gera artefatos (podcast, video, quiz, flashcards, relatorio, mind map, infografico, slides) com download local. Use quando o usuario pedir "joga no NotebookLM", "gera um podcast desses videos/artigos", "faz quiz/flashcards/resumo dessas fontes", ou para estudar um material grande. Combina com yt-search para levantar as fontes.
---

# NotebookLM Skill

## O que faz
Controla o Google NotebookLM programaticamente via CLI. Cria notebooks, adiciona fontes (URLs, PDFs, vídeos YouTube), gera artefatos (podcasts, vídeos, quizzes, relatórios, mind maps, infográficos, slides) e faz download.

> Biblioteca NAO oficial (https://github.com/teng-lin/notebooklm-py, MIT): usa APIs internas do
> Google, que podem mudar sem aviso, e tem limite de uso. Bom para pesquisa e uso pessoal.

## Setup (uma vez por maquina)
```bash
python3 -m venv ~/.venvs/notebooklm
~/.venvs/notebooklm/bin/pip install "notebooklm-py[browser]"
~/.venvs/notebooklm/bin/playwright install chromium   # o login abre um navegador
source ~/.venvs/notebooklm/bin/activate               # depois disso o comando e `notebooklm`
notebooklm login     # abre o navegador, salva a sessao em ~/.notebooklm/storage_state.json
```
- `~/.notebooklm/` guarda os cookies da conta Google: NUNCA commitar nem copiar para o repo.
- Em servidor sem tela, faca o `login` numa maquina com navegador e copie o `storage_state.json`
  (ou passe `--storage <arquivo>` em cada comando).
- Se `notebooklm` nao for encontrado, ative o venv (ou chame `~/.venvs/notebooklm/bin/notebooklm`).

## Pipeline típico
```bash
# 1. Criar notebook
notebooklm create "Pesquisa Semanal"

# 2. Adicionar fontes
notebooklm source add "https://youtube.com/watch?v=..."
notebooklm source add "./artigo.pdf"
notebooklm source add "https://blog.example.com/post"

# 3. Aguardar indexação
notebooklm source list  # verificar status

# 4. Gerar podcast
notebooklm generate audio "podcast conversacional em português sobre os temas"

# 5. Aguardar (10-20 min)
notebooklm artifact list  # verificar status
notebooklm artifact wait <id>

# 6. Download
notebooklm download audio ./podcast.mp3
```

## Formatos de saída
| Tipo | Tempo | Formato |
|------|-------|---------|
| Podcast | 10-20 min | MP3 |
| Vídeo | 15-45 min | MP4 |
| Quiz | 5-15 min | JSON/MD/HTML |
| Flashcards | 5-15 min | JSON/MD |
| Relatório | 5-15 min | MD/PDF |
| Mind Map | Instantâneo | JSON |
| Infográfico | 10-20 min | PNG |
| Slide Deck | 10-20 min | PPTX |

## Integração com yt-search
```bash
# 1. Buscar vídeos relevantes
python3 .claude/skills/yt-search/scripts/search.py marketing médico --count 5

# 2. Pegar URLs dos resultados
# 3. Adicionar como fontes no NotebookLM
notebooklm source add "https://youtube.com/watch?v=ABC123"

# 4. Gerar podcast a partir dos vídeos
notebooklm generate audio "resumo conversacional dos vídeos"
```

## Custo
Gratuito (Google NotebookLM). Apenas precisa de conta Google autenticada.
