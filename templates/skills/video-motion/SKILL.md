---
name: video-motion
description: Gera vídeos curtos de MOTION GRAPHICS por código (não é edição de cortes nem vídeo gerado por IA) para QUALQUER assunto - filme de produto/SaaS com a interface real em movimento, perfil de atleta, case de cliente, serviço, dados, notícia, aula - no estilo de reels e lançamentos premium (tipografia cinética, contêiner de interface que muda de forma conduzido por cursor, contadores, gráficos se desenhando, radar, linha do tempo com logos, mockup de site, imagem recortada na frente de palavra gigante, vídeo dentro das letras, câmera lenta). Motor próprio sobre HyperFrames (HTML + GSAP -> MP4) que lê um roteiro.json de cenas contadas em BATIDAS e gera imagem e trilha juntas (efeitos sonoros sintetizados, trilha original em código ou faixa fornecida, sidechain, -14 LUFS). Trabalha como um estúdio: marca REAL capturada do site, brief de diretor, tabela de batidas aprovada antes do código, loop de crítica com notas por quadro ANTES do render, 9:16/16:9/1:1 do mesmo roteiro e motion blur. Custo zero de IA. Use quando o usuário pedir: vídeo em motion, motion graphics, reel animado, vídeo de lançamento/produto/SaaS, animação de interface, showreel, "vídeo gerado por código", reels/shorts/stories animados, "transforma esses números em vídeo", HyperFrames, Remotion-like, kinetic typography, ou mandar um vídeo de referência e pedir "um assim". Também faz TUTORIAL NARRADO de sistema ("tutorial de como usar o menu X", "vídeo explicando a tela Y pra equipe"): telas recriadas em HTML a partir do código do app, cursor clicando e a tela respondendo, voz ElevenLabs com tempo por palavra e legenda karaokê (modo `tutorial/`). Também faz HISTÓRIA NARRADA ILUSTRADA estilo canal dark ("você construiu X", "você sobreviveu a Y", curiosidades com personagem animado, voz ElevenLabs): ver historia/LEIAME.md.
---

# /video-motion: estúdio de motion graphics por código

> Saída: MP4 1080x1920 (e/ou 1920x1080, 1080x1080) com trilha mixada. Entrada: `roteiro.json` com cenas de tipos prontos (`cenas.md`) ou cenas livres + material real (prints, logo, fontes, vídeos, música).
> O prompt é 10% do resultado; os outros 90% são o estúdio em volta: regras, marca real, referência, tabela de batidas e revisão em rodadas. Esta skill É esse estúdio.

## Modo HISTÓRIA narrada ilustrada / canal dark (17/11/2026)

Pedido de vídeo narrado de curiosidade/história ("você construiu um X", "você sobreviveu a Y", "faz um igual a esse viral", canal dark):
**não use o motor HyperFrames**. Leia `historia/LEIAME.md` inteiro: fórmula do texto (você + cadeia "Mas... Então... Essa é a..." + fato real
verificado + "Parabéns"), voz com tempo por palavra, personagem ARTICULADO (`ze()`), céu/luz por hora do dia, câmera `cg()` que fixa o chão,
corte chicote entre cenas, HUD, som com cara do lugar e Gemini ouvindo a mix. Modelo de partida: `exemplos/historia-caatinga/` (87 s, aprovado);
o outro exemplo é `exemplos/historia-acude/` (mundo único que se constrói). Render com 2 workers e `nice` (11 min, carga 12): avise antes.

## Modo TUTORIAL de sistema narrado (16/11/2026)

Pedido de tutorial/explicação de uma tela de sistema com voz: **não use o motor HyperFrames**. Leia `tutorial/LEIAME.md` inteiro e
siga: voz primeiro com tempo por palavra (`tutorial/narrar.py`, ElevenLabs), Gemini ouvindo (`tutorial/ouvir.py`), interface
RECRIADA em HTML a partir do código do app (tokens, fonte, componentes reais; dados fictícios), câmera + cursor + cliques que mudam
o estado da tela, marcador amarelo, legenda karaokê, som em código (`tutorial/som.py`) e mixagem com sidechain pela voz
(`tutorial/mix.py`), revisão por folhas (`tutorial/captura.py revisao`) e render com 2 workers e `nice` (4 workers levaram a VPS
a carga 16). Exemplo aprovado pelo dono: `exemplos/tutorial-pendentes/` (reel 64 s, 10 passos).

## Por que funciona

1. **Imagem e som saem dos MESMOS tempos.** `motor/montar.py` calcula das batidas quando cada coisa acontece e com esses tempos escreve a animação (`index.html`) E mixa a trilha (`assets/trilha.wav`). Nunca editar tempos só no HTML: muda o roteiro e roda o motor.
2. **Nada de "um prompt só".** Marca vem do site real, a história é aprovada em tabela de batidas, e o vídeo passa por rodadas de crítica com nota ANTES de gastar render.

## Ferramental (uma vez por máquina)

```bash
bash .claude/skills/video-motion/instalar.sh --com-recorte   # node 22, ffmpeg 7, hyperframes fixo, rembg; tudo em ~/.video-motion
source ~/.video-motion/env.sh                                   # função hf (= npx hyperframes)
```
Não instala nada no sistema (node 20 e ffmpeg 4.4 do Ubuntu 22.04 quebram o hyperframes). Python precisa de Pillow e numpy.

## Processo (siga na ordem)

### 1. Brief de diretor
Preencha `modelos/brief-diretor.md` com o usuário: entradas, **direção** (a linguagem visual em 1 ou 2 frases), estrutura em batidas, construção. Se ele não sabe a direção, pergunte a emoção, a referência e o que o espectador tem que lembrar. Mensagem em uma frase, duração 15 a 45 s.

### 2. Marca real (quando há marca/produto)
```bash
bash .claude/skills/video-motion/capturar_marca.sh https://site.com projeto/     # ~2,5 min
```
Gera `marca.json` (lido sozinho pelo motor: marca, cor, paleta, fontes), `marca.md` e `assets/marca/` (fontes do Google Fonts, prints da página, candidatos a logo). **Mostre o `marca.md` ao usuário e liste o que achou ANTES de animar**; complete o que estiver em "Falta" (logo vetorial, prints das telas logadas via Playwright). O kit fica em `~/.video-motion/marcas/<marca>`: o próximo vídeo da mesma marca reaproveita (`--atualizar` recaptura).
**Nunca redesenhar a interface do produto de imaginação**: recorte e anime o print real (`ui_produto` com `imagem` + `recorte`).

### 3. Referência (opcional, quando o usuário manda um vídeo "assim")
```bash
bash .claude/skills/video-motion/referencia.sh "https://youtube.com/watch?v=..." projeto/ [--de 0:10 --ate 0:40]
```
Baixa pela Apify (~US$0,006/MB), mede o ritmo (cortes/s, plano médio), roda a **perícia de movimento** (`motor/pericia.py`: perfil de energia, amplitude pico/mediana, % do filme em quase-parada, picos; vira as METAS do nosso filme) e gera folhas de quadros. Olhe as folhas e escreva `referencia.md`: **o mecanismo numa frase de espectador** ("o cursor dirige a tela e ela responde"; se não sai a frase, a referência é sequência de cenas, não filme), ritmo, transições, movimento **permitido e PROIBIDO** (a lista de proibidos vale mais), política de câmera (fixa ou quais movimentos), hierarquia de tipo, quantos acentos de cor (os bons têm UM), o que o som marca; **o que adotar e o que NÃO copiar** (conteúdo, marca e textos da referência nunca). Prescreva com restrições, não adjetivos: "limpo" não é instrução, "sem grain, sem vinheta, sem gradiente em texto" é.
Para recriar UM vídeo no nível dele com aprovação card a card, use a skill irmã `motion-por-referencia`.

### 4. Dados e material
Números, datas, nomes: **só dado real com fonte** (cite em `fonte`). Material: prints reais, fotos para recorte, vídeos, logos, música.

### 5. Roteiro e TABELA DE BATIDAS (aprovar antes de qualquer render)
Escolha cenas em `cenas.md`. Produto/SaaS: `titulo` (gancho) -> `ui_produto` (a história do uso em 5 a 10 estados) -> `livre` ou prova -> `assinatura`. Atleta/case: `titulo` -> `destaque` -> 2 a 4 cenas de prova -> `assinatura`.
Som (a música vem ANTES do primeiro tween; a grade de batidas sai dela):
- **Padrão: faixa gerada e MEDIDA.** Higgsfield MCP (`generate_audio`, modelo de música) com a estrutura escrita em segundos no prompt ("0-3 s intro esparsa com riser; 3 s drop; parada de 1 tempo em 11 s; impacto final em 14 s; sem voz"). Gere **3 variações** e escolha por número, não por ouvido: `hf beats` (BPM, onsets) + arco (intro baixa, entrada, cheio, UMA parada, fim limpo sem fade longo); loop chapado reprova. O modelo não obedece BPM com precisão: se o medido estiver a ~3% de um BPM redondo para o fps (30 fps: 120 = 15 quadros por tempo; 112,5 = 16), estique com `ffmpeg -af atempo=<alvo/medido>` e desloque o primeiro tempo 1 para um quadro inteiro. Faixa é matéria-prima: corte e recoloque **compassos inteiros** (no tempo 1, crossfade de 5 ms) para o arco caber no filme. Depois `musica.arquivo` + `bpm`.
- **Trilha original sintetizada** (`musica.sintetizar: true`, `bpm`, `clima`) só quando não pode gastar crédito: começa no tempo forte e não precisa de detecção, mas soa amadora perto de faixa gerada (teto ~6/10 medido no CRClinic).
- Onde cada coisa pousa: a **maior mudança de enquadramento no drop**; troca de cena no tempo 1 de compasso; frase de efeito na parada da música (ou crie a parada); soco final no tempo 1 depois da parada; rajada com durações variadas (1, 1, ½, ½, 1, 2 tempos), nunca todas iguais.
```bash
python3 .claude/skills/video-motion/motor/montar.py projeto/
```
Mostre ao usuário `out/batidas.md`: batida a batida, compasso, cena, o que acontece e o som. Leve a sério os `AVISO` do motor (tempo morto acima de 4 s, cena fora do tempo forte, gancho que só fecha depois de 2 s, cenas iguais seguidas). Ajustar a tabela custa segundos; re-renderizar custa minutos.

### 6. Loop de crítica (OBRIGATÓRIO antes do render)
```bash
bash .claude/skills/video-motion/revisar.sh projeto/          # ~1,5 min para 30 s: 1 quadro por batida, sem render
```
Olhe (Read) `out/revisao/rN/folha-batidas.jpg` (toda batida; faixa laranja = entra cena) e `folha-celular.jpg` (um quadro por compasso **no tamanho de tela de celular**). Preencha a rodada em `out/revisao.md`, nota 1 a 10, dizendo a batida em que se vê:
1. **Gancho** nos 2 primeiros segundos
2. **Leitura no tamanho do celular**
3. **Qualidade do movimento**
4. **Variedade** (algo novo a cada 2 a 4 s, sem padrão de IA)
5. **Fidelidade à marca**
6. **Sincronia com o som**

Corrija os **3 piores**, rode de novo. **Só renderize quando tudo estiver 8 ou mais.** Não mostre vídeo ao usuário antes disso.
**Cada formato tem sua rodada** (`revisar.sh projeto/ --formato 16:9`): o que funciona na vertical quebra na horizontal (no teste, a lâmina de transição ficava presa cobrindo a direita só no 16:9).

### 7. Renderizar e conferir
```bash
bash .claude/skills/video-motion/renderizar.sh projeto/ [--rascunho] [--formato 16:9|1:1|todos] [--motion-blur [4]]
```
Monta, lint, render, folha `out/folha.jpg`, LUFS, **perícia de movimento** (`out/pericia.json`: amplitude, quase-parada, picos e % de cortes a até 2 quadros de uma batida, meta >= 70%; com `referencia/ref.mp4` roda o **TESTE DE ACEITE** contra a referência e avisa se reprovou: diga isso ao entregar, nunca chame de pronto escondendo), versão web (~2,4 Mbps). Cortes duros em PARES colados (ex.: 17,93 e 18,20) = transição que pisca duas vezes: conserte. `--formato todos` faz cada item de `roteiro.formatos` (nomes `<projeto>-16x9.mp4`...). `--motion-blur` renderiza N subquadros e mistura (movimento rápido fica liso como câmera; custa N vezes o render: use no final). Com 4 subquadros, o que cruza a tela em menos de 1 s (lâmina) aparece em 3 a 4 faixas escalonadas: para isso use `--motion-blur 8` a 30 fps (limite 240 fps de render). O render recoloca a `trilha.wav` original no MP4 (o mixer do hyperframes tira ~1,5 dB). Olhe a folha sempre.

### 8. Entregar e guardar
Vídeo + o que é real/fonte de cada dado + o que é só para estudo (direitos de imagem/música de terceiros são do usuário). Se o usuário aprovou, anote no `marca.md` da biblioteca o que funcionou (cena, ritmo, tom) para manter o padrão no próximo vídeo da marca.

## Regras do estúdio (o que separa motion de "vídeo de IA")

**Proibido por padrão:** título centralizado sobre gradiente; tudo entrando com fade; rótulos de canto e molduras sem função; brilho/glow em interface; partículas genéricas; easing que quica; tempo morto.
**Sempre:** uma fonte de título + uma de interface (as da marca); **uma** cor de destaque; algo novo na tela a cada 2 a 4 s; cena nova no tempo forte; movimento com mola de sobra mínima (`mola()` no template) ou freio forte (`power3/4.out`), nunca linear em entrada.
**Material de verdade:** fonte nunca a padrão do modelo (a da marca; sem marca, escolha em Fontshare ou Google Fonts e declare no brief, e confira em TODA cena: o esquecimento mais comum é a fonte sumir na 2a rodada); ícone de biblioteca (LottieFiles em JSON, Flaticon, o SVG oficial) em vez de ícone desenhado de imaginação, e mande 1 ou 2 de exemplo para o resto seguir o estilo. Clipe de modelo de vídeo gerativo (Higgsfield, Seedance, MiniMax) erra letra e número: gere SEM texto e sobreponha o texto certo por código; prompt para esses modelos sempre em inglês técnico.
O motor já aplica: fundo liso (`estilo.fundo: "brilho"` religa os brilhos), sem glow (`estilo.brilho: true` religa), texto medido com a fonte real e encolhido para caber, avisos de ritmo.

**Vertical (9:16) se RECOMPÕE, não se corta:** 12% do topo e 15% de baixo livres de texto e UI crítica (o objeto herói pode invadir); título vira 2 a 3 linhas empilhadas; chips lado a lado viram coluna; movimento horizontal vira vertical (atravessar a tela vira mergulho, fila de cards vira torre com subida de câmera); split-screen vira cima/baixo. Ao entregar os formatos, diga quais batidas ficaram mais fortes em cada um.
**Iterações têm semântica:** "refaz para X" = mantém estilo, estrutura e tempos, troca só marca, texto e assets (diga o que ficou e o que mudou); "muda o estilo" = muda o DNA (easing, tipo de transição, linguagem de render), não só cosmética; "muda a cor" = refaz a paleta como SISTEMA com papéis (fundo, tinta, acento, onde cada uma pode aparecer), nunca recolor; reprovou no aceite = escolher UM soco e aprofundar as paradas, nunca "acelerar tudo".
**Pessoa falando no vídeo (talking head, PIP):** deixe o terço da tela livre para o apresentador e ponha cartão translúcido atrás de texto e logo sobre filmagem (sem ele, some no fundo).

## Skills irmãs (use a certa)

As do Felipe Borges marcadas (manual) não disparam sozinhas (para não roubar pedidos desta skill): o usuário chama com `/nome`, ou você lê `.claude/skills/<nome>/SKILL.md` inteiro e segue.

- Gravação bruta de alguém falando para virar reel (corta silêncio/erros + edita com interface animada): `/reel`.
- Recriar UM vídeo de referência no nível dele, com cards estáticos aprovados antes e aceite numérico: `motion-por-referencia` (manual).
- Showreel/sizzle de marca de 15-60 s no estilo "a interface narra" (chips, galerias de cards, transições T1-T8 com anatomia por quadro em `.claude/skills/showreel-interface/referencias/transicoes.md`): `showreel-interface` (manual).
- Carrossel do Instagram (estático ou vivo): `criador-de-carrosseis-simples`. Prompt para modelo de vídeo por texto (MiniMax e similares): `prompts-de-motion` (manual).

## Regras de qualidade (aprendidas em produção)

1. **Dado real ou nada.** Contador, gráfico e radar só com número de fonte citável.
2. **Recorte de pessoa: local, quadro parado e de frente.** `motor/recortar.py video.mp4 saida.png --tempos 12.0,12.2,13.0`. Pedir "fundo verde" a IA de imagem NÃO funciona com fundo poluído.
3. **Vídeo em cartão vertical recorta o centro**: `alinhamento: "100% 50%"` se o assunto está na lateral. Print em `ui_produto`: `alinhar: "esquerda"` quando o texto do site está à esquerda.
4. **Texto tem que caber**: o motor mede com a fonte real, mas fonte larga (Syne, Clash) encolhe muito: prefira linhas curtas (3 a 14 letras) a uma linha longa pequena.
5. **Nada aleatório no JS** (o render paraleliza em vários navegadores; `Math.random` daria um vídeo por navegador). Nada de CSS transition, setTimeout ou requestAnimationFrame: todo movimento é função do tempo da timeline.
6. **Não anime propriedades de layout** (letterSpacing, width, top) em HTML: use transform/opacity. Forma que muda de tamanho = atributos de `<rect>` SVG (como no `ui_produto`).
7. **Vídeo com data-start não pode ficar dentro de bloco que também tem data-start** (o motor põe vídeos numa camada própria).
8. **Só um .html com data-composition-id na raiz do projeto**; **`<audio>` sem id sai mudo** (o motor usa `id="trilha"`).
9. **Desfoque pesado no navegador é caro**: pré-desfoque vídeos no ffmpeg.
10. **Medir no build, nunca em callback** (o lint avisa `gsap_callback_dom_measurement`): o renderer busca quadros fora de ordem.
11. **Glifos da copy existem na fonte?** Setas (→), checks (✓) e símbolos somem (viram quadrado) no render headless sem fontes de sistema: confira o texto contra a fonte recortada ou troque o símbolo por SVG.

## Custo e tempo (4 núcleos, CPU)

- IA: zero (efeitos e trilha sintetizados, recorte local, gráficos em código). Apify só para baixar referência do YouTube.
- `revisar.sh`: ~1,5 min para 30 s (56 quadros). Render: ~5 min por formato para 30 s; `--motion-blur 4` ~4x.
- Captura de marca: ~2,5 min (uma vez por marca).

## Arquivos

- `motor/montar.py`: roteiro (+ `marca.json`) -> tempos, efeitos, trilha (-14 LUFS, sidechain), `index.html`, `out/batidas.md|json`, avisos de ritmo.
- `motor/template.html`: CSS + renderizador de cada tipo (GSAP, timeline pausada), `mola()`, `ui_produto`, ponte das cenas `livre`.
- `motor/trilha_sintetica.py`: trilha original (bumbo, chimbal, palma, baixo, pad, arpejo) na grade exata.
- `motor/pericia.py`: perícia de movimento (energia, amplitude, quase-parada, picos, % de cortes na batida) e teste de aceite `--contra referencia.mp4`; ideia da skill `motion-por-referencia` do Felipe Borges.
- `motor/folha.py`: folhas do loop de crítica. `motor/marca.py`: captura -> kit de marca. `motor/recortar.py`: recorte local (rembg).
- `revisar.sh` (loop de crítica), `renderizar.sh` (render final), `capturar_marca.sh`, `referencia.sh`, `instalar.sh`.
- `modelos/brief-diretor.md`: brief em 4 blocos. `cenas.md`: todos os tipos e campos.
- `exemplos/`: `perfil-atleta`, `case-site`, `filme-produto` (ui_produto + livre + trilha sintetizada + 9:16/16:9). Mídia não acompanha (a skill só tem texto).
- `historia/`: modo história narrada ilustrada (`LEIAME.md`, `ouvir_mix.py`); exemplos `exemplos/historia-caatinga/` e `exemplos/historia-acude/`.
- `tutorial/`: modo tutorial narrado (`LEIAME.md`, `narrar.py`, `ouvir.py`, `captura.py`, `som.py`, `mix.py`); exemplo `exemplos/tutorial-pendentes/`.

## Cena nova

- **Uma vez só:** use `tipo: "livre"` (JS próprio no projeto, recebendo os tempos das batidas e os sons declarados no roteiro). Veja `cenas.md`.
- **Para reusar:** em `montar.py` calcule os tempos internos (`c["tAlgo"]`), os sons (`ev`, `digitar`) e as ações (`acao`, vão para a tabela); em `template.html` crie `R.novo_tipo = (c, i) => {...}` usando só os tempos de `c`; documente em `cenas.md`; teste com `revisar.sh`.
