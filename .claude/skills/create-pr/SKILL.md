---
name: create-pr
description: Create a pull request on a GitHub repository. Use when user wants to submit changes to a repo, update documentation, or contribute code. Handles cloning, branching, committing, and PR creation.
---

# Create Pull Request Skill

Create pull requests on GitHub repositories with proper formatting and workflow.

## When to Use

- User wants to submit changes to a GitHub repo
- User wants to update documentation in an upstream repo
- User has local changes that need to be PR'd to another repository
- User says "create a PR", "submit changes", "open pull request"

## Requirements

- `gh` CLI must be authenticated (`gh auth status`)
- User must have push access to the repo (or fork permissions)

## Workflow

### Step 1: Gather Information

Ask the user for:
1. **Target repo** - GitHub URL or `owner/repo` format
2. **Changes** - Files to copy, or description of changes to make
3. **Branch name** - Suggest based on change type (e.g., `fix/issue-description`, `feat/new-feature`)
4. **PR title** - Short, descriptive title
5. **PR description** - What changed and why

### Step 2: Clone and Branch

```bash
# Clone to temp directory
cd /tmp && rm -rf {repo-name} && gh repo clone {owner/repo}
cd {repo-name}

# Create feature branch
git checkout -b {branch-name}
```

### Step 3: Apply Changes

Either:
- **Copy files** from user's local directory
- **Edit files** directly based on user's instructions
- **Create new files** as needed

### Step 4: Commit

Use conventional commit format:

```bash
git add .
git commit -m "$(cat <<'EOF'
{type}({scope}): {description}

{body - bullet points of changes}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {model} <noreply@anthropic.com>
EOF
)"
```

**Commit types:**
- `fix` - Bug fixes
- `feat` - New features
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `chore` - Maintenance tasks

### Step 5: Push and Create PR

```bash
# Push branch
git push -u origin {branch-name}

# Create PR
gh pr create --title "{title}" --body "$(cat <<'EOF'
## Summary
{bullet points of changes}

## Test plan
{how to verify the changes}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 6: Report

Return the PR URL to the user.

## Example Usage

**User:** "Create a PR to update the README in OpenBB-finance/backends-for-openbb"

**Assistant:**
1. Clone repo to `/tmp/backends-for-openbb`
2. Create branch `docs/update-readme`
3. Make changes to README.md
4. Commit with `docs: update README`
5. Push and create PR
6. Return PR URL

## Error Handling

| Error | Solution |
|-------|----------|
| `gh auth` fails | Ask user to run `gh auth login` |
| Push rejected | Check if user has write access, suggest fork |
| Branch exists | Delete or use different name |
| No changes | Inform user, skip PR creation |

## Fork Workflow

If user doesn't have push access:

```bash
# Fork the repo first
gh repo fork {owner/repo} --clone

# Push to fork
git push -u origin {branch-name}

# Create PR from fork
gh pr create --title "{title}" --body "{body}"
```
