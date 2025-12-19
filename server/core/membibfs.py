"""环路查找服务 - 基于内存的双向BFS高效环检测算法。

一次性从数据库读取所有数据到内存,然后在内存中进行双向BFS搜索。
相比于bibfs.py,避免了频繁的数据库访问,大幅提升性能。
"""

import time
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import deque, defaultdict
from server.opengauss.graph_dao import (
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
    """查询环路 - 使用纯内存双向BFS算法。

    Args:
        start_vid: 起始点ID
        max_depth: 最大搜索深度(环路长度)
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
    print(username)
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

        # 3. 一次性加载所有点和边数据到内存
        vertices_map, edges_out, edges_in = _load_graph_data(
            vertex_filter_v_types,
            vertex_filter_min_balance,
            edge_filter_e_types,
            edge_filter_min_amount,
            edge_filter_max_amount,
            username,
            **db_kwargs,
        )

        # 4. 执行内存双向BFS搜索
        cycles, seen_cycles = _memory_bidirectional_bfs(
            start_vid=start_vid,
            max_depth=max_depth,
            direction=direction,
            vertices_map=vertices_map,
            edges_out=edges_out,
            edges_in=edges_in,
            limit=limit,
            allow_duplicate_vertices=allow_duplicate_vertices,
            allow_duplicate_edges=allow_duplicate_edges,
        )

        # 5. 构造返回结果
        execution_time = int((time.time() - start_time) * 1000)

        if not cycles:
            return {
                "status": "success",
                "found": False,
                "meta": {"execution_time_ms": execution_time},
            }

        # 6. 获取环的详细信息
        cycle_data = []
        for cycle_path in cycles:
            vertices_data, edges_data = _get_cycle_details_from_memory(
                cycle_path, vertices_map
            )
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


def _load_graph_data(
    vertex_filter_v_types: Optional[List[str]],
    vertex_filter_min_balance: Optional[int],
    edge_filter_e_types: Optional[List[str]],
    edge_filter_min_amount: Optional[int],
    edge_filter_max_amount: Optional[int],
    username: str,
    **db_kwargs: Any,
) -> Tuple[Dict[int, Vertex], Dict[int, List[Edge]], Dict[int, List[Edge]]]:
    """一次性加载所有符合条件的点和边数据到内存。

    Returns:
        vertices_map: vid -> Vertex 映射
        edges_out: src_vid -> [Edge] 出边邻接表
        edges_in: dst_vid -> [Edge] 入边邻接表
    """
    # 1. 加载点数据
    vertex_conditions = []
    vertex_params = []
    vertex_table_name, edge_table_name = get_user_table_name(username)
    if vertex_filter_v_types:
        placeholders = ",".join(["%s"] * len(vertex_filter_v_types))
        vertex_conditions.append(f"v_type IN ({placeholders})")
        vertex_params.extend(vertex_filter_v_types)

    if vertex_filter_min_balance is not None:
        vertex_conditions.append("balance >= %s")
        vertex_params.append(vertex_filter_min_balance)

    vertex_sql = f"SELECT vid, v_type, create_time, balance FROM {vertex_table_name}"
    if vertex_conditions:
        vertex_sql += " WHERE " + " AND ".join(vertex_conditions)

    vertex_rows = fetch_all(
        vertex_sql, tuple(vertex_params) if vertex_params else None, **db_kwargs
    )
    vertices_map = {row[0]: Vertex.from_tuple(row) for row in vertex_rows}

    # 2. 加载边数据
    edge_conditions = []
    edge_params = []

    if edge_filter_e_types:
        placeholders = ",".join(["%s"] * len(edge_filter_e_types))
        edge_conditions.append(f"e_type IN ({placeholders})")
        edge_params.extend(edge_filter_e_types)

    if edge_filter_min_amount is not None:
        edge_conditions.append("amount >= %s")
        edge_params.append(edge_filter_min_amount)

    if edge_filter_max_amount is not None:
        edge_conditions.append("amount <= %s")
        edge_params.append(edge_filter_max_amount)

    edge_sql = f"SELECT eid, src_vid, dst_vid, amount, occur_time, e_type FROM {edge_table_name}"
    if edge_conditions:
        edge_sql += " WHERE " + " AND ".join(edge_conditions)

    edge_rows = fetch_all(
        edge_sql, tuple(edge_params) if edge_params else None, **db_kwargs
    )

    # 3. 构建邻接表
    edges_out = defaultdict(list)  # src_vid -> [Edge]
    edges_in = defaultdict(list)  # dst_vid -> [Edge]

    for row in edge_rows:
        edge = Edge.from_tuple(row)
        # 只保留源点和目标点都存在的边
        if edge.src_vid in vertices_map and edge.dst_vid in vertices_map:
            edges_out[edge.src_vid].append(edge)
            edges_in[edge.dst_vid].append(edge)

    return vertices_map, dict(edges_out), dict(edges_in)


def _memory_bidirectional_bfs(
    start_vid: int,
    max_depth: int,
    direction: str,
    vertices_map: Dict[int, Vertex],
    edges_out: Dict[int, List[Edge]],
    edges_in: Dict[int, List[Edge]],
    limit: int,
    allow_duplicate_vertices: bool,
    allow_duplicate_edges: bool,
) -> Tuple[List[List[Tuple[int, int, int, Edge]]], Set[Tuple]]:
    """纯内存双向BFS核心算法。

    Returns:
        Tuple: (环路列表, 已见环路签名集合)
    """
    # 检查起点是否在图中
    if start_vid not in vertices_map:
        return [], set()

    # 正向搜索状态: vid -> (parent_vid, edge, depth, path_vids, path_edges_full, occur_time)
    # path_edges_full 存储完整的 Edge 对象
    fwd_state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ] = {}
    # 反向搜索状态: vid -> (parent_vid, edge, depth, path_vids, path_edges_full, occur_time)
    bwd_state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ] = {}

    # 初始化起点
    fwd_state[start_vid] = (None, None, 0, [start_vid], [], 0)
    bwd_state[start_vid] = (None, None, 0, [start_vid], [], 0)

    # 当前层的节点
    fwd_frontier = {start_vid}
    bwd_frontier = {start_vid}

    cycles = []
    seen_cycles = set()  # 存储已见环路的签名
    current_depth = 1

    while current_depth <= max_depth // 2 and len(cycles) < limit:
        # 正向扩展
        new_fwd_frontier = _expand_forward_memory(
            fwd_frontier,
            fwd_state,
            edges_out,
            direction,
            current_depth,
        )

        if not new_fwd_frontier:
            break

        fwd_frontier = new_fwd_frontier

        # 检查碰撞
        new_cycles = _detect_cycles_memory(
            fwd_state,
            bwd_state,
            start_vid,
            edges_out,
            edges_in,
            allow_duplicate_vertices,
            allow_duplicate_edges,
            limit - len(cycles),
            seen_cycles,
        )
        cycles.extend(new_cycles)

        if len(cycles) >= limit:
            break

        # 反向扩展
        new_bwd_frontier = _expand_backward_memory(
            bwd_frontier,
            bwd_state,
            edges_in,
            direction,
            current_depth,
        )

        if not new_bwd_frontier:
            break

        bwd_frontier = new_bwd_frontier

        # 再次检查碰撞
        new_cycles = _detect_cycles_memory(
            fwd_state,
            bwd_state,
            start_vid,
            edges_out,
            edges_in,
            allow_duplicate_vertices,
            allow_duplicate_edges,
            limit - len(cycles),
            seen_cycles,
        )
        cycles.extend(new_cycles)

        current_depth += 1

    return cycles, seen_cycles


def _expand_forward_memory(
    frontier: Set[int],
    state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ],
    edges_out: Dict[int, List[Edge]],
    direction: str,
    target_depth: int,
) -> Set[int]:
    """内存正向扩展一层。"""
    new_frontier = set()

    for vid in frontier:
        parent_vid, parent_edge, depth, path_vids, path_edges, occur_time = state[vid]

        if depth != target_depth - 1:
            continue

        # 获取出边
        out_edges = edges_out.get(vid, [])

        for edge in out_edges:
            # 时序过滤
            if direction == "forward" and edge.occur_time <= occur_time:
                continue

            # 避免重复访问已在路径中的点
            if edge.dst_vid in path_vids:
                continue

            # 添加到新状态，保存完整Edge对象
            new_path_vids = path_vids + [edge.dst_vid]
            new_path_edges = path_edges + [edge]

            # 如果该点已经在这一层被访问过,跳过(保留第一次访问的路径)
            if edge.dst_vid in state and state[edge.dst_vid][2] == target_depth:
                continue

            state[edge.dst_vid] = (
                vid,
                edge,
                target_depth,
                new_path_vids,
                new_path_edges,
                edge.occur_time,
            )
            new_frontier.add(edge.dst_vid)

    return new_frontier


def _expand_backward_memory(
    frontier: Set[int],
    state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ],
    edges_in: Dict[int, List[Edge]],
    direction: str,
    target_depth: int,
) -> Set[int]:
    """内存反向扩展一层。"""
    new_frontier = set()

    for vid in frontier:
        parent_vid, parent_edge, depth, path_vids, path_edges, occur_time = state[vid]

        if depth != target_depth - 1:
            continue

        # 获取入边
        in_edges = edges_in.get(vid, [])

        for edge in in_edges:
            # 时序过滤(反向搜索时间更早)
            if (
                direction == "forward"
                and occur_time != 0
                and edge.occur_time >= occur_time
            ):
                continue

            # 避免重复访问已在路径中的点
            if edge.src_vid in path_vids:
                continue

            # 添加到新状态，保存完整Edge对象
            new_path_vids = path_vids + [edge.src_vid]
            new_path_edges = path_edges + [edge]

            # 如果该点已经在这一层被访问过,跳过
            if edge.src_vid in state and state[edge.src_vid][2] == target_depth:
                continue

            state[edge.src_vid] = (
                vid,
                edge,
                target_depth,
                new_path_vids,
                new_path_edges,
                edge.occur_time,
            )
            new_frontier.add(edge.src_vid)

    return new_frontier


def _detect_cycles_memory(
    fwd_state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ],
    bwd_state: Dict[
        int, Tuple[Optional[int], Optional[Edge], int, List[int], List[Edge], int]
    ],
    start_vid: int,
    edges_out: Dict[int, List[Edge]],
    edges_in: Dict[int, List[Edge]],
    allow_duplicate_vertices: bool,
    allow_duplicate_edges: bool,
    remaining_limit: int,
    seen_cycles: Set[Tuple],
) -> List[List[Tuple[int, int, int, Edge]]]:
    """检测两个方向的碰撞,找出环路。"""
    cycles = []

    # 找到碰撞点(同时在正向和反向状态中,且不是起点)
    collision_vids = (set(fwd_state.keys()) & set(bwd_state.keys())) - {start_vid}

    for meet_vid in collision_vids:
        if len(cycles) >= remaining_limit:
            break

        # 获取正向和反向路径
        _, _, _, fwd_path_vids, fwd_path_edges, _ = fwd_state[meet_vid]
        _, _, _, bwd_path_vids, bwd_path_edges, _ = bwd_state[meet_vid]

        # 构造完整环路
        # 正向路径: start_vid -> ... -> meet_vid
        fwd_path = []
        for i, edge in enumerate(fwd_path_edges):
            src = fwd_path_vids[i]
            dst = fwd_path_vids[i + 1]
            fwd_path.append((src, dst, edge.eid, edge))

        # 反向路径: meet_vid -> ... -> start_vid (需要反转)
        bwd_path = []
        for i in range(len(bwd_path_edges) - 1, -1, -1):
            edge = bwd_path_edges[i]
            src = bwd_path_vids[i + 1]
            dst = bwd_path_vids[i]
            bwd_path.append((src, dst, edge.eid, edge))

        # 合并路径
        full_cycle = fwd_path + bwd_path

        # 验证环路
        if _validate_cycle(
            full_cycle, start_vid, allow_duplicate_vertices, allow_duplicate_edges
        ):
            # 生成环路签名并检查是否已存在
            cycle_signature = _get_cycle_signature(full_cycle)
            if cycle_signature not in seen_cycles:
                seen_cycles.add(cycle_signature)
                cycles.append(full_cycle)

    return cycles


def _validate_cycle(
    cycle: List[Tuple[int, int, int, Edge]],
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
        for src, dst, _, _ in cycle:
            if dst != start_vid and dst in vertices:
                return False
            vertices.append(dst)

    # 检查重复边
    if not allow_duplicate_edges:
        edges = set()
        for _, _, eid, _ in cycle:
            if eid in edges:
                return False
            edges.add(eid)

    return True


def _get_cycle_details_from_memory(
    cycle_path: List[Tuple[int, int, int, Edge]],
    vertices_map: Dict[int, Vertex],
) -> Tuple[List[Dict], List[Dict]]:
    """从内存中获取环路的详细信息。"""
    # 收集所有vid
    vids = set([cycle_path[0][0]])  # 起点

    for src, dst, _, _ in cycle_path:
        vids.add(dst)

    # 从内存获取点信息
    vertices = []
    for vid in vids:
        if vid in vertices_map:
            vertices.append(vertices_map[vid].to_dict())

    # 从cycle_path中获取完整边信息
    edges = []
    for src, dst, eid, edge in cycle_path:
        edges.append(edge.to_dict())

    return vertices, edges


def _get_cycle_details(
    cycle_path: List[Tuple[int, int, int]], username: str, **db_kwargs: Any
) -> Tuple[List[Dict], List[Dict]]:
    """获取环路中所有点和边的详细信息(从数据库)。"""

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


def _get_cycle_signature(cycle: List[Tuple[int, int, int, Edge]]) -> Tuple:
    """生成环路的唯一签名，用于去重。

    同一个环路，无论从哪个点开始，正向还是反向遍历，都应该生成相同的签名。
    例如: 1->2->3->1, 2->3->1->2, 3->1->2->3 是同一个环
          1->2->3->1 和 1->3->2->1 也是同一个环（反向）

    Args:
        cycle: 环路，格式为 [(src_vid, dst_vid, eid, edge_obj), ...]

    Returns:
        环路的归一化签名
    """
    if not cycle:
        return tuple()

    # 提取边ID序列
    edge_ids = [eid for _, _, eid, _ in cycle]

    # 找到最小边ID的位置，作为归一化起点
    min_eid = min(edge_ids)
    min_idx = edge_ids.index(min_eid)

    # 从最小边ID开始的正向序列
    normalized_forward = tuple(edge_ids[min_idx:] + edge_ids[:min_idx])

    # 从最小边ID开始的反向序列
    # 反向时，从最小边ID位置开始，逆序遍历
    reversed_sequence = edge_ids[: min_idx + 1][::-1] + edge_ids[min_idx + 1 :][::-1]
    if reversed_sequence:
        # 调整使得最小边ID在开头
        rev_min_idx = reversed_sequence.index(min_eid)
        normalized_reverse = tuple(
            reversed_sequence[rev_min_idx:] + reversed_sequence[:rev_min_idx]
        )
    else:
        normalized_reverse = tuple()

    # 返回字典序较小的那个作为唯一签名
    return (
        min(normalized_forward, normalized_reverse)
        if normalized_reverse
        else normalized_forward
    )
