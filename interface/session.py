"""CLI 会话管理。

管理本地配置文件，存储连接地址和令牌。
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Session:
    """会话管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化会话。
        
        Args:
            config_path: 配置文件路径，默认为 ~/.cgql_config.json
        """
        if config_path is None:
            config_path = os.path.join(Path.home(), ".cgql_config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件。"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_config(self) -> None:
        """保存配置文件。"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def set_host(self, host: str) -> None:
        """设置服务器地址。"""
        self.config['host'] = host
        self._save_config()
    
    def get_host(self) -> Optional[str]:
        """获取服务器地址。"""
        return self.config.get('host')
    
    def set_token(self, token: str, username: str) -> None:
        """保存令牌和用户名。"""
        self.config['token'] = token
        self.config['username'] = username
        self._save_config()
    
    def get_token(self) -> Optional[str]:
        """获取令牌。"""
        return self.config.get('token')
    
    def get_username(self) -> Optional[str]:
        """获取当前登录用户名。"""
        return self.config.get('username')
    
    def clear(self) -> None:
        """清除所有配置。"""
        self.config = {}
        self._save_config()
    
    def is_logged_in(self) -> bool:
        """检查是否已登录。"""
        return bool(self.get_token())
    
    def is_connected(self) -> bool:
        """检查是否已连接服务器。"""
        return bool(self.get_host())