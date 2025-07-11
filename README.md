# 📝 Obsidian Sync Scripts

Obsidian Vaultのタスク管理とデータ同期のためのスクリプト集です。

## 🚀 機能

### 1. Todoistとの双方向同期
- **bidirectional_sync.py**: TodoistとObsidianの双方向タスク同期
- **daily_tasks_sync.py**: 毎日のタスク自動同期

### 2. Discord連携
- **discord-meeting-minutes-bot**: 会議録自動生成
- **discord-voice-memo-bot**: 音声メモ自動変換
- **discord-obsidian-bot**: Obsidianデータ連携

### 3. 自動化システム
- **Gas Discord News Bot**: RSS配信自動化
- **Notion連携**: データ同期とバックアップ

## 📁 ディレクトリ構成

```
├── 01.Projects/          # プロジェクト関連
│   ├── discord-meeting-minutes-bot/
│   ├── discord-voice-memo-bot/
│   └── gas-discord-news-bot/
├── 02.Development/       # 開発環境
├── 03.Automation/        # 自動化スクリプト
│   ├── bidirectional_sync.py
│   └── discord-obsidian-bot/
├── 04.Config/           # 設定ファイル
│   └── obsidian-sync-README.md
├── 05.Archive/          # アーカイブ
└── ObsidianVault/       # Obsidianボールト
```

## 🛠️ セットアップ

### 前提条件
- Python 3.11+
- Todoist API Token
- Discord Bot Token（Discord連携を使用する場合）

### 環境設定

1. **環境変数の設定**
```bash
export TODOIST_API_TOKEN="your_todoist_api_token"
export DISCORD_BOT_TOKEN="your_discord_bot_token"
```

2. **依存関係のインストール**
```bash
cd 03.Automation
pip install -r requirements.txt
```

3. **同期スクリプトの実行**
```bash
python bidirectional_sync.py
```

## 📋 使用方法

### 毎日のタスク同期
```bash
# 手動実行
python 03.Automation/bidirectional_sync.py

# 自動実行（cronで設定）
0 7 * * * cd /path/to/obsidian-sync-scripts && python 03.Automation/bidirectional_sync.py
```

### Discord連携
各Discord Botのディレクトリ内のREADMEを参照してください。

## 🔧 カスタマイズ

### 同期設定の変更
`03.Automation/bidirectional_sync.py`の設定部分を編集：

```python
# 設定
OBSIDIAN_VAULT_PATH = "/path/to/your/obsidian/vault"
DAILY_NOTES_PATH = f"{OBSIDIAN_VAULT_PATH}/DailyNotes"
```

### 実行時間の変更
cronタブで実行時間を調整：
```bash
crontab -e
# 毎朝7時 → 8時に変更
0 8 * * * cd /path/to/obsidian-sync-scripts && python 03.Automation/bidirectional_sync.py
```

## 🐛 トラブルシューティング

### よくある問題

1. **API Token エラー**
   - 環境変数が正しく設定されているか確認
   - Todoist/Discord APIトークンの有効性を確認

2. **ファイルパスエラー**
   - ObsidianVaultのパスが正しいか確認
   - ディレクトリの権限を確認

3. **同期エラー**
   - ログファイルを確認
   - ネットワーク接続を確認

### ログの確認
```bash
tail -f 03.Automation/sync.log
```

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストやイシューは歓迎します！

## 📞 サポート

問題が発生した場合は、GitHubのIssueを作成してください。