"""
数据库 Schema 初始化脚本。

包含所有表的 DDL 定义，并提供初始化、重置功能。
"""

from typing import Any, List
from server.opengauss.graph_dao import (
    execute_ddl,
    fetch_all,
    test_connection,
)


# ==================== DDL 定义 ====================

def get_vertex_table_ddl() -> str:
    """返回 Vertex 表的 CREATE TABLE 语句。"""
    return """
    CREATE TABLE IF NOT EXISTS vertex (
        vid       BIGINT PRIMARY KEY,
        v_type    SMALLINT NOT NULL,
        create_time BIGINT NOT NULL,
        balance   BIGINT NOT NULL
    ) WITH (ORIENTATION = ROW);
    """


def get_edge_table_ddl() -> str:
    """返回 Edge 表的 CREATE TABLE 语句。"""
    return """
    CREATE TABLE IF NOT EXISTS edge (
        eid        BIGINT PRIMARY KEY,
        src_vid    BIGINT NOT NULL,
        dst_vid    BIGINT NOT NULL,
        amount     BIGINT NOT NULL,
        occur_time BIGINT NOT NULL,
        e_type     SMALLINT NOT NULL
    ) WITH (ORIENTATION = ROW);
    """


def get_user_table_ddl() -> str:
    """返回 User 表的 CREATE TABLE 语句（用于用户登录）。"""
    return """
    CREATE TABLE IF NOT EXISTS users (
        user_id       SERIAL PRIMARY KEY,
        username      VARCHAR(64) UNIQUE NOT NULL,
        password_hash VARCHAR(256) NOT NULL,
        created_at    BIGINT NOT NULL,
        last_login    BIGINT
    ) WITH (ORIENTATION = ROW);
    """


def get_edge_indexes_ddl() -> List[str]:
    """返回 Edge 表核心索引的 DDL 列表（用于时序剪枝加速）。"""
    return [
        "CREATE INDEX IF NOT EXISTS idx_edge_src_time ON edge(src_vid, occur_time);",
        "CREATE INDEX IF NOT EXISTS idx_edge_dst_time ON edge(dst_vid, occur_time);",
    ]


def get_user_indexes_ddl() -> List[str]:
    """返回 User 表索引的 DDL 列表。"""
    return [
        "CREATE INDEX IF NOT EXISTS idx_user_username ON users(username);",
    ]


def get_drop_tables_ddl() -> List[str]:
    """返回删除所有表的 DDL 列表。"""
    return [
        "DROP TABLE IF EXISTS edge CASCADE;",
        "DROP TABLE IF EXISTS vertex CASCADE;",
        "DROP TABLE IF EXISTS users CASCADE;",
    ]


# ==================== 初始化函数 ====================

def init_schema(**db_kwargs: Any) -> None:
    """初始化数据库 Schema：创建点边表、用户表及核心索引。
    
    Args:
        **db_kwargs: 数据库连接参数（可选），会覆盖默认配置
        
    Raises:
        Exception: 数据库操作失败
    """
    try:
        # 1. 创建 Vertex 表
        execute_ddl(get_vertex_table_ddl(), **db_kwargs)
        print("✓ Vertex 表创建成功")
        
        # 2. 创建 Edge 表
        execute_ddl(get_edge_table_ddl(), **db_kwargs)
        print("✓ Edge 表创建成功")
        
        # 3. 创建 User 表
        execute_ddl(get_user_table_ddl(), **db_kwargs)
        print("✓ Users 表创建成功")
        
        # 4. 创建 Edge 索引
        for idx_sql in get_edge_indexes_ddl():
            execute_ddl(idx_sql, **db_kwargs)
        print("✓ Edge 表索引创建成功")
        
        # 5. 创建 User 索引
        for idx_sql in get_user_indexes_ddl():
            execute_ddl(idx_sql, **db_kwargs)
        print("✓ Users 表索引创建成功")
        
        print("✓ Schema 初始化完成")
        
    except Exception as e:
        raise Exception(f"初始化 Schema 失败: {e}") from e


def drop_all_tables(**db_kwargs: Any) -> None:
    """删除所有表（危险操作，仅用于测试环境重置）。"""
    try:
        for drop_sql in get_drop_tables_ddl():
            execute_ddl(drop_sql, **db_kwargs)
        print("✓ 已删除所有表")
    except Exception as e:
        raise Exception(f"删除表失败: {e}") from e


def verify_schema(**db_kwargs: Any) -> bool:
    """验证 Schema 是否正确创建。
    
    Returns:
        bool: 所有表都存在返回 True，否则返回 False
    """
    try:
        tables = fetch_all("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' AND tablename IN ('vertex', 'edge', 'users');
        """, **db_kwargs)
        
        table_names = [t[0] for t in tables]
        expected_tables = ['vertex', 'edge', 'users']
        
        print(f"已创建的表: {table_names}")
        
        missing_tables = set(expected_tables) - set(table_names)
        if missing_tables:
            print(f"✗ 缺失的表: {missing_tables}")
            return False
        
        print("✓ 所有必需的表都已创建")
        return True
        
    except Exception as e:
        print(f"✗ 验证 Schema 失败: {e}")
        return False


# ==================== 主函数 ====================

def initialize_database(**db_kwargs) -> bool:
    """初始化数据库 Schema。
    
    Args:
        **db_kwargs: 数据库连接参数（可选），会覆盖默认配置
        
    Returns:
        bool: 初始化成功返回 True，失败返回 False
    """
    try:
        print("=" * 50)
        print("开始初始化数据库 Schema...")
        print("=" * 50)
        
        # 1. 测试连接
        print("\n[1/3] 测试数据库连接...")
        if not test_connection(**db_kwargs):
            print("✗ 数据库连接失败，请检查配置")
            return False
        
        # 2. 创建表和索引
        print("\n[2/3] 创建 Schema（表和索引）...")
        init_schema(**db_kwargs)
        
        # 3. 验证 Schema
        print("\n[3/3] 验证 Schema...")
        if not verify_schema(**db_kwargs):
            print("✗ Schema 验证失败")
            return False
        
        print("\n" + "=" * 50)
        print("✓ 数据库初始化完成！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return False


def reset_database(**db_kwargs) -> bool:
    """重置数据库（删除所有表后重新初始化）。
    
    仅用于开发/测试环境。
    
    Args:
        **db_kwargs: 数据库连接参数（可选）
        
    Returns:
        bool: 重置成功返回 True，失败返回 False
    """
    try:
        print("=" * 50)
        print("警告：即将删除所有数据表！")
        print("=" * 50)
        
        response = input("是否继续？(yes/no): ").strip().lower()
        if response != 'yes':
            print("✗ 已取消操作")
            return False
        
        # 1. 删除表
        print("\n[1/3] 删除已有表...")
        drop_all_tables(**db_kwargs)
        
        # 2. 重新初始化
        print("\n[2/3] 重新初始化 Schema...")
        init_schema(**db_kwargs)
        
        # 3. 验证 Schema
        print("\n[3/3] 验证 Schema...")
        if not verify_schema(**db_kwargs):
            print("✗ Schema 验证失败")
            return False
        
        print("\n" + "=" * 50)
        print("✓ 数据库重置完成！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 重置失败: {e}")
        return False


if __name__ == "__main__":
    # 快速初始化示例
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_database()
    else:
        initialize_database()
