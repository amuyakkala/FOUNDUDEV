import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users_file = 'users.json'
        self.chat_history_dir = 'chat_history'
        self._ensure_directories()
        self._load_users()
    
    def _ensure_directories(self):
        """Ensure necessary directories exist."""
        if not os.path.exists(self.chat_history_dir):
            os.makedirs(self.chat_history_dir)
    
    def _load_users(self):
        """Load users from JSON file."""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
            self._save_users()
    
    def _save_users(self):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _get_chat_history_file(self, user_name: str) -> str:
        """Get the path to a user's chat history file."""
        return os.path.join(self.chat_history_dir, f"{user_name}.json")
    
    def create_user(self, name: str) -> Dict:
        """Create a new user or get existing user."""
        if name not in self.users:
            self.users[name] = {
                'name': name,
                'conversation_count': 0,
                'last_active': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            self._save_users()
        return self.users[name]
    
    def get_user(self, name: str) -> Optional[Dict]:
        """Get user by name."""
        return self.users.get(name)
    
    def get_all_users(self) -> List[Dict]:
        """Get all users with their chat history."""
        users_list = []
        for name, data in self.users.items():
            user_data = data.copy()
            user_data['chat_history'] = self.get_chat_history(name)
            users_list.append(user_data)
        return users_list
    
    def get_chat_history(self, name: str) -> List[Dict]:
        """Get user's chat history."""
        history_file = self._get_chat_history_file(name)
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    
    def add_chat_history(self, name: str, user_message: str, bot_message: str):
        """Add a message pair to user's chat history."""
        history = self.get_chat_history(name)
        history.append({
            'user': user_message,
            'bot': bot_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update user's conversation count
        if name in self.users:
            self.users[name]['conversation_count'] = len(history)
            self.users[name]['last_active'] = datetime.now().isoformat()
            self._save_users()
        
        # Save updated history
        with open(self._get_chat_history_file(name), 'w') as f:
            json.dump(history, f, indent=2)
    
    def update_user(self, name: str, updates: Dict):
        """Update user data."""
        if name in self.users:
            self.users[name].update(updates)
            self.users[name]['last_active'] = datetime.now().isoformat()
            self._save_users()
    
    def delete_user(self, name: str):
        """Delete a user and their chat history."""
        if name in self.users:
            del self.users[name]
            self._save_users()
            
            # Delete chat history file
            history_file = self._get_chat_history_file(name)
            if os.path.exists(history_file):
                os.remove(history_file)
    
    def get_active_users(self, minutes: int = 30) -> List[Dict]:
        """Get users active in the last N minutes."""
        now = datetime.now()
        active_users = []
        
        for name, data in self.users.items():
            last_active = datetime.fromisoformat(data['last_active'])
            if (now - last_active).total_seconds() <= minutes * 60:
                active_users.append(data)
        
        return active_users 