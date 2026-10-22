# Brief de diretor (preencher ANTES do roteiro.json)

> Modelo em 4 blocos (entradas, direção, estrutura, construção). Quanto mais específico, menos o vídeo cai no "padrão de IA".
> Se o usuário não sabe preencher a direção, converse antes: qual emoção (calmo, urgente, alegre)? qual referência? o que o espectador tem que lembrar?

## Entradas
- Produto/assunto: <nome> (<url>). Frase principal: <título real do site ou a frase do usuário>.
- Marca: `capturar_marca.sh <url>` (logo real, cores, fontes, prints). Uma cor de destaque só.
- Telas reais: prints de cada estado em `assets/marca/prints/` (Playwright, 1440x900 e 390x844). Nunca redesenhar a interface de imaginação.
- Dados: só números com fonte citável.
- Som: faixa fornecida (`musica.arquivo`) OU trilha original sintetizada (`musica.sintetizar`, BPM, clima).
- Formatos: 9:16 primeiro; depois 16:9 e/ou 1:1 do mesmo roteiro.
- Referência de estilo (opcional): `referencia.sh <url>` -> referencia.md (copiar movimento e ritmo, nunca conteúdo).

## Direção
<Uma ou duas frases de linguagem visual. Exemplos:>
- "Filme de produto com interface em movimento. Um contêiner que nunca corta: cada estado é o mesmo elemento mudando de tamanho, raio e preenchimento, enquanto o conteúdo troca atrás de um desfoque curto. Um cursor conduz cada mudança. Fundo neutro, uma cor de destaque. Molas com sobra mínima."
- "Perfil de atleta: tipografia gigante, recorte na frente da palavra, números contando no impacto."
Proibido (sempre): título centralizado sobre gradiente, tudo entrando com fade, rótulos nos cantos e molduras sem função, brilho na interface, partículas genéricas, easing que quica, tempo morto.

## Estrutura (em batidas)
<BPM, quantos compassos (4 batidas cada), e a sequência de estados. Alguma coisa acontece em toda batida ou a cada 2 a 4 s no máximo.>
Exemplo (120 BPM, 14 compassos):
logo -> botão "Começar" (clique) -> campo com e-mail sendo digitado -> carregando -> check -> painel com a tela real rolando -> cartão com a frase do produto -> palavras finais -> assinatura.

## Construção
- Rodar `montar.py` e mostrar `out/batidas.md` (tabela batida a batida) ao usuário. Ajustar a tabela é muito mais barato que renderizar.
- Loop de crítica: `revisar.sh` -> nota 1 a 10 nos 6 critérios -> corrigir os 3 piores -> repetir até tudo 8 ou mais.
- Só então `renderizar.sh` (com `--motion-blur` no final, se o tempo de render couber).
- Ao aprovar: o kit da marca já fica em `~/.video-motion/marcas/<marca>`; anotar no `marca.md` o que funcionou (cena, ritmo, tom) para o próximo vídeo da mesma marca.
