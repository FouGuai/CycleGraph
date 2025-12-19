"""环路查找服务 - 基于双向BFS的高效环检测算法。

使用OpenGauss的UNLOGGED临时表进行边扩展,支持时序过滤和各种约束条件。
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Set, Tuple
from server.opengauss.graph_dao import (
    execute_ddl,
    execute_dml,
    fetch_all,
    fetch_one,
    Vertex,
    Edge,
    get_user_table_name,
)


def query_cycles(
    start_vid: int,
    max_depth: int,
    username: str,
    direction: str = "forward",
    vertex_filter_v_types: Optional[List[str]] = None,
    vertex_filter_min_balance: Optional[int] = None,
    edge_filter_e_types: Optional[List[str]] = None,
    edge_filter_min_amount: Optional[int] = None,
    edge_filter_max_amount: Optional[int] = None,
    limit: int = 10,
    allow_duplicate_vertices: bool = False,
    allow_duplicate_edges: bool = False,
    **db_kwargs: Any,
) -> Dict[str, Any]:
    """查询环路 - 使用双向BFS算法。

    Args:
        start_vid: 起始点ID
        max_depth: 最大搜索深度(环路长度)
        username: 用户名，用于确定查询哪个用户的表
        direction: 时序方向, "forward"(时间递增) 或 "any"(无时序要求)
        vertex_filter_v_types: 点类型过滤列表
        vertex_filter_min_balance: 点最小余额过滤
        edge_filter_e_types: 边类型过滤列表
        edge_filter_min_amount: 边最小金额过滤
        edge_filter_max_amount: 边最大金额过滤
        limit: 最多返回的环数量
        allow_duplicate_vertices: 是否允许环中出现重复点(除起点外)
        allow_duplicate_edges: 是否允许环中出现重复边
        **db_kwargs: 数据库连接参数

    Returns:
        Dict: 包含status, found, data(环列表), meta等信息
    """
    start_time = time.time()
    session_id = str(uuid.uuid4())

    try:
        # 1. 验证起始点存在
        start_vertex = _get_vertex(start_vid, username, **db_kwargs)
        if not start_vertex:
            return {"status": "error", "message": f"Start vertex {start_vid} not found"}

        # 2. 检查起始点是否满足过滤条件
        if not _vertex_matches_filter(
            start_vertex, vertex_filter_v_types, vertex_filter_min_balance
        ):
            return {
                "status": "success",
                "found": False,
                "message": "Start vertex does not match filters",
            }

        # 3. 执行双向BFS搜索
        cycles = _bidirectional_bfs(
            start_vid=start_vid,
            max_depth=max_depth,
            username=username,
            direction=direction,
            vertex_filter_v_types=vertex_filter_v_types,
            vertex_filter_min_balance=vertex_filter_min_balance,
            edge_filter_e_types=edge_filter_e_types,
            edge_filter_min_amount=edge_filter_min_amount,
            edge_filter_max_amount=edge_filter_max_amount,
            limit=limit,
            allow_duplicate_vertices=allow_duplicate_vertices,
            allow_duplicate_edges=allow_duplicate_edges,
            session_id=session_id,
            **db_kwargs,
        )

        # 4. 构造返回结果
        execution_time = int((time.time() - start_time) * 1000)

        if not cycles:
            return {
                "status": "success",
                "found": False,
                "meta": {"execution_time_ms": execution_time},
            }

        # 5. 获取环的详细信息
        cycle_data = []
        for cycle_path in cycles:
            vertices_data, edges_data = _get_cycle_details(cycle_path, username, **db_kwargs)
            cycle_data.append({"vertices": vertices_data, "edges": edges_data})

        return {
            "status": "success",
            "found": True,
            "count": len(cycle_data),
            "data": cycle_data,
            "meta": {"execution_time_ms": execution_time},
        }

    except Exception as e:
        return {"status": "error", "message": f"Cycle query failed: {e}"}
    finally:
        # 清理临时表
        _cleanup_temp_tables(session_id, **db_kwargs)


def _bidirectional_bfs(
    start_vid: int,
    max_depth: int,
    username: str,
    direction: str,
    vertex_filter_v_types: Optional[List[str]],
    vertex_filter_min_balance: Optional[int],
    edge_filter_e_types: Optional[List[str]],
    edge_filter_min_amount: Optional[int],
    edge_filter_max_amount: Optional[int],
    limit: int,
    allow_duplicate_vertices: bool,
    allow_duplicate_edges: bool,
    session_id: str,
    **db_kwargs: Any,
) -> List[List[Tuple[int, int, int]]]:
    """双向BFS核心算法。

    Returns:
        List[List[Tuple]]: 环路列表,每个环路是(src_vid, dst_vid, eid)的列表
    """
    # 创建正向和反向工作表
    fwd_table = f"fwd_{session_id.replace('-', '_')}"
    bwd_table = f"bwd_{session_id.replace('-', '_')}"

    _create_temp_table(fwd_table, **db_kwargs)
    _create_temp_table(bwd_table, **db_kwargs)

    # 初始化起点(occur_time设为0表示起点)
    _init_search(fwd_table, start_vid, **db_kwargs)
    _init_search(bwd_table, start_vid, **db_kwargs)

    cycles = []
    seen_cycles = set()  # 用于环去重
    current_depth = 1

    while current_depth <= max_depth // 2 and len(cycles) < limit:
        # 正向扩展
        fwd_count = _expand_forward(
            fwd_table,
            username,
            direction,
            edge_filter_e_types,
            edge_filter_min_amount,
            edge_filter_max_amount,
            vertex_filter_v_types,
            vertex_filter_min_balance,
            **db_kwargs,
        )

        if fwd_count == 0:
            break

        # 检查碰撞
        new_cycles = _detect_cycles(
            fwd_table,
            bwd_table,
            start_vid,
            username,
            allow_duplicate_vertices,
            allow_duplicate_edges,
            limit - len(cycles),
            seen_cycles,
            **db_kwargs,
        )
        cycles.extend(new_cycles)

        if len(cycles) >= limit:
            break

        # 反向扩展
        bwd_count = _expand_backward(
            bwd_table,
            username,
            direction,
            edge_filter_e_types,
            edge_filter_min_amount,
            edge_filter_max_amount,
            vertex_filter_v_types,
            vertex_filter_min_balance,
            **db_kwargs,
        )

        if bwd_count == 0:
            break

        # 再次检查碰撞
        new_cycles = _detect_cycles(
            fwd_table,
            bwd_table,
            start_vid,
            username,
            allow_duplicate_vertices,
            allow_duplicate_edges,
            limit - len(cycles),
            seen_cycles,
            **db_kwargs,
        )
        cycles.extend(new_cycles)

        current_depth += 1

    return cycles


def _create_temp_table(table_name: str, **db_kwargs: Any) -> None:
    """创建UNLOGGED临时表用于BFS扩展。"""
    sql = f"""
    CREATE UNLOGGED TABLE {table_name} (
        vid BIGINT NOT NULL,
        parent_vid BIGINT,
        occur_time BIGINT NOT NULL,
        eid BIGINT,
        depth INT NOT NULL,
        path_vids BIGINT[],
        path_eids BIGINT[]
    ) WITH (ORIENTATION = ROW);
    """
    execute_ddl(sql, **db_kwargs)

    # 创建索引加速JOIN
    execute_ddl(f"CREATE INDEX idx_{table_name}_vid ON {table_name}(vid);", **db_kwargs)


def _init_search(table_name: str, start_vid: int, **db_kwargs: Any) -> None:
    """初始化搜索表,插入起点。"""
    sql = f"""
    INSERT INTO {table_name} (vid, parent_vid, occur_time, eid, depth, path_vids, path_eids)
    VALUES (%s, NULL, 0, NULL, 0, ARRAY[%s]::BIGINT[], ARRAY[]::BIGINT[]);
    """
    execute_dml(sql, (start_vid, start_vid), **db_kwargs)


def _expand_forward(
    table_name: str,
    username: str,
    direction: str,
    edge_filter_e_types: Optional[List[str]],
    edge_filter_min_amount: Optional[int],
    edge_filter_max_amount: Optional[int],
    vertex_filter_v_types: Optional[List[str]],
    vertex_filter_min_balance: Optional[int],
    **db_kwargs: Any,
) -> int:
    """正向扩展一层。"""
    vertex_table_name, edge_table_name = get_user_table_name(username)
    conditions = []

    # 时序条件
    if direction == "forward":
        conditions.append("e.occur_time > t.occur_time")

    # 边过滤条件
    if edge_filter_e_types:
        e_types_str = "'" + "','".join(edge_filter_e_types) + "'"
        conditions.append(f"e.e_type IN ({e_types_str})")

    if edge_filter_min_amount is not None:
        conditions.append(f"e.amount >= {edge_filter_min_amount}")

    if edge_filter_max_amount is not None:
        conditions.append(f"e.amount <= {edge_filter_max_amount}")

    # 点过滤条件
    vertex_join = ""
    if vertex_filter_v_types or vertex_filter_min_balance is not None:
        vertex_join = f"JOIN {vertex_table_name} v ON v.vid = e.dst_vid"
        if vertex_filter_v_types:
            v_types_str = "'" + "','".join(vertex_filter_v_types) + "'"
            conditions.append(f"v.v_type IN ({v_types_str})")
        if vertex_filter_min_balance is not None:
            conditions.append(f"v.balance >= {vertex_filter_min_balance}")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # 获取当前最大深度
    max_depth_result = fetch_one(f"SELECT MAX(depth) FROM {table_name}", **db_kwargs)
    assert max_depth_result is not None
    current_max_depth = max_depth_result[0] if max_depth_result[0] is not None else 0

    sql = f"""
    INSERT INTO {table_name} (vid, parent_vid, occur_time, eid, depth, path_vids, path_eids)
    SELECT 
        e.dst_vid,
        t.vid,
        e.occur_time,
        e.eid,
        t.depth + 1,
        t.path_vids || e.dst_vid,
        t.path_eids || e.eid
    FROM {table_name} t
    JOIN {edge_table_name} e ON e.src_vid = t.vid
    {vertex_join}
    WHERE t.depth = {current_max_depth}
      AND {where_clause}
      AND NOT (e.dst_vid = ANY(t.path_vids));
    """

    return execute_dml(sql, **db_kwargs)


def _expand_backward(
    table_name: str,
    username: str,
    direction: str,
    edge_filter_e_types: Optional[List[str]],
    edge_filter_min_amount: Optional[int],
    edge_filter_max_amount: Optional[int],
    vertex_filter_v_types: Optional[List[str]],
    vertex_filter_min_balance: Optional[int],
    **db_kwargs: Any,
) -> int:
    """反向扩展一层。"""
    vertex_table_name, edge_table_name = get_user_table_name(username)
    conditions = []

    # 时序条件(反向搜索时间更早)
    if direction == "forward":
        conditions.append("e.occur_time < t.occur_time OR t.occur_time = 0")

    # 边过滤条件
    if edge_filter_e_types:
        e_types_str = "'" + "','".join(edge_filter_e_types) + "'"
        conditions.append(f"e.e_type IN ({e_types_str})")

    if edge_filter_min_amount is not None:
        conditions.append(f"e.amount >= {edge_filter_min_amount}")

    if edge_filter_max_amount is not None:
        conditions.append(f"e.amount <= {edge_filter_max_amount}")

    # 点过滤条件
    vertex_join = ""
    if vertex_filter_v_types or vertex_filter_min_balance is not None:
        vertex_join = f"JOIN {vertex_table_name} v ON v.vid = e.src_vid"
        if vertex_filter_v_types:
            v_types_str = "'" + "','".join(vertex_filter_v_types) + "'"
            conditions.append(f"v.v_type IN ({v_types_str})")
        if vertex_filter_min_balance is not None:
            conditions.append(f"v.balance >= {vertex_filter_min_balance}")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # 获取当前最大深度
    max_depth_result = fetch_one(f"SELECT MAX(depth) FROM {table_name}", **db_kwargs)
    assert max_depth_result is not None
    current_max_depth = max_depth_result[0] if max_depth_result[0] is not None else 0

    sql = f"""
    INSERT INTO {table_name} (vid, parent_vid, occur_time, eid, depth, path_vids, path_eids)
    SELECT 
        e.src_vid,
        t.vid,
        e.occur_time,
        e.eid,
        t.depth + 1,
        t.path_vids || e.src_vid,
        t.path_eids || e.eid
    FROM {table_name} t
    JOIN {edge_table_name} e ON e.dst_vid = t.vid
    {vertex_join}
    WHERE t.depth = {current_max_depth}
      AND {where_clause}
      AND NOT (e.src_vid = ANY(t.path_vids));
    """

    return execute_dml(sql, **db_kwargs)


def _detect_cycles(
    fwd_table: str,
    bwd_table: str,
    start_vid: int,
    username: str,
    allow_duplicate_vertices: bool,
    allow_duplicate_edges: bool,
    remaining_limit: int,
    seen_cycles: Set[Tuple[int, ...]],
    **db_kwargs: Any,
) -> List[List[Tuple[int, int, int]]]:
    """检测两个方向的碰撞,找出环路。"""
    # 找到碰撞点
    sql = f"""
    SELECT 
        f.vid as meet_vid,
        f.path_vids as fwd_vids,
        f.path_eids as fwd_eids,
        b.path_vids as bwd_vids,
        b.path_eids as bwd_eids
    FROM {fwd_table} f
    JOIN {bwd_table} b ON f.vid = b.vid
    WHERE f.vid != {start_vid}
    LIMIT {remaining_limit * 5};
    """

    collisions = fetch_all(sql, **db_kwargs)

    cycles = []
    for collision in collisions:
        meet_vid, fwd_vids, fwd_eids, bwd_vids, bwd_eids = collision

        # 构造完整环路
        # 正向路径: start_vid -> ... -> meet_vid
        # 反向路径: start_vid <- ... <- meet_vid (需要反转)

        # 获取正向路径的边信息
        fwd_path = []
        for i in range(len(fwd_eids)):
            src = fwd_vids[i] if i < len(fwd_vids) else meet_vid
            dst = fwd_vids[i + 1] if i + 1 < len(fwd_vids) else meet_vid
            eid = fwd_eids[i]
            fwd_path.append((src, dst, eid))

        # 获取反向路径的边信息(需要反转方向)
        bwd_path = []
        for i in range(len(bwd_eids) - 1, -1, -1):
            # 反向路径存储的是从meet_vid到start_vid,需要反转
            dst = bwd_vids[i] if i < len(bwd_vids) else start_vid
            src = bwd_vids[i + 1] if i + 1 < len(bwd_vids) else meet_vid
            eid = bwd_eids[i]
            bwd_path.append((src, dst, eid))

        # 合并路径
        full_cycle = fwd_path + bwd_path

        # 验证环路
        if _validate_cycle(
            full_cycle, start_vid, allow_duplicate_vertices, allow_duplicate_edges
        ):
            # 路径去重：生成标准化签名
            signature = _get_cycle_signature(full_cycle)
            if signature not in seen_cycles:
                seen_cycles.add(signature)
                cycles.append(full_cycle)

                if len(cycles) >= remaining_limit:
                    break

    return cycles


def _validate_cycle(
    cycle: List[Tuple[int, int, int]],
    start_vid: int,
    allow_duplicate_vertices: bool,
    allow_duplicate_edges: bool,
) -> bool:
    """验证环路是否有效。"""
    if not cycle:
        return False

    # 检查是否形成环(最后一条边的dst应该等于起点)
    if cycle[-1][1] != start_vid:
        return False

    # 检查重复点
    if not allow_duplicate_vertices:
        vertices = [start_vid]
        for src, dst, _ in cycle:
            if dst != start_vid and dst in vertices:
                return False
            vertices.append(dst)

    # 检查重复边
    if not allow_duplicate_edges:
        edges = set()
        for _, _, eid in cycle:
            if eid in edges:
                return False
            edges.add(eid)

    return True


def _get_cycle_details(
    cycle_path: List[Tuple[int, int, int]], username: str, **db_kwargs: Any
) -> Tuple[List[Dict], List[Dict]]:
    """获取环路中所有点和边的详细信息。"""
    vertex_table_name, edge_table_name = get_user_table_name(username)
    # 收集所有vid和eid
    vids = set([cycle_path[0][0]])  # 起点
    eids = []
    for src, dst, eid in cycle_path:
        vids.add(dst)
        eids.append(eid)

    # 查询点信息
    vids_list = list(vids)
    vids_str = ",".join(map(str, vids_list))
    vertices_sql = f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name} WHERE vid IN ({vids_str})"
    vertices_data = fetch_all(vertices_sql, **db_kwargs)
    vertices = [Vertex.from_tuple(v).to_dict() for v in vertices_data]

    # 查询边信息
    eids_str = ",".join(map(str, eids))
    edges_sql = f"SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM {edge_table_name} WHERE eid IN ({eids_str})"
    edges_data = fetch_all(edges_sql, **db_kwargs)
    edges = [Edge.from_tuple(e).to_dict() for e in edges_data]

    return vertices, edges


def _get_vertex(vid: int, username: str, **db_kwargs: Any) -> Optional[Vertex]:
    """获取点信息。"""
    vertex_table_name, _ = get_user_table_name(username)
    result = fetch_one(
        f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name} WHERE vid = %s",
        (vid,),
        **db_kwargs,
    )
    return Vertex.from_tuple(result) if result else None


def _vertex_matches_filter(
    vertex: Vertex, v_types: Optional[List[str]], min_balance: Optional[int]
) -> bool:
    """检查点是否满足过滤条件。"""
    if v_types and vertex.v_type not in v_types:
        return False
    if min_balance is not None and vertex.balance < min_balance:
        return False
    return True


def _cleanup_temp_tables(session_id: str, **db_kwargs: Any) -> None:
    """清理临时表。"""
    safe_session = session_id.replace("-", "_")
    tables = [f"fwd_{safe_session}", f"bwd_{safe_session}"]

    for table in tables:
        try:
            execute_ddl(f"DROP TABLE IF EXISTS {table};", **db_kwargs)
        except Exception:
            pass  # 忽略清理错误


def _get_cycle_signature(cycle: List[Tuple[int, int, int]]) -> Tuple[int, ...]:
    """生成环路的唯一签名，用于去重。
    
    使用标准化的边ID序列作为环的唯一标识：
    1. 找到最小的边ID作为起点
    2. 从该边开始，按照环的顺序排列所有边ID
    3. 考虑正向和反向（防止 [1,2,3] 和 [3,2,1] 被认为是不同的环）
    
    Args:
        cycle: 环路，格式为 [(src_vid, dst_vid, eid), ...]
    
    Returns:
        环路的归一化签名
    """
    if not cycle:
        return tuple()
    
    edge_ids = [eid for _, _, eid in cycle]
    
    # 找到最小边ID的位置
    min_eid = min(edge_ids)
    min_idx = edge_ids.index(min_eid)
    
    # 从最小边ID开始，构造标准化序列
    normalized = edge_ids[min_idx:] + edge_ids[:min_idx]
    
    # 考虑反向：也从最小边开始，但是反向遍历
    reversed_cycle = list(reversed(edge_ids))
    min_idx_rev = reversed_cycle.index(min_eid)
    normalized_rev = reversed_cycle[min_idx_rev:] + reversed_cycle[:min_idx_rev]
    
    # 返回字典序较小的那个作为标准签名
    return tuple(normalized) if normalized <= normalized_rev else tuple(normalized_rev)
