# Cenas do /video-motion: referência do roteiro.json

Tudo é medido em **batidas** da música (`batidas`). O motor converte em segundos, coloca imagem e som nos mesmos tempos e encaixa as cenas em sequência. Coordenadas internas são do quadro do formato (1080x1920 na vertical). Faça cada cena com múltiplo de 2 batidas (4 é melhor) para a seguinte entrar no tempo forte, 1 ou 3 do compasso; com `subdivisao: 2`, múltiplo de 4 (o motor avisa).

## Campos gerais do roteiro

| Campo | Obrigatório | O que é |
|---|---|---|
| `formato` | não (padrão `9:16`) | `9:16` (1080x1920), `16:9` (1920x1080) ou `1:1` (1080x1080). Fora da vertical só valem `titulo`, `ui_produto`, `livre` e `assinatura` sem vídeo |
| `formatos` | não | Lista para `renderizar.sh --formato todos`, ex. `["9:16", "16:9"]` |
| `fps` | não (30) | 60 deixa o motion mais liso, dobra o tempo de render |
| `marca` | não | Texto da marca no topo e na assinatura |
| `rotulo` | não | Texto do canto superior direito na 1ª cena |
| `cor` | não | Cor de destaque `#hex` (a ÚNICA). Se faltar: `marca.json`, senão a cor do `logo_cor` |
| `paleta` | não | `{fundo, tinta, mudo, cartao, linha}` em hex (vem do `marca.json`) |
| `fontes` | não | `{titulo, ui}`: caminhos .woff2/.ttf (vem do `marca.json`). Padrão Inter Tight + JetBrains Mono |
| `estilo` | não | `{fundo: "liso" \| "brilho", brilho: false}`. Padrão liso e sem glow (regra anti-IA) |
| `kit_marca` | não (`marca.json`) | Arquivo do kit de marca; `false` para ignorar. O roteiro sempre ganha do kit |
| `logo_cor` | não | Imagem (escudo/logo) da qual tirar a cor dominante |
| `musica.arquivo` | não | Áudio ou vídeo com a música. Sem ele (ou com `sintetizar: true`) a trilha é original, gerada em código |
| `musica.sintetizar` | não | `true` = trilha original na grade exata (começa no tempo forte em 0 s; não precisa de `hf beats`) |
| `musica.clima` / `tom` / `modo` | não | Trilha sintetizada: `energico` (padrão) ou `calmo`; tom `A`, `C#`...; `menor` ou `maior` |
| `musica.inicio` | não | Segundo da música onde começa (de preferência numa batida forte) |
| `musica.bpm` | sim (120 na sintetizada) | BPM detectado (`hf beats` no projeto). Trap/hip-hop: use o BPM que o hyperframes der e `subdivisao: 2` |
| `musica.subdivisao` | não (1) | Multiplica a grade (2 = meia batida) |
| `musica.volume` | não (0.8) | Volume da música antes da mixagem |
| `fundo_video` | não | Vídeo de fundo desfocado (pré-desfoque no ffmpeg, não no navegador) |
| `fundo_ate_cena` | não (1) | Índice da última cena em que o fundo aparece |

## Campos de toda cena

| Campo | O que é |
|---|---|
| `tipo` | Um dos tipos abaixo |
| `batidas` | Duração da cena (exceto `video_palavras`, que soma as batidas dos clipes) |
| `rotulo` | Texto do canto superior direito durante a cena |
| `transicao` | Como ENTRA: `lamina` (padrão; duas lâminas diagonais + riser + grave), `flash` (clarão + impacto) ou `nenhuma` |

Texto com `*palavra*` sai na cor de destaque. Em `titulo` de cena, ` / ` quebra linha.

## Tipos

### `titulo`: frase de abertura
`linhas` (lista; a última entra com impacto e tremida), `passo` (batidas entre linhas, padrão 2; use 1 para o gancho fechar antes de 2 s), `legenda` (linha mono acima), `tamanho` (px, padrão 196; encolhe sozinho para caber com a fonte real). Linhas curtas: fonte larga encolhe muito.

### `destaque`: imagem recortada na frente de uma palavra gigante
`palavra` (vai em maiúsculas, cheia + contorno), `imagem` (PNG transparente, use `motor/recortar.py`), `numero` {`rotulo`, `valor`, `prefixo`, `sufixo`, `formato`} (pílula contando), `etiquetas` (lista digitada com som de teclado), `tamanho_palavra`. Paralaxe 3D automática. Ideal 16 batidas.

### `grafico_linha`: série no tempo se desenhando
`serie` [{`data` "dd/mm/aaaa", `valor`}], `formato_valor` (`euro_mi`, `real_mi`, `dolar_mi`, `porcento` ou número), `marcos` [{`data`, `icone`}] (aparecem quando a linha passa, com "pop"), `titulo`, `legenda` (digitada), `fonte`. A linha desenha em 9 batidas a partir da 3ª. Ideal 16 batidas.

### `linha_tempo`: etapas com ícone
`itens` [{`ano`, `nome`, `valor` (digitado), `icone`}] (sem ícone, usa a inicial). Uma etapa a cada 2,2 batidas, a última acende. Até 6 itens. Batidas ≈ 3 + 2,2 × itens.

### `radar`: atributos num polígono
`itens` [[nome, valor]] (3 a 8), `maximo` (padrão 100), `titulo`, `legenda`. O maior acende. Batidas ≈ 4 + 1,6 × itens.

### `barras`: comparação em barras
Mesmos campos do `radar`. Até 6 itens. Batidas ≈ 4 + 2 × itens.

### `video_palavras`: palavra + vídeo por compasso
`clipes` [{`palavra`, `video`, `batidas`, `indice` ("01 / 03"), `alinhamento` (object-position, ex. "100% 50%"), `congelar_em` (s dentro do clipe; o vídeo precisa terminar congelado com `tpad`), `anel` {`x`,`y`,`r`,`texto`} (coordenadas no cartão 948x1180), `lento_em` (s onde começa a câmera lenta já aplicada no arquivo)}], `etiqueta` (selo no cartão). Corte com impacto e flash entre clipes.

### `texto_video`: vídeo dentro das letras
`texto` (curto: 3 a 5 letras), `video`, `tamanho` (px, padrão 440; confira se cabe em 1080). 4 batidas.

### `numeros`: caixas com contadores
`itens` [[rótulo, valor (texto, aceita vírgula), destaque (true/false)]] (até 4, grade 2x2), `titulo`, `legenda`. Ideal 12 batidas.

### `mockup`: print de tela num aparelho
`imagem` (print; celular: largura 390 a 780 px, pode ser alto que rola), `aparelho` (`celular` ou `notebook`), `etiquetas` (aparecem ao lado com "pop" + teclado), `titulo`. O print rola sozinho se for mais alto que a tela. Ideal 14 a 16 batidas.

### `assinatura`: encerramento
`titulo`, `marca` (digitada; padrão = marca do roteiro), `fonte` (crédito dos dados), `video` (opcional, cartão no topo; `video_duracao` padrão 2,4 s). Ideal 10 batidas.

### `ui_produto`: filme de produto (um contêiner que nunca corta)
Cada estado é o MESMO elemento mudando de tamanho, raio e cor com mola; o conteúdo troca atrás de um desfoque curto; um cursor conduz cada troca e clica colado na batida. Campos da cena: `titulo` (opcional, no topo), `tamanho`, `centro_y` (px), `estados` (lista; a duração da cena é a soma).
Cada estado: `batidas`, `forma` {`w`, `h`, `raio`, `fundo` (`"acc"` = cor de destaque, `"cartao"`, ou `#hex`)}, `conteudo` (um dos abaixo), `acao` {`tipo`: `clique` (som + onda) \| `passar` \| `nenhuma`, `x`, `y` (0 a 1 dentro da forma)} = o que o cursor faz para ir ao próximo estado, `nota` (legenda mono embaixo).
Conteúdos: `{texto}` (botão; encolhe para caber) · `{campo, digitar}` (campo com rótulo e texto digitado com som; com `acao`, ganha botão de enviar e o cursor clica nele) · `{icone: carregando \| check \| x \| seta}` · `{imagem, recorte: [x,y,w,h], alinhar: esquerda\|centro\|direita, rolagem: px \| true}` (print REAL; o recorte é ajustado à proporção da forma) · `{lista: [...]}` · `{titulo, texto}` (cartão). `cor` força a cor do texto.
Ritmo: 3 a 8 batidas por estado. Exemplo completo em `exemplos/filme-produto`.

### `livre`: cena escrita na hora
Para o que nenhum tipo cobre (uma vez só). `arquivo`: JS do projeto com uma função `(c, i, x) => {...}`. Use SÓ os tempos de `c`: `c.t`, `c.dur`, `c.tBatidas[k]` (início da batida k da cena). `x` traz `tl` (timeline), `el(html, pai)`, `box` (a camada da cena), `esc`, `frase`, `entra`, `digita`, `borrao`, `tremida`, `mola()`, `janela`, `W`, `H`, `B`, `MX`, `VERT`, `cor`.
O som fica no roteiro (para sair na mixagem): `sons` [{`batida`, `som`: hit, pop, tick, clique, sopro, whoosh, whoosh_lr, riser, subdrop, freeze, `volume`}], `digitar` [{`batida`, `texto`}] e `acontece` [{`batida`, `texto`}] (vai para a tabela de batidas). Mesmas regras: nada aleatório, nada de CSS transition/timer, transform e opacity.

## Preparando material

- Vídeo de cartão: recorte e codifique com quadros-chave frequentes: `ffmpeg -ss A -t D -i src -an -vf fps=30,scale=1280:720 -g 30 -keyint_min 30 -c:v libx264 -crf 17 saida.mp4`.
- Câmera lenta: `split` + `trim` + `setpts=(PTS-STARTPTS)/0.45` + `concat` (exemplo no SKILL.md).
- Congelar o fim: `-vf tpad=stop_mode=clone:stop_duration=0.9`.
- Vídeo de fundo: `crop` vertical + `boxblur=24:2` + `eq=brightness=-0.2` (o desfoque no navegador custa muito no render).
- Ícones/logos: PNG com fundo transparente ou branco.
