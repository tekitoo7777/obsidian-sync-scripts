# GitHub Actions セットアップガイド

## 🚀 GitHub Actions で自動同期を設定する手順

### 1. GitHubリポジトリ作成

1. GitHubにログインし、新しいリポジトリを作成
2. リポジトリ名: `obsidian-sync-scripts`
3. このフォルダの内容をリポジトリにプッシュ

### 2. Secrets設定

GitHubリポジトリの設定で以下のSecretsを追加：

1. **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. 以下のSecretsを追加：

| Name | Value |
|------|-------|
| `TODOIST_API_TOKEN` | `45f3698e07894547badfea77db6df6a621002031` |

### 3. 自動実行スケジュール

GitHub Actionsは以下のスケジュールで自動実行されます：

- **毎日 7:00** (日本時間)
- **毎日 12:00** (日本時間)  
- **毎日 19:00** (日本時間)

### 4. 手動実行

1. GitHubリポジトリの **Actions** タブに移動
2. **Obsidian Todoist Sync** ワークフローを選択
3. **Run workflow** ボタンをクリック

### 5. 実行結果確認

1. **Actions** タブで実行ログを確認
2. `daily_notes/` フォルダに日次ノートが作成される
3. `sync_data.json` に同期結果が保存される

## 📁 出力ファイル構造

```
daily_notes/
├── 2025/
│   ├── 07/
│   │   ├── 10.md
│   │   └── 11.md
│   └── 08/
│       └── 01.md
└── sync_data.json
```

## 🔧 設定のカスタマイズ

### 実行頻度を変更する場合

`.github/workflows/sync.yml` の `cron` を編集：

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'  # 2時間ごと
    - cron: '0 9 * * *'    # 毎日9時（UTC）
```

### タスクフィルタを変更する場合

`cloud_sync.py` の `get_todoist_tasks()` メソッドを編集

## 🛠️ トラブルシューティング

### エラーが発生した場合

1. **Actions** タブでエラーログを確認
2. Secrets設定を確認
3. Todoist APIトークンの有効性を確認

### 手動テスト

ローカルで動作確認：

```bash
export TODOIST_API_TOKEN="your_token_here"
python cloud_sync.py
```

## 📋 利用可能な機能

- ✅ Todoistタスクの自動取得
- ✅ 日次ノートの自動作成
- ✅ GitHubへの自動保存
- ✅ 同期データの記録
- ✅ 手動実行対応
- ✅ エラーログ記録

これで、MACが起動していなくても自動でObsidianとTodoistの同期が行われます！