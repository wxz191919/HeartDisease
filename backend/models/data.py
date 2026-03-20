from datetime import datetime
from .user import db

class DataFile(db.Model):
    __tablename__ = 'data_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    record_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('处理中', '已完成', '失败'), default='处理中')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'uploadTime': self.upload_time.isoformat(),
            'recordCount': self.record_count,
            'status': self.status
        } 