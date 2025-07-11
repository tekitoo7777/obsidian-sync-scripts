#!/Users/tekitoo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault(Icloud) 2/scripts/venv/bin/python
"""
Bidirectional Sync Script
ObsidianとTodoistの双方向同期を行う
"""

import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path

# 設定
OBSIDIAN_VAULT_PATH = "/Users/tekitoo/Library/Mobile Documents/iCloud~md~obsidian/Documents/ObsidianVault"
DAILY_NOTES_PATH = f"{OBSIDIAN_VAULT_PATH}/Vault/02.Index"
SYNC_DATA_FILE = f"{OBSIDIAN_VAULT_PATH}/scripts/sync_data.json"

class TodoistAPI:
    def __init__(self):
        self.api_token = os.getenv('TODOIST_API_TOKEN')
        if not self.api_token:
            raise ValueError("TODOIST_API_TOKEN environment variable not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.todoist.com/rest/v2"

    def get_tasks(self, filter_str="today"):
        """タスクを取得"""
        response = requests.get(
            f"{self.base_url}/tasks",
            headers=self.headers,
            params={"filter": filter_str}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching tasks: {response.status_code}")
            return []

    def complete_task(self, task_id):
        """タスクを完了"""
        response = requests.post(
            f"{self.base_url}/tasks/{task_id}/close",
            headers=self.headers
        )
        return response.status_code == 204

    def create_task(self, content, description=None, due_string=None):
        """新しいタスクを作成"""
        data = {
            "content": content,
            "description": description,
            "due_string": due_string
        }
        response = requests.post(
            f"{self.base_url}/tasks",
            headers=self.headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()
        return None

class SyncManager:
    def __init__(self):
        self.todoist = TodoistAPI()
        self.sync_data = self.load_sync_data()

    def load_sync_data(self):
        """同期データを読み込み"""
        if os.path.exists(SYNC_DATA_FILE):
            with open(SYNC_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"task_mapping": {}, "last_sync": None}

    def save_sync_data(self):
        """同期データを保存"""
        with open(SYNC_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sync_data, f, ensure_ascii=False, indent=2)

    def get_daily_file_path(self, date=None):
        """日記ファイルパスを取得"""
        if date is None:
            date = datetime.now()
        
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        
        return f"{DAILY_NOTES_PATH}/{year}/{month}/{day}.md"

    def parse_obsidian_tasks(self, file_path):
        """Obsidianファイルからタスクを解析"""
        if not os.path.exists(file_path):
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 今日のタスクセクションを抽出
        pattern = r'#### ＜今日のタスク＞\n(.*?)(?=\n#### |$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return []

        tasks_section = match.group(1)
        
        # タスクを解析
        tasks = []
        for line in tasks_section.split('\n'):
            line = line.strip()
            if line.startswith('- ['):
                completed = 'x' in line[:5]
                task_content = re.sub(r'^- \[[x ]\] ', '', line)
                if task_content:
                    tasks.append({
                        'content': task_content,
                        'completed': completed,
                        'original_line': line
                    })
        
        return tasks

    def sync_obsidian_to_todoist(self):
        """ObsidianからTodoistへの同期"""
        print("🔄 Syncing Obsidian → Todoist...")
        
        daily_file = self.get_daily_file_path()
        obsidian_tasks = self.parse_obsidian_tasks(daily_file)
        todoist_tasks = self.todoist.get_tasks("today")
        
        # Todoistタスクをマッピング
        todoist_task_map = {task['content']: task for task in todoist_tasks}
        
        completed_count = 0
        
        for obs_task in obsidian_tasks:
            task_content = obs_task['content']
            
            # Todoistに対応するタスクがあるかチェック
            if task_content in todoist_task_map:
                todoist_task = todoist_task_map[task_content]
                
                # Obsidianで完了、Todoistで未完了の場合
                if obs_task['completed'] and not todoist_task.get('is_completed', False):
                    if self.todoist.complete_task(todoist_task['id']):
                        print(f"✅ Completed in Todoist: {task_content}")
                        completed_count += 1
                    else:
                        print(f"❌ Failed to complete in Todoist: {task_content}")
        
        print(f"📊 Completed {completed_count} tasks in Todoist")
        return completed_count

    def sync_todoist_to_obsidian(self):
        """TodoistからObsidianへの同期"""
        print("🔄 Syncing Todoist → Obsidian...")
        
        try:
            # 今日のタスクを取得
            todoist_tasks = self.todoist.get_tasks("today")
            if not todoist_tasks:
                print("📝 No tasks found for today")
                return True
            
            # 今日のファイルパスを取得
            daily_file = self.get_daily_file_path()
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(daily_file), exist_ok=True)
            
            # ファイルが存在しない場合は作成
            if not os.path.exists(daily_file):
                with open(daily_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {datetime.now().strftime('%Y-%m-%d')}\n\n## 今日のタスク\n\n")
            
            # ファイルを読み込み
            with open(daily_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # タスクセクションを更新
            task_lines = []
            for task in todoist_tasks:
                task_lines.append(f"- [ ] {task['content']} 🔥 [プロジェクト: {task.get('project_id', 'Unknown')}]")
            
            # タスクセクションを置換
            import re
            pattern = r'(#### ＜今日のタスク＞\n)(.*?)(?=\n#### |$)'
            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(
                    pattern, 
                    r'\1\n' + '\n'.join(task_lines) + '\n',
                    content, 
                    flags=re.DOTALL
                )
            else:
                # タスクセクションが見つからない場合は追加
                new_content = content + f"\n#### ＜今日のタスク＞\n\n" + '\n'.join(task_lines) + '\n'
            
            # ファイルに書き込み
            with open(daily_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Todoist → Obsidian sync completed: {len(todoist_tasks)} tasks")
            return True
            
        except Exception as e:
            print(f"❌ Todoist → Obsidian sync failed: {e}")
            return False

    def full_sync(self):
        """完全な双方向同期"""
        print(f"🚀 Starting bidirectional sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Todoist → Obsidian
        todoist_success = self.sync_todoist_to_obsidian()
        
        # 2. Obsidian → Todoist
        completed_count = self.sync_obsidian_to_todoist()
        
        # 3. 同期データを更新
        self.sync_data['last_sync'] = datetime.now().isoformat()
        self.save_sync_data()
        
        print(f"🎉 Bidirectional sync completed!")
        print(f"   - Todoist → Obsidian: {'✅' if todoist_success else '❌'}")
        print(f"   - Obsidian → Todoist: {completed_count} tasks completed")

def main():
    """メイン処理"""
    try:
        sync_manager = SyncManager()
        sync_manager.full_sync()
    except Exception as e:
        print(f"❌ Error during sync: {e}")

if __name__ == "__main__":
    main() 