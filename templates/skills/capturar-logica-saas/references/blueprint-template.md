# Template do BLUEPRINT-<SISTEMA>.md

Esqueleto do documento final. Le como "manual de funcionamento" pro agente/dev que vai
RECONSTRUIR o sistema noutra VPS, nao como diario da captura. Preencher a partir do
manifest + screenshots. Estrutura destilada dos blueprints reais (Clinicorp 10 secoes,
Dietbox 12 secoes). Cortar/adicionar secoes conforme o dominio.

---

```markdown
# Como funciona o <SISTEMA> - Blueprint (logica/UX)

Documento de referencia pra construir um sistema de <dominio> proprio. Descreve o
funcionamento do <SISTEMA> (<o que e>), conta <apelido da conta>, capturado READ-ONLY em
<data>. Acompanha screens/ (referencia visual) e estrutura/manifest.json (DOM de cada tela).

## 1. Visao geral e arquitetura
- O que o sistema faz, pra quem, o modelo mental (ex.: agenda -> paciente -> tratamento).
- Tipo de app (SPA? server-rendered? mobile companion?), tipo de login, multi-clinica/multi-unidade.
- Papeis de usuario (RBAC) e o que cada um ve.

## 2. Navegacao e shell
- Menu principal (itens, em ordem) e como se navega (rota real vs SPA "/").
- Topbar, seletor de clinica/unidade, busca global.
- Mapa: qual item leva a que tela.

## 3. Modulo <A> (ex.: Agenda)
- Pra que serve, o que aparece (grade, lista, cards).
- Acoes (criar, editar, confirmar, cancelar) e onde ficam.
- Formulario de criar/editar: TODOS os campos (nome, tipo, obrigatorio?, opcoes de select).
- Regras/estados observados (cores, badges, filtros).

## 4. Modulo <B> ... (repetir por modulo)

## 5. Cadastros de base
- Entidades cadastraveis (cliente/paciente, servico/procedimento, profissional, categoria...).
- Campos de cada cadastro (do manifest: labels + fields + selectOptions).

## 6. Configuracoes
- Cada secao de config (costuma ser o MAPA das entidades e regras do sistema):
  horarios, especialidades, tabelas de preco, formas de pagamento, templates de mensagem,
  regua de cobranca, seguranca/2FA, permissoes...
- Para cada uma: o que configura e como afeta o resto.

## 7. Relatorios
- Catalogo por categoria (nome de cada relatorio).
- Padrao de relatorio (filtros: periodo, unidade, tipo de grafico; export).
- Obs.: colunas so renderizam com dados no periodo; aqui vai a ESTRUTURA, nao valores reais.

## 8. Comunicacao / automacoes (se houver)
- Canais (SMS/email/WhatsApp/push), gatilhos (confirmacao, lembrete, retorno), "quando enviar".
- (Nao incluir o conteudo real dos templates se for PII/propriedade do cliente.)

## 9. Tela de detalhe / prontuario / ficha (se houver)
- As ABAS e a composicao (SO a estrutura; screenshots com dado real ficam FORA do pacote).

## 10. Fluxos publicos / lead (se houver)
- Pagina publica (agendamento online, captura de lead): a tela de entrada e os passos.
- (Nao percorrido ate criar registro real.)

## 11. App/companion do cliente (se houver)
- O que o cliente ve, o que e automatico vs curado pelo profissional, como se libera.

## 12. Modelagem de entidades sugerida (pra reconstruir)
- Lista de entidades e seus campos-chave, derivada dos cadastros e forms.
- Relacoes (1:N, N:N) inferidas da navegacao.
- Enums observados (situacao, tipo, canal...).
- E a ponte da captura pro schema que sera escrito na outra VPS.
```

---

## Dicas de preenchimento

- Puxar campos direto do `manifest-sanitizado.json` (labels + fields + selectOptions por tela).
- Cada modulo ganha 1-2 screenshots de referencia citados pelo nome do arquivo.
- Marcar o que NAO foi percorrido (fluxos de escrita) como "estrutura descrita, nao executado".
- Escrever pra quem NAO viu o sistema: incluir o "porque" de cada tela, nao so o "o que".
- Sem travessao (em-dash), PT-BR com acentuacao.
