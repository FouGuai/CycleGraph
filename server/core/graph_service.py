"""图数据服务。

提供点、边的查询和插入功能。
"""

import time
from typing import List, Dict, Any, Optional
from server.opengauss.graph_dao import (
    execute_dml,
    fetch_all,
    fetch_one,
    Vertex,
    Edge,
    get_user_table_name,
)

import server.core.bibfs as cycle_ag
import server.core.membibfs as mem_cycle_ag


# ==================== Vertex 操作 ====================


def query_vertices(
    username: str,
    vid: Optional[int] = None,
    v_types: Optional[List[str]] = None,
    min_create_time: Optional[int] = None,
    max_create_time: Optional[int] = None,
    min_balance: Optional[int] = None,
    max_balance: Optional[int] = None,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """查询点。

    Args:
        username: 用户名，用于确定查询哪个用户的表
    """
    try:
        conditions = []
        params = []

        if vid is not None:
            conditions.append("vid = %s")
            params.append(vid)

        if v_types:
            placeholders = ",".join(["%s"] * len(v_types))
            conditions.append(f"v_type IN ({placeholders})")
            params.extend(v_types)

        if min_create_time is not None:
            conditions.append("create_time >= %s")
            params.append(min_create_time)

        if max_create_time is not None:
            conditions.append("create_time <= %s")
            params.append(max_create_time)

        if min_balance is not None:
            conditions.append("balance >= %s")
            params.append(min_balance)

        if max_balance is not None:
            conditions.append("balance <= %s")
            params.append(max_balance)

        vertex_table_name, _ = get_user_table_name(username)
        sql = f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        results = fetch_all(sql, tuple(params), **db_kwargs)
        vertices = [Vertex.from_tuple(row).to_dict() for row in results]

        return {
            "status": "success",
            "found": len(vertices) > 0,
            "count": len(vertices),
            "data": vertices,
        }

    except Exception as e:
        return {"status": "error", "message": f"Query vertices failed: {e}"}


def insert_vertex(
    username: str,
    v_type: str,
    vid: Optional[int] = None,
    create_time: Optional[int] = None,
    balance: int = 0,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """插入点。

    Args:
        username: 用户名，用于确定操作哪个用户的表
    """
    try:
        vertex_table_name, _ = get_user_table_name(username)
        # 验证输入
        if not v_type or (isinstance(v_type, str) and not v_type.strip()):
            return {"status": "error", "message": "Vertex type cannot be empty"}

        if vid is not None:
            if not isinstance(vid, int) or vid <= 0:
                return {
                    "status": "error",
                    "message": "Vertex ID must be a positive integer",
                }

            # 检查ID是否已存在
            existing = fetch_one(
                f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s", (vid,), **db_kwargs
            )
            if existing:
                return {"status": "error", "message": f"Vertex {vid} already exists"}

        if balance < 0:
            return {"status": "error", "message": "Balance must be non-negative"}

        if create_time is not None and create_time <= 0:
            return {
                "status": "error",
                "message": "Create time must be a positive integer",
            }

        # 如果未指定 vid，生成一个
        if vid is None:
            # 获取当前最大 vid
            result = fetch_one(f"SELECT MAX(vid) FROM {vertex_table_name}", **db_kwargs)
            max_vid = result[0] if result and result[0] is not None else 0
            vid = max_vid + 1

        # 如果未指定创建时间，使用当前时间
        if create_time is None:
            create_time = int(time.time())

        # 插入点
        execute_dml(
            f"INSERT INTO {vertex_table_name} (vid, v_type, create_time, balance) VALUES (%s, %s, %s, %s)",
            (vid, v_type, create_time, balance),
            **db_kwargs,
        )

        return {
            "status": "success",
            "message": f"Vertex {vid} created successfully.",
            "data": {
                "vid": vid,
                "v_type": v_type,
                "create_time": create_time,
                "balance": balance,
            },
        }

    except Exception as e:
        # 检查是否是重复键错误
        error_msg = str(e).lower()
        if "duplicate" in error_msg or "unique" in error_msg:
            return {"status": "error", "message": f"Vertex {vid} already exists"}
        return {"status": "error", "message": f"Insert vertex failed: {e}"}


# ==================== Edge 操作 ====================


def query_edges(
    username: str,
    eid: Optional[int] = None,
    src_vid: Optional[int] = None,
    dst_vid: Optional[int] = None,
    e_types: Optional[List[str]] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    min_occur_time: Optional[int] = None,
    max_occur_time: Optional[int] = None,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """查询边。

    Args:
        username: 用户名，用于确定查询哪个用户的表
    """
    try:
        _, edge_table_name = get_user_table_name(username)
        conditions = []
        params = []

        if eid is not None:
            conditions.append("eid = %s")
            params.append(eid)

        if src_vid is not None:
            conditions.append("src_vid = %s")
            params.append(src_vid)

        if dst_vid is not None:
            conditions.append("dst_vid = %s")
            params.append(dst_vid)

        if e_types:
            placeholders = ",".join(["%s"] * len(e_types))
            conditions.append(f"e_type IN ({placeholders})")
            params.extend(e_types)

        if min_amount is not None:
            conditions.append("amount >= %s")
            params.append(min_amount)

        if max_amount is not None:
            conditions.append("amount <= %s")
            params.append(max_amount)

        if min_occur_time is not None:
            conditions.append("occur_time >= %s")
            params.append(min_occur_time)

        if max_occur_time is not None:
            conditions.append("occur_time <= %s")
            params.append(max_occur_time)

        sql = f"SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM {edge_table_name}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        results = fetch_all(sql, tuple(params), **db_kwargs)
        edges = [Edge.from_tuple(row).to_dict() for row in results]

        return {
            "status": "success",
            "found": len(edges) > 0,
            "count": len(edges),
            "data": edges,
        }

    except Exception as e:
        return {"status": "error", "message": f"Query edges failed: {e}"}


def insert_edge(
    username: str,
    eid: Optional[int],
    src_vid: int,
    dst_vid: int,
    amount: int,
    occur_time: Optional[int] = None,
    e_type: int = 0,
    create_vertices: bool = False,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """插入边。

    Args:
        username: 用户名，用于确定操作哪个用户的表
    """
    try:
        vertex_table_name, edge_table_name = get_user_table_name(username)
        if eid is None:
            # 获取当前最大 vid
            result = fetch_one(f"SELECT MAX(eid) FROM {edge_table_name}", **db_kwargs)
            max_eid = result[0] if result and result[0] is not None else 0
            eid = max_eid + 1
        elif not isinstance(eid, int) or eid <= 0:
            return {"status": "error", "message": "Edge ID must be a positive integer"}

        if not isinstance(src_vid, int) or src_vid <= 0:
            return {
                "status": "error",
                "message": "Source vertex ID must be a positive integer",
            }

        if not isinstance(dst_vid, int) or dst_vid <= 0:
            return {
                "status": "error",
                "message": "Destination vertex ID must be a positive integer",
            }

        if not isinstance(amount, int) or amount < 0:
            return {"status": "error", "message": "Amount must be a positive integer"}

        if occur_time is not None and occur_time < 0:
            return {
                "status": "error",
                "message": "Occur time must be a positive integer",
            }

        if not e_type or (isinstance(e_type, str) and not e_type.strip()):
            return {"status": "error", "message": "Edge type cannot be empty"}

        # 检查边ID是否已存在
        existing_edge = fetch_one(
            f"SELECT 1 FROM {edge_table_name} WHERE eid = %s", (eid,), **db_kwargs
        )
        if existing_edge:
            return {"status": "error", "message": f"Edge {eid} already exists"}

        # 如果未指定发生时间，使用当前时间
        if occur_time is None:
            occur_time = int(time.time())

        # 如果需要自动创建点
        if create_vertices:
            # 检查源点是否存在
            src_exists = fetch_one(
                f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s",
                (src_vid,),
                **db_kwargs,
            )
            if not src_exists:
                insert_vertex(username, v_type="auto", vid=src_vid, **db_kwargs)

            # 检查目标点是否存在
            dst_exists = fetch_one(
                f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s",
                (dst_vid,),
                **db_kwargs,
            )
            if not dst_exists:
                insert_vertex(username, v_type="auto", vid=dst_vid, **db_kwargs)
        else:
            # 验证点是否存在
            src_exists = fetch_one(
                f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s",
                (src_vid,),
                **db_kwargs,
            )
            if not src_exists:
                return {
                    "status": "error",
                    "message": f"Source vertex {src_vid} does not exist",
                }

            dst_exists = fetch_one(
                f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s",
                (dst_vid,),
                **db_kwargs,
            )
            if not dst_exists:
                return {
                    "status": "error",
                    "message": f"Destination vertex {dst_vid} does not exist",
                }

        # 插入边
        execute_dml(
            f"INSERT INTO {edge_table_name} (eid, src_vid, dst_vid, amount, occur_time, e_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (eid, src_vid, dst_vid, amount, occur_time, e_type),
            **db_kwargs,
        )

        return {
            "status": "success",
            "message": f"Edge {eid} created successfully.",
            "data": {
                "eid": eid,
                "src_vid": src_vid,
                "dst_vid": dst_vid,
                "amount": amount,
                "occur_time": occur_time,
                "e_type": e_type,
            },
        }

    except Exception as e:
        # 检查是否是重复键错误
        error_msg = str(e).lower()
        if "duplicate" in error_msg or "unique" in error_msg:
            return {"status": "error", "message": f"Edge {eid} already exists"}
        if "foreign key" in error_msg or "violates" in error_msg:
            return {
                "status": "error",
                "message": "Source or destination vertex does not exist",
            }
        return {"status": "error", "message": f"Insert edge failed: {e}"}


def query_cycles(
    username: str,
    start_vid: int,
    max_depth: int,
    direction: str = "forward",
    vertex_filter_v_type: Optional[List[str]] = None,
    vertex_filter_min_balance: Optional[int] = None,
    edge_filter_e_type: Optional[List[str]] = None,
    edge_filter_min_amount: Optional[int] = None,
    edge_filter_max_amount: Optional[int] = None,
    limit: int = 10,
    allow_duplicate_vertices: bool = False,
    allow_duplicate_edges: bool = False,
    use_memory: bool = True,
) -> Dict[str, Any]:
    """查询环路。

    Args:
        username: 用户名，用于确定查询哪个用户的表
        use_memory: 是否使用内存版本(默认True)。内存版本会先加载数据到内存，
                   适合数据库访问较慢的场景；False则使用数据库临时表版本。
    """
    # 验证输入
    if not isinstance(start_vid, int) or start_vid <= 0:
        return {
            "status": "error",
            "message": "Start vertex ID must be a positive integer",
        }

    if not isinstance(max_depth, int) or max_depth <= 0:
        return {"status": "error", "message": "Max depth must be a positive integer"}

    if max_depth > 20:
        return {
            "status": "error",
            "message": "Max depth cannot exceed 20 for performance reasons",
        }

    if direction not in ["forward", "any"]:
        return {"status": "error", "message": "Direction must be 'forward' or 'any'"}

    if vertex_filter_min_balance is not None and vertex_filter_min_balance < 0:
        return {
            "status": "error",
            "message": "Vertex minimum balance must be non-negative",
        }

    if edge_filter_min_amount is not None and edge_filter_min_amount < 0:
        return {
            "status": "error",
            "message": "Edge minimum amount must be non-negative",
        }

    if edge_filter_max_amount is not None and edge_filter_max_amount < 0:
        return {
            "status": "error",
            "message": "Edge maximum amount must be non-negative",
        }

    if edge_filter_min_amount is not None and edge_filter_max_amount is not None:
        if edge_filter_min_amount > edge_filter_max_amount:
            return {
                "status": "error",
                "message": "Edge minimum amount cannot be greater than maximum amount",
            }

    if limit <= 0:
        return {"status": "error", "message": "Limit must be a positive integer"}

    if limit > 1000:
        return {
            "status": "error",
            "message": "Limit cannot exceed 1000 for performance reasons",
        }

    # 根据参数选择使用哪个版本
    if use_memory:
        return mem_cycle_ag.query_cycles(
            start_vid,
            max_depth,
            username,
            direction,
            vertex_filter_v_type,
            vertex_filter_min_balance,
            edge_filter_e_type,
            edge_filter_min_amount,
            edge_filter_max_amount,
            limit,
            allow_duplicate_vertices,
            allow_duplicate_edges,
        )
    else:
        return cycle_ag.query_cycles(
            start_vid,
            max_depth,
            direction,
            vertex_filter_v_type,
            vertex_filter_min_balance,
            edge_filter_e_type,
            edge_filter_min_amount,
            edge_filter_max_amount,
            limit,
            allow_duplicate_vertices,
            allow_duplicate_edges,
        )


# 在文件末尾添加删除函数
def delete_vertex(username: str, vid: int, **db_kwargs: Any) -> Dict[str, Any]:
    """删除点及其相关的所有边。

    Args:
        username: 用户名，用于确定操作哪个用户的表
        vid: 要删除的点ID
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: 删除结果
    """
    try:
        vertex_table_name, edge_table_name = get_user_table_name(username)
        # 验证输入
        if not isinstance(vid, int) or vid <= 0:
            return {
                "status": "error",
                "message": "Vertex ID must be a positive integer",
            }

        # 检查点是否存在
        existing = fetch_one(
            f"SELECT 1 FROM {vertex_table_name} WHERE vid = %s", (vid,), **db_kwargs
        )
        if not existing:
            return {"status": "error", "message": f"Vertex {vid} does not exist"}

        # 统计相关边的数量
        edge_count_result = fetch_one(
            f"SELECT COUNT(*) FROM {edge_table_name} WHERE src_vid = %s OR dst_vid = %s",
            (vid, vid),
            **db_kwargs,
        )
        edges_deleted = edge_count_result[0] if edge_count_result else 0

        # 删除相关的边（作为源点或目标点）
        execute_dml(
            f"DELETE FROM {edge_table_name} WHERE src_vid = %s OR dst_vid = %s",
            (vid, vid),
            **db_kwargs,
        )

        # 删除点
        execute_dml(
            f"DELETE FROM {vertex_table_name} WHERE vid = %s", (vid,), **db_kwargs
        )

        return {
            "status": "success",
            "message": f"Vertex {vid} deleted successfully. {edges_deleted} related edges also deleted.",
            "data": {"vid": vid, "edges_deleted": edges_deleted},
        }

    except Exception as e:
        return {"status": "error", "message": f"Delete vertex failed: {e}"}


def delete_edge(username: str, eid: int, **db_kwargs: Any) -> Dict[str, Any]:
    """删除边。

    Args:
        username: 用户名，用于确定操作哪个用户的表
        eid: 要删除的边ID
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: 删除结果
    """
    try:
        _, edge_table_name = get_user_table_name(username)
        # 验证输入
        if not isinstance(eid, int) or eid <= 0:
            return {"status": "error", "message": "Edge ID must be a positive integer"}

        # 检查边是否存在
        existing = fetch_one("SELECT 1 FROM edge WHERE eid = %s", (eid,), **db_kwargs)
        if not existing:
            return {"status": "error", "message": f"Edge {eid} does not exist"}

        # 删除边
        rows_affected = execute_dml(
            f"DELETE FROM {edge_table_name} WHERE eid = %s", (eid,), **db_kwargs
        )

        if rows_affected > 0:
            return {
                "status": "success",
                "message": f"Edge {eid} deleted successfully.",
                "data": {"eid": eid},
            }
        else:
            return {"status": "error", "message": f"Edge {eid} does not exist"}

    except Exception as e:
        return {"status": "error", "message": f"Delete edge failed: {e}"}


def update_vertex(
    username: str,
    vid: int,
    v_type: Optional[str] = None,
    balance: Optional[int] = None,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """更新点的属性。

    Args:
        username: 用户名，用于确定操作哪个用户的表
        vid: 要更新的点ID（必需）
        v_type: 新的点类型（可选）
        balance: 新的余额（可选）
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: 更新结果
    """
    try:
        vertex_table_name, _ = get_user_table_name(username)
        # 验证点ID
        if not isinstance(vid, int) or vid <= 0:
            return {
                "status": "error",
                "message": "Vertex ID must be a positive integer",
            }

        # 检查点是否存在
        existing = fetch_one(
            f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name} WHERE vid = %s",
            (vid,),
            **db_kwargs,
        )
        if not existing:
            return {"status": "error", "message": f"Vertex {vid} does not exist"}

        # 至少需要提供一个要更新的字段
        if v_type is None and balance is None:
            return {
                "status": "error",
                "message": "At least one field must be provided for update",
            }

        # 验证新值
        if v_type is not None:
            if not isinstance(v_type, str) or not v_type.strip():
                return {"status": "error", "message": "Vertex type cannot be empty"}

        if balance is not None:
            if not isinstance(balance, int) or balance < 0:
                return {
                    "status": "error",
                    "message": "Balance must be a non-negative integer",
                }

        # 构建更新语句
        update_fields = []
        params = []

        if v_type is not None:
            update_fields.append("v_type = %s")
            params.append(v_type)

        if balance is not None:
            update_fields.append("balance = %s")
            params.append(balance)

        params.append(vid)

        sql = f"UPDATE {vertex_table_name} SET {', '.join(update_fields)} WHERE vid = %s"
        execute_dml(sql, tuple(params), **db_kwargs)

        # 查询更新后的数据
        updated = fetch_one(
            f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name} WHERE vid = %s",
            (vid,),
            **db_kwargs,
        )

        assert updated is not None
        updated_vertex = Vertex.from_tuple(updated)

        return {
            "status": "success",
            "message": f"Vertex {vid} updated successfully.",
            "data": updated_vertex.to_dict(),
        }

    except Exception as e:
        return {"status": "error", "message": f"Update vertex failed: {e}"}


def update_edge(
    username: str,
    eid: int,
    amount: Optional[int] = None,
    occur_time: Optional[int] = None,
    e_type: Optional[str] = None,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """更新边的属性。

    Args:
        username: 用户名，用于确定操作哪个用户的表
        eid: 要更新的边ID（必需）
        amount: 新的交易金额（可选）
        occur_time: 新的发生时间（可选）
        e_type: 新的边类型（可选）
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: 更新结果
    """
    try:
        _, edge_table_name = get_user_table_name(username)
        # 验证边ID
        if not isinstance(eid, int) or eid <= 0:
            return {
                "status": "error",
                "message": "Edge ID must be a positive integer",
            }

        # 检查边是否存在
        existing = fetch_one(
            f"SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM {edge_table_name} WHERE eid = %s",
            (eid,),
            **db_kwargs,
        )
        if not existing:
            return {"status": "error", "message": f"Edge {eid} does not exist"}

        # 至少需要提供一个要更新的字段
        if amount is None and occur_time is None and e_type is None:
            return {
                "status": "error",
                "message": "At least one field must be provided for update",
            }

        # 验证新值
        if amount is not None:
            if not isinstance(amount, int) or amount < 0:
                return {
                    "status": "error",
                    "message": "Amount must be a non-negative integer",
                }

        if occur_time is not None:
            if not isinstance(occur_time, int) or occur_time <= 0:
                return {
                    "status": "error",
                    "message": "Occur time must be a positive integer",
                }

        if e_type is not None:
            if not isinstance(e_type, str) or not e_type.strip():
                return {"status": "error", "message": "Edge type cannot be empty"}

        # 构建更新语句
        update_fields = []
        params = []

        if amount is not None:
            update_fields.append("amount = %s")
            params.append(amount)

        if occur_time is not None:
            update_fields.append("occur_time = %s")
            params.append(occur_time)

        if e_type is not None:
            update_fields.append("e_type = %s")
            params.append(e_type)

        params.append(eid)

        sql = f"UPDATE {edge_table_name} SET {', '.join(update_fields)} WHERE eid = %s"
        execute_dml(sql, tuple(params), **db_kwargs)

        # 查询更新后的数据
        updated = fetch_one(
            f"SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM {edge_table_name} WHERE eid = %s",
            (eid,),
            **db_kwargs,
        )

        assert updated is not None
        updated_edge = Edge.from_tuple(updated)

        return {
            "status": "success",
            "message": f"Edge {eid} updated successfully.",
            "data": updated_edge.to_dict(),
        }

    except Exception as e:
        return {"status": "error", "message": f"Update edge failed: {e}"}
