---
name: video-motion
description: Gera vídeos curtos de MOTION GRAPHICS por código (não é edição de cortes nem vídeo gerado por IA) para QUALQUER assunto - perfil de atleta, case de cliente, produto, serviço, dados, notícia, aula - no estilo de reels premium (tipografia cinética, contadores, gráficos se desenhando, radar, linha do tempo com logos, mockup de site em celular, imagem recortada na frente de palavra gigante com paralaxe, vídeo dentro das letras, congelamento com anel de destaque, câmera lenta). Motor próprio sobre HyperFrames (HTML + GSAP -> MP4) que lê um roteiro.json de cenas contadas em BATIDAS da música e gera imagem e trilha juntas: som de teclado por letra, riser, grave, whoosh com pan, impactos, música abaixando sob os efeitos (sidechain) e volume final a -14 LUFS. Renderiza no próprio servidor, custo zero de IA. Use quando o usuário pedir: vídeo em motion, reel animado, motion graphics, animação com dados, "vídeo gerado por código", reels/shorts/stories animados, vídeo de apresentação de jogador/produto/case, "transforma esses números em vídeo", HyperFrames, Remotion-like, kinetic typography.
---

# /video-motion: reels de motion graphics por código

> Saída: MP4 vertical 1080x1920 (30 ou 60 fps) com trilha mixada. Entrada: um `roteiro.json` com cenas de tipos prontos (`cenas.md`) + material (imagens, vídeos, logos, música). O mesmo motor serve para qualquer assunto: só o roteiro muda.

## Por que funciona (a regra que sustenta a skill)

**Imagem e som saem dos MESMOS tempos.** O `motor/montar.py` calcula, a partir das batidas, quando cada palavra entra, cada número conta e cada letra é digitada; com esses tempos ele escreve a animação (`index.html`) E mixa a trilha (`assets/trilha.wav`). Nunca editar tempos só no HTML: muda o roteiro e roda o motor de novo.

## Ferramental (uma vez por máquina)

```bash
bash ~/.claude/skills/video-motion/instalar.sh --com-recorte   # node 22, ffmpeg 7, hyperframes fixo, rembg; tudo em ~/.video-motion
source ~/.video-motion/env.sh                                   # deixa disponível a função hf (= npx hyperframes)
```
Não instala nada no sistema. Motivos (Ubuntu 22.04): node do sistema costuma ser 20 (hyperframes pede 22), ffmpeg 4.4 quebra a mixagem de áudio (`setts=duration`), falta `unzip` para o hyperframes baixar o Chrome (usa o headless shell do Playwright se existir).

## Processo (siga na ordem)

### 1. Entender o assunto e levantar DADOS REAIS
- Qual a mensagem em uma frase? Quem assiste? Duração alvo (25 a 45 s).
- Números, datas, nomes, logos: **só dado real com fonte** (cite a fonte na cena `assinatura` ou em `fonte`). Nunca inventar estatística para encher um contador; se o dado é fraco, use outro tipo de cena.
- Material: fotos (para recorte), vídeos (lances, telas gravadas, b-roll), prints (mockup), logos/ícones, música.

### 2. Montar o roteiro (rascunho de cenas)
Escolha 6 a 10 cenas em `cenas.md`. Estrutura que funciona:
`titulo` (gancho) -> `destaque` (quem/o quê) -> 2 a 4 cenas de prova (`grafico_linha`, `linha_tempo`, `radar`/`barras`, `numeros`, `mockup`, `video_palavras`, `texto_video`) -> `assinatura`.
Alterne densidade: cena cheia de dado, depois cena de impacto (vídeo, palavra grande).

### 3. Detectar a batida e escrever o roteiro.json
```bash
mkdir -p projeto/assets && cp musica.mp3 projeto/assets/
# crie um index.html mínimo só com <audio id="m" data-timeline-role="music" src="assets/musica.mp3"> OU use o bpm conhecido
hf beats projeto        # -> beats/assets/musica.mp3.json com bpm
```
Preencha `musica.bpm` e `musica.inicio` (um segundo de batida forte). Trap/hip-hop: o hyperframes costuma dar metade do tempo (ex.: 80) -> use `subdivisao: 2`.

### 4. Mostrar a TABELA DE CENAS ao usuário antes de renderizar
Rode só o motor (`python3 ~/.claude/skills/video-motion/motor/montar.py projeto`): ele imprime cena, início e batidas. Mostre essa tabela + os dados usados. Render custa minutos; ajuste antes.

### 5. Renderizar e CONFERIR
```bash
bash ~/.claude/skills/video-motion/renderizar.sh projeto            # final
bash ~/.claude/skills/video-motion/renderizar.sh projeto --rascunho # rápido, para ajustar
```
O script monta, roda o lint (para no 1º ERRO), renderiza com prioridade baixa, gera `out/folha.jpg` (1 quadro/s), mede o volume e cria `out/<nome>-web.mp4` (~2,4 Mbps, cabe em 15 MB para ~45 s).
**Olhe a folha de quadros sempre** (Read na imagem). Procure: texto estourando a largura, elemento encobrindo outro, cena vazia, quadro errado em vídeo. Extraia quadros pontuais com `ffmpeg -ss T -i out/x.mp4 -frames:v 1 q.png` para conferir de perto.

### 6. Entregar
Vídeo (ou página com `<video>`) + o que é real/fonte de cada dado + o que foi usado só para estudo (direitos de imagem/música de terceiros são decisão do usuário).

## Regras de qualidade (aprendidas em produção)

1. **Dado real ou nada.** Contador, gráfico e radar só com número de fonte citável.
2. **Recorte de pessoa: local, quadro parado e de frente.** `motor/recortar.py video.mp4 saida.png --tempos 12.0,12.2,13.0` testa vários instantes; braço borrado de movimento sai cortado. Pedir "fundo verde" a IA de imagem NÃO funciona com fundo poluído (torcida, multidão).
3. **Vídeo em cartão vertical recorta o centro.** Se o assunto está na lateral, use `alinhamento: "100% 50%"`. Anel de destaque: marque x/y olhando o quadro congelado com grade (as coordenadas são do cartão 948x1180 depois do recorte).
4. **Texto gigante tem que caber:** `palavra` longa diminui sozinha, mas confira; `texto_video` com 3 a 5 letras.
5. **Nada aleatório no JS** (tremida e grão usam sequências fixas): o render paraleliza em vários navegadores e `Math.random` faria cada um ver um vídeo diferente.
6. **Não anime propriedades de layout** (letterSpacing, width, top): travam no render quadro a quadro; use transform (x, y, scale) e opacity.
7. **Vídeo com data-start não pode ficar dentro de bloco que também tem data-start** (o motor já põe os vídeos numa camada própria). Se escrever cena nova, siga o padrão.
8. **Só um .html com data-composition-id na raiz do projeto** (outro html na raiz vira 2ª composição e duplica o áudio).
9. **`<audio>` sem id sai mudo** (o motor já usa `id="trilha"`).
10. **Desfoque pesado no navegador é caro**: pré-desfoque vídeos no ffmpeg.

## Custo e tempo

- IA: zero (efeitos sonoros sintetizados no ffmpeg, recorte local, gráficos em código).
- Render (4 núcleos, CPU): ~6 min para 45 s em 1080x1920 (30 ou 60 fps; a captura do navegador domina). `--rascunho` corta bastante.
- Telemetria do hyperframes desligada no env.sh.

## Arquivos

- `motor/montar.py`: roteiro -> tempos, efeitos sonoros, trilha mixada (-14 LUFS, sidechain), index.html.
- `motor/template.html`: CSS + renderizador de cada tipo de cena (GSAP, timeline pausada).
- `motor/recortar.py`: recorte local (rembg) de foto ou quadros de vídeo.
- Fontes (Inter Tight, JetBrains Mono, licença OFL) e GSAP são baixados pelo `instalar.sh`; a skill só tem texto.
- `instalar.sh` / `renderizar.sh`: ferramental isolado e pipeline de render + conferência.
- `cenas.md`: todos os tipos de cena e campos.
- `exemplos/`: `perfil-atleta` (todos os tipos de dados + vídeos) e `case-site` (mockup + barras). Os arquivos de mídia não acompanham a skill; o README de cada exemplo diz o que colocar em `assets/`.

## Adicionando um tipo de cena

1. Em `montar.py`: calcule os tempos internos (`c["tAlgo"]`) e os eventos de som (`ev`, `digitar`) no bloco da agenda.
2. Em `template.html`: crie `R.novo_tipo = (c, i) => {...}` usando só os tempos de `c` (nunca recalcule no JS).
3. Documente em `cenas.md` e teste com `--rascunho` + folha de quadros.
