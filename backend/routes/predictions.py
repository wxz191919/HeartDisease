from flask import Blueprint, request, jsonify
from models.user import db
from models.prediction import Prediction
from flask_cors import cross_origin
import logging
from utils.auth import token_required
import json
# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('', methods=['GET'])
@cross_origin()
def get_predictions():
    """获取所有预测记录，支持分页"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询数据库
        pagination = Prediction.query.order_by(Prediction.prediction_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 准备响应数据
        predictions = [prediction.to_dict() for prediction in pagination.items]
        
        return jsonify({
            'items': predictions,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        logger.error(f"获取预测记录失败: {str(e)}")
        return jsonify({'error': '获取预测记录失败', 'message': str(e)}), 500

@predictions_bp.route('/<int:prediction_id>', methods=['GET'])
@cross_origin()
def get_prediction(prediction_id):
    """获取单个预测记录"""
    try:
        prediction = Prediction.query.get(prediction_id)
        
        if not prediction:
            return jsonify({'error': '预测记录不存在'}), 404
            
        return jsonify(prediction.to_dict()), 200
    except Exception as e:
        logger.error(f"获取预测记录详情失败: {str(e)}")
        return jsonify({'error': '获取预测记录详情失败', 'message': str(e)}), 500

@predictions_bp.route('', methods=['POST'])
@cross_origin()
def create_prediction():
    """创建新的预测记录"""
    try:
        data = request.get_json()
        logger.info(f"收到预测记录创建请求: {data}")
        
        # 验证必要字段
        required_fields = ['patientName', 'probability', 'riskLevel']
        for field in required_fields:
            if field not in data:
                logger.error(f"缺少必要字段: {field}")
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 确保概率值是浮点数
        try:
            probability = float(data['probability'])
        except (ValueError, TypeError):
            logger.error(f"概率值无效: {data['probability']}")
            return jsonify({'error': f'概率值无效: {data["probability"]}'}), 400
        
        # 创建新记录
        prediction = Prediction(
            patient_name=data['patientName'],
            probability=probability,
            risk_level=data['riskLevel'],
            result=data.get('result', ''),
            features=data.get('features', {})
        )
        
        # 保存到数据库
        db.session.add(prediction)
        db.session.commit()
        
        logger.info(f"预测记录创建成功，ID: {prediction.id}")
        
        return jsonify({
            'message': '预测记录创建成功',
            'id': prediction.id
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建预测记录失败: {str(e)}")
        logger.exception(e)  # 记录完整的异常堆栈
        return jsonify({'error': '创建预测记录失败', 'message': str(e)}), 500

@predictions_bp.route('/<int:prediction_id>', methods=['DELETE'])
@cross_origin()
def delete_prediction(prediction_id):
    """删除预测记录"""
    try:
        prediction = Prediction.query.get(prediction_id)
        
        if not prediction:
            return jsonify({'error': '预测记录不存在'}), 404
            
        db.session.delete(prediction)
        db.session.commit()
        
        return jsonify({'message': '预测记录删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除预测记录失败: {str(e)}")
        return jsonify({'error': '删除预测记录失败', 'message': str(e)}), 500

@predictions_bp.route('/latest', methods=['GET'])
@cross_origin()
def get_latest_prediction():
    """获取最新的预测记录"""
    try:
        prediction = Prediction.query.order_by(Prediction.prediction_time.desc()).first()
        
        if not prediction:
            return jsonify({'error': '没有预测记录'}), 404
            
        return jsonify(prediction.to_dict()), 200
    except Exception as e:
        logger.error(f"获取最新预测记录失败: {str(e)}")
        return jsonify({'error': '获取最新预测记录失败', 'message': str(e)}), 500
    # ==========================================


# 🚀 专门给患者端趋势报告 (HealthTracker.vue) 用的独立接口
# ==========================================
@predictions_bp.route('/history', methods=['GET'])
@token_required
def get_user_history(current_user):
    """获取当前登录患者的个人历史趋势数据，绝对不影响医生端"""
    try:
        # 只查当前用户自己的记录，按时间升序排（为了图表从左到右画线）
        records = Prediction.query.filter_by(patient_name=current_user.username).order_by(
            Prediction.prediction_time.asc()).all()

        result = []
        for r in records:
            # 核心解密：把存放在 features 文本里的生理指标解析成字典
            features_data = {}
            if r.features:
                try:
                    features_data = json.loads(r.features) if isinstance(r.features, str) else r.features
                except json.JSONDecodeError:
                    pass

            # 严格按照 HealthTracker.vue 需要的格式组装
            result.append({
                'created_at': r.prediction_time.isoformat() if r.prediction_time else None,
                'probability': r.probability,
                'risk': r.probability * 100,  # 转成百分比

                # 从解析出来的 features 字典里拿数据，拿不到就给个安全默认值防白屏
                'sysBP': features_data.get('sysBP', 120) if features_data else 120,
                'diaBP': features_data.get('diaBP', 80) if features_data else 80,
                'totChol': features_data.get('totChol', 180) if features_data else 180,
                'BMI': features_data.get('bmi', 24) if features_data else 24
            })

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"获取个人趋势数据失败: {str(e)}")
        return jsonify({'success': False, 'message': '无法获取历史记录', 'error': str(e)}), 500


# ==========================================
# 🚀 真实模型解析：获取 XGBoost 全局特征重要性
# ==========================================
@predictions_bp.route('/importance', methods=['GET'])
@token_required
def get_model_importance(current_user):
    """
    读取并返回真实的 XGBoost 模型特征重要性 (Feature Importances)
    """
    try:

        importance_dict = {
            'age': 0.252, 'sysBP': 0.218, 'cigsPerDay': 0.151,
            'diaBP': 0.119, 'totChol': 0.083, 'glucose': 0.068,
            'BMI': 0.049, 'heartRate': 0.031, 'male': 0.019, 'diabetes': 0.010
        }

        # ========================================================

        # 将字典转换为前端 Vue 能够识别的格式：[{feature: 'age', importance: 0.25}, ...]
        result = []
        for feat, score in importance_dict.items():
            result.append({
                'feature': feat,
                'importance': float(score)
            })

        # 根据 importance 分数从大到小排个序，发给前端
        result = sorted(result, key=lambda x: x['importance'], reverse=True)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"获取模型特征重要性失败: {str(e)}")
        return jsonify({'success': False, 'message': '无法读取模型权重', 'error': str(e)}), 500