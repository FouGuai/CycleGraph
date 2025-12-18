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
    Edge
)


# ==================== Vertex 操作 ====================

def query_vertices(
    vid: Optional[int] = None,
    v_types: Optional[List[int]] = None,
    min_create_time: Optional[int] = None,
    max_create_time: Optional[int] = None,
    min_balance: Optional[int] = None,
    max_balance: Optional[int] = None,
    **db_kwargs: Any
) -> Dict[str, Any]:
    """查询点。"""
    try:
        conditions = []
        params = []
        
        if vid is not None:
            conditions.append("vid = %s")
            params.append(vid)
        
        if v_types:
            placeholders = ','.join(['%s'] * len(v_types))
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
        
        sql = "SELECT vid, v_type, create_time, balance FROM vertex"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        results = fetch_all(sql, tuple(params), **db_kwargs)
        vertices = [Vertex.from_tuple(row).to_dict() for row in results]
        
        return {
            "status": "success",
            "found": len(vertices) > 0,
            "count": len(vertices),
            "data": vertices
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Query vertices failed: {e}"
        }


def insert_vertex(
    v_type: int,
    vid: Optional[int] = None,
    create_time: Optional[int] = None,
    balance: int = 0,
    **db_kwargs: Any
) -> Dict[str, Any]:
    """插入点。"""
    try:
        # 如果未指定 vid，生成一个
        if vid is None:
            # 获取当前最大 vid
            result = fetch_one("SELECT MAX(vid) FROM vertex", **db_kwargs)
            max_vid = result[0] if result and result[0] is not None else 0
            vid = max_vid + 1
        
        # 如果未指定创建时间，使用当前时间
        if create_time is None:
            create_time = int(time.time())
        
        # 插入点
        execute_dml(
            "INSERT INTO vertex (vid, v_type, create_time, balance) VALUES (%s, %s, %s, %s)",
            (vid, v_type, create_time, balance),
            **db_kwargs
        )
        
        return {
            "status": "success",
            "message": f"Vertex {vid} created successfully.",
            "data": {
                "vid": vid,
                "v_type": v_type,
                "create_time": create_time,
                "balance": balance
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Insert vertex failed: {e}"
        }


# ==================== Edge 操作 ====================

def query_edges(
    eid: Optional[int] = None,
    src_vid: Optional[int] = None,
    dst_vid: Optional[int] = None,
    e_types: Optional[List[int]] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    min_occur_time: Optional[int] = None,
    max_occur_time: Optional[int] = None,
    **db_kwargs: Any
) -> Dict[str, Any]:
    """查询边。"""
    try:
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
            placeholders = ','.join(['%s'] * len(e_types))
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
        
        sql = "SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM edge"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        results = fetch_all(sql, tuple(params), **db_kwargs)
        edges = [Edge.from_tuple(row).to_dict() for row in results]
        
        return {
            "status": "success",
            "found": len(edges) > 0,
            "count": len(edges),
            "data": edges
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Query edges failed: {e}"
        }


def insert_edge(
    eid: int,
    src_vid: int,
    dst_vid: int,
    amount: int,
    occur_time: Optional[int] = None,
    e_type: int = 0,
    create_vertices: bool = False,
    **db_kwargs: Any
) -> Dict[str, Any]:
    """插入边。"""
    try:
        # 如果未指定发生时间，使用当前时间
        if occur_time is None:
            occur_time = int(time.time())
        
        # 如果需要自动创建点
        if create_vertices:
            # 检查源点是否存在
            src_exists = fetch_one("SELECT 1 FROM vertex WHERE vid = %s", (src_vid,), **db_kwargs)
            if not src_exists:
                insert_vertex(v_type=0, vid=src_vid, **db_kwargs)
            
            # 检查目标点是否存在
            dst_exists = fetch_one("SELECT 1 FROM vertex WHERE vid = %s", (dst_vid,), **db_kwargs)
            if not dst_exists:
                insert_vertex(v_type=0, vid=dst_vid, **db_kwargs)
        
        # 插入边
        execute_dml(
            "INSERT INTO edge (eid, src_vid, dst_vid, amount, occur_time, e_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (eid, src_vid, dst_vid, amount, occur_time, e_type),
            **db_kwargs
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
                "e_type": e_type
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Insert edge failed: {e}"
        }
