#!/usr/bin/env python3
"""HTTP 服务器 - 通过 HTTP 协议提供图数据库服务。

使用 Flask 框架,单个 POST 路由接收所有命令。
"""

from flask import Flask, request, jsonify, make_response
from typing import Dict, Any
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from server.core.cli import execute_command
from server.core.auth_service import verify_token, clear_token

app = Flask(__name__)


# 不需要验证 token 的命令
NO_AUTH_COMMANDS = {"register", "login"}


@app.route("/execute", methods=["POST"])
def execute():
    """执行客户端发送的命令。

    请求格式:
    {
        "command": ["query", "vertex", "--vid", "123"]
    }

    响应格式:
    {
        "status": "success",
        "data": {...}
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or "command" not in data:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid request: missing 'command' field",
                    }
                ),
                400,
            )

        command = data["command"]
        if not isinstance(command, list) or len(command) == 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid command format: must be a non-empty list",
                    }
                ),
                400,
            )

        # 获取 cookie 中的 token
        token = request.cookies.get("token")

        # 判断是否需要验证 token
        command_name = command[0] if command else ""

        # register, login 不需要验证
        if command_name not in NO_AUTH_COMMANDS:
            # 其他命令需要验证 token
            username = verify_token(token) if token else None
            if not username:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Invalid or expired token. Please login again.",
                        }
                    ),
                    401,
                )

        # 执行命令
        result = execute_command(command)

        # 创建响应
        response = make_response(jsonify(result))

        # 特殊处理：登录成功设置 cookie
        if command_name == "login" and result.get("status") == "success":
            response.set_cookie(
                "token",
                result.get("token", ""),
                httponly=True,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,  # 7天过期
            )

        # 特殊处理：登出清除 cookie 和数据库中的 token
        if command_name == "logout" and token:
            clear_token(token)
            response.set_cookie("token", "", expires=0)

        return response

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查接口。"""
    return jsonify({"status": "success", "message": "Server is running"})


@app.route("/", methods=["GET"])
def index():
    """根路径 - 返回服务器信息。"""
    return jsonify(
        {
            "name": "CycleGraph HTTP Server",
            "version": "1.0.0",
            "endpoints": {
                "execute": "POST /execute - Execute cgql commands",
                "health": "GET /health - Health check",
            },
        }
    )


def run(args):
    """启动服务器。"""

    print("=" * 50)
    print("CycleGraph HTTP Server")
    print("=" * 50)
    print(f"Server running on http://{args.host}:{args.port}")
    print(f"Debug mode: {args.debug}")
    print("=" * 50)
    print("\nEndpoints:")
    print(f"  POST http://{args.host}:{args.port}/execute - Execute commands")
    print(f"  GET  http://{args.host}:{args.port}/health  - Health check")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host=args.host, port=args.port, debug=args.debug)
