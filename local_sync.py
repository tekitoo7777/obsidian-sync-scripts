#!/usr/bin/env python3
"""
Local Sync Script for Obsidian
ローカル同期スクリプト - GitHubからObsidianに同期
"""

import os
import json
import requests
import re
from datetime import datetime
from pathlib import Path
from config import Config

class LocalSync:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.repo_name = 'tekitoo7777/obsidian-sync-scripts'
        
    def get_github_file_content(self, file_path):
        """GitHubリポジトリからファイル内容を取得"""
        try:
            url = f"https://api.github.com/repos/{self.repo_name}/contents/{file_path}"
            headers = {
                "Accept": "application/vnd.github.v3+json"
            }
            
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                import base64
                content_data = response.json()
                content = base64.b64decode(content_data['content']).decode('utf-8')
                return content
            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ GitHubファイル取得エラー: {e}")
            return None
    
    def update_obsidian_file(self, github_content):
        """GitHubの内容でObsidianファイルを更新"""
        try:
            today = datetime.now()
            obsidian_file_path = Config.get_daily_file_path(today)
            
            # Obsidianファイルの既存内容を取得
            existing_content = ""
            if os.path.exists(obsidian_file_path):
                with open(obsidian_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # GitHubから取得したタスクリストを抽出
            github_tasks = self.extract_tasks_from_github_content(github_content)
            
            if not github_tasks:
                print("⚠️ GitHubファイルからタスクを抽出できませんでした")
                return False
            
            # Obsidianファイルのタスクセクションを更新
            if existing_content:
                # 既存のタスクセクションを置換
                task_section_pattern = r'(#### ＜今日のタスク＞\s*\n)(.*?)(\n#### ＜AI振り返り＞|$)'
                new_task_section = f"#### ＜今日のタスク＞\n{github_tasks}\n\n"
                
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
            else:
                # ファイルが存在しない場合は新規作成
                date_str = today.strftime("%Y-%m-%d")
                updated_content = f"""---
tags:
  - daily
  - diary
---
### {date_str}

#### <今日の失敗テーマ>

##### 不安メモ

#### <朝日記>
##### やりたいこと: 

##### 感謝: 

##### 今日の貯金意識: 

#### ＜今日のタスク＞
{github_tasks}

#### ＜AI振り返り＞

#### <夜振り返り>
##### 歩数

##### ダラダラ
**時間:** 
**理由:** 
**次回の改善案:** 

##### 💰 お金関連
**今日の支出:** 
**副業関連の活動:** 
**貯金への貢献度(1-5):** 

##### 1️⃣今日の出来事を記入する: 

##### 2️⃣感情や気分の変化: 

##### 3️⃣今日の価値観との一致度(10点満点): 
**点数:** 
**理由:** 

##### 4️⃣成長確認: 

##### 5️⃣今日のユーモア: 

##### 6️⃣次のアクション: 

##### 7️⃣どのような出来事が心に残ったか: 

##### 8️⃣感謝はあるか:

##### 9️⃣明日の重点ポイント:

---
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Local Sync)*
"""
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(obsidian_file_path), exist_ok=True)
            
            # ファイルに書き込み
            with open(obsidian_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Obsidianファイル更新: {obsidian_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Obsidianファイル更新エラー: {e}")
            return False
    
    def extract_tasks_from_github_content(self, content):
        """GitHubの内容からタスクリストを抽出（未完了と完了済み両方）"""
        try:
            # "## 今日のタスク" セクションからタスクを抽出
            task_section_pattern = r'## 今日のタスク\s*\n(.*?)(?=\n## |$)'
            match = re.search(task_section_pattern, content, re.DOTALL)
            
            if match:
                tasks_text = match.group(1).strip()
                
                # タスクを未完了と完了済みに分離（順序を保持）
                lines = tasks_text.split('\n')
                processed_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('- [ ]') or line.startswith('- [x]'):
                        processed_lines.append(line)
                    elif line:  # 空行でない場合は継続行として処理
                        if processed_lines:
                            processed_lines[-1] += ' ' + line
                
                return '\n'.join(processed_lines)
            else:
                print("⚠️ タスクセクションが見つかりませんでした")
                return ""
                
        except Exception as e:
            print(f"❌ タスク抽出エラー: {e}")
            return ""
    
    def run_sync(self):
        """ローカル同期を実行"""
        print("🚀 ローカル同期を開始...")
        
        # 今日の日付でGitHubファイルを取得
        today = datetime.now()
        github_file_path = f"daily_notes/{today.strftime('%Y')}/{today.strftime('%m')}/{today.strftime('%d')}.md"
        
        print(f"📥 GitHubファイル取得: {github_file_path}")
        github_content = self.get_github_file_content(github_file_path)
        
        if not github_content:
            print("❌ GitHubファイルが見つかりませんでした")
            return False
        
        # Obsidianファイルを更新
        success = self.update_obsidian_file(github_content)
        
        if success:
            print("✅ ローカル同期完了")
        else:
            print("❌ ローカル同期失敗")
        
        return success

def main():
    """メイン関数"""
    try:
        sync = LocalSync()
        sync.run_sync()
    except Exception as e:
        print(f"❌ 同期エラー: {e}")
        exit(1)

if __name__ == "__main__":
    main()