from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    url_for,
    redirect,
    session,
    flash,
)
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db
from sqlalchemy import func
from werkzeug.exceptions import HTTPException
from prompts.coffee_personality_prompt import COFFEE_TYPES
from utils.llm_handler import analyze_coffee_personality
from models.survey_log import SurveyLog
from utils.security import verify_password

# 로깅 설정
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# Flask 앱 생성 - 템플릿과 정적 파일 경로 설정
app = Flask(__name__, 
    static_folder='../static',    # 상대 경로 수정
    template_folder='../templates' # 상대 경로 수정
)

# 설정
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///whorucoffee.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': os.getenv('SECRET_KEY', 'default-secret-key')
})

# DB 초기화
db.init_app(app)

# DB 테이블 생성
with app.app_context():
    db.create_all()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("관리자 로그인이 필요합니다.", "error")
            return redirect(url_for("admin_login", next=request.url))
        if "admin_last_activity" in session:
            last_activity = session["admin_last_activity"]
            if (datetime.now(timezone.utc) - last_activity).total_seconds() > 3600:
                session.clear()
                flash("세션이 만료되었습니다. 다시 로그인해주세요.", "error")
                return redirect(url_for("admin_login"))
        session["admin_last_activity"] = datetime.now(timezone.utc)
        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error in index route: {e}")
        return jsonify(error=str(e)), 500

@app.route('/question')
def question():
    return render_template("question.html")

# 유형 이름 매핑 수정
TYPE_MAPPING = {
    '진성 한국인': 'korean_authentic',
    '유러피안 커피 애호가': 'european_enthusiast',
    '프리미엄 탐험가': 'premium_explorer',
    '가성비 실속파': 'value_seeker',
    '카페인 러버': 'caffeine_lover',
    '소셜 커피러': 'social_coffee',
    '헬시 드링커': 'healthy_drinker',
    '라이트 컨슈머': 'light_consumer'
}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        answers = request.form.get('answers')
        if not answers:
            return jsonify({"error": "No answers provided"}), 500
            
        answers_dict = json.loads(answers)
        response = analyze_coffee_personality(answers_dict)
        
        if not response.get('success'):
            raise ValueError("LLM analysis failed")
            
        result = response['result']
        
        # DB 로깅
        try:
            survey_log = SurveyLog(
                answers=answers_dict,
                result_type=result.get('type', 'unknown')
            )
            db.session.add(survey_log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Logging error: {str(e)}")
            pass
        
        coffee_type = result.get('type', '')
        print(f"=== LLM이 반환한 유형: {coffee_type} ===")
        
        if not coffee_type:
            return render_template('error.html', 
                               error_message="커피 유형을 결정할 수 없습니다.")
        
        # 한글 유형을 영어로 매핑
        template_name = TYPE_MAPPING.get(coffee_type, 'default')
        print(f"=== 매핑된 템플릿 이름: {template_name} ===")
        
        if template_name == 'default':
            print(f"!!! 주의: 매핑되지 않은 유형 발견: {coffee_type} !!!")
        
        # 이미지 파일명에 .jpeg 확장자 사용
        result['image'] = f"{template_name}.jpeg"
        
        template_path = f'results/{template_name}.html'
        print(f"Rendering template: {template_path} for type: {coffee_type}")
        
        return render_template(template_path, 
                            type_info=result)
            
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return render_template('error.html', 
                           error_message=f"결과를 처리하는 중 오류가 발생했습니다: {str(e)}")

@app.route('/result')
def result():
    type_name = request.args.get("type", "진성 한국인")

    # 타입별 템플릿 매핑
    template_mapping = {
        "진성 한국인": "results/korean_authentic.html",
        "유러피안 커피 애호가": "results/european_enthusiast.html",
        "프리미엄 탐험가": "results/premium_explorer.html",
        "가성비 실속파": "results/value_seeker.html",
        "카페인 러버": "results/caffeine_lover.html",
        "소셜 커피러": "results/social_coffee.html",
        "헬시 드링커": "results/healthy_drinker.html",
        "라이트 컨슈머": "results/light_consumer.html",
    }

    # 해당 타입의 템플릿 선택
    template = template_mapping.get(type_name, "results/korean_authentic.html")

    return render_template(template, type_info=COFFEE_TYPES[type_name], type=type_name)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_stats"))

    if request.method == "POST":
        password = request.form.get("password")
        stored_hash = app.config["ADMIN_PASSWORD_HASH"]

        if not stored_hash:
            logger.error("Admin password hash not configured")
            flash("관리자 계정이 설정되지 않았습니다.", "error")
            return render_template("admin/login.html")

        try:
            if verify_password(stored_hash, password):
                session["is_admin"] = True
                session["admin_last_activity"] = datetime.now(timezone.utc)
                session.permanent = True

                next_page = request.args.get("next")
                if next_page and next_page.startswith("/admin"):
                    return redirect(next_page)
                return redirect(url_for("admin_stats"))
            else:
                flash("비밀번호가 올바르지 않습니다.", "error")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash("로그인 처리 중 오류가 발생했습니다.", "error")

    return render_template("admin/login.html")

@app.route('/admin/stats')
@admin_required
def admin_stats():
    try:
        # 전체 응답 수
        total_responses = SurveyLog.query.count()

        # 타입별 분포
        type_distribution = (
            db.session.query(SurveyLog.result_type, func.count(SurveyLog.id))
            .group_by(SurveyLog.result_type)
            .all()
        )

        # 최근 24시간 응답 수
        recent_responses = SurveyLog.query.filter(
            SurveyLog.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
        ).count()

        return render_template(
            "admin/stats.html",
            total_responses=total_responses,
            type_distribution=type_distribution,
            recent_responses=recent_responses,
        )
    except Exception as e:
        logger.error(f"Admin stats error: {str(e)}")
        return jsonify({"error": "통계 데이터를 불러오는데 실패했습니다."}), 500

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("index"))

# 전역 에러 핸들러
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return (
            render_template(
                "error.html", error_message=e.description, error_code=e.code
            ),
            e.code,
        )

    # 예상치 못한 에러
    logger.error(f"Unexpected error: {str(e)}")
    return (
        render_template(
            "error.html",
            error_message="예상치 못한 오류가 발생했습니다.",
            error_code=500,
        ),
        500,
    )

# LLM 응답 처리 개선
def analyze_with_llm_safe(answers_dict):
    try:
        llm_result = analyze_coffee_personality(answers_dict)
        if not llm_result.get("success"):
            logger.error(f"LLM analysis failed: {llm_result.get('error')}")
            raise Exception("LLM 분석 실패")

        return llm_result["result"]["type"]

    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        # 기본 타입 결정 로직
        answers_str = json.dumps(answers_dict)
        if "convenience" in answers_str:
            return "진성 한국인"
        elif "quality" in answers_str:
            return "프리미엄 탐험가"
        elif "health" in answers_str:
            return "헬시 드링커"
        return "라이트 컨슈머"

# 세션 관리 개선
def check_session():
    """세션 상태 확인 및 관리"""
    if "last_activity" not in session:
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        return True

    try:
        last_activity = datetime.fromisoformat(session["last_activity"])
        now = datetime.now(timezone.utc)

        # 30분 이상 활동이 없으면 세션 만료
        if (now - last_activity).total_seconds() > 1800:
            session.clear()
            return False

        # 활동 시간 업데이트
        session["last_activity"] = now.isoformat()
        return True
    except Exception as e:
        # 세션 데이터가 잘못된 경우 세션 초기화
        session.clear()
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        return True

@app.before_request
def before_request():
    """모든 요청 전에 세션 체크"""
    check_session()

# 대신 이렇게 수정
if __name__ == "__main__":
    app.run(debug=True)
