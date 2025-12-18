#!/usr/bin/env python3
"""CLI 功能测试脚本。

测试所有 CLI 命令的功能是否正常。
"""
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface.cli import execute_command


def run_command(args_list: list) -> dict:
    """运行 CLI 命令并返回结果字典。
    
    Args:
        args_list: 命令参数列表,例如 ['register', '--username', 'testuser', '--password', 'test123']
        
    Returns:
        dict: 执行结果字典
    """
    cmd_str = ' '.join(args_list)
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
    result = run_command(['register', '--username', 'testuser', '--password', 'test123'])
    assert result.get('status') == 'success', "注册失败"
    
    # 2. 重复注册（应该失败）
    print("\n[1.2] 重复注册（应失败）")
    result = run_command(['register', '--username', 'testuser', '--password', 'test123'])
    assert result.get('status') == 'error', "重复注册应该失败"
    
    # 3. 登录
    print("\n[1.3] 登录")
    result = run_command(['login', '--username', 'testuser', '--password', 'test123'])
    assert result.get('status') == 'success', "登录失败"
    
    # 4. 错误密码登录（应该失败）
    print("\n[1.4] 错误密码登录（应失败）")
    result = run_command(['login', '--username', 'testuser', '--password', 'wrong'])
    assert result.get('status') == 'error', "错误密码登录应该失败"
    
    # 5. whoami
    print("\n[1.5] 查看当前用户")
    result = run_command(['whoami'])
    assert result.get('current_user') == 'testuser', "当前用户名不匹配"
    
    print("\n✓ 用户认证测试通过")


def test_connect():
    """测试连接管理。"""
    print("\n" + "=" * 50)
    print("测试 2: 连接管理")
    print("=" * 50)
    
    print("\n[2.1] 连接服务器")
    result = run_command(['connect', 'http://127.0.0.1:8000'])
    assert result.get('status') == 'success', "连接失败"
    
    print("\n✓ 连接管理测试通过")


def test_vertex_operations():
    """测试点操作。"""
    print("\n" + "=" * 50)
    print("测试 3: 点操作")
    print("=" * 50)
    
    # 1. 插入点（自动生成 ID）
    print("\n[3.1] 插入点（自动生成 ID）")
    result = run_command(['insert', 'vertex', '--v-type', '1', '--balance', '10000'])
    assert result.get('status') == 'success', "插入点失败"
    auto_vid = result['data']['vid']
    print(f"生成的 vid: {auto_vid}")
    
    # 2. 插入点（指定 ID）
    print("\n[3.2] 插入点（指定 ID）")
    test_vid = 999999
    result = run_command(['insert', 'vertex', '--v-type', '2', '--vid', str(test_vid), '--balance', '50000'])
    assert result.get('status') == 'success', "插入指定 ID 的点失败"
    
    # 3. 查询所有点
    print("\n[3.3] 查询所有点")
    result = run_command(['query', 'vertex'])
    assert result.get('status') == 'success', "查询点失败"
    assert result.get('count', 0) >= 2, "点数量不足"
    
    # 4. 按 vid 查询
    print("\n[3.4] 按 vid 查询")
    result = run_command(['query', 'vertex', '--vid', str(test_vid)])
    assert result.get('found') == True, "按 vid 查询失败"
    
    # 5. 按 v-type 查询
    print("\n[3.5] 按 v-type 查询")
    result = run_command(['query', 'vertex', '--v-type', '1'])
    assert result.get('status') == 'success', "按类型查询失败"
    
    # 6. 按余额范围查询
    print("\n[3.6] 按余额范围查询")
    result = run_command(['query', 'vertex', '--min-balance', '40000', '--max-balance', '60000'])
    assert result.get('status') == 'success', "按余额查询失败"
    
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
    result = run_command([
        'insert', 'edge',
        '--eid', str(test_eid),
        '--src-vid', str(vid1),
        '--dst-vid', str(vid2),
        '--amount', '5000',
        '--e-type', '0'
    ])
    assert result.get('status') == 'success', "插入边失败"
    
    # 2. 插入边（自动创建点）
    print("\n[4.2] 插入边（自动创建不存在的点）")
    new_eid = 888889
    new_src = 111111
    new_dst = 222222
    result = run_command([
        'insert', 'edge',
        '--eid', str(new_eid),
        '--src-vid', str(new_src),
        '--dst-vid', str(new_dst),
        '--amount', '3000',
        '--create-vertices'
    ])
    assert result.get('status') == 'success', "插入边（自动创建点）失败"
    
    # 3. 查询所有边
    print("\n[4.3] 查询所有边")
    result = run_command(['query', 'edge'])
    assert result.get('status') == 'success', "查询边失败"
    assert result.get('count', 0) >= 2, "边数量不足"
    
    # 4. 按 eid 查询
    print("\n[4.4] 按 eid 查询")
    result = run_command(['query', 'edge', '--eid', str(test_eid)])
    assert result.get('found') == True, "按 eid 查询失败"
    
    # 5. 按 src-vid 查询
    print("\n[4.5] 按 src-vid 查询")
    result = run_command(['query', 'edge', '--src-vid', str(vid1)])
    assert result.get('status') == 'success', "按源点查询失败"
    
    # 6. 按金额范围查询
    print("\n[4.6] 按金额范围查询")
    result = run_command(['query', 'edge', '--min-amount', '4000', '--max-amount', '6000'])
    assert result.get('status') == 'success', "按金额查询失败"
    
    print("\n✓ 边操作测试通过")


def test_logout():
    """测试登出。"""
    print("\n" + "=" * 50)
    print("测试 5: 登出")
    print("=" * 50)
    
    print("\n[5.1] 登出")
    result = run_command(['logout'])
    assert result.get('status') == 'success', "登出失败"
    
    print("\n[5.2] 登出后查询（应失败）")
    result = run_command(['query', 'vertex'])
    assert result.get('status') == 'error', "登出后仍能查询"
    
    print("\n[5.3] whoami（应显示未登录）")
    result = run_command(['whoami'])
    assert result.get('status') == 'error', "登出后 whoami 应失败"
    
    print("\n✓ 登出测试通过")


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


if __name__ == '__main__':
    sys.exit(main())