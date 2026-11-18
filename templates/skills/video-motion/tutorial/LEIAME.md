# Modo TUTORIAL: sistema real, narrado, com as coisas acontecendo

Feito em 16/11/2026 no tutorial do menu Pendentes (um CRM dentro do Chatwoot). O dono: "isso ficou surreal de bom".
Exemplo completo em `../exemplos/tutorial-pendentes/` (`filme.html` + scripts).

**Quando usar:** "tutorial de como usar X", "vídeo explicando a tela Y", "mostra pra equipe como faz Z", com narração.
O pedido é "mostrando, movimentando, não um print com zoom": o cursor clica e a tela RESPONDE (aba troca a lista, contador
muda, conversa abre, campo é digitado, calendário abre, linha sai da lista).
**Não usa o motor HyperFrames desta skill:** é o método sem framework (`render(t)` puro + Playwright + FFmpeg), escrito do zero.

## A ideia que faz funcionar

1. **A voz vem primeiro e manda no tempo.** A narração sai com o tempo de cada palavra (`narrar.py`), e cada evento
   do filme é ancorado numa palavra: o clique em "Chamar" acontece quando a voz diz "Chamar". Vídeo = voz + 0,4 s.
2. **A interface é RECRIADA em HTML, fiel, a partir do CÓDIGO do sistema** (exceção consciente à regra "nunca redesenhar
   de imaginação": não é imaginação, é o mesmo CSS). Tokens de cor do CSS do app, a fonte real (woff2 tirado do build),
   os mesmos componentes (botão primário amarelo, pílula ativa preta, badge, avatar de iniciais), os mesmos textos da tela.
   Recriar permite animar ESTADO (lista trocando, contador, digitação), coisa que um print não faz.
3. **Dados fictícios sempre** (nomes, IDs, telefones inventados). Prints reais com dados de cliente só como referência
   em `ref/`, nunca no vídeo nem publicados.
4. **Largura de celular:** cada tela é desenhada num mundo de 480 px (layout responsivo/mobile do próprio app) e a câmera
   aproxima ~2,1x dentro de uma janela 1000x1250 no reel 1080x1920. Texto de 14 px vira ~29 px: lê no celular.

## Passo a passo

1. **Entender a tela e o fluxo** pelo código (componentes, spec) e listar os passos que o usuário faz. 6 a 9 passos em ~60 s.
2. **Referência visual real** (Playwright logado, só leitura):
   - Chatwoot: token de sessão do usuário Suporte por rails runner
     (`u=User.find(1); h=u.create_new_auth_token`) e cookie `cw_d_session_info` = JSON `{access-token, token-type, client, expiry, uid}`
     (urlencoded) no domínio do Chatwoot. Tirar prints desktop 1440x900 e celular 430x932.
   - Dashboard App/iframe: clique pela posição na tela (o texto "Pipeline" existe no menu e na aba), e `page.frames` para ler o iframe.
   - Telas do CRM fora do iframe: `sessionStorage.crm_jwt` (o `sessao-provider` usa quando não está no Chatwoot).
3. **Tokens e fonte do código:** `crm.css` (variáveis `--crm-*`), `ui.tsx` (classes dos botões/pílulas/badges); fonte em
   `.next/.../media/*.woff2` (pegue o arquivo do subset `latin`, o que tem `unicode-range: U+0000-00FF`).
4. **Roteiro de narração** (`narracao.txt`, um passo por linha, "você", frases curtas, siglas escritas como se falam).
   `python3 narrar.py narracao.txt` e depois `GEMINI_API_KEY=... python3 ouvir.py assets/narracao.mp3` (o Gemini ouve e aponta
   pronúncia ruim). Corrija a escrita e gere de novo ANTES de montar o filme: depois disso a voz nova muda todos os tempos.
5. **`filme.html`** (copie o do exemplo e troque as cenas). Anatomia:
   - `#palco` 1080x1920; `#topo` = "PASSO N" + título grande (troca com subida); `#janela` (40,300,1000x1250, raio 52)
     com `#mundo` (as cenas, uma `section.cena` por tela, todas na origem) e `#cursor`; `#legenda` embaixo; `#fim` = cartão final amarelo.
   - **Câmera** `CAM = [[início, fim, cx, cy, escala], ...]` com `io()`; corte seco = início e fim colados (`[27.95, 27.96, ...]`).
   - **Cursor** em coordenadas do MUNDO convertidas pra tela (`tela(pt, cam)`), assim não escala com o zoom. `CUR` = movimentos
     até âncoras medidas (`anc(id)` soma offsetLeft/Top até `#mundo`, medido UMA vez depois das fontes), `CLIQUES` = tempos
     (cursor encolhe + anel amarelo expande), `CUR_VIS` = quando aparece. Esconda o cursor parado (ele "mora" no último alvo).
   - **Telas respondem ao clique** no mesmo tempo do clique: botão afunda (`aperta(id, t)`), rótulo vira "Abrindo…", aba troca
     a lista com entrada escalonada, contador rola (`Math.round(lerp(...))`), texto digitado por `slice`, calendário abre, mensagem
     sobe com mola, linha riscada sai pro lado e as de baixo sobem (soma das alturas medidas).
   - **Navegação** entre telas = crossfade curto + a tela nova desliza 60 px (`slide(a)`), com whoosh.
   - **Motivo amarelo** (a cor de destaque do produto) atravessa o filme: selo do menu, marcador de caneta (`.mk` scaleX 0->1)
     no que a voz cita, anel do clique, palavra ativa da legenda, cartão final.
   - **Notas** (balão preto "quem chamar") EM CIMA do elemento, uma de cada vez, saem antes da próxima; à direita cortam na borda.
   - **Legenda karaokê** das palavras da narração: blocos de até 5 palavras (quebra em pausa > 0,28 s), palavra falada em tinta,
     futura apagada, a da vez com fundo amarelo. Serve pra quem assiste sem som.
6. **Revisão** (`TOTAL=64 WORKERS=2 python3 captura.py revisao rN`, ~20 s): olhe a `folha.jpg` e monte 4 quadros lado a lado
   no tamanho real (`ffmpeg ... hstack=4`) dos momentos-chave. Corrija e repita. Na 1a rodada do Pendentes: notas cobrindo
   texto, calendário fora do quadro, fantasma do gancho por cima da tela seguinte, espaço entre palavras sumindo, borda do
   mundo aparecendo no plano aberto.
7. **Som** (`~/.video-motion/venv/bin/python som.py`): trilha leve em código (pad + baixo + arpejo + bateria leve, 100 BPM) e um
   efeito por ação com os MESMOS tempos do filme (clique com corpo, whoosh na troca de tela, notas subindo/descendo nos
   contadores, pop nas mensagens, teclas na digitação, sino no sucesso). `python3 mix.py 64`: voz + trilha com sidechain + fx, -14 LUFS.
8. **Render** fora do horário de atendimento ou com aviso: `TOTAL=64 WORKERS=2 nice -n 15 python3 captura.py tudo out/video.mp4`
   (1.920 quadros; com 4 workers foram 4 min e carga 16 na VPS). Conferir folha do MP4 final (`fps=1/4,tile=8x2`).
9. **Entregar** ao dono pelo canal combinado (ex.: Evolution `message/sendMedia`, `mediatype: video`, base64 por stdin) e dizer o que é limite
   (voz, sotaque) e o que é fácil de trocar.

## Gotchas medidos

- **Espaço entre palavras some** com o Manrope do subset do Next ("Agendadopara"): `word-spacing: .16em` nas cenas do CRM.
- **Voz George no free:** "EVO" sai "Ivo"; Chatwoot, Pipeline e template com sotaque. Gemini: clareza 9, naturalidade 7.
  Escrever como se fala ("Évo") e, se o cliente quiser voz brasileira, plano pago (vozes `professional` dão 402 no free).
- **`visibility`:** use `show(el, o)` (opacity + `visibility: hidden` só quando 0); nunca `visible` num filho.
- Pai com transform (câmera) não muda `offsetLeft/Top`: medir uma vez com tudo em identidade e guardar em `POS`.
- Cena com transform própria (slide) + filho medido: meça antes do primeiro render.
- Trilha mono x estéreo no ffmpeg: `aformat=channel_layouts=stereo` em todas as entradas antes do `sidechaincompress`.
- Arquivo de palavras: `assets/palavras.js` por `<script src>` (fetch de `file://` falha no Chromium).
