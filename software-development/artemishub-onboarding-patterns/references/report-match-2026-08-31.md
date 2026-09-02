# Relatório de Compatibilidade Empresa×Editais — modular, testado, dados vivos (2026-08-31)

**Solicitante:** Tácio — relatório beta enriquecido, 20 editais default, IDV Artemis, modular sem hardcode, com testes e conexão real PG, sem erro silencioso. Ver `src/lib/report/` e `src/components/empresa/ExportEmpresaMatchReport/`.

## Arquitetura

**Local:** `/empresas/:id` hero → `ExportEmpresaMatchReportButton` + modal (limite/scoreMin/flags/observações).

**IDV:** `ARTEMIS_TOKENS` em `tipos.ts` espelha `src/index.css` (`navy #0a192f`, `blue #0d47a1`, `green #009b50`, `yellow #ffc107`).

**Faixa beta:** `BETA_NOTICE` em `#ffc107` em todas as páginas: "Projeto beta — ArtemisHub pode conter erros de extração... Sempre valide no site oficial."

## Módulos

- `tipos.ts` — tokens, `BETA_NOTICE`, `MatchEnriquecido/ReportOptions/ReportData` (limite 20)
- `fetchReportData.ts` — `apiFetch` real (precisou `export async function apiFetch` em `offline-api.ts`), `GET /api/empresas-parque/{id}` + `GET /api/editais?limit=300` + `GET /api/analises-ia/{id}` em `Promise.allSettled` (best-effort só análises). Erro empresa/editais `throw`, nunca `catch(()=>{})`.
- `buildMatches.ts` — puro `calcScore/calcBreakdown`
- `formatReport.ts` — `linkDoEdital` com fallback `https://artemis.idconsultoria.ai/editais/{id}`
- `generateEmpresaReportPdf.ts` — recebe `ReportData` pronto (sem fetch), `jspdf`+`autoTable`, capa navy, tabela matches, fichas com link + análise enriquecida

## Testes vitest (jsdom)

`vitest@3.1.1 jsdom@24.1.0 @testing-library/react@16` + `vitest.config.ts` + `src/test-setup.ts`
- `buildMatches.test.ts` (3), `fetchReportData.test.ts` (3), `generatePdf.test.ts` (2) → 8/8
- `npx tsc --noEmit` 0, `npm run build` 12s, deploy Oracle `docker compose build && up -d` health ok

## Pitfalls
- Nunca mockar arrays no build final — dado vem de `apiFetch` vivo
- `Promise.allSettled` só para análises; empresa/editais são fatais
