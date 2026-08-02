# Pre-Merge Branch Divergence Analysis

Before merging a feature branch into a target (usually `master`), assess divergence to anticipate conflicts and pick the right strategy.

## Quick Divergence Check

```bash
# Ahead/behind counts
git rev-list --left-right --count master...feature-branch

# Interpretação (two numbers: behind ahead):
# 0 35 → feature is 35 ahead, master has nothing new → clean fast-forward
# 8 35 → diverged: 8 commits on master, 35 on feature → likely conflicts
# 0 0  → identical → nothing to merge
```

## Full Assessment Sequence

```bash
# 1. Merge-base (common ancestor)
git merge-base master feature-branch

# 2. Count divergence each way
echo "feature is $(git rev-list --count feature-branch ^master) commits ahead"
echo "master is  $(git rev-list --count master ^feature-branch) commits behind"

# 3. See what each side has that the other doesn't
git log --oneline master ^feature-branch   # new on master only
git log --oneline feature-branch ^master    # new on feature only

# 4. First-parent history to understand branch structure
git log --oneline --first-parent master | head -10

# 5. Check if there were any previous merges between these branches
git log --all --oneline --grep="feature-branch" --merges

# 6. Dry-run the merge (detects conflicts without committing)
git merge --no-commit --no-ff feature-branch 2>&1 || echo "CONFLICTS FOUND"
git merge --abort 2>/dev/null
```

## Thresholds

| Ahead | Behind | Risk | Recommended action |
|-------|--------|------|--------------------|
| 0     | N      | None | Fast-forward merge |
| 1–5   | 0      | Low  | Direct merge |
| 0     | 1–5    | Low  | Rebase + push |
| 1–5   | 1–5    | Medium | PR with CI checks |
| 6+    | 6+     | **High** | Create PR for manual conflict resolution — do NOT attempt terminal merge |

## Recovery After Failed Merge

If `git merge` created conflicts and left a dirty tree:

```bash
git merge --abort
```

Then offer the user three options:
1. **PR route** — push the feature branch as-is and create a PR; GitHub's conflict UI is far better than resolving dozens of conflicts in a terminal
2. **Cherry-pick** — if only a few feature commits are needed, cherry-pick them onto a clean master: `git checkout master && git cherry-pick <sha1> <sha2>`
3. **Force-push** — only when you own the branch exclusively and its history is correct; `git push origin feature-branch --force` then merge via PR
