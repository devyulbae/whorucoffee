from datetime import datetime
from extensions import db


class SurveyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.JSON, nullable=False)  # 설문 응답 저장
    result_type = db.Column(db.String(50), nullable=False)  # 결과 타입
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SurveyLog {self.id}>'
