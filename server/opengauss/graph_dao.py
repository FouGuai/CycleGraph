"""OpenGauss 图数据库 DAO 层 - 面向过程实现。

提供点边表的 DDL 初始化、索引创建及通用 SQL 执行接口。
"""
from typing import Any, List, Optional, Tuple

import psycopg2

from connection import connect


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


def get_edge_indexes_ddl() -> List[str]:
    """返回 Edge 表核心索引的 DDL 列表（用于时序剪枝加速）。"""
    return [
        "CREATE INDEX IF NOT EXISTS idx_edge_src_time ON edge(src_vid, occur_time);",
        "CREATE INDEX IF NOT EXISTS idx_edge_dst_time ON edge(dst_vid, occur_time);",
    ]


# ==================== 初始化函数 ====================

def init_schema(**db_kwargs: Any) -> None:
    """初始化数据库 Schema：创建点边表及核心索引。
    
    Args:
        **db_kwargs: 数据库连接参数（可选），会覆盖默认配置
        
    Raises:
        psycopg2.Error: 数据库操作失败
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        conn.autocommit = False
        cur = conn.cursor()
        
        # 1. 创建 Vertex 表
        cur.execute(get_vertex_table_ddl())
        print("✓ Vertex 表创建成功")
        
        # 2. 创建 Edge 表
        cur.execute(get_edge_table_ddl())
        print("✓ Edge 表创建成功")
        
        # 3. 创建索引
        for idx_sql in get_edge_indexes_ddl():
            cur.execute(idx_sql)
        print("✓ Edge 表索引创建成功")
        
        conn.commit()
        cur.close()
        print("✓ Schema 初始化完成")
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"初始化 Schema 失败: {e}") from e
    finally:
        if conn:
            conn.close()


def drop_all_tables(**db_kwargs: Any) -> None:
    """删除点边表（危险操作，仅用于测试环境重置）。"""
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS edge CASCADE;")
        cur.execute("DROP TABLE IF EXISTS vertex CASCADE;")
        conn.commit()
        cur.close()
        print("✓ 已删除所有表")
    finally:
        if conn:
            conn.close()


# ==================== 通用 SQL 执行接口 ====================

def execute_ddl(sql: str, **db_kwargs: Any) -> None:
    """执行 DDL 语句（CREATE/DROP/ALTER 等无返回值操作）。
    
    Args:
        sql: 要执行的 SQL 语句
        **db_kwargs: 数据库连接参数
        
    Raises:
        psycopg2.Error: SQL 执行失败
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"执行 DDL 失败: {sql[:100]}... | 错误: {e}") from e
    finally:
        if conn:
            conn.close()


def execute_dml(sql: str, params: Optional[Tuple] = None, **db_kwargs: Any) -> int:
    """执行 DML 语句（INSERT/UPDATE/DELETE），返回影响的行数。
    
    Args:
        sql: 要执行的 SQL 语句
        params: 参数化查询的参数元组
        **db_kwargs: 数据库连接参数
        
    Returns:
        int: 受影响的行数
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute(sql, params)
        rowcount = cur.rowcount
        conn.commit()
        cur.close()
        return rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"执行 DML 失败: {sql[:100]}... | 错误: {e}") from e
    finally:
        if conn:
            conn.close()


def fetch_all(sql: str, params: Optional[Tuple] = None, **db_kwargs: Any) -> List[Tuple]:
    """执行 SELECT 查询并返回所有结果行。
    
    Args:
        sql: 查询 SQL 语句
        params: 参数化查询的参数元组
        **db_kwargs: 数据库连接参数
        
    Returns:
        List[Tuple]: 查询结果列表
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute(sql, params)
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        raise Exception(f"查询失败: {sql[:100]}... | 错误: {e}") from e
    finally:
        if conn:
            conn.close()


def fetch_one(sql: str, params: Optional[Tuple] = None, **db_kwargs: Any) -> Optional[Tuple]:
    """执行 SELECT 查询并返回第一行结果。
    
    Args:
        sql: 查询 SQL 语句
        params: 参数化查询的参数元组
        **db_kwargs: 数据库连接参数
        
    Returns:
        Optional[Tuple]: 查询结果的第一行，若无结果返回 None
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        raise Exception(f"查询失败: {sql[:100]}... | 错误: {e}") from e
    finally:
        if conn:
            conn.close()


# ==================== 便捷测试函数 ====================

def test_connection(**db_kwargs: Any) -> bool:
    """测试数据库连接是否正常。"""
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        print(f"✓ 数据库连接成功: {version[0]}")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    # 快速测试
    print("=== 测试数据库连接 ===")
    test_connection()
    
    print("\n=== 初始化 Schema ===")
    init_schema()
    
    print("\n=== 验证表是否存在 ===")
    tables = fetch_all("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename IN ('vertex', 'edge');
    """)
    print(f"已创建的表: {[t[0] for t in tables]}")