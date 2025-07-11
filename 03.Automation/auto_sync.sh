#!/bin/bash

# Obsidian Auto Sync Script
# 毎日のタスクを自動同期

# ログファイルの設定
LOG_FILE="/Users/tekitoo/Library/Mobile Documents/iCloud~md~obsidian/Documents/03.Automation/sync.log"
SCRIPT_DIR="/Users/tekitoo/Library/Mobile Documents/iCloud~md~obsidian/Documents/03.Automation"

# 現在の日時をログに記録
echo "=== Auto Sync Started: $(date) ===" >> "$LOG_FILE"

# 仮想環境をアクティベート
cd "$SCRIPT_DIR"
source venv/bin/activate

# 同期スクリプトを実行
python3 bidirectional_sync.py >> "$LOG_FILE" 2>&1

# 実行結果をログに記録
if [ $? -eq 0 ]; then
    echo "✅ Auto sync completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "❌ Auto sync failed at $(date)" >> "$LOG_FILE"
fi

echo "=== Auto Sync Ended: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"