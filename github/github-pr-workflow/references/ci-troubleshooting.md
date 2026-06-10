# CI Troubleshooting Quick Reference

Common CI failure patterns and how to diagnose them from the logs.

## Reading CI Logs

```bash
# With gh
gh run view <RUN_ID> --log-failed

# With curl — download and extract
curl -sL -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/actions/runs/<RUN_ID>/logs \
  -o /tmp/ci-logs.zip && unzip -o /tmp/ci-logs.zip -d /tmp/ci-logs
```

## Common Failure Patterns

### Test Failures

**Signatures in logs:**
```
FAILED tests/test_foo.py::test_bar - AssertionError
E       assert 42 == 43
ERROR tests/test_foo.py - ModuleNotFoundError
```

**Diagnosis:**
1. Find the test file and line number from the traceback
2. Use `read_file` to read the failing test
3. Check if it's a logic error in the code or a stale test assertion
4. Look for `ModuleNotFoundError` — usually a missing dependency in CI

**Common fixes:**
- Update assertion to match new expected behavior
- Add missing dependency to requirements.txt / pyproject.toml
- Fix flaky test (add retry, mock external service, fix race condition)

---

### Lint / Formatting Failures

**Signatures in logs:**
```
src/auth.py:45:1: E302 expected 2 blank lines, got 1
src/models.py:12:80: E501 line too long (95 > 88 characters)
error: would reformat src/utils.py
```

**Diagnosis:**
1. Read the specific file:line numbers mentioned
2. Check which linter is complaining (flake8, ruff, black, isort, mypy)

**Common fixes:**
- Run the formatter locally: `black .`, `isort .`, `ruff check --fix .`
- Fix the specific style violation by editing the file
- If using `patch`, make sure to match existing indentation style

---

### Type Check Failures (mypy / pyright)

**Signatures in logs:**
```
src/api.py:23: error: Argument 1 to "process" has incompatible type "str"; expected "int"
src/models.py:45: error: Missing return statement
```

**Diagnosis:**
1. Read the file at the mentioned line
2. Check the function signature and what's being passed

**Common fixes:**
- Add type cast or conversion
- Fix the function signature
- Add `# type: ignore` comment as last resort (with explanation)

---

### Build / Compilation Failures

**Signatures in logs:**
```
ModuleNotFoundError: No module named 'some_package'
ERROR: Could not find a version that satisfies the requirement foo==1.2.3
npm ERR! Could not resolve dependency
```

**Diagnosis:**
1. Check requirements.txt / package.json for the missing or incompatible dependency
2. Compare local vs CI Python/Node version

**Common fixes:**
- Add missing dependency to requirements file
- Pin compatible version
- Update lockfile (`pip freeze`, `npm install`)

---

### Permission / Auth Failures

**Signatures in logs:**
```
fatal: could not read Username for 'https://github.com': No such device or address
Error: Resource not accessible by integration
403 Forbidden
```

**Diagnosis:**
1. Check if the workflow needs special permissions (token scopes)
2. Check if secrets are configured (missing `GITHUB_TOKEN` or custom secrets)

**Common fixes:**
- Add `permissions:` block to workflow YAML
- Verify secrets exist: `gh secret list` or check repo settings
- For fork PRs: some secrets aren't available by design

---

### Timeout Failures

**Signatures in logs:**
```
Error: The operation was canceled.
The job running on runner ... has exceeded the maximum execution time
```

**Diagnosis:**
1. Check which step timed out
2. Look for infinite loops, hung processes, or slow network calls

**Common fixes:**
- Add timeout to the specific step: `timeout-minutes: 10`
- Fix the underlying performance issue
- Split into parallel jobs

---

### Docker / Container Failures

**Signatures in logs:**
```
docker: Error response from daemon
### Docker / Container Failures

**Signatures in logs:**
```\ndocker: Error response from daemon\nfailed to solve: ... not found\nCOPY failed: file not found in build context\n```

**Diagnosis:**
1. Check Dockerfile for the failing step\n2. Verify the referenced files exist in the repo

**Common fixes:**
- Fix path in COPY/ADD command
- Update base image tag
- Add missing file to `.dockerignore` exclusion or remove from it

---

### SSH Deploy Failures (appleboy/ssh-action)

**Signatures in logs:**
```\nlevel=warning msg="The \\\"PR_NUMBER\\\" variable is not set. Defaulting to a blank string."\nreference "...:pr-": not found\n```

**Root cause:** Shell variables set via `VAR=value` on one line are NOT exported to child processes. `docker compose pull` can't see the variable.

**Fix:** Add `export VAR_NAME` after setting it, before any `docker compose` commands.

**Full pattern:**
```\nscript: |\n  PR_NUMBER=${{ github.event.number }}\n  export PR_NUMBER\n  docker compose pull\n  docker compose up -d\n```

---

### Workflow File Validation Failures (Zero Jobs)

**Signatures:** Run fails instantly with "workflow file issue", zero jobs in the run, no logs.

**Root cause:** GitHub's YAML parser accepts the file (no syntax error) but rejects its semantic structure.

**Common causes:**
- `needs:` referencing a job with incompatible `if:` condition (creates scheduling deadlock that GitHub can't resolve)
- Backtick escaping issues inside YAML `|` blocks with JavaScript template literals
- Missing `github-token` on `actions/github-script@v7`
- Incorrect quoting of expressions like `github.event.action != 'closed'` (use single or double quotes consistently)

**Fix:** Simplify the workflow — inline dependent jobs, remove `needs`, use string concatenation in JS instead of template literals, add explicit `github-token`.

---

### TypeScript Build Failures in Docker

**Signatures:**
```\n#16 ERROR: process "/bin/sh -c npm run build" did not complete successfully: exit code: 2\nerror TS2307: Cannot find module '...'\nerror TS2322: Type '...' is not assignable to type '...'\n```

**Root cause:** `tsc -b` (used by `npm run build`) is stricter than `vitest`. Vitest uses `esbuild`/`vite` for transform and may skip type-checking in files not under test.

**Common patterns that vitest misses but tsc catches:**
- Wrong import paths (`../../` instead of `../`) in test files — vitest resolves them via vite config aliases, tsc doesn't
- `require()` calls in ESM `.tsx` files
- Missing props in component interfaces (passing `selected`, `selectionIndex` to a component that doesn't declare them)
- `addEventListener("keydown", handler)` where handler type is `(e: KeyboardEvent) => void` but `EventListener` expects `(e: Event) => void`

**Fix:** Run `npm run build` (or `tsc -b`) BEFORE pushing. If `vitest` passes but the build fails, it's a real TypeScript error, not a CI environment issue.

---

### Permission / Auth Failures

```
CI Failed
├── Test failure
│   ├── Assertion mismatch → update test or fix logic
│   └── Import/module error → add dependency
├── Lint failure → run formatter, fix style
├── Type error → fix types
├── Build failure
│   ├── Missing dep → add to requirements
│   └── Version conflict → update pins
├── Permission error → update workflow permissions (needs user)
└── Timeout → investigate perf (may need user input)
```

## Re-running After Fix

```bash
git add <fixed_files> && git commit -m "fix: resolve CI failure" && git push

# Then monitor
gh pr checks --watch 2>/dev/null || \
  echo "Poll with: curl -s -H 'Authorization: token ...' https://api.github.com/repos/.../commits/$(git rev-parse HEAD)/status"
```
