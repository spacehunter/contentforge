#!/bin/bash
# ContentForge Daily Morning Status Report
# Delivered to telegram: Home channel

CF_DIR="/home/nova/contentforge"
LOGS_DIR="$CF_DIR/.dev"
REPORT_FILE="/tmp/contentforge-morning-report.txt"
DATE=$(date '+%A, %B %d, %Y')

echo "📊 CONTENTFORGE DAILY STATUS REPORT" > "$REPORT_FILE"
echo "Date: $DATE" >> "$REPORT_FILE"
echo "======================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Git stats
cd "$CF_DIR" 2>/dev/null || exit 0
if [ -d .git ]; then
  echo "📝 Git Activity:" >> "$REPORT_FILE"
  git log --oneline --since="24 hours ago" 2>/dev/null | sed 's/^/  /' >> "$REPORT_FILE" || echo "  No commits in last 24h" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
fi

# Line counts
echo "📁 Codebase Stats:" >> "$REPORT_FILE"
find "$CF_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.css" \) -not -path "*/node_modules/*" -not -path "*/.venv/*" | wc -l | sed 's/^/  Files: /' >> "$REPORT_FILE"

# ROADMAP progress
echo "" >> "$REPORT_FILE"
echo "📋 ROADMAP Progress:" >> "$REPORT_FILE"
if [ -f "$CF_DIR/ROADMAP.md" ]; then
  grep -E '^\s*- \[.(.)\]' "$CF_DIR/ROADMAP.md" | sed 's/^/  /' >> "$REPORT_FILE" || echo "  (No tasks tracked)" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "🚀 Working toward monetizable SaaS — each hour = 1 feature." >> "$REPORT_FILE"

cat "$REPORT_FILE"