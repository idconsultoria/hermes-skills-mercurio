---
name: github-pr-workflow
description: "GitHub umbrella — authentication, PR lifecycle, code review, and repo management.

Load this skill for any GitHub operation: auth (PAT, SSH, gh CLI), branch-and-PR workflows, code review with inline comments, and repository management (clone, create, fork, releases, secrets, CI). Uses gh CLI and REST API with curl fallbacks for headless environments."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    keywords: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge, PR-preview, Nginx-Proxy-Manager, ARM64, deployment]
    related_skills: [github-auth, github-code-review, deployment-pipeline, oracle-host-access]
---

# GitHub — Complete Workflow Umbrella

Covers the full GitHub lifecycle: authentication, repository management, pull request workflow, and code review. Each section shows `gh` first, then `git` + `curl` fallback.

## GitHub Authentication

Set up GitHub authentication for agent workflows. Two paths: `gh` CLI (richer API) or `git` + `curl` (always available). See `references/github-auth-headless-pat-setup.md` for non-interactive PAT storage and `scripts/gh-env-auth.sh` for quick auth detection.

### Detection Flow

```bash
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → use `gh` everywhere
2. If `gh` installed but not authenticated → use `gh auth login`
3. If `gh` not installed → use `git` + `curl` with personal access token

### Quick Auth Detection (reusable snippet)

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
```

### Install gh Without sudo (Linux)
```bash
ARCH=$(uname -m)
case "$ARCH" in x86_64|amd64) GH_ARCH="amd64" ;; aarch64|arm64) GH_ARCH="arm64" ;; *) echo "Unsupported"; exit 1 ;; esac
LATEST=$(curl -sI "https://github.com/cli/cli/releases/latest" | grep -i "^location:" | grep -oP 'tag/v\K[0-9.]+')
curl -sL "https://github.com/cli/cli/releases/download/v${LATEST}/gh_${LATEST}_linux_${GH_ARCH}.tar.gz" -o /tmp/gh.tar.gz
tar xzf /tmp/gh.tar.gz -C /tmp/
mkdir -p ~/.local/bin && cp "/tmp/gh_${LATEST}_linux_${GH_ARCH}/bin/gh" ~/.local/bin/gh && chmod +x ~/.local/bin/gh
```

### Token-Based Login (Headless)
```bash
env -u GITHUB_TOKEN gh auth login --with-token <<< "$GITHUB_TOKEN"
gh auth setup-git
```

> **Full auth reference:** `references/github-auth-headless-pat-setup.md` — SSH keys, PAT scopes (`repo`, `workflow`, `read:org`), credential helpers, git identity config, multi-account patterns.

## Pull Request Workflow

Complete PR lifecycle: branch → commit → open PR → CI checks → merge.

## Prerequisites

- Authenticated with GitHub (see Authentication section above)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

> The auth snippet above is the single source. See `scripts/gh-env-auth.sh` for a standalone version.

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

### Pitfall: Branch checkout from detached HEAD creates the wrong name

When checking out a branch from a detached HEAD state (e.g., after a `cherry-pick` on a temp branch), `git checkout <branch-name>` creates a **local branch tracking `origin/<branch-name>`** but the local name can be `temp-fix-branch` if you were on a branch with that name.

**Check before pushing:**

```bash
# Always verify the BRANCH NAME matches what you intend to push
git branch --show-current
# If it says 'temp-fix-branch' when you wanted 'feat/my-feature':
git checkout -B feat/my-feature origin/feat/my-feature
git cherry-pick temp-fix-branch
git branch -D temp-fix-branch
git push origin feat/my-feature
```

### Recovery: committed directly to master by accident

If you committed directly to `master` (or `main`) and need to move the commit into a PR:

```bash
# 1. Create a branch from the unintended commit (keeps the commit)
git branch feat/my-feature

# 2. Reset master back to before your commit (local only)
#    Use git log to find the commit hash just before yours
git log --oneline -5
git reset --hard <hash-before-your-commit>

# 3. Push the feature branch
git push -u origin feat/my-feature

# 4. Create PR from the branch
#    gh pr create --base master --head feat/my-feature

# IMPORTANT: Do NOT force-push master after reset.
# Many CI/CD setups block force-push to master for safety.
# Instead, create the PR from the branch and merge normally.
```

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 4. CI Monitoring & Auto-Fixing

For CI monitoring, auto-fixing CI failures, and preview deployment, see `deployment-pipeline`.

## 5. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 6. Code Review

Perform code reviews on local changes before pushing, or review open PRs on GitHub. See `references/code-review-output-template.md` for the review output format.

### Reviewing Local Changes (Pre-Push)
```bash
git diff main...HEAD --stat      # scope
git diff main...HEAD              # full diff
git diff main...HEAD --name-only  # file list
```

### Review Checklist
- **Correctness:** Edge cases handled? Error paths graceful?
- **Security:** No hardcoded secrets, input validation, SQL injection/XSS
- **Code Quality:** Clear naming, no duplication, single-responsibility functions
- **Testing:** New code paths tested? Edge cases covered?
- **Performance:** No N+1 queries, appropriate caching, no blocking ops in async paths
- **Documentation:** Public APIs documented, non-obvious logic explained

### Leave Inline Review Comments
```bash
# With gh
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."

# With curl — atomic multi-comment review
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{\"commit_id\":\"$HEAD_SHA\",\"event\":\"COMMENT\",\"body\":\"Review\",\"comments\":[...]}"
```

> **Full code review workflow:** `references/code-review-output-template.md` — structured output format, review checklist, end-to-end PR review recipe with checkout + test + post pattern.




## 7. Repository Management

Clone, create, fork, and manage repos. See `references/github-api-cheatsheet.md` for the full reference table.

### Common Operations
```bash
# Clone
git clone https://github.com/owner/repo.git
git clone --depth 1 https://github.com/owner/repo.git  # shallow

# Create (gh)
gh repo create my-project --public --clone

# Create (curl)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name":"my-project","private":false,"auto_init":true}'

# Fork
gh repo fork owner/repo --clone

# Releases
gh release create v1.0.0 --generate-notes

# Secrets
gh secret set API_KEY --body "value"

# Workflows
gh workflow list
gh run list --limit 10
gh run rerun <RUN_ID> --failed
```

### Committing Files Without a Local Clone
Use the Git Data API (blob→tree→commit→refs) or the simpler Contents API for single-file edits. See `references/github-api-cheatsheet.md` for full curl equivalents and the Python blob/tree/commit/refs pattern.

> **Full repo management reference:** `references/github-api-cheatsheet.md` — all operations with gh + curl fallbacks.

## 8. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see `deployment-pipeline` skill)

# 8. Merge when green (see Section 5)
```

## Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
