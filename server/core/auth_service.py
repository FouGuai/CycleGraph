"""用户认证服务。

提供用户注册、登录、令牌验证等功能。
"""

import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from server.opengauss.graph_dao import execute_dml, fetch_one, User


def hash_password(password: str) -> str:
    """对密码进行哈希加密。"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """生成访问令牌。"""
    return secrets.token_urlsafe(32)


def register_user(username: str, password: str, **db_kwargs: Any) -> Dict[str, Any]:
    """注册新用户。

    Args:
        username: 用户名
        password: 密码
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: {"status": "success"/"error", "message": "...", "data": {...}}
    """
    try:
        # 检查用户是否已存在
        existing = fetch_one(
            "SELECT user_id FROM users WHERE username = %s", (username,), **db_kwargs
        )

        if existing:
            return {"status": "error", "message": "Username already exists"}

        # 创建新用户
        password_hash = hash_password(password)
        created_at = int(time.time())

        execute_dml(
            """INSERT INTO users (username, password_hash, created_at) 
               VALUES (%s, %s, %s)""",
            (username, password_hash, created_at),
            **db_kwargs,
        )

        return {
            "status": "success",
            "message": f"User '{username}' registered successfully",
        }

    except Exception as e:
        return {"status": "error", "message": f"Registration failed: {e}"}


def login_user(username: str, password: str, **db_kwargs: Any) -> Dict[str, Any]:
    """用户登录。

    Args:
        username: 用户名
        password: 密码
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: {"status": "success"/"error", "token": "...", "message": "..."}
    """
    try:
        # 查询用户
        result = fetch_one(
            "SELECT user_id, username, password_hash, created_at, last_login FROM users WHERE username = %s",
            (username,),
            **db_kwargs,
        )

        if not result:
            return {"status": "error", "message": "Wrong username or password"}

        user = User.from_tuple(result)

        # 验证密码
        if user.password_hash != hash_password(password):
            return {"status": "error", "message": "Wrong username or password"}

        # 更新最后登录时间
        execute_dml(
            "UPDATE users SET last_login = %s WHERE user_id = %s",
            (int(time.time()), user.user_id),
            **db_kwargs,
        )

        # 生成令牌（实际应用中应存储到 token 表）
        token = generate_token()

        return {"status": "success", "token": token, "username": user.username}

    except Exception as e:
        return {"status": "error", "message": f"Login failed: {e}"}


def verify_token(token: str) -> bool:
    """验证令牌是否有效（简化版本）。

    实际应用中应该：
    1. 将 token 存储到数据库的 tokens 表
    2. 验证时查询数据库并检查过期时间
    """
    # 简化版本：只要不为空就认为有效
    return bool(token)
