#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
心脏病预测模型测试脚本
用于测试心脏病预测模型的预测功能
"""

from predict_api import prediction_api
import pandas as pd
import os

def test_single_prediction():
    """
    测试单个样本预测
    """
    # 获取样本输入
    sample_input = prediction_api.get_sample_input()
    
    # 打印样本输入
    print("样本输入:")
    for key, value in sample_input.items():
        desc = prediction_api.get_feature_descriptions().get(key, key)
        print(f"  {key} ({desc}): {value}")
    
    # 进行预测
    result = prediction_api.predict(sample_input)
    
    # 打印预测结果
    if result['success']:
        print("\n预测结果:")
        print(f"  预测类别: {'有心脏病风险' if result['prediction'] == 1 else '无心脏病风险'}")
        print(f"  风险概率: {result['probability']:.4f}")
        print(f"  风险等级: {result['risk_level']}")
    else:
        print(f"\n预测失败: {result.get('error', '未知错误')}")

def test_batch_prediction():
    """
    测试批量预测
    """
    # 加载数据集
    data_path = 'data/heart.csv'  # 修改为相对路径
    if not os.path.exists(data_path):
        print(f"数据文件不存在: {data_path}")
        return
    
    # 读取前5条记录
    data = pd.read_csv(data_path).head(5)
    
    print(f"\n批量预测 ({len(data)} 条记录):")
    
    # 对每条记录进行预测
    for i, row in data.iterrows():
        # 转换为字典
        input_data = row.drop('TenYearCHD').to_dict()
        
        # 进行预测
        result = prediction_api.predict(input_data)
        
        # 打印预测结果
        if result['success']:
            print(f"  记录 {i+1}: 实际值={row['TenYearCHD']}, 预测值={result['prediction']}, 概率={result['probability']:.4f}")
        else:
            print(f"  记录 {i+1}: 预测失败 - {result.get('error', '未知错误')}")

if __name__ == "__main__":
    print("测试心脏病预测模型...")
    
    # 检查模型是否已加载
    if prediction_api.model is None:
        print("模型未加载，请先训练模型")
    else:
        # 测试单个样本预测
        test_single_prediction()
        
        # 测试批量预测
        test_batch_prediction()
    
    print("\n测试完成！") 