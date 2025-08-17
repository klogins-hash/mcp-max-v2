# GitHub CLI Permanent Connection Setup

## Quick Setup

Run the setup script:
```bash
./setup-github-cli.sh
```

## Manual Setup Options

### Option 1: Browser Authentication (Recommended)
```bash
gh auth login --web --git-protocol https
```

### Option 2: Personal Access Token
1. Generate token at: https://github.com/settings/tokens
2. Required scopes: `repo`, `workflow`, `read:org`
3. Login with token:
```bash
gh auth login --with-token
```

## Make Connection Permanent

1. **Configure Git to use GitHub CLI**:
```bash
gh auth setup-git
```

2. **Set Git credential caching** (keeps credentials for 1 hour):
```bash
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'
```

3. **For permanent storage on macOS** (already configured):
```bash
git config --global credential.helper osxkeychain
```

## Verify Connection
```bash
gh auth status
gh repo list --limit 5
```

## Environment Variable (Optional)
Add to `~/.zshrc` for automatic token usage:
```bash
export GITHUB_TOKEN=$(gh auth token)
```

## Useful Commands
- `gh repo clone owner/repo` - Clone repositories
- `gh pr create` - Create pull requests
- `gh issue list` - List issues
- `gh workflow run` - Trigger workflows
