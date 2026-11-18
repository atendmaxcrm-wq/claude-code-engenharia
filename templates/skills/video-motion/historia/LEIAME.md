# Modo HISTÓRIA narrada ilustrada (canal dark, "você construiu X", "você sobreviveu a Y")

Feito em 17/11/2026 a partir de 2 virais de referência que o dono mandou:
- "Você construiu uma super colônia de formigas" (Canteiro Lab, Shorts, 1 mi de views): 3D low-poly, subsolo em corte, câmera sempre andando, legenda 1 palavra por vez com o NOME DA PEÇA em amarelo, etiquetas pílula com ponto vermelho.
- "Sobrevivendo 1 Ano Trancado num Bunker" (Leo no Fim do Mundo, 13 min): 2D vetorial chapado, bonequinho de capacete, corte do subsolo, ícones, mostradores, mapa, troca de quadro a cada ~1 s.

Dois filmes feitos e aprovados pelo dono ("gostei demais"), com exemplos completos em `../exemplos/`:
- `historia-acude/`: "Você construiu um açude no sertão" (85 s). Um MUNDO único em corte que vai se construindo; boneco de palito com poses.
- `historia-caatinga/`: "Você sobreviveu à caatinga" (87 s). 12 CENAS com câmera própria, corte chicote, personagem ARTICULADO, luz por hora do dia, noite com lanterna, HUD. **É o modelo de partida** (melhor animação).

Não usa o motor HyperFrames: é o método sem framework (`render(t)` em canvas + Playwright + FFmpeg), igual ao modo tutorial. Reusa `../tutorial/narrar.py`, `mix.py`, `captura.py`.

## A fórmula da história (o que prende)

1. **Abre com o "você" no meio do problema** (0-3 s): "Se você enterrar uma rainha...", "Seu carro quebrou no meio da caatinga".
2. **Cadeia problema -> solução -> nome**: "Mas [problema]. Então [solução]. Essa é a [peça]." 6 a 9 elos. Cada elo = uma cena nova = algo novo na tela a cada 2-4 s.
3. **Virada com fato real**: "Parece loucura/exagero, mas..." + fato curioso VERIFICADO (cidade submersa pelo Castanhão; umbu = "árvore que dá de beber" em tupi).
4. **Fecho**: "Parabéns, você construiu/sobreviveu a X" + confete/título.
5. Variante survival (bunker): marcadores de tempo ("Dia 1", "5h", "Dia 197") e HUD com recurso esvaziando (água, comida, ar).
6. **Fatos: só com fonte.** Pesquise antes de escrever (WebSearch) e guarde as fontes; nada de "dica de sobrevivência" inventada. Escreva números por extenso.

## Pipeline (ordem, ~2 h por vídeo)

1. **Referência** (se vier link): metadados + legenda pela Apify `streamers/youtube-scraper` (`downloadSubtitles`); vídeo pelo `streamers/youtube-video-downloader` em 480p. GOTCHA: link `youtube.com/shorts/ID` FALHA no downloader; use `watch?v=ID`. Folha de quadros (`ffmpeg fps=1/3,tile`) e LER as imagens. A legenda dá a fórmula do texto.
2. **Roteiro** `narracao.txt` (1 bloco por linha; o " ... " entre linhas vira respiro). Conte os caracteres ANTES (ElevenLabs free = 10.000/mês; ~1.250 caracteres = ~85 s). Confira o saldo: `GET /v1/user/subscription`.
3. **Voz**: `python3 ../tutorial/narrar.py narracao.txt` (George `eleven_v4`, palavras com tempo em `assets/palavras.js`). Gemini ouve (`../tutorial/ouvir.py`): nomes regionais saem marcados ("caatinga", "cangaceiros"); voz brasileira só no plano pago.
4. **Tempos**: imprima `palavra@tempo` (+0,4 s de atraso) e ancore TODA ação numa palavra (`W('palavra', n)`). Blocos `L[i]` = primeira palavra de cada linha = troca de cena.
5. **Filme** (`filme.html`, copie `exemplos/historia-caatinga/` e troque as cenas). Peças prontas lá dentro:
   - `ze(t, x, y, pose, dir, sombra)`: personagem articulado (membros em 2 segmentos com contorno, pose por ÂNGULOS: `qF/jF/qT/jT` pernas, `oF/cF/oT/cT` braços a partir de "para baixo" = 0, `inc`, `alt`, `cab`; rosto: `boca` neutra/sorriso/O/aberta/careta/triste, `sob`, `olho`, `arregala`, `fecha`, `suor`; `prop` = objeto na mão). `anda(fase)` dá o ciclo de caminhada (fase = x/22 para o pé não patinar).
   - `ceu(hr)` + `luz(hr)`: céu, sol, lua, estrelas e tinta multiply pela HORA DO DIA (meio-dia estourado, amanhecer rosa, pôr do sol, noite). Time-lapse = animar `hr`.
   - Noite com lanterna: buffer escuro + `destination-out` em cone (ver cena 8).
   - `cg(t, x, s, dy, chao)`: câmera que põe o CHÃO numa altura fixa da tela (padrão 1280): sem isso a ação fica no terço de cima e sobra areia vazia.
   - Corte chicote entre cenas (`render`): as duas cenas desenhadas em buffers e deslizadas com rastro. Custa 2 cenas por quadro na transição.
   - `hud(t)` ("DIA N" + garrafa %), `pilula()`/`tag()` (etiqueta com ponto vermelho, `chave` = palavra amarela grande), `cartao()` (card que sobe com mola), `legenda()` (1 palavra por vez, palavras-chave amarelas).
   - Cenário: `arvoreBranca` (caatinga seca, galhos recursivos), `juazeiro`, `umbuzeiro` (com raízes e batatas enchendo de água), `mandacaru`, `xiquexique`, `macambira`, `coroa`, `pedra`, `carro`, `casa` com fumaça, `serraFundo` (paralaxe), `corte` (subsolo em camadas).
   - Do açude (`exemplos/historia-acude/`): barragem em camadas que caem com poeira, blocos socados, pedras caindo uma a uma, água com ondas/brilhos/pingos/spray, bode, pássaros, carrinho de mão, poses de trabalho (cava, pilão, carrinho, gira volante).
6. **Revisão por folha** (`TOTAL=.. WORKERS=2 nice -n 15 python3 captura.py revisao rN`, ~40 s) + 4 quadros no tamanho real (`hstack=4`). Olhe: chão na altura certa, personagem grande (>= 1/6 da tela), nada no topo 12%/base 15% crítico, etiqueta legível no celular (>= 44 px).
7. **Som** (`som.py` do exemplo): trilha em código com cara do lugar (baião = zabumba/triângulo/sanfona no açude; viola caipira + cigarras de dia + grilos à noite + batida de coração na tensão na caatinga) e um efeito por ação, nos mesmos tempos. `python3 mix.py <dur>` (sidechain pela voz, -14 LUFS). **Gemini ouve a mix** (`ouvir_mix.py`) e abaixe o que ele apontar (água/chuva/pedras/chocalho tendem a ficar altos).
8. **Render**: `TOTAL=<dur> WORKERS=2 nice -n 15 python3 captura.py tudo out/video.mp4`. Açude 6 min (carga 8); caatinga 11 min (carga 12, por causa dos chicotes). Em horário de atendimento, AVISE o dono antes.
9. **Entrega**: WhatsApp pela Evolution (`message/sendMedia`, base64 por stdin); confira DELIVERY_ACK no banco.

## Para virar automação de canal dark (próximo passo combinado com o dono)

O que já é repetível: fórmula do texto, voz com tempos, som e mix, render, envio. O que ainda é feito à mão por vídeo: escolher tema, conferir fatos e DESENHAR as cenas no `filme.html`. Caminho:
1. Biblioteca de cenários e poses (já existe no exemplo) + um "roteiro.json" de cenas (cena, cenário, ações ancoradas em palavras) que o filme lê, em vez de código por cena.
2. Gerador de roteiro (LLM) que devolve texto + roteiro.json + fontes dos fatos, com checagem dos fatos antes da voz.
3. Voz paga (ElevenLabs Creator ou similar) com voz brasileira: o free (10k/mês) dá ~7 vídeos de 85 s e sem regravação.
4. Render fora do horário (cron noturno) e fila de publicação; 16:9 para YouTube longo pede outra composição (não é cortar o 9:16).

## Gotchas medidos

- **`globalAlpha` fora de 0..1 é IGNORADO** (fica o valor anterior, ex.: nuvens brancas no meio da chuva). Sempre `cl()`.
- `-x ** 2` é erro de sintaxe em JS (página não carrega e o captura só diz "waitForFunction"): use `(-x) ** 2` ou `Math.pow`. Para achar erro de página: Playwright com `pg.on("pageerror")`.
- Ângulo de braço/perna: 0 = para baixo, positivo = para frente; antebraço = ângulo do braço + cotovelo. Inverter a convenção deixa todo mundo de braço pra cima.
- Câmera com `y` fixo deixa o chão no meio da tela e o personagem pequeno: use `cg()` (chão em ~1280) e escala 1,5-2,3 nas cenas com personagem.
- Árvore branca em chão bege some no plano bem aberto: aumente a escala/escureça nesse plano.
- Pessoa dentro de buraco em corte parece "balde em cima do chão" se a borda do terreno não estiver desenhada: faixa clara na superfície + boca do buraco mais escura.
- Narração: escreva como se fala; nomes regionais e siglas saem com sotaque na voz George.
