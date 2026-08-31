# Skills Arquivadas

## Lote 1 (2026-04-29): consolidadas em /site-elite

Estas 8 skills foram consolidadas em `/site-elite` em 2026-04-29.

| Skill arquivada | Substituida por |
|----------------|-----------------|
| frontend-design | /site-elite + references/02-vibe-questionnaire.md |
| modern-ui-design | /site-elite + references/01-design-system-distiller.md |
| design-system | /site-elite + references/01-design-system-distiller.md |
| upgrade-visual | /site-elite (workflow completo aplica upgrade) |
| interaction-patterns | /site-elite + references/04-motion-recipes-gsap.md |
| capturar-efeitos | /site-elite + references/09-aura-build-arsenal.md |
| component-builder | /site-elite (Fase 2 cobre estrutura de componentes) |

> Nota: `clonar-design` estava neste lote, mas foi REATIVADA em 2026-06-23 (ver abaixo).

## Lote 2 (2026-06-23): /site-elite aposentada

A propria `/site-elite` foi aposentada em 2026-06-23. Motivo: na pratica produzia
sites genericos (slop), porque destila um "design system" no abstrato (texto sobre
texto) em vez de ancorar numa referencia visual real. Foi substituida por duas
capacidades superiores, validadas em producao:

| Skill aposentada | Substituida por |
|------------------|-----------------|
| site-elite | /replicar-sistema (replicar de referencia real: print/video -> mockup canonico aprovado -> rubrica cirurgica + auditar-fidelidade) |
| site-elite | /site-3d (sites 3D premium nivel Awwwards: React Three Fiber + drei + scroll/mouse + gate de performance mobile) |

`clonar-design` foi REATIVADA (saiu do archive de volta para skills ativas), agora
com `assets/design-scraper.py` self-contained. Ela alimenta a /replicar-sistema com
o design system extraido de um site real (cores, tipografia, animacoes, libs, video).

### Skills mantidas ativas (nunca arquivadas)

- /replicar-sistema - referencia real (print/video) -> mockup canonico -> rubrica cirurgica. Autoridade de acabamento premium.
- /auditar-fidelidade - quality gate de completude (renderiza a referencia, le o JS, acha o que falta). Chamada pela /replicar-sistema na fase final.
- /clonar-design - extrai design system completo de um site real (input para /replicar-sistema).
- /site-3d - sites 3D premium (R3F). Invoca /gsap-animations (DOM-first) e /replicar-sistema (3D sobre referencia).
- /gsap-animations - deep-dive GSAP (ScrollTrigger, SplitText, pin, horizontal scroll).
- /clonar-site - engenharia reversa pixel-perfect de site inteiro por URL.
- /criacao-form - dominio separado (wizards/diagnosticos com IA).
- /site-elite-cinema - camada cinematografica (Veo 3.1 + scroll-scrub). Dominio audiovisual distinto; mantida.

## Por que arquivar e nao deletar

Caso a substituicao nao funcione na pratica, e trivial restaurar. Apos 2 meses de
uso estavel das skills substitutas sem regressao, as arquivadas podem ser deletadas.
