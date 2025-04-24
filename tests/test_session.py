import pytest
import json
from datetime import datetime, timedelta
from whorucoffee import create_app
from whorucoffee.extensions import db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_key'
    })
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_session_active(client):
    """유효한 세션 테스트"""
    response = client.get('/')
    assert response.status_code == 200

def test_session_expiry(client):
    """세션 만료 테스트"""
    with client.session_transaction() as session:
        session['last_activity'] = datetime.utcnow() - timedelta(minutes=31)
    response = client.get('/')
    assert response.status_code == 200

def test_session_active_post(client):
    """유효한 세션 테스트 (post 요청)"""
    with client.session_transaction() as session:
        session["last_activity"] = datetime.utcnow()

    test_answers = {"선호하는 커피 추출 방식": ["에스프레소"]}
    response = client.post(
        "/analyze", data={"answers": json.dumps(test_answers)}
    )
    assert response.status_code == 200
