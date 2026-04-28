#!/bin/bash
# ContentForge Hourly Development - ~/.hermes/cron/hourly/contentforge-dev.sh

CF_DIR="/home/nova/contentforge"
LOG_FILE="/home/nova/contentforge/.dev/hourly-$(date +\%Y\%m\%d\%H).log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$CF_DIR/.dev"
(
  echo "=== ContentForge Dev Run: $DATE ==="
  echo ""
  
  # Check what todo/roadmap task is next
  if [ -f "$CF_DIR/ROADMAP.md" ]; then
    echo "--- Current ROADMAP ---"
    head -40 "$CF_DIR/ROADMAP.md"
    echo ""
  fi
  
  # Track git status
  cd "$CF_DIR" 2>/dev/null || exit 0
  if [ -d .git ]; then
    echo "--- Git Status ---"
    git status --short
    git log --oneline -3
    echo ""
  fi
  
  # Check if server is running
  echo "--- Backend Health ---"
  curl -s http://localhost:8000/health || echo "Backend not running"
  
  echo ""
  echo "=== Run Complete ==="
) >> "$LOG_FILE" 2>&1

# Keep only last 48 logs
find "$CF_DIR/.dev" -name "hourly-*.log" -mmin +2880 -delete 2>/dev/null
