#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
心脏病预测模型完整流程脚本
包括数据加载、模型训练和预测测试
"""

import os
import sys
import time

def run_command(command):
    """
    运行命令并打印输出
    """
    print(f"\n执行命令: {command}")
    start_time = time.time()
    exit_code = os.system(command)
    end_time = time.time()
    
    if exit_code == 0:
        print(f"命令执行成功，耗时: {end_time - start_time:.2f} 秒")
    else:
        print(f"命令执行失败，退出码: {exit_code}")
        sys.exit(exit_code)

def main():
    """
    主函数，运行完整流程
    """
    print("=" * 80)
    print("心脏病预测模型完整流程")
    print("=" * 80)
    
    # 检查数据文件是否存在
    data_path = 'data/heart.csv'  # 修改为相对路径
    if not os.path.exists(data_path):
        print(f"数据文件不存在: {data_path}")
        sys.exit(1)
    
    # 1. 训练模型
    print("\n1. 训练模型")
    run_command("python run_training.py")
    
    # 2. 测试预测
    print("\n2. 测试预测")
    run_command("python test_prediction.py")
    
    print("\n" + "=" * 80)
    print("流程完成！")
    print("=" * 80)

if __name__ == "__main__":
    main() 