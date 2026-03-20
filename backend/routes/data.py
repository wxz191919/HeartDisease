import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.data import DataFile, db
import pandas as pd
from datetime import datetime
from models.prediction import Prediction

data_bp = Blueprint('data', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@data_bp.route('/data', methods=['GET'])
@jwt_required()
def get_data_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    user_id = get_jwt_identity()
    pagination = DataFile.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@data_bp.route('/data/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': '没有文件被上传'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'message': '不支持的文件类型'}), 400
        
    user_id = get_jwt_identity()
    filename = secure_filename(file.filename)
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    saved_filename = f"{user_id}_{timestamp}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, saved_filename)
    
    try:
        # 保存文件
        file.save(file_path)
        
        # 读取CSV文件获取记录数
        df = pd.read_csv(file_path)
        record_count = len(df)
        
        # 创建数据库记录
        data_file = DataFile(
            filename=saved_filename,
            original_filename=filename,
            file_path=file_path,
            record_count=record_count,
            user_id=user_id,
            status='已完成'
        )
        
        db.session.add(data_file)
        db.session.commit()
        
        return jsonify({'message': '文件上传成功', 'data': data_file.to_dict()}), 201
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'message': f'文件处理失败: {str(e)}'}), 500

@data_bp.route('/data/download/<int:file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    user_id = get_jwt_identity()
    data_file = DataFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not data_file:
        return jsonify({'message': '文件不存在'}), 404
        
    if not os.path.exists(data_file.file_path):
        return jsonify({'message': '文件已被删除'}), 404
        
    return send_file(
        data_file.file_path,
        as_attachment=True,
        download_name=data_file.original_filename
    )

@data_bp.route('/data/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()
    data_file = DataFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not data_file:
        return jsonify({'message': '文件不存在'}), 404
        
    try:
        # 删除物理文件
        if os.path.exists(data_file.file_path):
            os.remove(data_file.file_path)
            
        # 删除数据库记录
        db.session.delete(data_file)
        db.session.commit()
        
        return jsonify({'message': '文件删除成功'}), 200
        
    except Exception as e:
        return jsonify({'message': f'文件删除失败: {str(e)}'}), 500

@data_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    user_id = get_jwt_identity()
    
    # 获取统计数据
    total_cases = DataFile.query.filter_by(user_id=user_id).count()
    
    # 获取本月新增数据
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_new = DataFile.query.filter(
        DataFile.user_id == user_id,
        DataFile.upload_time >= current_month
    ).count()
    
    # 从预测表中获取预测次数和高风险病例数
    from models.prediction import Prediction
    
    # 获取预测次数
    predictions_count = Prediction.query.count()
    
    # 获取高风险病例数
    high_risk_count = Prediction.query.filter(
        Prediction.risk_level == '高风险'
    ).count()
    
    # 统计数据
    stats = {
        'totalCases': total_cases,
        'monthlyNew': monthly_new,
        'predictions': predictions_count,
        'highRisk': high_risk_count
    }
    
    # 获取最近活动
    recent_files = DataFile.query.filter_by(user_id=user_id).order_by(
        DataFile.upload_time.desc()
    ).limit(5)
    
    # 获取最近预测活动
    recent_predictions = Prediction.query.order_by(
        Prediction.prediction_time.desc()
    ).limit(5)
    
    # 合并活动列表
    activities = []
    
    # 添加文件上传活动
    for f in recent_files:
        activities.append({
            'id': f'file_{f.id}',
            'title': f'上传了文件 {f.original_filename}',
            'description': f'包含 {f.record_count} 条记录',
            'time': f.upload_time.isoformat()
        })
    
    # 添加预测活动
    for p in recent_predictions:
        activities.append({
            'id': f'pred_{p.id}',
            'title': f'进行了预测 {p.patient_name}',
            'description': f'风险等级: {p.risk_level}, 概率: {p.probability:.2f}',
            'time': p.prediction_time.isoformat()
        })
    
    # 按时间排序
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    # 只保留前5条
    activities = activities[:5]
    
    return jsonify({
        'stats': stats,
        'activities': activities
    })