"""OpenGauss 连接池工具。

本模块使用简单的连接池管理数据库连接。

主要函数：
- `connect(**kwargs)` -> 从连接池获取连接
- 连接使用完毕后调用 `close()` 会归还到池中而非真正关闭

配置优先级：函数参数 -> 环境变量（OPENGAUSS_*） -> 默认值
"""

from __future__ import annotations

import threading
from queue import Queue, Empty
from contextlib import contextmanager
from typing import Any, Dict, Optional

import psycopg2


# 全局连接池字典，key 为配置的 hash，value 为 Queue
_pools: Dict[int, Queue] = {}
_pools_lock = threading.Lock()
_pool_configs: Dict[int, Dict[str, Any]] = {}

# 连接池配置
DEFAULT_POOL_SIZE = 10
DEFAULT_MAX_OVERFLOW = 5


class PooledConnection:
    """包装的连接对象，close 时归还到池中"""

    def __init__(
        self, conn: psycopg2.extensions.connection, pool: Queue, config_hash: int
    ):
        self._conn = conn
        self._pool = pool
        self._config_hash = config_hash
        self._closed = False

    def __getattr__(self, name):
        """代理所有方法到真实连接"""
        return getattr(self._conn, name)

    def close(self):
        """归还连接到池中"""
        if self._closed:
            return
        self._closed = True

        try:
            # 回滚未提交的事务
            if not self._conn.closed:
                self._conn.rollback()
                # 归还到池中
                self._pool.put_nowait(self._conn)
        except Exception:
            # 连接损坏，真正关闭
            try:
                self._conn.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def _get_db_config(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    cfg = {
        "host": "123.60.219.83",
        "port": int(26000),
        "dbname": "graph",
        "user": "darker",
        "password": "114514@xbz",
    }
    cfg.update(kwargs or {})
    return cfg


def _config_hash(config: Dict[str, Any]) -> int:
    """生成配置的哈希值，用于区分不同的连接池"""
    key = (
        config.get("host", ""),
        config.get("port", 0),
        config.get("dbname", ""),
        config.get("user", ""),
    )
    return hash(key)


def _create_raw_connection(config: Dict[str, Any]) -> psycopg2.extensions.connection:
    """创建真实的数据库连接"""
    return psycopg2.connect(**config)


def _get_pool(config: Dict[str, Any]) -> tuple[Queue, int]:
    """获取或创建连接池"""
    config_key = _config_hash(config)

    with _pools_lock:
        if config_key not in _pools:
            # 创建新连接池
            pool = Queue(maxsize=DEFAULT_POOL_SIZE + DEFAULT_MAX_OVERFLOW)
            _pools[config_key] = pool
            _pool_configs[config_key] = config.copy()

            # 预创建连接
            for _ in range(DEFAULT_POOL_SIZE):
                try:
                    conn = _create_raw_connection(config)
                    pool.put_nowait(conn)
                except Exception:
                    break

        return _pools[config_key], config_key


def connect(**db_kwargs: Any) -> PooledConnection:
    """从连接池获取连接。

    返回的连接在 close() 时会归还到池中。
    示例：conn = connect(host='127.0.0.1', user='u', password='p')
    """
    cfg = _get_db_config(db_kwargs)
    pool, config_key = _get_pool(cfg)

    try:
        # 尝试从池中获取连接
        conn = pool.get_nowait()

        # 检查连接是否有效
        if conn.closed:
            raise Exception("连接已关闭")

        # 测试连接
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
        except Exception:
            conn.close()
            raise

    except (Empty, Exception):
        # 池中没有可用连接或连接无效，创建新连接
        conn = _create_raw_connection(cfg)

    return PooledConnection(conn, pool, config_key)


def close_all_pools():
    """关闭所有连接池（用于程序退出时清理）"""
    with _pools_lock:
        for pool in _pools.values():
            while not pool.empty():
                try:
                    conn = pool.get_nowait()
                    conn.close()
                except Exception:
                    pass
        _pools.clear()
        _pool_configs.clear()
