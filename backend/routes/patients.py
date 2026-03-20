from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.patient import Patient, db
from models.prediction import Prediction
from sqlalchemy import or_, desc
import traceback
from utils.auth import token_required, admin_required

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('', methods=['GET'])
@token_required
def get_patients(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Patient.query
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.name.ilike(search_term),
                    Patient.contact_number.ilike(search_term),
                    Patient.address.ilike(search_term)
                )
            )
        
        # 尝试使用新版SQLAlchemy的分页方法，如果失败则使用旧版方法
        try:
            # 新版SQLAlchemy分页方法
            pagination = query.paginate(page=page, per_page=per_page)
        except TypeError:
            # 旧版SQLAlchemy分页方法
            pagination = query.paginate(page, per_page, False)
        
        patients = pagination.items
        total = pagination.total
        
        # 获取每个病人的最新预测结果
        patient_data = []
        for patient in patients:
            patient_dict = patient.to_dict()
            
            # 查询该病人的最新预测记录
            latest_prediction = Prediction.query.filter(
                Prediction.patient_name == patient.name
            ).order_by(desc(Prediction.prediction_time)).first()
            
            # 如果有预测记录，添加风险等级信息
            if latest_prediction:
                patient_dict['riskLevel'] = latest_prediction.risk_level
                patient_dict['probability'] = latest_prediction.probability
                patient_dict['predictionId'] = latest_prediction.id
                patient_dict['predictionTime'] = latest_prediction.prediction_time.isoformat()
            
            patient_data.append(patient_dict)
        
        return jsonify({
            'patients': patient_data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in get_patients: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(current_user, patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        print(f"Error in get_patient: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('', methods=['POST'])
@token_required
def create_patient(current_user):
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'gender', 'age']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        new_patient = Patient(
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            contact_number=data.get('phone'),  # 前端传入的是phone字段
            address=data.get('address'),
            doctor_id=current_user.id
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        return jsonify({'message': 'Patient created successfully', 'patient': new_patient.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_patient: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(current_user, patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            patient.name = data['name']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'age' in data:
            patient.age = data['age']
        if 'phone' in data:
            patient.contact_number = data['phone']  # 前端传入的是phone字段
        if 'address' in data:
            patient.address = data['address']
        
        db.session.commit()
        
        return jsonify({'message': 'Patient updated successfully', 'patient': patient.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_patient: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@token_required
def delete_patient(current_user, patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({'message': 'Patient deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_patient: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 