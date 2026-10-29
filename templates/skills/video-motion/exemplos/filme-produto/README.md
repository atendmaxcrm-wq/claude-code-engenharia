# Exemplo: filme de produto

Mostra `ui_produto` (botão -> campo digitado -> carregando -> check -> print real -> cartão), uma cena `livre` (`cenas/sinal.js`), trilha original sintetizada a 120 BPM e dois formatos (9:16 e 16:9) do mesmo roteiro.

Para rodar com a SUA marca:
```bash
bash .claude/skills/video-motion/capturar_marca.sh https://seusite.com .   # gera marca.json + assets/marca/
# troque no roteiro.json os textos e o print (assets/marca/prints/...) pelos do seu produto
bash .claude/skills/video-motion/revisar.sh .                                # loop de crítica até tudo >= 8
bash .claude/skills/video-motion/renderizar.sh . --formato todos
```
Feito com o site da Novuum (Syne + DM Mono, #39e88e); o print usado foi `assets/marca/prints/scroll-000.png` da captura.
