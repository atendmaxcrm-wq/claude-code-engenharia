# Cenas do /video-motion: referência do roteiro.json

Tudo é medido em **batidas** da música (`batidas`). O motor converte em segundos, coloca imagem e som nos mesmos tempos e encaixa as cenas em sequência. Coordenadas internas são do quadro 1080x1920 (vertical).

## Campos gerais do roteiro

| Campo | Obrigatório | O que é |
|---|---|---|
| `formato` | não (padrão `9:16`) | v1 da skill: só vertical 1080x1920 (Reels, Shorts, Stories) |
| `fps` | não (30) | 60 deixa o motion mais liso, dobra o tempo de render |
| `marca` | não | Texto da marca no topo e na assinatura |
| `rotulo` | não | Texto do canto superior direito na 1ª cena |
| `cor` | não | Cor de destaque `#hex`. Se faltar e houver `logo_cor`, a cor sai do logo |
| `logo_cor` | não | Imagem (escudo/logo) da qual tirar a cor dominante |
| `musica.arquivo` | sim | Áudio ou vídeo com a música |
| `musica.inicio` | não | Segundo da música onde começa (de preferência numa batida forte) |
| `musica.bpm` | sim | BPM detectado (`hf beats` no projeto). Trap/hip-hop: use o BPM que o hyperframes der e `subdivisao: 2` |
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
`linhas` (lista, cada uma entra num compasso; a última com impacto e tremida), `legenda` (linha mono acima), `tamanho` (px, padrão 196). Precisa de ~2 batidas por linha + 4 de respiro.

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

## Preparando material

- Vídeo de cartão: recorte e codifique com quadros-chave frequentes: `ffmpeg -ss A -t D -i src -an -vf fps=30,scale=1280:720 -g 30 -keyint_min 30 -c:v libx264 -crf 17 saida.mp4`.
- Câmera lenta: `split` + `trim` + `setpts=(PTS-STARTPTS)/0.45` + `concat` (exemplo no SKILL.md).
- Congelar o fim: `-vf tpad=stop_mode=clone:stop_duration=0.9`.
- Vídeo de fundo: `crop` vertical + `boxblur=24:2` + `eq=brightness=-0.2` (o desfoque no navegador custa muito no render).
- Ícones/logos: PNG com fundo transparente ou branco.
