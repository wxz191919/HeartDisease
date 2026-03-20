#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
心脏病预测模型API
提供HTTP接口来使用心脏病预测模型
"""

from flask import Flask, request, jsonify
from predict_api import prediction_api
from flask_cors import CORS
import os
import numpy as np
import pandas as pd
import base64
from io import BytesIO
import traceback

app = Flask(__name__)
# 启用CORS，允许所有来源的跨域请求
CORS(app)

# 创建预测API实例
prediction_api = prediction_api

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    try:
        if prediction_api.model is None:
            if not prediction_api.load_model():
                return jsonify({
                    'status': 'error',
                    'message': '模型未加载且无法加载'
                }), 500
        
        return jsonify({
            'status': 'ok',
            'message': '服务正常运行'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'健康检查失败: {str(e)}'
        }), 500

@app.route('/api/features', methods=['GET'])
def get_features():
    """
    获取特征信息接口
    """
    return jsonify({
        'features': prediction_api.get_feature_names(),
        'descriptions': prediction_api.get_feature_descriptions(),
        'sample_input': prediction_api.get_sample_input()
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    预测接口
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '请求数据为空',
                'success': False
            }), 400
        
        # 进行预测
        result = prediction_api.predict(data)
        
        return jsonify(result)
    except Exception as e:
        print(f"预测失败: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f'预测失败: {str(e)}',
            'success': False
        }), 500



@app.route('/api/feature_importance', methods=['GET'])
def feature_importance():
    """
    获取特征重要性数据接口
    """
    try:
        # 检查模型是否已加载
        if prediction_api.model is None:
            return jsonify({
                'error': '模型未加载',
                'success': False
            }), 500
        
        # 获取特征重要性数据
        importance_data = prediction_api.get_feature_importance()
        
        return jsonify({
            'feature_importance': importance_data,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': f'获取特征重要性失败: {str(e)}',
            'success': False
        }), 500



@app.route('/api/feature_analysis', methods=['GET'])
def feature_analysis():
    """
    获取特征重要性分析接口
    """
    try:
        # 检查模型是否已加载
        if prediction_api.model is None:
            print("模型未加载，尝试加载模型...")
            if not prediction_api.load_model():
                print("模型加载失败")
                return jsonify({
                    'error': '模型未加载且无法加载',
                    'success': False
                }), 500
            print("模型加载成功")
        
        # 获取特征重要性分析
        result = prediction_api.get_feature_importance_analysis()
        print(f"特征重要性分析结果: {'成功' if result.get('success') else '失败'}")
        
        if result.get('success'):
            # 直接返回结果，不要嵌套
            return jsonify({
                'image': result.get('image'),
                'feature_importance': result.get('feature_importance'),
                'success': True
            })
        else:
            return jsonify({
                'error': result.get('error', '特征重要性分析失败'),
                'success': False
            }), 500
            
    except Exception as e:
        print(f"获取特征重要性分析失败: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'error': f'获取特征重要性分析失败: {str(e)}',
            'success': False
        }), 500

@app.route('/api/shap_values_for_instance', methods=['POST'])
def shap_values_for_instance():
    """
    获取特定实例的特征重要性分析接口
    """
    try:
        # 检查模型是否已加载
        if prediction_api.model is None:
            print("模型未加载，尝试加载模型...")
            if not prediction_api.load_model():
                print("模型加载失败")
                return jsonify({
                    'error': '模型未加载且无法加载',
                    'success': False
                }), 500
            print("模型加载成功")
        
        # 获取请求数据
        data = request.get_json()
        print(f"收到特征重要性分析请求，数据: {data}")
        
        if not data:
            print("请求数据为空")
            return jsonify({
                'error': '请求数据为空',
                'success': False
            }), 400
        
        # 确保数据是字典格式
        if not isinstance(data, dict):
            print(f"请求数据格式错误，不是字典: {type(data)}")
            return jsonify({
                'error': f'请求数据格式错误，应为字典，实际为: {type(data).__name__}',
                'success': False
            }), 400
        
        # 获取特定实例的特征重要性分析
        try:
            result = prediction_api.get_shap_values_for_instance(data)
            print(f"特征重要性分析结果: {'成功' if result.get('success') else '失败'}")
            
            if result.get('success'):
                # 直接返回结果，不要嵌套在feature_analysis下
                return jsonify({
                    'image': result.get('image'),
                    'feature_importance': result.get('feature_importance'),
                    'success': True
                })
            else:
                return jsonify({
                    'error': result.get('error', '特征重要性分析失败'),
                    'success': False
                }), 500
                
        except Exception as error:
            print(f"特征重要性分析失败: {str(error)}")
            traceback.print_exc()
            
            return jsonify({
                'error': f'特征重要性分析失败: {str(error)}',
                'success': False
            }), 500
            
    except Exception as e:
        print(f"处理特征重要性分析请求时发生错误: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'error': f'获取特征重要性分析失败: {str(e)}',
            'success': False
        }), 500


# ==========================================
# 🚀 真实医疗宏观数据：全球心脏病负担统计接口
# ==========================================
@app.route('/api/global-analysis', methods=['GET'])
def get_global_analysis():
    try:
        # 指向你刚刚放好的真实 Kaggle 数据集
        data_path = 'data/global_cvd_burden_2025_2050.csv'
        if not os.path.exists(data_path):
            return jsonify({'success': False, 'message': '未找到真实数据集文件'})

        df = pd.read_csv(data_path)

        # 提取 2025 年的截面数据作为当前全球现状
        df_2025 = df[df['year'] == 2025]

        # 1. 测算全球总死亡人数 (基于数据集中的 crude_cvd_deaths)
        total_deaths = int(df_2025['crude_cvd_deaths'].sum())

        # 2. 按大洲聚合死亡分布
        continent_group = df_2025.groupby('continent')['crude_cvd_deaths'].sum().reset_index()
        continent_data = [{'name': row['continent'], 'value': int(row['crude_cvd_deaths'])} for _, row in
                          continent_group.iterrows()]

        # 3. 提炼四大核心致死因素的全球平均归因占比
        risk_factors = [
            {'name': '高血压致死', 'value': round(df_2025['high_sbp_attributable_deaths_pct'].mean(), 1)},
            {'name': '高LDL(胆固醇)致死', 'value': round(df_2025['high_ldl_attributable_deaths_pct'].mean(), 1)},
            {'name': '高BMI(肥胖)致死', 'value': round(df_2025['high_bmi_attributable_deaths_pct'].mean(), 1)},
            {'name': '吸烟致死', 'value': round(df_2025['tobacco_attributable_deaths_pct'].mean(), 1)}
        ]

        # 4. 提取 2025-2050 的全球恶化趋势
        trend_group = df.groupby('year')['crude_cvd_deaths'].sum().reset_index()
        trend_years = [int(y) for y in trend_group['year']]
        trend_deaths = [int(d) for d in trend_group['crude_cvd_deaths']]
        # === 🚀 只准加，不准删：新增第5步，精准提取各国死亡率用于地图 ===
        country_data = []
        for _, row in df_2025.iterrows():
            country_data.append({
                'name': str(row['country']),  # 提取国家名称
                'value': round(float(row['crude_mortality_rate_per_100k']), 2)  # 提取每10万人死亡率
            })
        return jsonify({
            'success': True,
            'data': {
                'total_deaths': total_deaths,
                'continent_data': continent_data,
                'risk_factors': risk_factors,
                'trend': {
                    'years': trend_years,
                    'deaths': trend_deaths
                }
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
if __name__ == '__main__':
    # 设置端口
    port = int(os.environ.get('PORT', 5002))
    
    # 启动服务
    app.run(host='0.0.0.0', port=port, debug=True) 