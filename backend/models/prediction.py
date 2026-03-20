from models.user import db
import datetime
import json

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    prediction_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(200))
    features = db.Column(db.Text)  # 存储为JSON字符串
    
    def __init__(self, patient_name, probability, risk_level, result, features):
        self.patient_name = patient_name
        self.probability = float(probability)  # 确保概率是浮点数
        self.risk_level = risk_level
        self.result = result
        
        # 确保features是有效的JSON
        if isinstance(features, dict):
            self.features = json.dumps(features)
        elif isinstance(features, str):
            # 如果已经是字符串，尝试解析确保是有效的JSON
            try:
                json.loads(features)
                self.features = features
            except json.JSONDecodeError:
                self.features = json.dumps({})
        else:
            self.features = json.dumps({})
    
    def to_dict(self):
        # 确保features是有效的JSON
        features_dict = {}
        if self.features:
            try:
                features_dict = json.loads(self.features)
            except json.JSONDecodeError:
                features_dict = {}
        
        return {
            'id': self.id,
            'patientName': self.patient_name,
            'predictionTime': self.prediction_time.isoformat(),
            'probability': self.probability,
            'riskLevel': self.risk_level,
            'result': self.result,
            'features': features_dict
        } 