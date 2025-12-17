"""OpenGauss 过程化连接工具。

本模块不使用连接池，调用时即时建立连接，使用完毕后立即关闭。

主要函数：
- `connect(**kwargs)` -> 建立并返回 psycopg2 连接
- `connection_ctx(**kwargs)` -> 上下文管理器，yield (conn, cur)
- `execute` / `executemany` / `fetch_one` / `fetch_all`

配置优先级：函数参数 -> 环境变量（OPENGAUSS_*） -> 默认值
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional

import psycopg2
import psycopg2.extras


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

def connect(**db_kwargs: Any) -> psycopg2.extensions.connection:
	"""创建并返回一个新的数据库连接。

	示例：connect(host='127.0.0.1', user='u', password='p')
	"""
	cfg = _get_db_config(db_kwargs)
	return psycopg2.connect(**cfg)



