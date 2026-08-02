# Frontend Overdue Diagnostic — Jul 2026

## Problema

Tarefas atrasadas aparecem em **Próximos 7 Dias** (Upcoming) mas **não** em **Hoje** (Today),
embora ambos usem a mesma query: `GET /tasks/?status=inbox,next_action,waiting&due_before=<startOfDay>`.

## Diagnóstico (rastreio completo)

### 1. DB production — dados corretos

```sql
-- Via SSH → docker exec taskflow-db psql
SELECT id, title, status, due_date
FROM tasks
WHERE user_id = 'c9223bfd-...'  -- Gustavo Mello
  AND status IN ('inbox','next_action','waiting')
  AND due_date <= '2026-07-28T03:00:00Z';

-- → 4 tasks retornadas (correto)
```

### 2. Chamada direta à API — funciona

```bash
curl -s "http://localhost:8000/api/v1/tasks/?status=inbox,next_action,waiting\
&due_before=2026-07-28T03:00:00Z&limit=20" \
  -H "Authorization: Bearer $TOKEN"
# → Retorna as 4 tasks com is_overdue: true, overdue_days: 1+
```

### 3. Component trace — a causa

**Today.tsx** usa `<TaskList>` que contém `useInfiniteQuery`. Durante o loading inicial,
o componente renderiza `<TaskListSkeleton />`, **engolindo a prop `overdueTasks`**:

```tsx
// TaskList.tsx — linhas 178-189
if (isLoading) {
    return (
      <div>
        <div className="px-6 py-5 border-b border-border">
          <h1>{title}</h1>
        </div>
        <TaskListSkeleton />
      </div>
    );
}
```

**Upcoming.tsx** renderiza a seção de atrasadas **inline** (fora de qualquer componente
com loading state), então ela aparece independentemente da query principal.

### 4. `_to_local_date` no ReportService — bug de timezone

```python
# report_service.py:442
@staticmethod
def _to_local_date(dt: datetime) -> date:
    return dt.astimezone(timezone.utc).date()  # ❌ usa UTC, não BRT
```

Isso afeta o **Panorama (MorningReport)** — tasks com `due_date = 2026-07-28T02:59:00Z`
(que são 23:59 BRT de 27/07) são classificadas como 28/07, não 27/07.

### 5. Efeito da normalização de date-only

O commit `07045eb` normaliza tasks **date-only**:

```
input:  "2026-07-27T00:00:00Z", due_date_has_time=false
output: 2026-07-28T02:59:00Z  (23:59 BRT = 02:59+00:00 do dia seguinte)
```

Isso é correto para representar "fim do dia 27 no BRT", mas significa que a
comparação `due_before = startOfDay(BRT)` precisa ser 03:00Z para incluir essas tasks.

## Como reproduzir

1. Criar task com `due_date=2026-07-27T00:00:00Z, due_date_has_time=false, status=next_action`
2. A API retorna `due_date: 2026-07-28T02:59:00Z` e `is_overdue: true`
3. Abrir /today → se a query principal do TaskList ainda estiver carregando,
   o skeleton oculta a seção de atrasadas
4. Abrir /upcoming → a seção inline de atrasadas aparece (não depende de skeleton)

## Correções necessárias

1. **Today.tsx**: extrair a seção de atrasadas para renderizar inline (fora do TaskList),
   igual ao Upcoming.tsx faz. Ou modificar TaskList para renderizar a seção mesmo
   durante isLoading.

2. **report_service.py**: `_to_local_date` deve usar o timezone do usuário (GMT-3):
   ```python
   return dt.astimezone(timezone(timedelta(hours=-3))).date()
   ```

## Referências

- `Today.tsx` — query key `["tasks", "overdue-today"]`
- `Upcoming.tsx` — query key `["tasks", "overdue-upcoming"]`, seção inline
- `TaskList.tsx` — `useInfiniteQuery(["tasks", filters])`, skeleton no isLoading
- `task_repository.py` — `due_before` filter: `Task.due_date <= due_before`
- `report_service.py` — `_to_local_date` com UTC bug
- Commit `07045eb` — timezone fix para date-only tasks
