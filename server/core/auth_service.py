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
        
        # 为用户创建专属的点表和边表
        from server.opengauss.graph_dao import init_user_tables
        init_user_tables(username, **db_kwargs)

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
        
        # 验证用户的点表和边表是否存在，如果不存在则创建
        from server.opengauss.graph_dao  import verify_user_tables, init_user_tables
        if not verify_user_tables(username, **db_kwargs):
            try:
                init_user_tables(username, **db_kwargs)
            except Exception as table_error:
                return {
                    "status": "error",
                    "message": f"Failed to initialize user tables: {table_error}"
                }

        # 生成令牌
        token = generate_token()

        # 更新最后登录时间和token
        execute_dml(
            "UPDATE users SET last_login = %s, token = %s WHERE user_id = %s",
            (int(time.time()), token, user.user_id),
            **db_kwargs,
        )

        result = {"status": "success", "token": token, "username": user.username}
        return result

    except Exception as e:
        return {"status": "error", "message": f"Login failed: {e}"}


def verify_token(token: str, **db_kwargs: Any) -> Optional[str]:
    """验证令牌是否有效,并返回用户名。

    Args:
        token: 访问令牌
        **db_kwargs: 数据库连接参数

    Returns:
        Optional[str]: 如果token有效返回用户名,否则返回None
    """
    if not token:
        return None

    try:
        result = fetch_one(
            "SELECT username FROM users WHERE token = %s",
            (token,),
            **db_kwargs,
        )
        return result[0] if result else None
    except Exception:
        return None


def clear_token(token: str, **db_kwargs: Any) -> bool:
    """清除用户的token（登出时调用）。

    Args:
        token: 要清除的令牌
        **db_kwargs: 数据库连接参数

    Returns:
        bool: 清除成功返回True
    """
    try:
        execute_dml(
            "UPDATE users SET token = NULL WHERE token = %s",
            (token,),
            **db_kwargs,
        )
        return True
    except Exception:
        return False
