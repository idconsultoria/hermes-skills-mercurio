# Checklists de revisão

## A. Diagrama de processo

1. **Ramos de decisão completos.** Cada gateway com as duas saídas rotuladas (aprovado/reprovado, sim/não). Ausência do ramo negativo = processo sem tratamento de exceção.
2. **Gate existe onde o texto exige.** Se a especificação lista N pontos de aprovação humana, o diagrama precisa de N gateways.
3. **Loop fechado de verdade.** Métrica que alimenta a estratégia, negócio perdido que deveria alimentar a oferta e pesquisa de satisfação que deveria alimentar a próxima oferta são loops **distintos** — confira cada um contra o que o texto promete.
4. **Consistência com a tabela de papéis.** Raias espelham os papéis do documento; supervisor/governança têm raia ou participante; handoff obrigatório (ex.: via CRM) aparece como elemento.
5. **Prazos onde há prazo.** Validade de proposta, cadência de follow-up e ciclo de medição no desenho (timer/anotação), não só na prosa.
6. **Semântica.** Para artefato que será editado ou virou base de implementação: `.bpmn` XML real, não SVG desenhado à mão rotulado "BPMN 2.0".
7. **Contagem conferida** (`viewBox`, nº de tarefas, nº de gateways) contra o documento.

## B. Especificação operacional

- **Metas e KPIs:** meta numérica por fase/canal, amarrada ao que foi pactuado com o cliente (faturamento, MRR, nº de contratos, canais novos). Sem isso, processo não é mensurável.
- **Alvo e critérios de qualificação:** ICP definido e critérios de MQL/SQL explícitos; termo citado e não definido é item em aberto.
- **Prazos (SLAs):** validade da proposta, nº de tentativas de follow-up, prazo de resposta de cada etapa.
- **Dono humano de cada gate, por nome** — cargo genérico ("liderança", "gestor") não é dono.
- **Critério de transição humano × IA** nas etapas de decisão; sem ele, não existe regra de escalonamento.
- **Exceções/fora-de-fluxo:** lead sem resposta (nurturing), proposta perdida (motivo retroalimenta a oferta), inadimplência, cancelamento, contrato pontual × recorrente.
- **LGPD e opt-out** em qualquer cadência fria (e-mail/WhatsApp): base legal, descadastro, registro de consentimento.
- **KPIs de funil por etapa** (conversão, ciclo médio, CAC) e custo por agente — sem isso não se decide se a automação se paga.
- **Ferramentas por etapa** e onde vivem os artefatos versionados (scripts, planos, propostas).
- **Governança do próprio documento:** versão, autor, data, cadência de revisão.

## C. Renderização e impressão

| Sintoma | Causa | Correção |
|---|---|---|
| Diagrama sai como mancha preta em conversor não-navegador | Estilo do SVG vem de `var(--x)`; variável não resolve e `fill` default do SVG é preto | Cor literal no SVG (atributo `fill` ou `<style>` interno com hex) ou gerar o PDF pelo navegador |
| PDF com tudo espremido numa página ilegível | Canvas de largura fixa em px sem `@media print` | Paisagem pré-dimensionada, tiling em páginas ou export nativo PNG/PDF |
| Tipografia perdida no arquivo | Fonte carregada por `<link>` do Google Fonts | Embutir a fonte ou definir fallback de sistema |
| Ferramenta de render falha depois de "instalada com sucesso" | Pacote de navegador transitório/stub | Fazer um render real (ou screenshot de HTML trivial) antes de construir o fluxo |

## D. Formato do retorno

1. O que está **completo** (primeiro, e com honestidade).
2. Lacunas **por tema**, cada uma com o motivo prático de importar.
3. **Conflitos a confirmar com o dono** — bloco separado, pedindo a resposta.
4. **Sugestões numeradas**, submetidas à aprovação antes de qualquer alteração.

## E. Documento no timbrado (Google Doc gerado a partir de Markdown)

**Pré-condição de destino:** o documento nasce no dono da cópia, então confirme antes de gerar
que a credencial que vai copiar o modelo tem `canAddChildren` na pasta de destino — e crie a
subpasta com **essa mesma credencial**. Pasta de outro dono (Drive do cliente, Drive da ID)
recusa a cópia com erro de permissão depois do trabalho todo feito.

O `OK` do gerador **não** é entrega verificada. Confira por API **e** no render.

**Por API (leitura do documento):**

1. **Placeholders residuais = 0:** conte as strings editáveis da capa e do cabeçalho (tipo de
documento, título expandido, título hero, cliente, running title). Qualquer uma acima de zero é
capa ou cabeçalho quebrado.
2. **Negrito íntegro:** percorra os `textRun` com `bold` e procure trecho em negrito **começando
no meio de palavra** (run em negrito precedido de caractere alfanumérico sem negrito). É o
sintoma de índice deslocado na inserção; zero é o esperado.
3. **Âncora da contracapa:** o último parágrafo do corpo tem de conter o glifo de área privada do
modelo (`\ue907`). Se sumiu, a contracapa não renderiza.
4. **Cabeçalho e rodapé:** leia o texto de header/footer de verdade — eles vivem dentro de tabela
no header, então um walk só de parágrafos devolve vazio e dá falso negativo.

**No render (export → PDF → páginas):**

5. `pdfinfo … | grep Pages` para o tamanho real; `pdftotext -layout` para localizar **em que
página caiu cada tabela** — busque uma célula-âncora (valor em R$, código de linha), não o
título da seção.
6. `pdftoppm -png -r 80-90 -f <p> -l <p>` + inspeção visual da capa, da primeira página de corpo,
de cada tabela grande e da última página (contracapa, sem texto do corpo).
7. **Tabela que quebra de página perde os títulos das colunas** — o Docs não repete a linha de
cabeçalho por padrão. Aplique o pin de linha de cabeçalho em todas as tabelas e confirme a
repetição na página de continuação: o campo não volta na leitura da API, então a prova é o render.
8. **Capa e contracapa se julgam na renderização.** Se a capa do modelo vier branca no export
(elemento posicionado que o export não localiza), o veredito é o documento aberto no editor —
render é evidência, editor é a verdade.

**Quanto ao conteúdo:**

9. **Documento de gestão não é log de trabalho.** Artefato de referência do ciclo (capa + tese +
plano + anexos) não carrega caminho de arquivo, estado de infraestrutura, nota de bastidor nem
narrativa de como o agente produziu o material. Se tem, não é minúcia: é defeito de propósito.
10. **A régua e o manual do projeto que executa o plano têm de dizer a mesma coisa.** Quando o
artefato define metas ou ordem de execução, o `.md` fonte vai também para o diretório do projeto
executor e entra na leitura obrigatória do manual de agentes dele — plano e manual contando
histórias diferentes é o defeito mais caro deste tipo de entrega.
