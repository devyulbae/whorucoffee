from flask import Flask
from .extensions import db
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 기본 앱 생성 함수
def create_app(test_config=None):
    # Flask 앱 초기화
    app = Flask(__name__)

    # 기본 설정
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///whorucoffee.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': os.getenv('FLASK_SECRET_KEY', 'dev'),
        'ADMIN_PASSWORD_HASH': os.getenv('ADMIN_PASSWORD_HASH')
    })

    # 테스트 설정이 있다면 적용
    if test_config:
        app.config.update(test_config)

    # SQLAlchemy 초기화
    db.init_app(app)

    # Blueprint 등록
    from .api.index import bp
    app.register_blueprint(bp)

    # 데이터베이스 생성
    with app.app_context():
        db.create_all()

    return app

# 기본 앱 생성
app = create_app()

# 다른 모듈에서 사용할 수 있도록 export
__all__ = ["app", "db"]
