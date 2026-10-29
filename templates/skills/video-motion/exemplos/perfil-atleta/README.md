# Exemplo: perfil de atleta

Usa quase todos os tipos de cena: titulo, destaque (jogador recortado na frente do nome), grafico_linha (valor de mercado), linha_tempo (clubes), radar (atributos), video_palavras (lances com congelamento + anel e camera lenta), texto_video ("GOL"), numeros (temporada) e assinatura.

Dados reais de um jogador publico (Transfermarkt e Sofascore). Historico de valor e transferencias saem da API publica do Transfermarkt:
`https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/<id>` e `/ceapi/transferHistory/list/<id>`;
escudos em `https://tmssl.akamaized.net/images/wappen/head/<clubId>.png`.

Coloque em `assets/` (nao acompanham a skill por direitos):
- `musica.mp3` (e ajuste `musica.inicio`/`bpm`)
- `jogador.png` (recorte: `motor/recortar.py lances.mp4 assets/jogador.png --tempos ...`)
- `drible.mp4`, `finalizacao.mp4` (congelada no fim com tpad), `golmask.mp4`, `gol.mp4` (com camera lenta), `comemora.mp4`, `fundo.mp4` (desfocado)
- `escudos/<id>.png`
