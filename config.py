#!/usr/bin/env python3
"""
Configuration file for Obsidian-Todoist sync system
設定ファイル - ObsidianとTodoistの同期システム
"""

import os
from pathlib import Path

class Config:
    """同期システムの設定クラス"""
    
    # パス設定
    OBSIDIAN_VAULT_PATH = "/Users/tekitoo/Library/Mobile Documents/iCloud~md~obsidian/Documents/ObsidianVault"
    DAILY_NOTES_PATH = f"{OBSIDIAN_VAULT_PATH}/Vault/02.Index"
    SCRIPTS_PATH = f"{OBSIDIAN_VAULT_PATH}/scripts"
    SYNC_DATA_FILE = f"{SCRIPTS_PATH}/sync_data.json"
    
    # Todoist API設定
    TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN', '45f3698e07894547badfea77db6df6a621002031')
    TODOIST_API_BASE_URL = "https://api.todoist.com/rest/v2"
    TODOIST_SYNC_API_URL = "https://api.todoist.com/sync/v9"
    
    # 同期設定
    EVENING_CLEANUP_HOUR = 20  # 夜間クリーンアップ開始時刻
    HISTORY_DAYS = 3  # 完了タスクの履歴取得日数
    MAX_ACTIVITY_LIMIT = 100  # アクティビティ取得の最大件数
    
    # ファイルテンプレート設定
    TASK_SECTION_HEADER = "#### ＜今日のタスク＞"
    AI_SECTION_HEADER = "#### ＜AI振り返り＞"
    
    # タスクソース順序
    TASK_SOURCE_ORDER = ['今日期限', '期限切れ', '期限なし(重要)', '今日完了']
    
    # ログ設定
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def get_daily_file_path(cls, date=None):
        """指定日の日記ファイルパスを取得"""
        from datetime import datetime
        
        if date is None:
            date = datetime.now()
        
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        
        return f"{cls.DAILY_NOTES_PATH}/{year}/{month}/{day}.md"
    
    @classmethod
    def get_todoist_headers(cls):
        """Todoist API のヘッダーを取得"""
        return {
            "Authorization": f"Bearer {cls.TODOIST_API_TOKEN}",
            "Content-Type": "application/json"
        } 