"""OpenGauss 图数据库 DAO 层 - 面向过程实现。

提供通用 SQL 执行接口和数据类定义。
"""

from typing import Any, List, Optional, Tuple
from dataclasses import dataclass

import psycopg2

from server.opengauss.connection import connect


# ==================== 数据类定义 ====================


@dataclass
class Vertex:
    """点数据类"""

    vid: int
    v_type: str
    create_time: int
    balance: int

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "vid": self.vid,
            "v_type": self.v_type,
            "create_time": self.create_time,
            "balance": self.balance,
        }

    @classmethod
    def from_tuple(cls, data: Tuple) -> "Vertex":
        """从数据库查询结果元组创建实例"""
        return cls(vid=data[0], v_type=data[1], create_time=data[2], balance=data[3])


@dataclass
class Edge:
    """边数据类"""

    eid: int
    src_vid: int
    dst_vid: int
    amount: int
    occur_time: int
    e_type: str

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "eid": self.eid,
            "src_vid": self.src_vid,
            "dst_vid": self.dst_vid,
            "amount": self.amount,
            "occur_time": self.occur_time,
            "e_type": self.e_type,
        }

    @classmethod
    def from_tuple(cls, data: Tuple) -> "Edge":
        """从数据库查询结果元组创建实例"""
        return cls(
            eid=data[0],
            src_vid=data[1],
            dst_vid=data[2],
            amount=data[3],
            occur_time=data[4],
            e_type=data[5],
        )


@dataclass
class User:
    """用户数据类"""

    user_id: int
    username: str
    password_hash: str
    created_at: int
    last_login: Optional[int] = None

    def to_dict(self) -> dict:
        """转换为字典（不包含密码哈希）"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at,
            "last_login": self.last_login,
        }

    @classmethod
    def from_tuple(cls, data: Tuple) -> "User":
        """从数据库查询结果元组创建实例"""
        return cls(
            user_id=data[0],
            username=data[1],
            password_hash=data[2],
            created_at=data[3],
            last_login=data[4] if len(data) > 4 else None,
        )


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


def fetch_all(
    sql: str, params: Optional[Tuple] = None, **db_kwargs: Any
) -> List[Tuple]:
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


def fetch_one(
    sql: str, params: Optional[Tuple] = None, **db_kwargs: Any
) -> Optional[Tuple]:
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


def execute_batch(sql: str, params_list: List[Tuple], **db_kwargs: Any) -> int:
    """批量执行 DML 语句。

    Args:
        sql: 要执行的 SQL 语句
        params_list: 参数元组列表
        **db_kwargs: 数据库连接参数

    Returns:
        int: 总共受影响的行数
    """
    conn = None
    try:
        conn = connect(**db_kwargs)
        cur = conn.cursor()
        total_rows = 0
        for params in params_list:
            cur.execute(sql, params)
            total_rows += cur.rowcount
        conn.commit()
        cur.close()
        return total_rows
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"批量执行失败: {sql[:100]}... | 错误: {e}") from e
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

    print("\n=== 测试数据类 ===")
    # 测试 Vertex
    v = Vertex(vid=1, v_type="test", create_time=1234567890, balance=10000)
    print(f"Vertex: {v.to_dict()}")

    # 测试 Edge
    e = Edge(
        eid=1,
        src_vid=1,
        dst_vid=2,
        amount=5000,
        occur_time=1234567890,
        e_type="teset_e_type",
    )
    print(f"Edge: {e.to_dict()}")

    # 测试 User
    u = User(
        user_id=1, username="alice", password_hash="hash123", created_at=1234567890
    )
    print(f"User: {u.to_dict()}")
