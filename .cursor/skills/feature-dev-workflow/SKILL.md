---
name: feature-dev-workflow
description: Guides AI through a structured feature development lifecycle with planning, branching, building, committing, and pull requests. Use when the user wants to start a new feature, build something new, or asks to follow the dev workflow.
---

# Feature Development Workflow

This skill defines the end-to-end workflow for developing a new feature. Follow these phases in order. Never skip planning; never create a PR without tests.

## Phase 1: Ideation and Planning

**Goal**: Understand what we're building before writing any code.

1. Discuss the feature idea with the user
2. Ask clarifying questions (one at a time, per user preference)
3. Switch to Plan mode and create a plan using `CreatePlan`
4. **Do NOT make any code changes until the plan is approved**
5. Wait for explicit user approval before proceeding to Phase 2

## Phase 2: Branch Creation

**Goal**: Isolate the work on a feature branch.

Once the plan is approved:

1. Ensure the repo has no uncommitted changes on the current branch:
   ```bash
   git status
   ```
2. Create and checkout a new branch:
   ```bash
   git checkout -b feat/<short-description>
   ```
   - Use kebab-case for the description (e.g. `feat/grid-labels`, `feat/png-export`)
   - Keep it short -- 2-4 words max
3. Confirm to the user that the branch is ready

## Phase 3: Build

**Goal**: Implement the feature incrementally, following the plan.

1. Create todos from the plan using `TodoWrite` to track progress
2. Work through each todo one at a time
3. Follow all project conventions (see `.cursor/rules/`)
4. After completing each todo:
   - Check lints with `ReadLints` on edited files
   - Fix any introduced lint errors
   - Mark the todo as completed
   - Proceed to Phase 4 (commit) before starting the next todo

## Phase 4: Incremental Commits

**Goal**: Keep a clean, reviewable commit history with small, focused commits.

After completing each todo/task from the plan:

1. Stage and commit the relevant changes:
   ```bash
   git add <files>
   git commit -m "Descriptive message here"
   ```
2. **Commit message style**: Simple descriptive sentences
   - Start with a verb: "Add", "Fix", "Update", "Remove", "Refactor"
   - Examples: "Add grid label rendering", "Fix icon path for AWS nodes", "Update README with label docs"
   - No conventional commit prefixes (no `feat:`, `fix:`, etc.)
3. Only commit after verifying the change works (lints pass, no obvious breakage)
4. Return to Phase 3 for the next todo

## Phase 5: Finalize and Pull Request

**Goal**: Ensure quality, then open a PR for review.

When all todos are completed:

### Pre-PR checklist

Run through this checklist before creating the PR:

1. **Run tests**:
   ```bash
   uv run pytest
   ```
   If any test fails, fix it and commit the fix before proceeding.

2. **Update documentation** (per project rules):
   - Update `README.md` if the feature adds user-facing functionality
   - Update `docs/` pages if the API changed or a new feature was added
   - Add an example if appropriate
   - Commit documentation updates separately: "Update docs for <feature>"

3. **Review the full diff** against the base branch:
   ```bash
   git diff main...HEAD
   ```

### Create the Pull Request

**Strategy**: Try GitHub MCP first, fall back to `gh` CLI.

#### Option A: GitHub MCP

Check if a GitHub MCP server is available by looking in the MCP descriptors folder. If a server with pull request creation capabilities exists, use it:

```
CallMcpTool:
  server: <github-mcp-server-name>
  toolName: create_pull_request (or similar -- read the tool descriptor first)
  arguments:
    title: "<short feature summary>"
    body: "<PR body, see template below>"
    base: "main"
    head: "feat/<short-description>"
```

Always read the MCP tool descriptor before calling it to get the exact parameter names.

#### Option B: GitHub CLI fallback

If no GitHub MCP is available, use `gh`:

```bash
git push -u origin HEAD
gh pr create --title "<short feature summary>" --body "$(cat <<'EOF'
<PR body, see template below>
EOF
)"
```

### PR body template

```markdown
## Summary
- <1-3 bullet points describing what was built>

## Changes
- <list of notable implementation details>

## Test plan
- [ ] All existing tests pass (`uv run pytest`)
- [ ] <specific things to verify for this feature>

## Docs
- <list of documentation updates made, or "No docs changes needed">
```

### After PR creation

- Share the PR URL with the user
- The workflow is complete

## Phase Transitions Summary

```
Idea --> Plan (no code!) --> Branch --> Build/Commit loop --> Tests + Docs --> PR
```

Only move forward when the current phase is fully complete. If something fails (tests, lints), fix it in the current phase before advancing.
