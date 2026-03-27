# Workflow de Engenharia - Regras Automaticas

## Roteamento Inteligente de Pedidos (OBRIGATORIO)

Quando o usuario pedir QUALQUER coisa, ANTES de comecar a implementar, classifique
o pedido e siga o processo correto automaticamente. O usuario NAO precisa saber qual
comando usar.

### Como classificar:

Pedido do usuario
    |
    |-- E um BUG / algo nao funciona / erro / quebrou?
    |   -> Seguir processo de /investigar-bug
    |   -> Consultar troubleshooting.md primeiro
    |   -> Diagnosticar causa raiz ANTES de propor fix
    |
    |-- E FEATURE NOVA / algo que nao existe ainda?
    |   -> Seguir processo de /nova-feature (skill planejar-feature)
    |   -> Consultar memoria -> analisar impacto -> apresentar plano -> aguardar aprovacao
    |
    |-- E MELHORIA / trocar implementacao / melhorar algo existente?
    |   |
    |   |-- Envolve trocar lib ou abordagem tecnica?
    |   |   -> Seguir processo de /pesquisar-tech PRIMEIRO
    |   |   -> Pesquisar alternativas -> matriz de decisao -> recomendacao
    |   |   -> Apos decisao: seguir /migrar-componente
    |   |
    |   |-- E ajuste na implementacao atual (sem trocar lib)?
    |       -> Analisar impacto se arquivo core (skill analise-impacto)
    |       -> Planejar -> implementar -> validar
    |
    |-- E TAREFA GRANDE / complexa / multiplos arquivos?
    |   -> Preferir /agent-teams-v2 (orquestracao nativa)
    |   -> Alternativa simples: /agent-teams (subagents basicos)
    |   -> Decompor em ondas paralelas -> apresentar plano -> aguardar aprovacao
    |
    |-- E AJUSTE SIMPLES / texto / cor / campo / tweak pequeno?
    |   -> Implementar direto (sem processo formal)
    |   -> Mas SEMPRE: testar apos mudanca
    |
    |-- Nao tem certeza da classificacao?
        -> Perguntar ao usuario antes de comecar

### Sinais para detectar cada tipo:

Bug: "nao funciona", "erro", "quebrou", "travou", "nao aparece", "500/404/403", "tela branca"
Feature nova: "quero criar", "adicionar", "nova tela", "novo modulo", "implementar [algo que nao existe]"
Melhoria/troca: "melhorar", "trocar", "mudar o comportamento", "refatorar"
Tarefa grande: "implementar [feature complexa]", multiplos componentes, banco + API juntos
Ajuste simples: "mudar texto", "trocar cor", "ajustar espacamento", "corrigir typo"

### Comunicar ao usuario

Ao classificar, INFORME brevemente o que vai fazer:

"Entendi que voce quer melhorar X. Como envolve possivelmente trocar a
abordagem tecnica, vou primeiro pesquisar as melhores opcoes antes de implementar."

"Isso e uma feature nova. Vou consultar a memoria do projeto e montar um plano de
implementacao antes de comecar."

"Parece um bug. Vou investigar a causa raiz antes de propor correcao."

## Ciclo Obrigatorio

Independente da classificacao, toda tarefa segue:

ENTENDER -> PESQUISAR (se necessario) -> PLANEJAR -> IMPLEMENTAR -> VALIDAR

### 1. Consultar Memoria Primeiro
- changelog.md - ja foi feito algo similar?
- troubleshooting.md - problema conhecido?
- insights.md - decisoes, armadilhas?

### 2. Nunca Implementar sem Entender
- Ler o codigo antes de propor mudancas
- Entender o contexto (quem chama, quem depende)
- Para arquivos core: analise de impacto obrigatoria

### 3. Planejar Antes de Codar
- Ajuste simples: implementar direto
- Feature media (2-5 arquivos): listar passos, implementar sequencial
- Feature grande (5+ arquivos): usar /agent-teams-v2 (recomendado) ou /agent-teams
- SEMPRE apresentar plano para features medias/grandes antes de implementar

### 4. Validar Sempre
- Verificar se o servico responde apos mudancas
- Verificar logs para erros
- Testar endpoint especifico se alterou rotas
- NUNCA considerar tarefa pronta sem teste

### 5. Documentar ao Final
Sessoes produtivas devem terminar com /atualizar-memoria
