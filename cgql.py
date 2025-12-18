#!/usr/bin/env python3
"""cgql - CycleGraph 命令行客户端。

独立的客户端工具,通过 HTTP 协议与服务器通信。
本地存储 token 和服务器地址,支持所有 cgql 命令。
"""

import requests
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 本地会话文件路径
SESSION_FILE = Path.home() / ".cgql_session.json"


class Session:
    """会话管理器 - 管理本地 token 和服务器地址。"""

    def __init__(self):
        self.token: Optional[str] = None
        self.host: str = "http://127.0.0.1:8000"
        self.load()

    def load(self):
        """从本地文件加载会话信息。"""
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    self.host = data.get("host", "http://127.0.0.1:8000")
            except Exception:
                pass

    def save(self):
        """保存会话信息到本地文件。"""
        try:
            with open(SESSION_FILE, "w") as f:
                json.dump({"token": self.token, "host": self.host}, f)
        except Exception as e:
            print(f"Warning: Failed to save session: {e}", file=sys.stderr)

    def clear(self):
        """清除会话信息。"""
        self.token = None
        if SESSION_FILE.exists():
            try:
                SESSION_FILE.unlink()
            except Exception:
                pass


def send_request(session: Session, command: list) -> Dict[str, Any]:
    """发送请求到服务器。

    Args:
        session: 会话对象
        command: 命令参数列表

    Returns:
        服务器响应的字典
    """
    try:
        # 构建请求
        url = f"{session.host}/execute"
        headers = {"Content-Type": "application/json"}
        cookies = {"token": session.token} if session.token else {}
        payload = {"command": command}

        # 发送请求
        response = requests.post(
            url, json=payload, headers=headers, cookies=cookies, timeout=30
        )

        # 处理响应
        if response.status_code == 200:
            result = response.json()

            # 登录成功 - 保存 token (优先从cookie获取，其次从响应body获取)
            if command[0] == "login" and result.get("status") == "success":
                token_from_cookie = response.cookies.get("token")
                token_from_body = result.get("token")

                # 优先使用cookie中的token，如果没有则使用body中的token
                token_to_save = token_from_cookie or token_from_body
                if token_to_save:
                    session.token = token_to_save
                    session.save()

            return result
        else:
            # HTTP 错误
            try:
                error_data = response.json()
                return error_data
            except Exception:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                }

    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": f"Connection failed: Unable to reach server at {session.host}",
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout"}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {str(e)}"}


def handle_special_commands(
    session: Session, command: list
) -> Optional[Dict[str, Any]]:
    """处理特殊的本地命令。

    Args:
        session: 会话对象
        command: 命令参数列表

    Returns:
        如果是特殊命令返回结果字典,否则返回 None
    """
    if len(command) == 0:
        return None

    # connect 命令 - 更新本地服务器地址
    if command[0] == "connect" and len(command) >= 2:
        session.host = command[1]
        session.save()
        return {
            "status": "success",
            "message": f"Successfully connected to {session.host}. Session configuration saved.",
        }

    # whoami 命令 - 本地检查
    if command[0] == "whoami":
        if session.token:
            # 发送到服务器验证
            return None
        else:
            return {"status": "error", "message": "Not logged in"}

    # logout 命令 - 需要清除本地会话
    if command[0] == "logout":
        # 先发送到服务器清除服务器端 token
        result = send_request(session, command)
        # 再清除本地会话
        session.clear()
        return result

    return None


def main():
    """客户端主入口函数。"""
    # 初始化会话
    session = Session()

    # 获取命令行参数
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "No command provided. Use 'cgql --help' for usage information.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    command = sys.argv[1:]

    # 处理特殊命令
    result = handle_special_commands(session, command)

    # 如果不是特殊命令,发送到服务器
    if result is None:
        result = send_request(session, command)

    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 根据状态码退出
    if result.get("status") == "error":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
