# Test-Fix Loop Pattern (Sprint Engineering QA)

Pattern used in Sprint 1 TaskFlow to achieve 100% green suite: 199 passed, 1 xpassed, 1 warning.

## Flow

```
Pi cost generates code (47 tasks)           → Layer 1
  ├── Hermes deploys + fixes permissions    → Layer 1.5
Agy review (tmux, diagnosis)               → Layer 2
  └── feedbacks.md with problem table
Pi best (dedicated session, MiniMax M3)    → Layer 3 ($~0.60)
  └── rewriters broken services/routes
Agy (final fix pass, via tmux -x 120 -y 40)→ Layer 4
  └── fixes: MissingGreenlet, conftest paths, cleanup tests
Hermes verify (run suite in container)     → Layer 5
  └── 199 passed → ACORDO: SPRINT N CONCLUIDA
```

## Key invariants

- Every layer writes back to the shared volume (`/opt/data/code/workstation/`) — never trust tool-only state
- Agy runs on the HOST (via SSH), not in the container — faster disk I/O, correct UID for file writes
- Pi best runs in the CONTAINER (local) — lower latency to shared volume
- Agy final pass uses `tmux -x 120 -y 40` (critical — without these flags the session crashes)
- Always kill old agy sessions before creating new ones (leak: observed 24h+ stale sessions)
- After agy completes, the watchdog `tail` may show 0 lines (tmux server dies when last window closes) — check file modification on the shared volume instead
