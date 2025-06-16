#!/usr/bin/env python3
"""
DEEPSEEK模型测试脚本
用于测试模型的基本功能和性能
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_chat(prompt, max_length=None, temperature=None):
    """测试聊天接口"""
    print(f"\n💬 测试问题: {prompt}")
    
    data = {"prompt": prompt}
    if max_length:
        data["max_length"] = max_length
    if temperature:
        data["temperature"] = temperature
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"⏱️  响应时间: {end_time - start_time:.2f}秒")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 AI回复: {result['response']}")
        else:
            print(f"❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试DEEPSEEK模型...")
    
    # 1. 健康检查
    if not test_health():
        print("❌ 服务未启动或模型未加载，请先运行 python main.py")
        return
    
    print("\n" + "="*50)
    
    # 2. 基础对话测试
    test_cases = [
        "你好，请介绍一下你自己",
        "请写一个Python函数来计算斐波那契数列",
        "解释一下什么是递归",
        "如何在Python中处理异常？",
        "请写一个简单的快速排序算法"
    ]
    
    for prompt in test_cases:
        test_chat(prompt)
        print("\n" + "-"*30)
    
    # 3. 参数测试
    print("\n🔧 测试不同参数...")
    test_chat("写一个Hello World程序", max_length=100, temperature=0.1)
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main() 