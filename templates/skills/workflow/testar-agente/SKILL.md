---
name: testar-agente
description: Testa um agente de IA nosso de ponta a ponta com persona simulado, leitura do resultado GRAVADO e juizes independentes contra gabarito. Use antes de considerar qualquer agente pronto, ao mudar prompt de agente, ou quando o dono perguntar "ta bom mesmo?", "veja se esta num nivel muito bom", "testa esse agente". Aplica a licao de que pedido no prompt nao e garantia: o que importa vira invariante de codigo.
---

# Testar um agente de IA nosso

Padrão completo em `docs/PADRAO-TESTE-AGENTES.md`. Leia antes de começar.

## Quando usar

- Antes de dizer que um agente está pronto
- Depois de mexer no system prompt de qualquer agente
- Quando o dono pedir para avaliar qualidade ("está num nível bom?", "compara com o concorrente")
- Antes de mostrar um agente para cliente

## O ciclo

1. **Persona com a verdade em arquivo.** Dossiê markdown com os dados reais da pessoa. O simulado
   não pode inventar fora dele, e é isso que permite provar fabricação depois.

2. **Conversa pelo endpoint real, na org real.**
   ```bash
   node scripts/bancada-agente-conversa.js --org=<uuid> --persona=<arquivo.md> \
     --endpoint=/perfil-medico/chat --out=/tmp/transcript.md
   ```
   Org de cliente real exige backup antes e restauração conferida depois
   (`/root/backups/<tabela>/`). Apague também os rascunhos que o teste criar.

3. **Leia o que ficou GRAVADO, inteiro.** Nunca só o transcript: o agente mostra um resultado na
   tela e manda outro, menor, para a ferramenta de gravação.
   ```bash
   node scripts/dump-doctor-kb.js <organization_id>
   ```

4. **Juízes independentes em paralelo**, um por dimensão: completude contra gabarito, fidelidade de
   voz, fabricação, qualidade do entregável, experiência. Peça nota, veredito e evidência literal.
   Confira a evidência antes de corrigir: juiz erra.

5. **Corrija como invariante de código** quando o comportamento for essencial, e rode o ciclo de
   novo comparando as notas.

## Invariantes prontos para reusar

`routes/perfilMedico.js` exporta `cartaFoiApresentada`, `filtrarVozVerbatim`, `temasNaoPerguntados`,
`despejouPerguntas`, `normalizarVoz`, `normalizarConfianca`. Todos seguem o mesmo princípio: o
histórico da conversa chega inteiro no endpoint, então dá para PROVAR em vez de confiar na palavra
do modelo. A tabela completa está no doc do padrão.

## Regras que valem sempre

- Campo de FATO nunca é obrigatório no schema da tool: obrigar a preencher é convite a inventar.
  Só campo de controle (lacunas, confiança, confirmação) é obrigatório.
- Campo vazio vira lacuna declarada pelo servidor, não pela boa vontade do modelo.
- Escrita que sobrescreve conteúdo humano precisa guardar a versão anterior.
- Teste toda regex de detecção com o texto real que o modelo produz, não com o texto que você imagina.
