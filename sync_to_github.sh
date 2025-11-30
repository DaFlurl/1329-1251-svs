#!/bin/bash

echo "Setting up GitHub synchronization..."
echo

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Please set GITHUB_TOKEN environment variable"
    echo "Example: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

echo "Creating GitHub repository..."
python tools/github_manager.py sync

if [ $? -eq 0 ]; then
    echo
    echo "Success! Repository synchronized to GitHub"
    echo
    echo "Repository URL: https://github.com/FlorinStrobel/AgentDaf1.1"
    echo "Branch: feature/user-profile-enhancement-2"
else
    echo
    echo "Failed to synchronize to GitHub"
    echo "Please check your token and network connection"
fi