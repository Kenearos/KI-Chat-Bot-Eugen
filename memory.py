"""
Conversation Memory for Eugen Bot
Stores and retrieves chat history per user with time-based filtering
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ConversationMemory:
    """Manages persistent conversation history for each user"""

    def __init__(self, data_dir="data/conversations", max_messages=25, retention_hours=1):
        """
        Initialize conversation memory

        Args:
            data_dir (str): Directory to store conversation JSON files
            max_messages (int): Maximum messages to store per user
            retention_hours (int): How long to keep messages in context
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.max_messages = max_messages
        self.retention_hours = retention_hours

    def _get_user_file(self, username):
        """Get the file path for a user's conversation history"""
        # Sanitize username for filesystem
        safe_username = "".join(c for c in username.lower() if c.isalnum() or c in "._-")
        return self.data_dir / f"{safe_username}.json"

    def get_user_history(self, username, limit=5):
        """
        Load recent chat history for a user

        Args:
            username (str): Twitch username
            limit (int): Maximum number of messages to return

        Returns:
            list: List of message dicts with role, content, timestamp
        """
        file_path = self._get_user_file(username)

        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error loading history for {username}: {e}")
            return []

        # Filter by retention time
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        recent = []

        for msg in history:
            try:
                msg_time = datetime.fromisoformat(msg['timestamp'])
                if msg_time > cutoff_time:
                    recent.append(msg)
            except (KeyError, ValueError):
                continue

        # Return only the most recent messages up to limit
        return recent[-limit:] if recent else []

    def add_message(self, username, role, content):
        """
        Add a message to user's conversation history

        Args:
            username (str): Twitch username
            role (str): 'user' or 'assistant'
            content (str): Message content
        """
        file_path = self._get_user_file(username)

        # Load existing history
        history = []
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception as e:
                print(f"Error loading history for {username}: {e}")
                history = []

        # Add new message
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Enforce max message limit
        if len(history) > self.max_messages:
            history = history[-self.max_messages:]

        # Save back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history for {username}: {e}")

    def format_for_prompt(self, history):
        """
        Convert history to format suitable for AI API

        Args:
            history (list): List of message dicts from get_user_history

        Returns:
            list: List of dicts with 'role' and 'content' keys
        """
        return [
            {
                "role": msg['role'],
                "content": msg['content']
            }
            for msg in history
        ]

    def clear_user_history(self, username):
        """
        Clear all history for a specific user

        Args:
            username (str): Twitch username
        """
        file_path = self._get_user_file(username)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Error clearing history for {username}: {e}")

    def get_all_users(self):
        """
        Get list of all users with conversation history

        Returns:
            list: List of usernames
        """
        users = []
        for file_path in self.data_dir.glob("*.json"):
            users.append(file_path.stem)
        return users

    def get_user_message_count(self, username):
        """
        Get total message count for a user

        Args:
            username (str): Twitch username

        Returns:
            int: Number of messages in history
        """
        file_path = self._get_user_file(username)
        if not file_path.exists():
            return 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return len(history)
        except Exception:
            return 0
