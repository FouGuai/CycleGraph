#!/usr/bin/env python3
"""CLI 功能测试脚本。

测试所有 CLI 命令的功能是否正常。
"""
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from interface.cli import execute_command


def run_command(args_list: list) -> dict:
    """运行 CLI 命令并返回结果字典。

    Args:
        args_list: 命令参数列表,例如 ['register', '--username', 'testuser', '--password', 'test123']

    Returns:
        dict: 执行结果字典
    """
    cmd_str = " ".join(args_list)
    print(f"\n>>> cgql {cmd_str}")

    result = execute_command(args_list)

    print(f"<<< {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result


def test_auth():
    """测试用户认证功能。"""
    print("\n" + "=" * 50)
    print("测试 1: 用户认证")
    print("=" * 50)

    # 1. 注册用户
    print("\n[1.1] 注册新用户")
    result = run_command(
        ["register", "--username", "testuser", "--password", "test123"]
    )
    assert result.get("status") == "success", "注册失败"

    # 2. 重复注册（应该失败）
    print("\n[1.2] 重复注册（应失败）")
    result = run_command(
        ["register", "--username", "testuser", "--password", "test123"]
    )
    assert result.get("status") == "error", "重复注册应该失败"

    # 3. 登录
    print("\n[1.3] 登录")
    result = run_command(["login", "--username", "testuser", "--password", "test123"])
    assert result.get("status") == "success", "登录失败"

    # 4. 错误密码登录（应该失败）
    print("\n[1.4] 错误密码登录（应失败）")
    result = run_command(["login", "--username", "testuser", "--password", "wrong"])
    assert result.get("status") == "error", "错误密码登录应该失败"

    # 5. whoami
    print("\n[1.5] 查看当前用户")
    result = run_command(["whoami"])
    assert result.get("current_user") == "testuser", "当前用户名不匹配"

    print("\n✓ 用户认证测试通过")


def test_connect():
    """测试连接管理。"""
    print("\n" + "=" * 50)
    print("测试 2: 连接管理")
    print("=" * 50)

    print("\n[2.1] 连接服务器")
    result = run_command(["connect", "http://127.0.0.1:8000"])
    assert result.get("status") == "success", "连接失败"

    print("\n✓ 连接管理测试通过")


def test_vertex_operations():
    """测试点操作。"""
    print("\n" + "=" * 50)
    print("测试 3: 点操作")
    print("=" * 50)

    # 1. 插入点（自动生成 ID）
    print("\n[3.1] 插入点（自动生成 ID）")
    result = run_command(["insert", "vertex", "--v-type", "1", "--balance", "10000"])
    assert result.get("status") == "success", "插入点失败"
    auto_vid = result["data"]["vid"]
    print(f"生成的 vid: {auto_vid}")

    # 2. 插入点（指定 ID）
    print("\n[3.2] 插入点（指定 ID）")
    test_vid = 999999
    result = run_command(
        [
            "insert",
            "vertex",
            "--v-type",
            "vvvtype",
            "--vid",
            str(test_vid),
            "--balance",
            "50000",
        ]
    )
    assert result.get("status") == "success", "插入指定 ID 的点失败"

    # 3. 查询所有点
    print("\n[3.3] 查询所有点")
    result = run_command(["query", "vertex"])
    assert result.get("status") == "success", "查询点失败"
    assert result.get("count", 0) >= 2, "点数量不足"

    # 4. 按 vid 查询
    print("\n[3.4] 按 vid 查询")
    result = run_command(["query", "vertex", "--vid", str(test_vid)])
    assert result.get("found") == True, "按 vid 查询失败"

    # 5. 按 v-type 查询
    print("\n[3.5] 按 v-type 查询")
    result = run_command(["query", "vertex", "--v-type", "1"])
    assert result.get("status") == "success", "按类型查询失败"

    # 6. 按余额范围查询
    print("\n[3.6] 按余额范围查询")
    result = run_command(
        ["query", "vertex", "--min-balance", "40000", "--max-balance", "60000"]
    )
    assert result.get("status") == "success", "按余额查询失败"

    print("\n✓ 点操作测试通过")
    return auto_vid, test_vid


def test_edge_operations(vid1: int, vid2: int):
    """测试边操作。"""
    print("\n" + "=" * 50)
    print("测试 4: 边操作")
    print("=" * 50)

    # 1. 插入边
    print("\n[4.1] 插入边")
    test_eid = 888888
    result = run_command(
        [
            "insert",
            "edge",
            "--eid",
            str(test_eid),
            "--src-vid",
            str(vid1),
            "--dst-vid",
            str(vid2),
            "--amount",
            "5000",
            "--e-type",
            "0",
        ]
    )
    assert result.get("status") == "success", "插入边失败"

    # 2. 插入边（自动创建点）
    print("\n[4.2] 插入边（自动创建不存在的点）")
    new_eid = 888889
    new_src = 111111
    new_dst = 222222
    result = run_command(
        [
            "insert",
            "edge",
            "--eid",
            str(new_eid),
            "--src-vid",
            str(new_src),
            "--dst-vid",
            str(new_dst),
            "--amount",
            "3000",
            "--create-vertices",
        ]
    )
    assert result.get("status") == "success", "插入边（自动创建点）失败"

    # 3. 查询所有边
    print("\n[4.3] 查询所有边")
    result = run_command(["query", "edge"])
    assert result.get("status") == "success", "查询边失败"
    assert result.get("count", 0) >= 2, "边数量不足"

    # 4. 按 eid 查询
    print("\n[4.4] 按 eid 查询")
    result = run_command(["query", "edge", "--eid", str(test_eid)])
    assert result.get("found") == True, "按 eid 查询失败"

    # 5. 按 src-vid 查询
    print("\n[4.5] 按 src-vid 查询")
    result = run_command(["query", "edge", "--src-vid", str(vid1)])
    assert result.get("status") == "success", "按源点查询失败"

    # 6. 按金额范围查询
    print("\n[4.6] 按金额范围查询")
    result = run_command(
        ["query", "edge", "--min-amount", "4000", "--max-amount", "6000"]
    )
    assert result.get("status") == "success", "按金额查询失败"

    print("\n✓ 边操作测试通过")


def test_logout():
    """测试登出。"""
    print("\n" + "=" * 50)
    print("测试 5: 登出")
    print("=" * 50)

    print("\n[5.1] 登出")
    result = run_command(["logout"])
    assert result.get("status") == "success", "登出失败"

    print("\n[5.2] 登出后查询（应失败）")
    result = run_command(["query", "vertex"])
    assert result.get("status") == "error", "登出后仍能查询"

    print("\n[5.3] whoami（应显示未登录）")
    result = run_command(["whoami"])
    assert result.get("status") == "error", "登出后 whoami 应失败"

    print("\n✓ 登出测试通过")


def test_cycle_operations():
    """测试环路查询功能。"""
    print("\n" + "=" * 50)
    print("测试 6: 环路查询")
    print("=" * 50)

    # 准备测试数据：创建一个简单的环路
    # 环路结构: v1 -> v2 -> v3 -> v1
    print("\n[6.0] 准备测试数据：创建环路结构")

    # 创建点
    v1 = 100001
    v2 = 100002
    v3 = 100003

    run_command(
        [
            "insert",
            "vertex",
            "--vid",
            str(v1),
            "--v-type",
            "cycle_test",
            "--balance",
            "50000",
        ]
    )
    run_command(
        [
            "insert",
            "vertex",
            "--vid",
            str(v2),
            "--v-type",
            "cycle_test",
            "--balance",
            "60000",
        ]
    )
    run_command(
        [
            "insert",
            "vertex",
            "--vid",
            str(v3),
            "--v-type",
            "cycle_test",
            "--balance",
            "70000",
        ]
    )

    # 创建边形成环路（时间递增）
    import time

    base_time = int(time.time())

    e1 = 200001
    e2 = 200002
    e3 = 200003

    run_command(
        [
            "insert",
            "edge",
            "--eid",
            str(e1),
            "--src-vid",
            str(v1),
            "--dst-vid",
            str(v2),
            "--amount",
            "10000",
            "--occur-time",
            str(base_time),
            "--e-type",
            "transfer",
        ]
    )

    run_command(
        [
            "insert",
            "edge",
            "--eid",
            str(e2),
            "--src-vid",
            str(v2),
            "--dst-vid",
            str(v3),
            "--amount",
            "12000",
            "--occur-time",
            str(base_time + 10),
            "--e-type",
            "transfer",
        ]
    )

    run_command(
        [
            "insert",
            "edge",
            "--eid",
            str(e3),
            "--src-vid",
            str(v3),
            "--dst-vid",
            str(v1),
            "--amount",
            "15000",
            "--occur-time",
            str(base_time + 20),
            "--e-type",
            "transfer",
        ]
    )

    print("✓ 测试数据准备完成")

    # 测试 1: 基本环路查询（forward 方向）
    print("\n[6.1] 基本环路查询（forward 方向）")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
        ]
    )
    assert result.get("status") == "success", "环路查询失败"
    assert result.get("found") == True, "应该找到环路"
    assert result.get("count", 0) >= 1, "应该至少找到一个环路"
    print(f"找到 {result.get('count', 0)} 个环路")

    # 测试 2: any 方向查询
    print("\n[6.2] any 方向查询（无时序要求）")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "any",
        ]
    )
    assert result.get("status") == "success", "any 方向查询失败"
    print(f"找到 {result.get('count', 0)} 个环路")

    # 测试 3: 深度限制测试
    print("\n[6.3] 深度限制测试（深度不足应找不到环）")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "2",
            "--direction",
            "forward",
        ]
    )
    assert result.get("status") == "success", "查询应该成功"
    # 注意：深度为2可能找不到长度为3的环
    print(f"深度限制为2时，找到 {result.get('count', 0)} 个环路")

    # 测试 4: 点类型过滤
    print("\n[6.4] 点类型过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--vertex-filter-v-type",
            "cycle_test",
        ]
    )
    assert result.get("status") == "success", "点类型过滤查询失败"
    if result.get("found"):
        print(f"类型过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 5: 点余额过滤
    print("\n[6.5] 点余额过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--vertex-filter-min-balance",
            "40000",
        ]
    )
    assert result.get("status") == "success", "点余额过滤查询失败"
    if result.get("found"):
        print(f"余额过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 6: 边类型过滤
    print("\n[6.6] 边类型过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--edge-filter-e-type",
            "transfer",
        ]
    )
    assert result.get("status") == "success", "边类型过滤查询失败"
    if result.get("found"):
        print(f"边类型过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 7: 边金额过滤（最小金额）
    print("\n[6.7] 边最小金额过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--edge-filter-min-amount",
            "9000",
        ]
    )
    assert result.get("status") == "success", "边最小金额过滤查询失败"
    if result.get("found"):
        print(f"最小金额过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 8: 边金额过滤（最大金额）
    print("\n[6.8] 边最大金额过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--edge-filter-max-amount",
            "20000",
        ]
    )
    assert result.get("status") == "success", "边最大金额过滤查询失败"
    if result.get("found"):
        print(f"最大金额过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 9: 金额范围过滤
    print("\n[6.9] 边金额范围过滤测试")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--edge-filter-min-amount",
            "9000",
            "--edge-filter-max-amount",
            "16000",
        ]
    )
    assert result.get("status") == "success", "边金额范围过滤查询失败"
    if result.get("found"):
        print(f"金额范围过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 10: 组合过滤
    print("\n[6.10] 组合过滤测试（点类型 + 点余额 + 边金额）")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--vertex-filter-v-type",
            "cycle_test",
            "--vertex-filter-min-balance",
            "45000",
            "--edge-filter-min-amount",
            "9000",
        ]
    )
    assert result.get("status") == "success", "组合过滤查询失败"
    print(f"组合过滤后找到 {result.get('count', 0)} 个环路")

    # 测试 11: 起始点不存在
    print("\n[6.11] 起始点不存在的情况")
    result = run_command(
        ["query", "cycle", "--start-vid", "999999999", "--max-depth", "10"]
    )
    assert result.get("status") == "error", "起始点不存在应该返回错误"
    print("✓ 正确处理起始点不存在的情况")

    # 测试 12: 过滤条件过严导致找不到环
    print("\n[6.12] 过滤条件过严（应找不到环）")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
            "--edge-filter-min-amount",
            "100000",  # 金额过大
        ]
    )
    assert result.get("status") == "success", "查询应该成功"
    assert result.get("found") == False, "过滤条件过严应找不到环"
    print("✓ 正确处理过滤条件过严的情况")

    # 测试 13: 验证返回数据结构
    print("\n[6.13] 验证返回数据结构")
    result = run_command(
        [
            "query",
            "cycle",
            "--start-vid",
            str(v1),
            "--max-depth",
            "10",
            "--direction",
            "forward",
        ]
    )
    if result.get("found"):
        assert "data" in result, "应包含 data 字段"
        assert isinstance(result["data"], list), "data 应该是列表"

        first_cycle = result["data"][0]
        assert "vertices" in first_cycle, "环路应包含 vertices"
        assert "edges" in first_cycle, "环路应包含 edges"
        assert isinstance(first_cycle["vertices"], list), "vertices 应该是列表"
        assert isinstance(first_cycle["edges"], list), "edges 应该是列表"

        # 验证点的数据结构
        if first_cycle["vertices"]:
            vertex = first_cycle["vertices"][0]
            assert "vid" in vertex, "点应包含 vid"
            assert "v_type" in vertex, "点应包含 v_type"
            assert "balance" in vertex, "点应包含 balance"
            print(f"示例点数据: {vertex}")

        # 验证边的数据结构
        if first_cycle["edges"]:
            edge = first_cycle["edges"][0]
            assert "eid" in edge, "边应包含 eid"
            assert "src_vid" in edge, "边应包含 src_vid"
            assert "dst_vid" in edge, "边应包含 dst_vid"
            assert "amount" in edge, "边应包含 amount"
            assert "occur_time" in edge, "边应包含 occur_time"
            print(f"示例边数据: {edge}")

        print("✓ 数据结构验证通过")

    # 测试 14: 元数据验证
    print("\n[6.14] 元数据验证")
    result = run_command(
        ["query", "cycle", "--start-vid", str(v1), "--max-depth", "10"]
    )
    assert "meta" in result, "应包含 meta 字段"
    assert "execution_time_ms" in result["meta"], "meta 应包含执行时间"
    print(f"执行时间: {result['meta']['execution_time_ms']} ms")

    print("\n✓ 环路查询测试通过")


def main():
    """运行所有测试。"""
    print("\n" + "=" * 70)
    print(" CLI 功能测试套件 ".center(70, "="))
    print("=" * 70)

    try:
        # 测试 1: 用户认证
        test_auth()

        # 测试 2: 连接管理
        test_connect()

        # 测试 3: 点操作
        vid1, vid2 = test_vertex_operations()

        # 测试 4: 边操作
        test_edge_operations(vid1, vid2)
        
          # 测试 6: 环路查询
        test_cycle_operations()

        # 测试 5: 登出
        test_logout()
        
      
        
        print("\n" + "=" * 70)
        print(" ✓ 所有测试通过 ".center(70, "="))
        print("=" * 70)

        return 0

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
