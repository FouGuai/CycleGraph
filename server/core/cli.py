#!/usr/bin/env python3
"""cgql 命令行工具主入口。

提供用户认证、连接管理、查询和插入功能。
"""
import argparse
import json
import sys
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field

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


# ==================== 命令配置数据结构 ====================


@dataclass
class Argument:
    """参数定义"""

    flags: List[str]  # 参数标志，如 ['--username', '-u']
    help: str  # 帮助信息
    required: bool = False
    type: Optional[type] = None
    default: Any = None
    action: Optional[str] = None
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None
    dest: Optional[str] = None


@dataclass
class Command:
    """命令定义"""

    name: str  # 命令名称
    aliases: List[str] = field(default_factory=list)  # 命令别名
    help: str = ""  # 帮助信息
    arguments: List[Argument] = field(default_factory=list)  # 参数列表
    handler: Optional[Callable] = None  # 处理函数
    subcommands: List["Command"] = field(default_factory=list)  # 子命令


# ==================== 命令处理器 ====================


def handle_register(args) -> Dict[str, Any]:
    """处理注册命令"""
    return register_user(args.username, args.password)


def handle_login(args) -> Dict[str, Any]:
    """处理登录命令"""
    result = login_user(args.username, args.password)
    if result["status"] != "success":
        return {"status": result["status"], "message": result.get("message", "")}
    return {"status": result["status"], "token": result.get("token", "")}


def handle_logout(args) -> Dict[str, Any]:
    """处理登出命令"""
    return {"status": "success", "message": "Logged out and session cleared."}


def handle_whoami(args) -> Dict[str, Any]:
    """处理查看当前用户命令"""
    return {
        "status": "error",
        "message": "This command should be handled by server",
    }


def handle_connect(args) -> Dict[str, Any]:
    """处理连接命令"""
    return {
        "status": "success",
        "message": f"Successfully connected to {args.host}. Session configuration saved.",
    }


def handle_query_vertex(args) -> Dict[str, Any]:
    """处理查询点命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return query_vertices(
        username=username,
        vid=args.vid,
        v_types=args.v_type,
        min_create_time=args.min_time,
        max_create_time=args.max_time,
        min_balance=args.min_balance,
        max_balance=args.max_balance,
    )


def handle_query_edge(args) -> Dict[str, Any]:
    """处理查询边命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return query_edges(
        username=username,
        eid=args.eid,
        src_vid=args.src_vid,
        dst_vid=args.dst_vid,
        e_types=args.e_type,
        min_amount=args.min_amount,
        max_amount=args.max_amount,
        min_occur_time=args.min_occur_time,
        max_occur_time=args.max_occur_time,
    )


def handle_query_cycle(args) -> Dict[str, Any]:
    """处理查询环路命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    kwargs = {
        "username": username,
        "start_vid": args.start_vid,
        "max_depth": args.max_depth,
        "direction": args.direction,
        "limit": args.limit,
        "allow_duplicate_vertices": args.allow_duplicate_vertices,
        "allow_duplicate_edges": args.allow_duplicate_edges,
    }

    # 添加可选的过滤参数
    optional_params = [
        ("vertex_filter_v_type", "vertex_filter_v_type"),
        ("vertex_filter_min_balance", "vertex_filter_min_balance"),
        ("edge_filter_e_type", "edge_filter_e_type"),
        ("edge_filter_min_amount", "edge_filter_min_amount"),
        ("edge_filter_max_amount", "edge_filter_max_amount"),
    ]

    for arg_name, param_name in optional_params:
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            kwargs[param_name] = getattr(args, arg_name)

    return query_cycles(**kwargs)


def handle_insert_vertex(args) -> Dict[str, Any]:
    """处理插入点命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return insert_vertex(
        username=username,
        v_type=args.v_type,
        vid=args.vid,
        create_time=args.create_time,
        balance=args.balance,
    )


def handle_insert_edge(args) -> Dict[str, Any]:
    """处理插入边命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return insert_edge(
        username=username,
        eid=args.eid,
        src_vid=args.src_vid,
        dst_vid=args.dst_vid,
        amount=args.amount,
        occur_time=args.occur_time,
        e_type=args.e_type,
        create_vertices=args.create_vertices,
    )


def handle_delete_vertex(args) -> Dict[str, Any]:
    """处理删除点命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return delete_vertex(username=username, vid=args.vid)


def handle_delete_edge(args) -> Dict[str, Any]:
    """处理删除边命令"""
    username = getattr(args, 'username_context', None)
    if not username:
        return {"status": "error", "message": "User not authenticated"}
    
    return delete_edge(username=username, eid=args.eid)


# ==================== 命令定义 ====================


def get_command_tree() -> List[Command]:
    """获取命令树配置"""

    # 公共参数定义
    username_arg = Argument(
        flags=["--username", "-u"], help="用户名", required=True, type=str
    )
    password_arg = Argument(
        flags=["--password", "-p"], help="密码", required=True, type=str
    )

    # 点过滤参数
    vid_arg = Argument(flags=["--vid"], help="点 ID", type=int)
    v_type_arg = Argument(
        flags=["--vt", "--v-type"], help="点类型", type=str, nargs="+", dest="v_type"
    )
    min_balance_arg = Argument(
        flags=["--min-bal", "--min-balance"],
        help="最小余额",
        type=int,
        dest="min_balance",
    )
    max_balance_arg = Argument(
        flags=["--max-bal", "--max-balance"],
        help="最大余额",
        type=int,
        dest="max_balance",
    )
    min_time_arg = Argument(flags=["--min-time"], help="最小创建时间", type=int)
    max_time_arg = Argument(flags=["--max-time"], help="最大创建时间", type=int)

    # 边过滤参数
    eid_arg = Argument(flags=["--eid"], help="边 ID", type=int)
    src_vid_arg = Argument(
        flags=["--src", "--src-vid"], help="源点 ID", type=int, dest="src_vid"
    )
    dst_vid_arg = Argument(
        flags=["--dst", "--dst-vid"], help="目标点 ID", type=int, dest="dst_vid"
    )
    e_type_arg = Argument(
        flags=["--et", "--e-type"], help="边类型", type=str, nargs="+", dest="e_type"
    )
    min_amount_arg = Argument(
        flags=["--min-amt", "--min-amount"],
        help="最小交易金额",
        type=int,
        dest="min_amount",
    )
    max_amount_arg = Argument(
        flags=["--max-amt", "--max-amount"],
        help="最大交易金额",
        type=int,
        dest="max_amount",
    )
    min_occur_time_arg = Argument(
        flags=["--min-time"], help="最小发生时间", type=int, dest="min_occur_time"
    )
    max_occur_time_arg = Argument(
        flags=["--max-time"], help="最大发生时间", type=int, dest="max_occur_time"
    )

    return [
        # ==================== 认证命令 ====================
        Command(
            name="register",
            help="注册新用户",
            arguments=[username_arg, password_arg],
            handler=handle_register,
        ),
        Command(
            name="login",
            help="用户登录",
            arguments=[username_arg, password_arg],
            handler=handle_login,
        ),
        Command(name="logout", help="登出并清除会话", handler=handle_logout),
        Command(name="whoami", help="查看当前登录用户", handler=handle_whoami),
        # ==================== 连接命令 ====================
        Command(
            name="connect",
            help="连接到服务器",
            arguments=[
                Argument(
                    flags=["host"],
                    help="服务器地址 (例如: http://127.0.0.1:8000)",
                    type=str,
                )
            ],
            handler=handle_connect,
        ),
        # ==================== 查询命令 ====================
        Command(
            name="query",
            aliases=["q"],
            help="查询数据",
            subcommands=[
                Command(
                    name="vertex",
                    aliases=["v"],
                    help="查询点",
                    arguments=[
                        vid_arg,
                        v_type_arg,
                        min_time_arg,
                        max_time_arg,
                        min_balance_arg,
                        max_balance_arg,
                    ],
                    handler=handle_query_vertex,
                ),
                Command(
                    name="edge",
                    aliases=["e"],
                    help="查询边",
                    arguments=[
                        eid_arg,
                        src_vid_arg,
                        dst_vid_arg,
                        e_type_arg,
                        min_amount_arg,
                        max_amount_arg,
                        min_occur_time_arg,
                        max_occur_time_arg,
                    ],
                    handler=handle_query_edge,
                ),
                Command(
                    name="cycle",
                    aliases=["c"],
                    help="查询环路",
                    arguments=[
                        Argument(
                            flags=["--start", "--start-vid"],
                            help="起始点 ID",
                            required=True,
                            type=int,
                            dest="start_vid",
                        ),
                        Argument(
                            flags=["--depth", "--max-depth"],
                            help="最大深度",
                            required=True,
                            type=int,
                            dest="max_depth",
                        ),
                        Argument(
                            flags=["--dir", "--direction"],
                            help="方向 (forward/any)",
                            type=str,
                            default="forward",
                            choices=["forward", "any"],
                            dest="direction",
                        ),
                        # 点过滤
                        Argument(
                            flags=["--vt", "--v-type"],
                            help="点类型过滤",
                            type=str,
                            nargs="+",
                            dest="vertex_filter_v_type",
                        ),
                        Argument(
                            flags=["--min-bal", "--min-balance"],
                            help="点最小余额过滤",
                            type=int,
                            dest="vertex_filter_min_balance",
                        ),
                        # 边过滤
                        Argument(
                            flags=["--et", "--e-type"],
                            help="边类型过滤",
                            type=str,
                            nargs="+",
                            dest="edge_filter_e_type",
                        ),
                        Argument(
                            flags=["--min-amt", "--min-amount"],
                            help="边最小金额过滤",
                            type=int,
                            dest="edge_filter_min_amount",
                        ),
                        Argument(
                            flags=["--max-amt", "--max-amount"],
                            help="边最大金额过滤",
                            type=int,
                            dest="edge_filter_max_amount",
                        ),
                        # 结果控制
                        Argument(
                            flags=["--limit"],
                            help="最多返回的环路数量",
                            type=int,
                            default=10,
                        ),
                        Argument(
                            flags=["--allow-dup-v", "--allow-duplicate-vertices"],
                            help="允许环路中重复访问同一个点",
                            action="store_true",
                            dest="allow_duplicate_vertices",
                        ),
                        Argument(
                            flags=["--allow-dup-e", "--allow-duplicate-edges"],
                            help="允许环路中重复使用同一条边",
                            action="store_true",
                            dest="allow_duplicate_edges",
                        ),
                    ],
                    handler=handle_query_cycle,
                ),
            ],
        ),
        # ==================== 插入命令 ====================
        Command(
            name="insert",
            aliases=["i"],
            help="插入数据",
            subcommands=[
                Command(
                    name="vertex",
                    aliases=["v"],
                    help="插入点",
                    arguments=[
                        Argument(
                            flags=["--vt", "--v-type"],
                            help="点类型",
                            required=True,
                            type=str,
                            dest="v_type",
                        ),
                        Argument(
                            flags=["--vid"],
                            help="点 ID (可选，默认自动生成)",
                            type=int,
                        ),
                        Argument(
                            flags=["--time", "--create-time"],
                            help="创建时间 (Unix 时间戳)",
                            type=int,
                            dest="create_time",
                        ),
                        Argument(
                            flags=["--bal", "--balance"],
                            help="初始余额",
                            type=int,
                            default=0,
                            dest="balance",
                        ),
                    ],
                    handler=handle_insert_vertex,
                ),
                Command(
                    name="edge",
                    aliases=["e"],
                    help="插入边",
                    arguments=[
                        Argument(
                            flags=["--eid"], help="边 ID", type=int
                        ),
                        Argument(
                            flags=["--src", "--src-vid"],
                            help="源点 ID",
                            required=True,
                            type=int,
                            dest="src_vid",
                        ),
                        Argument(
                            flags=["--dst", "--dst-vid"],
                            help="目标点 ID",
                            required=True,
                            type=int,
                            dest="dst_vid",
                        ),
                        Argument(
                            flags=["--amt", "--amount"],
                            help="交易金额",
                            type=int,
                            default=0,
                            dest="amount",
                        ),
                        Argument(
                            flags=["--time", "--occur-time"],
                            help="发生时间 (Unix 时间戳)",
                            type=int,
                            dest="occur_time",
                        ),
                        Argument(
                            flags=["--et", "--e-type"],
                            help="边类型",
                            type=str,
                            default="+",
                            dest="e_type",
                        ),
                        Argument(
                            flags=["--create-v", "--create-vertices"],
                            help="自动创建不存在的点",
                            action="store_true",
                            dest="create_vertices",
                        ),
                    ],
                    handler=handle_insert_edge,
                ),
            ],
        ),
        # ==================== 删除命令 ====================
        Command(
            name="delete",
            aliases=["d"],
            help="删除数据",
            subcommands=[
                Command(
                    name="vertex",
                    aliases=["v"],
                    help="删除点",
                    arguments=[
                        Argument(
                            flags=["--vid"],
                            help="要删除的点 ID",
                            required=True,
                            type=int,
                        )
                    ],
                    handler=handle_delete_vertex,
                ),
                Command(
                    name="edge",
                    aliases=["e"],
                    help="删除边",
                    arguments=[
                        Argument(
                            flags=["--eid"],
                            help="要删除的边 ID",
                            required=True,
                            type=int,
                        )
                    ],
                    handler=handle_delete_edge,
                ),
            ],
        ),
    ]


# ==================== 解析器构建 ====================


def build_parser() -> argparse.ArgumentParser:
    """根据命令树配置构建解析器"""
    parser = argparse.ArgumentParser(
        prog="cgql",
        description="CycleGraph Query Language - 图数据库命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    command_tree = get_command_tree()
    _add_commands_to_parser(subparsers, command_tree)

    return parser


def _add_commands_to_parser(
    subparsers: argparse._SubParsersAction, commands: List[Command]
) -> None:
    """递归添加命令到解析器"""
    for cmd in commands:
        # 创建子命令解析器
        cmd_parser = subparsers.add_parser(
            cmd.name, aliases=cmd.aliases, help=cmd.help
        )

        # 添加参数
        for arg in cmd.arguments:
            kwargs = {"help": arg.help}
            if arg.required:
                kwargs["required"] = True
            if arg.type:
                kwargs["type"] = arg.type
            if arg.default is not None:
                kwargs["default"] = arg.default
            if arg.action:
                kwargs["action"] = arg.action
            if arg.nargs:
                kwargs["nargs"] = arg.nargs
            if arg.choices:
                kwargs["choices"] = arg.choices
            if arg.dest:
                kwargs["dest"] = arg.dest

            cmd_parser.add_argument(*arg.flags, **kwargs)

        # 如果有子命令，递归添加
        if cmd.subcommands:
            sub_subparsers = cmd_parser.add_subparsers(
                dest=f"{cmd.name}_type", help="子命令类型"
            )
            _add_commands_to_parser(sub_subparsers, cmd.subcommands)

        # 设置处理器
        if cmd.handler:
            cmd_parser.set_defaults(handler=cmd.handler)


# ==================== 命令执行 ====================


_PARSER = build_parser()


def execute_command(args_list: List[str], username: Optional[str] = None) -> Dict[str, Any]:
    """执行 CLI 命令并返回结果字典。

    Args:
        args_list: 命令参数列表,例如 ['register', '--username', 'alice', '--password', 'pass123']
        username: 当前登录的用户名(从token验证获得),用于多用户表隔离

    Returns:
        Dict: 执行结果的字典
    """
    try:
        args = _PARSER.parse_args(args_list)
    except SystemExit:
        return {"status": "error", "message": "Invalid command or arguments"}

    # 检查是否有处理器
    if not hasattr(args, "handler"):
        return {"status": "error", "message": "Unknown command"}

    try:
        # 将 username 附加到 args 对象上，供处理器使用
        args.username_context = username
        return args.handler(args)
    except Exception as e:
        return {"status": "error", "message": f"Command execution failed: {str(e)}"}


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