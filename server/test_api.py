#!/usr/bin/env python3
"""
API测试脚本
测试所有API端点的基本功能
"""
import requests
import json
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def test_endpoint(method: str, url: str, description: str, params: Dict[str, Any] = None) -> bool:
    """测试单个API端点"""
    try:
        print_info(f"测试: {description}")
        print(f"  请求: {method} {url}")
        
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.request(method, url, json=params)
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  返回数据量: {len(data) if isinstance(data, list) else 1}")
            print_success(f"{description} - 成功")
            return True
        elif response.status_code == 404:
            print_warning(f"{description} - 未找到数据（这可能是正常的）")
            return True
        else:
            print_error(f"{description} - 失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"{description} - 异常: {str(e)}")
        return False


def main():
    """执行所有API测试"""
    print("\n" + "="*60)
    print("开始API功能测试")
    print("="*60 + "\n")
    
    results = []
    
    # 1. 测试朝代API
    print("\n【朝代API测试】")
    results.append(test_endpoint("GET", f"{BASE_URL}/dynasties", "获取朝代列表"))
    results.append(test_endpoint("GET", f"{BASE_URL}/dynasties/ming", "获取明朝详情"))
    
    # 2. 测试皇帝API
    print("\n【皇帝API测试】")
    results.append(test_endpoint("GET", f"{BASE_URL}/emperors", "获取皇帝列表"))
    results.append(test_endpoint("GET", f"{BASE_URL}/emperors", "按朝代筛选皇帝", {"dynasty_id": "ming"}))
    results.append(test_endpoint("GET", f"{BASE_URL}/emperors", "分页查询皇帝", {"skip": 0, "limit": 5}))
    
    # 测试皇帝详情（需要先获取一个皇帝ID）
    try:
        response = requests.get(f"{BASE_URL}/emperors", params={"limit": 1})
        if response.status_code == 200 and len(response.json()) > 0:
            emperor_id = response.json()[0]["emperor_id"]
            results.append(test_endpoint("GET", f"{BASE_URL}/emperors/{emperor_id}", f"获取皇帝详情 ({emperor_id})"))
        else:
            print_warning("无法获取皇帝ID，跳过详情测试")
    except Exception as e:
        print_warning(f"获取皇帝ID失败: {str(e)}")
    
    # 3. 测试事件API
    print("\n【事件API测试】")
    results.append(test_endpoint("GET", f"{BASE_URL}/events", "获取事件列表"))
    results.append(test_endpoint("GET", f"{BASE_URL}/events", "按朝代筛选事件", {"dynasty_id": "ming"}))
    results.append(test_endpoint("GET", f"{BASE_URL}/events", "按类型筛选事件", {"event_type": "战争"}))
    results.append(test_endpoint("GET", f"{BASE_URL}/events", "分页查询事件", {"skip": 0, "limit": 5}))
    
    # 测试事件详情
    try:
        response = requests.get(f"{BASE_URL}/events", params={"limit": 1})
        if response.status_code == 200 and len(response.json()) > 0:
            event_id = response.json()[0]["event_id"]
            results.append(test_endpoint("GET", f"{BASE_URL}/events/{event_id}", f"获取事件详情 ({event_id})"))
        else:
            print_warning("无法获取事件ID，跳过详情测试")
    except Exception as e:
        print_warning(f"获取事件ID失败: {str(e)}")
    
    # 4. 测试人物API
    print("\n【人物API测试】")
    results.append(test_endpoint("GET", f"{BASE_URL}/persons", "获取人物列表"))
    results.append(test_endpoint("GET", f"{BASE_URL}/persons", "按朝代筛选人物", {"dynasty_id": "ming"}))
    results.append(test_endpoint("GET", f"{BASE_URL}/persons", "按类型筛选人物", {"person_type": "文臣"}))
    results.append(test_endpoint("GET", f"{BASE_URL}/persons", "分页查询人物", {"skip": 0, "limit": 5}))
    
    # 测试人物详情
    try:
        response = requests.get(f"{BASE_URL}/persons", params={"limit": 1})
        if response.status_code == 200 and len(response.json()) > 0:
            person_id = response.json()[0]["person_id"]
            results.append(test_endpoint("GET", f"{BASE_URL}/persons/{person_id}", f"获取人物详情 ({person_id})"))
        else:
            print_warning("无法获取人物ID，跳过详情测试")
    except Exception as e:
        print_warning(f"获取人物ID失败: {str(e)}")
    
    # 5. 测试时间轴API
    print("\n【时间轴API测试】")
    results.append(test_endpoint("GET", f"{BASE_URL}/timeline/ming", "获取明朝时间轴"))
    
    # 统计结果
    print("\n" + "="*60)
    print("测试结果统计")
    print("="*60)
    total = len(results)
    success = sum(results)
    print(f"总测试数: {total}")
    print(f"成功: {Colors.GREEN}{success}{Colors.END}")
    print(f"失败: {Colors.RED}{total - success}{Colors.END}")
    print(f"成功率: {success/total*100:.1f}%")
    print("="*60 + "\n")
    
    if success == total:
        print_success("所有测试通过！")
    else:
        print_error(f"有 {total - success} 个测试失败")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print_error(f"测试过程中发生错误: {str(e)}")
