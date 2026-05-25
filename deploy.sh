#!/bin/bash
# Deploy to GitHub Pages
set -e

cd D:/budget

# Add all changed files
git add -A

# Commit
git commit -m "fix: SW periodic update check + voice auto-retry on mobile

- Bump SW cache to v3 for fresh install
- Add periodic SW update check every 30 min
- Add force-refresh button in header and summary
- Add app version display
- Voice: add timing guard (2s minimum) to prevent flicker on mobile
- Voice: auto-retry once if recognition ends too quickly
- Voice: track gotResult flag to avoid double-retry
- Voice: add onstart handler to track start timestamp

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>" || echo "Nothing to commit"

# Push
git push origin main
