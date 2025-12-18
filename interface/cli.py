#!/usr/bin/env python3
"""cgql 命令行工具主入口。

提供用户认证、连接管理、查询和插入功能。
"""
import argparse
import json
import sys
from typing import List, Optional

from session import Session
from server.core.auth_service import register_user, login_user
from server.core.graph_service import (
    query_vertices,
    query_edges,
    insert_vertex,
    insert_edge
)


def print_json(data: dict) -> None:
    """格式化打印 JSON 数据。"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        prog='cgql',
        description='CycleGraph Query Language - 图数据库命令行工具'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # ==================== 用户认证命令 ====================
    
    # register
    parser_register = subparsers.add_parser('register', help='注册新用户')
    parser_register.add_argument('--username', required=True, help='用户名')
    parser_register.add_argument('--password', required=True, help='密码')
    
    # login
    parser_login = subparsers.add_parser('login', help='用户登录')
    parser_login.add_argument('--username', required=True, help='用户名')
    parser_login.add_argument('--password', required=True, help='密码')
    
    # logout
    parser_logout = subparsers.add_parser('logout', help='登出并清除会话')
    
    # whoami
    parser_whoami = subparsers.add_parser('whoami', help='查看当前登录用户')
    
    # ==================== 连接管理命令 ====================
    
    # connect
    parser_connect = subparsers.add_parser('connect', help='连接到服务器')
    parser_connect.add_argument('host', help='服务器地址 (例如: http://127.0.0.1:8000)')
    
    # ==================== 查询命令 ====================
    
    parser_query = subparsers.add_parser('query', help='查询数据')
    query_subparsers = parser_query.add_subparsers(dest='query_type', help='查询类型')
    
    # query vertex
    parser_query_vertex = query_subparsers.add_parser('vertex', help='查询点')
    parser_query_vertex.add_argument('--vid', type=int, help='点 ID')
    parser_query_vertex.add_argument('--v-type', type=int, nargs='+', help='点类型')
    parser_query_vertex.add_argument('--min-create-time', type=int, help='最小创建时间')
    parser_query_vertex.add_argument('--max-create-time', type=int, help='最大创建时间')
    parser_query_vertex.add_argument('--min-balance', type=int, help='最小余额')
    parser_query_vertex.add_argument('--max-balance', type=int, help='最大余额')
    
    # query edge
    parser_query_edge = query_subparsers.add_parser('edge', help='查询边')
    parser_query_edge.add_argument('--eid', type=int, help='边 ID')
    parser_query_edge.add_argument('--src-vid', type=int, help='源点 ID')
    parser_query_edge.add_argument('--dst-vid', type=int, help='目标点 ID')
    parser_query_edge.add_argument('--e-type', type=int, nargs='+', help='边类型')
    parser_query_edge.add_argument('--min-amount', type=int, help='最小交易金额')
    parser_query_edge.add_argument('--max-amount', type=int, help='最大交易金额')
    parser_query_edge.add_argument('--min-occur-time', type=int, help='最小发生时间')
    parser_query_edge.add_argument('--max-occur-time', type=int, help='最大发生时间')
    
    # query cycle (暂时未实现)
    parser_query_cycle = query_subparsers.add_parser('cycle', help='查询环路')
    parser_query_cycle.add_argument('--start-vid', type=int, required=True, help='起始点 ID')
    parser_query_cycle.add_argument('--max-depth', type=int, required=True, help='最大深度')
    parser_query_cycle.add_argument('--direction', choices=['forward', 'any'], default='forward', help='方向')
    
    # ==================== 插入命令 ====================
    
    parser_insert = subparsers.add_parser('insert', help='插入数据')
    insert_subparsers = parser_insert.add_subparsers(dest='insert_type', help='插入类型')
    
    # insert vertex
    parser_insert_vertex = insert_subparsers.add_parser('vertex', help='插入点')
    parser_insert_vertex.add_argument('--v-type', type=int, required=True, help='点类型')
    parser_insert_vertex.add_argument('--vid', type=int, help='点 ID (可选，默认自动生成)')
    parser_insert_vertex.add_argument('--create-time', type=int, help='创建时间 (Unix 时间戳)')
    parser_insert_vertex.add_argument('--balance', type=int, default=0, help='初始余额')
    
    # insert edge
    parser_insert_edge = insert_subparsers.add_parser('edge', help='插入边')
    parser_insert_edge.add_argument('--eid', type=int, required=True, help='边 ID')
    parser_insert_edge.add_argument('--src-vid', type=int, required=True, help='源点 ID')
    parser_insert_edge.add_argument('--dst-vid', type=int, required=True, help='目标点 ID')
    parser_insert_edge.add_argument('--amount', type=int, required=True, help='交易金额')
    parser_insert_edge.add_argument('--occur-time', type=int, help='发生时间 (Unix 时间戳)')
    parser_insert_edge.add_argument('--e-type', type=int, default=0, help='边类型')
    parser_insert_edge.add_argument('--create-vertices', action='store_true', help='自动创建不存在的点')
    
    args = parser.parse_args()
    
    # 初始化会话
    session = Session()
    
    # 处理命令
    if args.command == 'register':
        result = register_user(args.username, args.password)
        print_json(result)
    
    elif args.command == 'login':
        result = login_user(args.username, args.password)
        if result['status'] == 'success':
            session.set_token(result['token'], result['username'])
        print_json({"status": result['status']})
    
    elif args.command == 'logout':
        session.clear()
        print("Logged out and session cleared.")
    
    elif args.command == 'whoami':
        if session.is_logged_in():
            print_json({
                "status": "success",
                "found": True,
                "current_user": session.get_username()
            })
        else:
            print_json({
                "status": "error",
                "message": "Not logged in"
            })
    
    elif args.command == 'connect':
        session.set_host(args.host)
        print(f"Successfully connected to {args.host}. Session configuration saved.")
    
    elif args.command == 'query':
        if not session.is_logged_in():
            print_json({"status": "error", "message": "Please login first"})
            sys.exit(1)
        
        if args.query_type == 'vertex':
            result = query_vertices(
                vid=args.vid,
                v_types=args.v_type,
                min_create_time=args.min_create_time,
                max_create_time=args.max_create_time,
                min_balance=args.min_balance,
                max_balance=args.max_balance
            )
            print_json(result)
        
        elif args.query_type == 'edge':
            result = query_edges(
                eid=args.eid,
                src_vid=args.src_vid,
                dst_vid=args.dst_vid,
                e_types=args.e_type,
                min_amount=args.min_amount,
                max_amount=args.max_amount,
                min_occur_time=args.min_occur_time,
                max_occur_time=args.max_occur_time
            )
            print_json(result)
        
        elif args.query_type == 'cycle':
            print_json({
                "status": "error",
                "message": "Cycle query not implemented yet"
            })
    
    elif args.command == 'insert':
        if not session.is_logged_in():
            print_json({"status": "error", "message": "Please login first"})
            sys.exit(1)
        
        if args.insert_type == 'vertex':
            result = insert_vertex(
                v_type=args.v_type,
                vid=args.vid,
                create_time=args.create_time,
                balance=args.balance
            )
            print_json(result)
        
        elif args.insert_type == 'edge':
            result = insert_edge(
                eid=args.eid,
                src_vid=args.src_vid,
                dst_vid=args.dst_vid,
                amount=args.amount,
                occur_time=args.occur_time,
                e_type=args.e_type,
                create_vertices=args.create_vertices
            )
            print_json(result)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
