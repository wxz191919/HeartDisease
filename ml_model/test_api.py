#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
心脏病预测模型API测试脚本
用于测试心脏病预测模型API
"""

import requests
import json
import pandas as pd
import os

# API地址
API_BASE_URL = 'http://localhost:5003/api'

def test_health_check():
    """
    测试健康检查接口
    """
    url = f"{API_BASE_URL}/health"
    response = requests.get(url)
    
    print("健康检查:")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_get_features():
    """
    测试获取特征信息接口
    """
    url = f"{API_BASE_URL}/features"
    response = requests.get(url)
    
    print("获取特征信息:")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"特征数量: {len(data['features'])}")
        print(f"特征列表: {data['features']}")
        print(f"样本输入: {json.dumps(data['sample_input'], indent=2, ensure_ascii=False)}")
    else:
        print(f"响应: {response.text}")
    print()

def test_predict():
    """
    测试预测接口
    """
    url = f"{API_BASE_URL}/predict"
    
    # 获取样本输入
    features_url = f"{API_BASE_URL}/features"
    features_response = requests.get(features_url)
    sample_input = features_response.json()['sample_input']
    
    # 发送预测请求
    response = requests.post(url, json=sample_input)
    
    print("预测:")
    print(f"状态码: {response.status_code}")
    print(f"请求数据: {json.dumps(sample_input, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"预测结果: {'有心脏病风险' if result['prediction'] == 1 else '无心脏病风险'}")
        print(f"风险概率: {result['probability']:.4f}")
        print(f"风险等级: {result['risk_level']}")
    else:
        print(f"响应: {response.text}")
    print()

def test_batch_predict():
    """
    测试批量预测接口
    """
    url = f"{API_BASE_URL}/batch_predict"
    
    # 加载数据集
    data_path = 'data/heart.csv'
    if not os.path.exists(data_path):
        print(f"数据文件不存在: {data_path}")
        return
    
    # 读取前5条记录
    data = pd.read_csv(data_path).head(5)
    
    # 准备请求数据
    request_data = []
    for _, row in data.iterrows():
        # 转换为字典并删除目标变量
        input_data = row.drop('TenYearCHD').to_dict()
        request_data.append(input_data)
    
    # 发送批量预测请求
    response = requests.post(url, json=request_data)
    
    print("批量预测:")
    print(f"状态码: {response.status_code}")
    print(f"请求数据数量: {len(request_data)}")
    
    if response.status_code == 200:
        results = response.json()['results']
        print(f"响应数据数量: {len(results)}")
        
        for i, (result, row) in enumerate(zip(results, data.iterrows())):
            actual = row[1]['TenYearCHD']
            predicted = result['prediction']
            probability = result['probability']
            print(f"记录 {i+1}: 实际值={actual}, 预测值={predicted}, 概率={probability:.4f}")
    else:
        print(f"响应: {response.text}")
    print()

def main():
    """
    主函数
    """
    print("=" * 80)
    print("心脏病预测模型API测试")
    print("=" * 80)
    
    # 测试健康检查接口
    test_health_check()
    
    # 测试获取特征信息接口
    test_get_features()
    
    # 测试预测接口
    test_predict()
    
    # 测试批量预测接口
    test_batch_predict()
    
    print("=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main() 