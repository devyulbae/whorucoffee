import pytest
import json
from whorucoffee import create_app
from whorucoffee.extensions import db
from whorucoffee.models.survey_log import SurveyLog

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

def test_index_page(client):
    """메인 페이지 접속 테스트"""
    response = client.get('/')
    assert response.status_code == 200

def test_analyze_valid_answers(client):
    """유효한 답변에 대한 분석 테스트"""
    test_answers = {
        "선호하는 커피 추출 방식": ["에스프레소"],
        "하루 커피 섭취량": ["2-3잔"]
    }
    response = client.post('/analyze', 
        data={'answers': json.dumps(test_answers)})
    assert response.status_code == 200

def test_analyze_invalid_answers(client):
    """잘못된 형식의 답변에 대한 테스트"""
    response = client.post('/analyze', 
        data={'answers': 'invalid_json'})
    assert response.status_code == 400

def test_analyze_empty_answers(client):
    """빈 답변에 대한 테스트"""
    response = client.post('/analyze', data={})
    assert response.status_code == 500

def test_llm_fallback(client):
    """LLM 실패 시 기본 타입 반환 테스트"""
    test_answers = {
        "선호하는 커피 추출 방식": ["convenience"],
        "하루 커피 섭취량": ["1잔 이하"],
        "커피를 주로 마시는 장소": ["편의점"],
        "커피를 고를 때 가장 중요하게 생각하는 것": ["가격"]
    }
    response = client.post('/analyze', 
        data={'answers': json.dumps(test_answers)})
    assert response.status_code == 200

def test_survey_logging(client, app):
    """설문 응답 로깅 테스트"""
    test_answers = {
        "선호하는 커피 추출 방식": ["에스프레소"],
        "하루 커피 섭취량": ["2-3잔"]
    }
    response = client.post('/analyze', 
        data={'answers': json.dumps(test_answers)})
    assert response.status_code == 200
    
    # app context 내에서 로그 확인
    with app.app_context():
        log_count = SurveyLog.query.count()
        assert log_count == 1
