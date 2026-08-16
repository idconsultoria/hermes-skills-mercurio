# Placeholders do Modelo HTML

O modelo (`templates/modelo_proposta.html`) tem 87 placeholders `{{NOME}}`. Preencher via `scripts/preencher_proposta.py` com um JSON `{"NOME": "valor"}`.

## Capa
| Placeholder | Uso |
|---|---|
| `CLIENTE_LOGO_URL` | URL/arquivo da logo do cliente (box tracejado na capa e no slide final) |
| `CLIENTE_NOME` | Nome do cliente (capa, final, disclaimer) |
| `TITULO_PROPOSTA` | Título principal (96px) |
| `SUB_TITULO_PROPOSTA` | Subtítulo (36px, ex: "Melhoria de Processos com IA") |
| `DATA` | Data da proposta |
| `VALIDADE` | Válida até (data) — capa, condições, final |

## Resumo Executivo (fundo teal)
| Placeholder | Uso |
|---|---|
| `RESUMO_EXECUTIVO` | Parágrafo de resumo |
| `ENTREGAVEL_1..3` | O que entregamos (3 itens) |
| `RESULTADO_1..3` | Resultados esperados (3 itens) |
| `INVEST_RESUMO` | Linha de investimento no resumo (ex: "a partir de R$ X") |

## Entendimento do Desafio
| Placeholder | Uso |
|---|---|
| `CONTEXTO_PROBLEMA` | Lead do desafio |
| `CENARIO_ATUAL_1..2` | Cenário atual |
| `CUSTO_INACAO_1..2` | Custo de não agir |

## Escopo & Entregáveis
| Placeholder | Uso |
|---|---|
| `ESCOPO_1..3` | Incluído no escopo |
| `FORA_ESCOPO_1..2` | Fora do escopo (exclusões) |

## Quem já confiou (prova social — usar portfolio.md)
| Placeholder | Uso |
|---|---|
| `PROVA_SOCIAL_INTRO` | Lead |
| `CASE_1..3_METRICA` | Métrica (ex: "210 processos") |
| `CASE_1..3_DESC` | Descrição do case |
| `DEPOIMENTO_1..2` | Depoimento |
| `DEPOIMENTO_1..2_AUTOR` | Autor do depoimento |

## Metodologia & Cronograma
| Placeholder | Uso |
|---|---|
| `METODOLOGIA_DESC` | Lead |
| `FASE_1..4_NOME` | Nome da fase |
| `FASE_1..4_DESC` | Descrição da fase |
| `DURACAO_TOTAL` | Duração total |

## Impacto Esperado (ROI)
| Placeholder | Uso |
|---|---|
| `ROI_INTRO` | Lead |
| `ROI_METRICA_1..3` | Métrica (ex: "R$ 200K/ano") |
| `ROI_DESC_1..3` | Descrição da métrica |

## Investimento — Opções (GBB)
| Placeholder | Uso |
|---|---|
| `INVEST_INTRO` | Lead |
| `OPCAO_1_NOME` / `OPCAO_1_VALOR` / `OPCAO_1_ITEM_1..3` | Opção Essencial |
| `OPCAO_2_NOME` / `OPCAO_2_VALOR` / `OPCAO_2_ITEM_1..3` | Opção Recomendada (card destacado) |
| `OPCAO_3_NOME` / `OPCAO_3_VALOR` / `OPCAO_3_ITEM_1..3` | Opção Completa |
| `RACIONAL_PRECO` | Racional (ex: "investimento ≈ X% do valor gerado") |
| `PACOTE_LABEL` | Label do pacote (ex: "Pacote Completo — 10% off") |
| `PACOTE_VALOR` | Valor do pacote |

## Garantia
| Placeholder | Uso |
|---|---|
| `GARANTIA_DESC` | Lead |
| `GARANTIA_1..2` | O que garantimos |
| `RISCO_1..2` | Como reduzimos o risco |

## Condições Comerciais
| Placeholder | Uso |
|---|---|
| `COND_PAGAMENTO_1..2` | Pagamento (entrada + parcelas) |
| `COND_EXTRA_1..2` | Condições extras |

## Responsabilidades
| Placeholder | Uso |
|---|---|
| `RESP_INTRO` | Lead |
| `RESP_CONSULTORIA_1..2` | Compromissos da ID |
| `RESP_CLIENTE_1..3` | Compromissos do cliente |

## Sobre a ID Consultoria
| Placeholder | Uso |
|---|---|
| `SOBRE_ID_INTRO` | Lead |
| `ESPECIALIDADE_1..3` | Especialidades |
| `METODO_1..2` | Método |

## Próximos Passos
| Placeholder | Uso |
|---|---|
| `PROXIMOS_PASSOS_DESC` | Lead |
| `CONTATO_NOME` | Nome do contato |
| `CONTATO_CARGO` | Cargo |
| `CONTATO_EMAIL` | Email |
| `CONTATO_TELEFONE` | Telefone |

## Verificação
Após preencher: `grep -o '{{[A-Z_]*}}' Proposta_<cliente>.html` deve retornar **vazio** (nenhum placeholder restante).
