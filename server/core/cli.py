#!/usr/bin/env python3
"""cgql 命令行工具主入口。

提供用户认证、连接管理、查询和插入功能。
"""
import argparse
import json
import sys
from typing import List, Optional, Dict, Any

from server.core.auth_service import register_user, login_user
from server.core.graph_service import (
    query_vertices,
    query_edges,
    insert_vertex,
    insert_edge,
    query_cycles,
    delete_vertex,
    delete_edge,
)


def execute_command(args_list: List[str]) -> Dict[str, Any]:  # type: ignore
    """执行 CLI 命令并返回结果字典。

    Args:
        args_list: 命令参数列表,例如 ['register', '--username', 'alice', '--password', 'pass123']

    Returns:
        Dict: 执行结果的字典
    """
    parser = argparse.ArgumentParser(
        prog="cgql", description="CycleGraph Query Language - 图数据库命令行工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # ==================== 用户认证命令 ====================

    # register
    parser_register = subparsers.add_parser("register", help="注册新用户")
    parser_register.add_argument("--username", "-u", required=True, help="用户名")
    parser_register.add_argument("--password", "-p", required=True, help="密码")

    # login
    parser_login = subparsers.add_parser("login", help="用户登录")
    parser_login.add_argument("--username", "-u", required=True, help="用户名")
    parser_login.add_argument("--password", "-p", required=True, help="密码")

    # logout
    parser_logout = subparsers.add_parser("logout", help="登出并清除会话")

    # whoami
    parser_whoami = subparsers.add_parser("whoami", help="查看当前登录用户")

    # ==================== 连接管理命令 ====================

    # connect
    parser_connect = subparsers.add_parser("connect", help="连接到服务器")
    parser_connect.add_argument("host", help="服务器地址 (例如: http://127.0.0.1:8000)")

    # ==================== 查询命令 ====================

    parser_query = subparsers.add_parser("query", aliases=["q"], help="查询数据")
    query_subparsers = parser_query.add_subparsers(dest="query_type", help="查询类型")

    # query vertex
    parser_query_vertex = query_subparsers.add_parser(
        "vertex", aliases=["v"], help="查询点"
    )
    parser_query_vertex.add_argument("--vid", type=int, help="点 ID")
    parser_query_vertex.add_argument(
        "--vt", "--v-type", type=str, nargs="+", dest="v_type", help="点类型"
    )
    parser_query_vertex.add_argument("--min-time", type=int, help="最小创建时间")
    parser_query_vertex.add_argument("--max-time", type=int, help="最大创建时间")
    parser_query_vertex.add_argument(
        "--min-bal", "--min-balance", type=int, dest="min_balance", help="最小余额"
    )
    parser_query_vertex.add_argument(
        "--max-bal", "--max-balance", type=int, dest="max_balance", help="最大余额"
    )

    # query edge
    parser_query_edge = query_subparsers.add_parser(
        "edge", aliases=["e"], help="查询边"
    )
    parser_query_edge.add_argument("--eid", type=int, help="边 ID")
    parser_query_edge.add_argument(
        "--src", "--src-vid", type=int, dest="src_vid", help="源点 ID"
    )
    parser_query_edge.add_argument(
        "--dst", "--dst-vid", type=int, dest="dst_vid", help="目标点 ID"
    )
    parser_query_edge.add_argument(
        "--et", "--e-type", type=str, nargs="+", dest="e_type", help="边类型"
    )
    parser_query_edge.add_argument(
        "--min-amt", "--min-amount", type=int, dest="min_amount", help="最小交易金额"
    )
    parser_query_edge.add_argument(
        "--max-amt", "--max-amount", type=int, dest="max_amount", help="最大交易金额"
    )
    parser_query_edge.add_argument(
        "--min-time", type=int, dest="min_occur_time", help="最小发生时间"
    )
    parser_query_edge.add_argument(
        "--max-time", type=int, dest="max_occur_time", help="最大发生时间"
    )

    # query cycle
    parser_query_cycle = query_subparsers.add_parser(
        "cycle", aliases=["c"], help="查询环路"
    )
    parser_query_cycle.add_argument(
        "--start",
        "--start-vid",
        type=int,
        required=True,
        dest="start_vid",
        help="起始点 ID",
    )
    parser_query_cycle.add_argument(
        "--depth",
        "--max-depth",
        type=int,
        required=True,
        dest="max_depth",
        help="最大深度",
    )
    parser_query_cycle.add_argument(
        "--dir",
        "--direction",
        choices=["forward", "any"],
        default="forward",
        dest="direction",
        help="方向",
    )
    # 点过滤参数
    parser_query_cycle.add_argument(
        "--vt",
        "--v-type",
        type=str,
        nargs="+",
        dest="vertex_filter_v_type",
        help="点类型过滤",
    )
    parser_query_cycle.add_argument(
        "--min-bal",
        "--min-balance",
        type=int,
        dest="vertex_filter_min_balance",
        help="点最小余额过滤",
    )
    # 边过滤参数
    parser_query_cycle.add_argument(
        "--et",
        "--e-type",
        type=str,
        nargs="+",
        dest="edge_filter_e_type",
        help="边类型过滤",
    )
    parser_query_cycle.add_argument(
        "--min-amt",
        "--min-amount",
        type=int,
        dest="edge_filter_min_amount",
        help="边最小金额过滤",
    )
    parser_query_cycle.add_argument(
        "--max-amt",
        "--max-amount",
        type=int,
        dest="edge_filter_max_amount",
        help="边最大金额过滤",
    )
    # 结果控制参数
    parser_query_cycle.add_argument(
        "--limit", type=int, default=10, help="最多返回的环路数量"
    )
    parser_query_cycle.add_argument(
        "--allow-dup-v",
        "--allow-duplicate-vertices",
        action="store_true",
        dest="allow_duplicate_vertices",
        help="允许环路中重复访问同一个点",
    )
    parser_query_cycle.add_argument(
        "--allow-dup-e",
        "--allow-duplicate-edges",
        action="store_true",
        dest="allow_duplicate_edges",
        help="允许环路中重复使用同一条边",
    )

    # ==================== 插入命令 ====================

    parser_insert = subparsers.add_parser("insert", aliases=["i"], help="插入数据")
    insert_subparsers = parser_insert.add_subparsers(
        dest="insert_type", help="插入类型"
    )

    # insert vertex
    parser_insert_vertex = insert_subparsers.add_parser(
        "vertex", aliases=["v"], help="插入点"
    )
    parser_insert_vertex.add_argument(
        "--vt", "--v-type", type=str, required=True, dest="v_type", help="点类型"
    )
    parser_insert_vertex.add_argument(
        "--vid", type=int, help="点 ID (可选，默认自动生成)"
    )
    parser_insert_vertex.add_argument(
        "--time",
        "--create-time",
        type=int,
        dest="create_time",
        help="创建时间 (Unix 时间戳)",
    )
    parser_insert_vertex.add_argument(
        "--bal", "--balance", type=int, default=0, dest="balance", help="初始余额"
    )

    # insert edge
    parser_insert_edge = insert_subparsers.add_parser(
        "edge", aliases=["e"], help="插入边"
    )
    parser_insert_edge.add_argument("--eid", type=int, required=True, help="边 ID")
    parser_insert_edge.add_argument(
        "--src", "--src-vid", type=int, required=True, dest="src_vid", help="源点 ID"
    )
    parser_insert_edge.add_argument(
        "--dst", "--dst-vid", type=int, required=True, dest="dst_vid", help="目标点 ID"
    )
    parser_insert_edge.add_argument(
        "--amt", "--amount", type=int, required=True, dest="amount", help="交易金额"
    )
    parser_insert_edge.add_argument(
        "--time",
        "--occur-time",
        type=int,
        dest="occur_time",
        help="发生时间 (Unix 时间戳)",
    )
    parser_insert_edge.add_argument(
        "--et", "--e-type", type=str, default="+", dest="e_type", help="边类型"
    )
    parser_insert_edge.add_argument(
        "--create-v",
        "--create-vertices",
        action="store_true",
        dest="create_vertices",
        help="自动创建不存在的点",
    )

    parser_delete = subparsers.add_parser("delete", aliases=["d"], help="删除数据")
    delete_subparsers = parser_delete.add_subparsers(
        dest="delete_type", help="删除类型"
    )

    # delete vertex
    parser_delete_vertex = delete_subparsers.add_parser(
        "vertex", aliases=["v"], help="删除点"
    )
    parser_delete_vertex.add_argument(
        "--vid", type=int, required=True, help="要删除的点 ID"
    )

    # delete edge
    parser_delete_edge = delete_subparsers.add_parser(
        "edge", aliases=["e"], help="删除边"
    )
    parser_delete_edge.add_argument(
        "--eid", type=int, required=True, help="要删除的边 ID"
    )

    try:
        args = parser.parse_args(args_list)
    except SystemExit:
        return {"status": "error", "message": "Invalid command or arguments"}

    # 处理命令
    if args.command == "register":
        result = register_user(args.username, args.password)
        return result

    elif args.command == "login":
        result = login_user(args.username, args.password)
        if result["status"] != "success":
            return {"status": result["status"], "message": result.get("message", "")}
        return {"status": result["status"], "token": result.get("token", "")}

    elif args.command == "logout":
        return {"status": "success", "message": "Logged out and session cleared."}

    elif args.command == "whoami":
        # whoami需要在服务器端通过token验证
        return {
            "status": "error",
            "message": "This command should be handled by server",
        }

    elif args.command == "connect":
        return {
            "status": "success",
            "message": f"Successfully connected to {args.host}. Session configuration saved.",
        }

    elif args.command == "query":
        # 查询操作的登录验证由服务器端处理
        if args.query_type == "vertex":
            result = query_vertices(
                vid=args.vid,
                v_types=args.v_type,
                min_create_time=args.min_time,
                max_create_time=args.max_time,
                min_balance=args.min_balance,
                max_balance=args.max_balance,
            )
            return result

        elif args.query_type == "edge":
            result = query_edges(
                eid=args.eid,
                src_vid=args.src_vid,
                dst_vid=args.dst_vid,
                e_types=args.e_type,
                min_amount=args.min_amount,
                max_amount=args.max_amount,
                min_occur_time=args.min_occur_time,
                max_occur_time=args.max_occur_time,
            )
            return result

        elif args.query_type == "cycle":
            # 构建过滤参数
            kwargs = {
                "start_vid": args.start_vid,
                "max_depth": args.max_depth,
                "direction": args.direction,
            }

            # 添加可选参数
            if hasattr(args, "vertex_filter_v_type") and args.vertex_filter_v_type:
                kwargs["vertex_filter_v_type"] = args.vertex_filter_v_type
            if (
                hasattr(args, "vertex_filter_min_balance")
                and args.vertex_filter_min_balance
            ):
                kwargs["vertex_filter_min_balance"] = args.vertex_filter_min_balance
            if hasattr(args, "edge_filter_e_type") and args.edge_filter_e_type:
                kwargs["edge_filter_e_type"] = args.edge_filter_e_type
            if hasattr(args, "edge_filter_min_amount") and args.edge_filter_min_amount:
                kwargs["edge_filter_min_amount"] = args.edge_filter_min_amount
            if hasattr(args, "edge_filter_max_amount") and args.edge_filter_max_amount:
                kwargs["edge_filter_max_amount"] = args.edge_filter_max_amount
            if hasattr(args, "limit") and args.limit:
                kwargs["limit"] = args.limit
            if (
                hasattr(args, "allow_duplicate_vertices")
                and args.allow_duplicate_vertices
            ):
                kwargs["allow_duplicate_vertices"] = args.allow_duplicate_vertices
            if hasattr(args, "allow_duplicate_edges") and args.allow_duplicate_edges:
                kwargs["allow_duplicate_edges"] = args.allow_duplicate_edges
            result = query_cycles(**kwargs)
            return result

    elif args.command == "insert":
        # 插入操作的登录验证由服务器端处理
        if args.insert_type == "vertex":

            result = insert_vertex(
                v_type=args.v_type,
                vid=args.vid,
                create_time=args.create_time,
                balance=args.balance,
            )
            return result

        elif args.insert_type == "edge":
            result = insert_edge(
                eid=args.eid,
                src_vid=args.src_vid,
                dst_vid=args.dst_vid,
                amount=args.amount,
                occur_time=args.occur_time,
                e_type=args.e_type,
                create_vertices=args.create_vertices,
            )
            return result
    elif args.command == "delete":
        # 删除操作的登录验证由服务器端处理
        if args.delete_type == "vertex":
            # 验证输入
            if not isinstance(args.vid, int) or args.vid <= 0:
                return {
                    "status": "error",
                    "message": "Vertex ID must be a positive integer",
                }

            result = delete_vertex(vid=args.vid)
            return result

        elif args.delete_type == "edge":
            # 验证输入
            if not isinstance(args.eid, int) or args.eid <= 0:
                return {
                    "status": "error",
                    "message": "Edge ID must be a positive integer",
                }

            result = delete_edge(eid=args.eid)
            return result
    else:
        return {"status": "error", "message": "Unknown command"}


def execute_command_from_string(command_str: str) -> str:
    """从命令字符串执行并返回 JSON 字符串。

    Args:
        command_str: 命令字符串,例如 "register --username alice --password pass123"

    Returns:
        str: JSON 格式的结果字符串
    """
    args_list = command_str.split()
    result = execute_command(args_list)
    return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    """命令行入口函数,用于直接从终端调用。"""
    result = execute_command(sys.argv[1:])
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
