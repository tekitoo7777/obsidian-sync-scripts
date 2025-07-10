#!/usr/bin/env python3
"""
Cloud Sync Script for GitHub Actions
GitHub Actions用のクラウド同期スクリプト
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import base64
from github import Github
from config import Config

class CloudSync:
    def __init__(self):
        self.todoist_token = os.getenv('TODOIST_API_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_name = os.getenv('GITHUB_REPOSITORY', 'obsidian-sync-scripts')
        
        if not self.todoist_token:
            raise ValueError("TODOIST_API_TOKEN environment variable is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.todoist_token}",
            "Content-Type": "application/json"
        }
        
        # GitHub APIクライアント
        if self.github_token:
            self.github = Github(self.github_token)
            self.repo = self.github.get_repo(self.repo_name)
        else:
            self.github = None
            self.repo = None
    
    def get_todoist_tasks(self):
        """Todoistからタスクを取得"""
        try:
            print("🔍 Todoistタスクを取得中...")
            
            # 今日期限のタスク
            today_response = requests.get(
                "https://api.todoist.com/rest/v2/tasks",
                headers=self.headers,
                params={"filter": "today"}
            )
            
            if today_response.status_code != 200:
                print(f"❌ Todoist API error: {today_response.status_code}")
                return []
            
            tasks = today_response.json()
            print(f"📋 取得したタスク: {len(tasks)}個")
            
            return tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            return []
    
    def format_tasks_for_obsidian(self, tasks):
        """タスクをObsidian形式に変換"""
        if not tasks:
            return "タスクがありません"
        
        formatted_tasks = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for task in tasks:
            task_line = f"- [ ] {task['content']}"
            
            # 期限があれば追加
            if task.get('due'):
                due_date = task['due']['date']
                if due_date == today:
                    task_line += " 🔥"
                else:
                    task_line += f" (期限: {due_date})"
            
            # プロジェクトがあれば追加
            if task.get('project_id'):
                task_line += f" [プロジェクト: {task['project_id']}]"
            
            formatted_tasks.append(task_line)
        
        return "\n".join(formatted_tasks)
    
    def create_daily_note_content(self, tasks):
        """日次ノートのコンテンツを作成"""
        today = datetime.now()
        formatted_tasks = self.format_tasks_for_obsidian(tasks)
        
        # Obsidianファイルの既存内容を取得
        obsidian_file_path = Config.get_daily_file_path(today)
        existing_content = ""
        
        try:
            if os.path.exists(obsidian_file_path):
                with open(obsidian_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
        except Exception as e:
            print(f"⚠️ 既存ファイル読み込みエラー: {e}")
        
        # タスクセクションを更新
        if existing_content:
            # 既存のタスクセクションを置換
            import re
            task_section_pattern = r'(#### ＜今日のタスク＞\s*\n)(.*?)(\n#### ＜AI振り返り＞|$)'
            new_task_section = f"#### ＜今日のタスク＞\n{formatted_tasks}\n\n"
            
            if re.search(task_section_pattern, existing_content, re.DOTALL):
                updated_content = re.sub(
                    task_section_pattern,
                    lambda m: new_task_section + (m.group(3) if m.group(3) else ''),
                    existing_content,
                    flags=re.DOTALL
                )
            else:
                # タスクセクションが見つからない場合は末尾に追加
                updated_content = existing_content + f"\n\n{new_task_section}"
            
            return updated_content
        else:
            # ファイルが存在しない場合はシンプルな形式で作成
            date_str = today.strftime("%Y-%m-%d")
            content = f"""---
tags:
  - daily
  - diary
---
### {date_str}

#### ＜今日のタスク＞
{formatted_tasks}

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Todoist Sync)*
"""
            return content
    
    def save_to_obsidian(self, content):
        """Obsidianファイルに直接保存"""
        try:
            today = datetime.now()
            obsidian_file_path = Config.get_daily_file_path(today)
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(obsidian_file_path), exist_ok=True)
            
            # ファイルに書き込み
            with open(obsidian_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Obsidianファイル更新: {obsidian_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Obsidianファイル保存エラー: {e}")
            return False
    
    def save_to_github(self, content):
        """GitHubリポジトリにもバックアップ保存"""
        if not self.repo:
            print("⚠️ GitHub repository not configured - skipping backup")
            return True  # Obsidianへの保存が成功していればOK
        
        try:
            today = datetime.now()
            file_path = f"daily_notes/{today.strftime('%Y')}/{today.strftime('%m')}/{today.strftime('%d')}.md"
            
            # ファイルが存在するかチェック
            try:
                file = self.repo.get_contents(file_path)
                # ファイルが存在する場合は更新
                self.repo.update_file(
                    file_path,
                    f"Update daily note for {today.strftime('%Y-%m-%d')}",
                    content,
                    file.sha
                )
                print(f"✅ GitHub backup updated: {file_path}")
            except:
                # ファイルが存在しない場合は新規作成
                self.repo.create_file(
                    file_path,
                    f"Create daily note for {today.strftime('%Y-%m-%d')}",
                    content
                )
                print(f"✅ GitHub backup created: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ GitHubバックアップエラー: {e}")
            return True  # バックアップの失敗は致命的ではない
    
    def save_sync_data(self, tasks):
        """同期データをJSONファイルに保存"""
        try:
            sync_data = {
                "last_sync": datetime.now().isoformat(),
                "tasks_count": len(tasks),
                "sync_status": "success"
            }
            
            if self.repo:
                content = json.dumps(sync_data, ensure_ascii=False, indent=2)
                try:
                    file = self.repo.get_contents("sync_data.json")
                    self.repo.update_file(
                        "sync_data.json",
                        "Update sync data",
                        content,
                        file.sha
                    )
                except:
                    self.repo.create_file(
                        "sync_data.json",
                        "Create sync data",
                        content
                    )
                print("✅ Sync data saved to GitHub")
            else:
                # ローカルファイルに保存
                with open("sync_data.json", "w", encoding="utf-8") as f:
                    json.dump(sync_data, f, ensure_ascii=False, indent=2)
                print("✅ Sync data saved locally")
            
        except Exception as e:
            print(f"❌ 同期データ保存エラー: {e}")
    
    def run_sync(self):
        """同期を実行"""
        print("🚀 Obsidian-Todoist同期を開始...")
        
        # タスクを取得
        tasks = self.get_todoist_tasks()
        
        # 日次ノートを作成
        content = self.create_daily_note_content(tasks)
        
        # Obsidianファイルに保存
        obsidian_success = self.save_to_obsidian(content)
        
        # GitHubにもバックアップ保存
        github_success = self.save_to_github(content)
        
        if obsidian_success:
            print("✅ Obsidian同期完了")
        else:
            print("❌ Obsidian同期失敗")
        
        # 同期データを保存
        self.save_sync_data(tasks)
        
        return obsidian_success

def main():
    """メイン関数"""
    try:
        sync = CloudSync()
        sync.run_sync()
    except Exception as e:
        print(f"❌ 同期エラー: {e}")
        exit(1)

if __name__ == "__main__":
    main()