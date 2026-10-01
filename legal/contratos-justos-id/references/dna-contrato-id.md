# DNA do contrato da ID — a arquitetura do contrato justo

> Este é o esqueleto que a ID usa. Não é "modelo a preencher" — é a **ordem** em que as
> cláusulas aparecem, com o porquê de cada escolha. Textos prontos de cada cláusula estão em
> `redline-risco-b2b.md` (skill `direito-empresarial-brasileiro`).

## A ideia central

O cliente lê o contrato em três tempos, nesta ordem:

1. **Primeira página** — "o que é, quanto, quando, quem faz". Se ele não entende isso, para de ler.
2. **Meio** — as regras: escopo, marco, dinheiro, risco, propriedade, dados.
3. **Fim** — rescisão, foro, assinaturas. Ele lê por alto, mas assina.

Portanto: **informação crítica na frente, risco no meio, formalidade no fim**. Um contrato que
coloca a definição de escopo na cláusula 14 e a multa na cláusula 3 é um contrato que gera
revisão jurídica e atrito.

## Ordem padrão das seções

```
1.  Identificação e qualificação das partes
2.  Considerandos (por que estão assinando)
3.  Resumo do contrato (a página de 1 minuto)
4.  Objeto e escopo
5.  Fora do escopo
6.  Entregáveis e marcos (com aceite)
7.  Prazo, vigência e dependências
8.  Remuneração, parcelas e pagamento
9.  Mora, suspensão e inadimplemento
10. Propriedade intelectual (cessão + preexistentes)
11. Confidencialidade e segredo
12. Dados pessoais (LGPD)
13. Garantia
14. Independência das partes
15. Rescisão e seus efeitos
16. Foro e solução amigável
17. Disposições gerais
18. Assinaturas
Anexo I — Escopo detalhado
Anexo II — Cronograma / Ementa / Backlog
```

## Bloco 1–3 · Abertura que ganha a assinatura

### 1 · Identificação

Nome exatamente como no CNPJ da Receita, CNPJ completo, endereço da sede, e quem representa com
que poderes. Para a ID:

> **iD.teal Consultoria em Gestão Organizacional LTDA** (nome fantasia **ID Consultoria e
> Treinamento**), CNPJ nº 54.569.818/0001-59, sede na Rua Manoel Espírito Santo, nº 165, Sala 02,
> Bairro Grageru, Aracaju/SE, CEP 49.025-440, representada por **Gustavo Alexandre Souza Mello**,
> brasileiro, solteiro, CPF nº 076.429.105-09, RG 369.746-76 SSP/SE, Sócio-Administrador.

> ⚠️ **Por que a razão social importa:** contrato em nome do sócio é contrato pessoal. Se a ID
> for fechada ou o sócio se afastar, o contrato não a segue. E o nome fantasia evita que o
> cliente pense que "ID.TEAL" é outra empresa — não é.

### 2 · Considerandos — no máximo 3

Um considerando por razão real da contratação. Nada de história da ID, nada de bio dos sócios,
nada de história do projeto. Exemplo válido:

> CONSIDERANDO QUE a CONTRATANTE deseja eliminar a verificação manual de credenciais e
> documentos de seus colaboradores, reduzindo risco de acesso indevido e de entrada com
> documentação vencida;
>
> CONSIDERANDO QUE a CONTRATADA possui know-how reconhecido em desenvolvimento de sistemas web,
> segurança da informação e metodologias aceleradas por inteligência artificial;
>
> CONSIDERANDO QUE as partes mantêm relação comercial anterior, e resolvem formalizar esta
> contratação específica.

### 3 · Resumo do contrato — a página de 1 minuto

Bloco com: **o que é** (1 frase), **quanto** (valor + parcelas), **quando** (prazo + marco),
**quem faz** (equipe + coordenação), **o que o cliente entrega** (dependências com data),
**garantia** (prazo + cobertura), **propriedade** (do cliente, após quitação).

Este bloco é a novidade em relação aos contratos antigos da ID e é o que torna o contrato
"simples". Ele não substitui as cláusulas: é a bússola que faz o cliente ler o resto.

## Bloco 4–7 · Objeto, escopo, marcos e prazo

O coração. Regras:

- **Objeto**: uma frase, com verbo de entrega. "Desenvolvimento, implantação e treinamento" —
  não "prestação de serviços de consultoria".
- **Escopo**: lista **positiva** (o que tem) e **negativa** (o que não tem). A negativa é tão
  importante quanto a positiva: é o que impede scope creep sem briga.
- **Marcos**: data + entregável + critério de aceite. Vinculados a parcelas.
- **Aceite**: prazo correndo + o que conta como manifestação. Sem isso, o ID fica refém do
  silêncio (ver X.9 em `redline-risco-b2b`).
- **Dependências**: o que o cliente precisa entregar, com prazo, e a consequência do atraso
  (prorrogação automática). **Esta é a cláusula que mais protege o cronograma** e a que o
  cliente menos resiste — porque é razoável e ele mesmo se beneficia.

## Bloco 8–9 · Dinheiro

- Valor total + parcelas com datas. Sem "a definir".
- **Entrada antes do custo.** A ID não mobiliza antes de receber.
- **Cada parcela = um marco.** Não "R$ 1.000/mês", mas "R$ 1.000 na entrega da etapa 3".
- Mora: 2% + 1% a.m. sobre a parcela. Dentro do teto do art. 412 do CC.
- **Multa simétrica** (o atraso da ID tem a mesma penalidade). Isso é o que torna a cláusula
  justa e evita argumento de abusividade.
- Suspensão por atraso do cliente: comunique por email com antecedência. **O silêncio não é
  ferramenta** — o corte de serviço precisa ser comunicado.

## Bloco 10–12 · Patrimônio, segredo e dados

O bloco que a ID não pode negociar curto. Ver as cláusulas X.14–X.28 em `redline-risco-b2b`.

Três regras de ouro:

1. **Cessão após quitação** — e não antes. Cliente que não pagou não tem título.
2. **Preexistentes reservados** — metodologia, frameworks, base interna, know-how. Sem isso a
   ID entrega parte do próprio negócio.
3. **Vedação de treino de IA com dado do cliente** — protege o ativo de dados e é cláusula de
   compliance (Lei 12.846).

## Anatomia de uma boa cláusula

Uma cláusula da ID tem, na média, quatro elementos. Use este checklist ao escrever qualquer uma:

- [ ] **Sujeito claro** — quem faz (a ID? o cliente? um terceiro?).
- [ ] **Gatilho** — em que situação (data? evento? omissão?).
- [ ] **Ação ou consequência** — o que acontece (entrega? prorrogação? multa? suspensão?).
- [ ] **Limite** — até onde (tempo? valor? número de vezes?).

**Exemplo com os quatro:**

> **A CONTRATADA prorrogará automaticamente o cronograma por período igual ao atraso da
> CONTRATANTE**, se esta não designar responsável pela validação no prazo de 5 dias úteis a
> contar do envio da etapa, devendo comunicar a prorrogação por email no primeiro dia útil
> seguinte à constatação do atraso.
> (sujeito: ID · gatilho: omissão do cliente em 5 dias · consequência: prorrogação · limite:
> período igual ao atraso)

**Sem o limite**, isso vira "se o cliente atrasar muito, o prazo é outro" — e aí é discussão.

## Estilo de redação da ID

| Faça | Não faça |
|---|---|
| "A CONTRATADA entrega" com verbo claro | "A CONTRATADA prestará" em toda cláusula |
| Frases de até 2 linhas | Parágrafos de 8 linhas |
| Números por extenso **e** algarismo | Só algarismo (divergência em contrato) |
| "R$ 1.000,00 (mil reais)" | "R$ 1.000" |
| Definir termo no primeiro uso | Usar termo técnico sem definir |
| Enumerar exclusões | Dizer "o necessário para o escopo" |
| Números de cláusula estáveis (X.1, X.2) | Incisos soltos |

## Duas assinaturas, sempre

Via física: duas vias de igual teor, duas testemunhas, data e local. Assinatura eletrônica é
válida (MP 2.200-2/2001 e MP 14.063/2020) e mais cômoda para cliente em outro estado — mas se o
cliente pedir via física, provide e não recuse: é confiança.

---

*Este DNA é o padrão da ID Consultoria. Adaptações por cliente vão em
`arquetipos-contrato-id.md`.*
