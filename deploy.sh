#!/bin/bash
# Deploy to GitHub Pages
set -e

cd D:/budget

# Add all changed files
git add -A

# Commit
git commit -m "feat: quiz PWA with Excel import, chapter support, statistics

- Add Excel (.xlsx/.xls) import via SheetJS
- Add chapter/organization system for question banks
- Add chapter filter chips on home screen
- Add append-to-existing-bank import flow
- Support sequential/shuffled/random/wrong-answer practice modes
- Add statistics with per-question accuracy tracking
- Touch swipe navigation with answer feedback
- Full offline PWA with service worker

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>" || echo "Nothing to commit"

# Push to master branch
git push origin master
