#!/bin/bash

# GitHub CLI Permanent Connection Setup Script

echo "=== GitHub CLI Permanent Connection Setup ==="
echo

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI not found. Please install it first with: brew install gh"
    exit 1
fi

# Check current auth status
echo "Checking current authentication status..."
if gh auth status &> /dev/null; then
    echo "✓ Already authenticated with GitHub!"
    gh auth status
    echo
    echo "To switch accounts or re-authenticate, run: gh auth logout"
else
    echo "Not authenticated. Starting setup..."
    echo
    echo "Choose authentication method:"
    echo "1) Login with web browser (recommended)"
    echo "2) Login with authentication token"
    echo
    read -p "Enter choice (1 or 2): " choice

    case $choice in
        1)
            echo
            echo "Starting browser-based authentication..."
            echo "This will open your browser to authenticate with GitHub."
            echo
            gh auth login --web --git-protocol https
            ;;
        2)
            echo
            echo "To use a Personal Access Token:"
            echo "1. Go to https://github.com/settings/tokens"
            echo "2. Click 'Generate new token (classic)'"
            echo "3. Select scopes: repo, workflow, read:org"
            echo "4. Copy the token"
            echo
            read -p "Paste your token here: " token
            echo $token | gh auth login --with-token
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

# Configure git credential helper for HTTPS
echo
echo "Configuring Git credential helper..."
gh auth setup-git

# Set up additional Git configurations
echo
echo "Current Git configuration:"
echo "User: $(git config user.name)"
echo "Email: $(git config user.email)"

# Test the connection
echo
echo "Testing GitHub connection..."
if gh auth status; then
    echo
    echo "✓ GitHub CLI is successfully configured!"
    echo
    echo "You can now use commands like:"
    echo "  gh repo list              - List your repositories"
    echo "  gh repo clone owner/repo  - Clone a repository"
    echo "  gh pr list                - List pull requests"
    echo "  gh issue list             - List issues"
    echo
    echo "Your Git operations will now use GitHub CLI for authentication."
else
    echo "❌ Authentication failed. Please try again."
    exit 1
fi
