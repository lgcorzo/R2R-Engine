---
name: protect_branch
description: "Process to secure a GitHub repository by requiring code owner approval and branch protection."
---

# Skill: Protect Branch

This skill defines the process to secure a GitHub repository so that only authorized users (code owners) can approve Pull Requests.

## Prerequisites

1.  **GitHub CLI (`gh`)**: Must be installed and authenticated.
2.  **Git**: Repository must be local and connected to a remote.

## Steps

### 1. Identify User and Repository
Get the authenticated user and repository details.
```bash
gh auth status
git remote -v
git branch --show-current
```

### 2. Create CODEOWNERS
Define who can approve changes. Replace `@user` with the authorized GitHub username.
```bash
mkdir -p .github
echo "* @user" > .github/CODEOWNERS
git add .github/CODEOWNERS
git commit -m "Add CODEOWNERS file"
git push origin <branch_name>
```

### 3. Apply Branch Protection
Use the GitHub API to enforce code owner reviews and a minimum approval count.
```bash
echo '{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null
}' | gh api --method PUT /repos/:owner/:repo/branches/:branch/protection --input -
```

## Verification
Confirm the configuration.
```bash
gh api /repos/:owner/:repo/branches/:branch/protection
```
