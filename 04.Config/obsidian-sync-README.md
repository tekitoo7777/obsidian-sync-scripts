# 📅 Daily Tasks Sync - 自動タスク同期システム

毎朝7時にTodoistから今日のタスクを自動取得して、Obsidianの日記ファイルに挿入するシステムです。

## 🚀 セットアップ

### 1. Todoist APIトークンの設定

まず、Todoist APIトークンを環境変数に設定します：

```bash
# ~/.zshrc または ~/.bash_profile に追加
export TODOIST_API_TOKEN='your_api_token_here'

# 設定を反映
source ~/.zshrc
```

**Todoist APIトークンの取得方法：**
1. [Todoist設定](https://todoist.com/prefs/integrations) → 統合 → 開発者
2. APIトークンをコピー

### 2. 自動セットアップの実行

```bash
cd "Vault(Icloud) 2/scripts"
./setup_daily_sync.sh
```

このスクリプトが以下を実行します：
- 必要なPythonパッケージのインストール
- cronジョブの設定（毎朝7時実行）
- ログファイルの設定

## 🧪 テスト

セットアップ後、手動でテストできます：

```bash
cd "Vault(Icloud) 2/scripts"
./test_sync.sh
```

## 📁 ファイル構成

```
scripts/
├── daily_tasks_sync.py    # メインの同期スクリプト
├── setup_daily_sync.sh    # セットアップスクリプト
├── test_sync.sh           # テストスクリプト
├── daily_sync.log         # ログファイル（自動生成）
└── README.md              # このファイル
```

## ⚙️ 動作仕様

### 実行タイミング
- **毎朝7:00 AM**に自動実行
- cronジョブとして設定

### 処理内容
1. 今日の日付を取得
2. 対応する日記ファイルパスを生成：`Vault/02.Index/YYYY/MM/DD.md`
3. ファイルが存在しない場合は、テンプレートから作成
4. Todoist APIから今日のタスクを取得
5. `#### ＜今日のタスク＞`セクションにタスクを挿入

### ログ
- 実行ログは `daily_sync.log` に保存
- エラーも同じファイルに記録

## 🔧 管理コマンド

### cronジョブの確認
```bash
crontab -l
```

### ログの確認
```bash
tail -f "Vault(Icloud) 2/scripts/daily_sync.log"
```

### cronジョブの削除
```bash
crontab -e
# 該当行を削除して保存
```

## 🛠️ カスタマイズ

### 実行時間の変更
`setup_daily_sync.sh`の以下の行を編集：
```bash
# 毎朝7時 → 毎朝8時に変更する場合
echo "0 8 * * * cd '$SCRIPT_DIR' && /usr/bin/python3 '$PYTHON_SCRIPT' >> '$LOG_FILE' 2>&1" >> /tmp/new_cron
```

### タスクフィルターの変更
`daily_tasks_sync.py`の`get_todoist_tasks()`関数で、フィルターを変更：
```python
# 今日のタスク → 今日と明日のタスク
params={"filter": "today | tomorrow"}
```

## 🚨 トラブルシューティング

### よくある問題

1. **APIトークンエラー**
   ```
   Error: TODOIST_API_TOKEN environment variable not set
   ```
   → 環境変数が正しく設定されているか確認

2. **ファイル作成エラー**
   ```
   Error updating file: [Errno 2] No such file or directory
   ```
   → ディレクトリの権限を確認

3. **cronが実行されない**
   → `crontab -l`でジョブが登録されているか確認
   → ログファイルでエラーを確認

### デバッグ方法

1. **手動実行でテスト**
   ```bash
   ./test_sync.sh
   ```

2. **ログの確認**
   ```bash
   tail -20 daily_sync.log
   ```

3. **cronの動作確認**
   ```bash
   # cronサービスの状態確認
   sudo launchctl list | grep cron
   ```

## 📝 注意事項

- macOSの場合、cronの代わりにlaunchdを使用することも可能
- iCloudフォルダのため、同期タイミングによっては遅延が発生する可能性
- Todoistの利用制限（API呼び出し回数）に注意

## 🔄 アップデート

システムを更新する場合：

1. スクリプトファイルを編集
2. 再度セットアップを実行：
   ```bash
   ./setup_daily_sync.sh
   ``` 