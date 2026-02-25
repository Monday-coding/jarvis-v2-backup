#!/bin/bash
# Backup script to push changes to GitHub
# Usage: Run manually or schedule with cron

cd /home/jarvis/.openclaw/workspace

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to backup."
    exit 0
fi

# Add all changes
git add .

# Commit with timestamp
git commit -m "Backup: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin master

echo "Backup completed at $(date)"
