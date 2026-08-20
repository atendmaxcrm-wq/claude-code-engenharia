---
name: entrega-verificada
description: Ciclo de entrega verificada — monta uma SPEC com todo o plano, executa em ETAPAS, testa cada etapa em CÓDIGO e apertando os botões (headless ou o dono), e só avança quando a etapa está aprovada. Use para feature/redesign/refactor de qualquer tamanho. Termina com /atualizar-memoria.
user-invocable: true
---

# Entrega Verificada

Pedido do dono: **o que veio nos args** (ou o pedido corrente da conversa).

NÃO saia codando. Rode o ciclo abaixo. **Regra de ouro:** nada avança de etapa sem estar VERIFICADO — e verificado não é só `tsc`/`build` passar, é **o botão apertado fazendo o que promete**. "Botão que não faz o que promete = NÃO passou."

Este ciclo casa com `/loop` quando o dono quer autonomia: uma etapa por iteração, deploy, marca a spec, segue.

---

## Fase 0 — Entender + montar a SPEC (fonte de verdade)

1. **Consultar memória primeiro:** `/memoria/sistema/changelog.md`, `troubleshooting.md`, `insights.md`, e a memória persistente. Já foi feito algo parecido? Problema/armadilha conhecida? O estado REAL bate com o que a memória diz? (achado do dia: telas "que eu tinha como prontas" só tinham a COR, não o craft — **audite o estado real, não confie no otimismo da memória**).
2. **Ler o código real** (quem chama, quem depende, invariantes). Para varrer muitos arquivos, delegue a leitura a agentes (Explore/workflow) e fique com a conclusão, não com o dump.
3. **Escrever a spec** num arquivo `docs/SPEC-<slug>.md`. Ela é o checklist que o ciclo segue e MARCA. Deve conter:
   - **Objetivo** + o alvo/referência (print do Dribbble, tela já pronta que serve de padrão, kit de componentes). Se o dono for trazer referência, peça ANTES o print/link do estado exato desejado.
   - **Padrão/receita** (quando aplicável): tabela do-que-troca (antigo → novo), componentes a reusar.
   - **Invariantes (o que NÃO pode quebrar):** lógica/handlers/endpoints/props/tipos intactos; theme-aware nos 2 temas; acentuação PT-BR **sem travessão (em-dash)**; cores **semânticas** preservadas (verde de orçamento/status, alerta clínico, etc.).
   - **Etapas** (ondas), em ordem, cada uma com escopo pequeno e checklist `[ ]` por arquivo/peça.
   - **Critério de aceite POR etapa** = o teste da Fase 2 (código + apertar botões).
   - **Protocolo de deploy** (Fase 3).
   - **Log de progresso** (o ciclo preenche).
4. **Apresentar a spec ao dono** e pegar o ok do plano/ordem antes de executar (a menos que ele já tenha mandado rodar autônomo).

## Fase 1 — Executar UMA etapa por vez

- Fazer SÓ o escopo da etapa. Preservar 100% a função — só muda a casca/o comportamento que a etapa pede.
- Muitos arquivos independentes na mesma etapa → **paralelizar com um workflow** (1 agente por arquivo, cada um lê a spec + o kit + edita a casca). Coisa nuclear/acoplada (ou que precisa de julgamento fino) → fazer à mão, com cuidado.

## Fase 2 — VERIFICAR a etapa (o núcleo, 2 níveis)

**Nível 1 — código**
- `npx tsc --noEmit` filtrado nos arquivos da etapa; excluir os erros PRÉ-EXISTENTES conhecidos (ex.: framer `Variants`/`ease`, `import.meta.env`, `res.data` unknown, `MediaItem.views`, Badge `"danger"`). Erro NOVO = corrigir antes de seguir.
- **NUNCA `npm run build` só pra "verificar"** — build = deploy (nginx serve `/root/makewl-advisor/dist`). Para checar sem publicar, use `vite build --outDir /tmp/descartável`.

**Nível 2 — apertar os botões (funcional/visual) — é o que separa "passou" de "não passou"**
- Subir o headless: `puppeteer-core` (`/root/makewl-advisor/node_modules/puppeteer-core`) + `executablePath:'/usr/bin/google-chrome'`, `--no-sandbox`.
- **JWT forjado:** `jwt.sign({ userId, email, role, organizationId, organizationType }, JWT_SECRET)` com o `JWT_SECRET` de `/root/makewl-advisor-api/.env`; setar `localStorage.advisor_token`; navegar no domínio prod (`https://advisor.assessoriamakewl.com.br`) — o Vite dev (`:3006`) é inviável pela internet.
- **Screenshot nos 2 temas** (`localStorage.makewl-theme` = dark/light) e **LER o print** — não confiar no que o código "deveria" fazer.
- **CLICAR o que a etapa entrega** e confirmar o EFEITO REAL: o botão navega/salva/troca de verdade? o estado muda? o F5 mantém? Se há **gate por papel**, forjar os 3 papéis (super_admin / org_admin / viewer) e conferir cada um ANTES de virar live; se houver QUALQUER risco pro cliente, PARE e avise o dono.
- **SELECT no banco** quando a etapa promete persistência: provar que a linha existe/mudou **pelo caminho do produto** (não só que a UI escreveu "salvo"). A trava/aceite exige LASTRO — de onde o dado veio — não campo preenchido.
- **Se o headless estiver indisponível** (aconteceu: `pkill -9 -f google-chrome` quebra o Chrome da sessão inteira — **NÃO** fazer pkill amplo de chrome): PARE e **peça o dono apertar** os botões e confirmar, com hard-refresh, ANTES de marcar a etapa. O dono vira a conferência visual.

## Fase 3 — Deploy da etapa

- Bump `public/sw.js` CACHE_NAME (`vNNN` → `vNNN+1`) + `npm run build` + confirmar `dist/sw.js` na versão nova + smoke no domínio prod (bundle novo servindo, zero pageerror). O SW faz o app novo chegar sem "1 reload atrasado".

## Fase 4 — GATE de aprovação → só então avança

- Marcar a etapa `[x]` na spec + anotar a versão SW no log **SOMENTE quando**: tsc limpo + funcional verificado (headless OU dono apertou) + no ar.
- Se o dono está acompanhando, **mostrar o resultado e esperar o ok** antes da próxima etapa. Se algo saiu torto, **corrigir e RE-VERIFICAR** — não seguir com pendência arrastada.
- Repetir Fase 1 → 4 até todas as etapas prontas. No `/loop`, reagendar a próxima iteração; no fim, parar o loop e mandar PushNotification.

## Fim

- Rodar **`/atualizar-memoria`** (invocar a skill `atualizar-memoria`): markdown + pgvector, incluindo o padrão que funcionou e as armadilhas novas.

---

## Lições da prática (não repetir os erros)
- `pkill` amplo de chrome mata o headless de screenshot da sessão inteira. Não fazer.
- Não confiar na memória otimista: auditar o estado REAL antes de dar por pronto (ex.: "Metas convertido" era falso — só os dropdowns).
- Semânticos ficam na cor semântica (verde de orçamento, alerta clínico, status).
- Referência do Dribbble/print: o "cara" costuma morar num detalhe (empty-state, o símbolo certo, o composer) — replicar de perto, não refinar sutil; e conferir os 2 temas (o que some no dark aparece no light e vice-versa).
- Deploy em LOTE por etapa; nunca buildar só pra ver.
