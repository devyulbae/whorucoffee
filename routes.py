from .prompts.coffee_personality_prompt import COFFEE_TYPES
import logging
from .models.survey_log import SurveyLog
from . import db
import json
from flask import jsonify, request, redirect, url_for, session, flash
from sqlalchemy import func
from datetime import datetime, timedelta
from functools import wraps
from .config import Config
from .utils.security import verify_password

# 로깅 설정
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def get_default_type(answers):
    """LLM 실패시 기본 타입을 결정하는 함수"""
    # 간단한 로직으로 기본 타입 결정
    if "convenience" in str(answers):
        return COFFEE_TYPES["진성 한국인"]
    elif "quality" in str(answers):
        return COFFEE_TYPES["프리미엄 탐험가"]
    elif "health" in str(answers):
        return COFFEE_TYPES["헬시 드링커"]
    else:
        return COFFEE_TYPES["라이트 컨슈머"]


@app.route("/analyze", methods=["POST"])
def analyze_coffee_personality():
    try:
        answers = request.form.get("answers")
        if not answers:
            raise ValueError("No answers provided")

        answers_dict = json.loads(answers)

        # LLM 호출 시도
        try:
            llm_result = analyze_with_llm(answers_dict)
            if llm_result["success"]:
                coffee_type = llm_result["result"]["type"]
                type_info = COFFEE_TYPES[coffee_type]

                # 응답 로깅
                survey_log = SurveyLog(answers=answers_dict, result_type=coffee_type)
                db.session.add(survey_log)
                db.session.commit()

            else:
                raise Exception(llm_result["error"])

        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            type_info = get_default_type(answers)

        return render_template(
            "results/base_result.html", type_info=type_info, error_message=None
        )

    except Exception as e:
        logger.error(f"General Error: {str(e)}")
        return render_template(
            "error.html",
            error_message="죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
        )


@app.route("/admin/stats")
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
            SurveyLog.created_at >= datetime.utcnow() - timedelta(days=1)
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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("관리자 로그인이 필요합니다.", "error")
            return redirect(url_for("admin_login", next=request.url))
        if "admin_last_activity" in session:
            # 마지막 활동으로부터 1시간 경과시 자동 로그아웃
            last_activity = session["admin_last_activity"]
            if (datetime.utcnow() - last_activity).total_seconds() > 3600:
                session.clear()
                flash("세션이 만료되었습니다. 다시 로그인해주세요.", "error")
                return redirect(url_for("admin_login"))
        session["admin_last_activity"] = datetime.utcnow()
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_stats"))

    if request.method == "POST":
        password = request.form.get("password")
        stored_hash = Config.ADMIN_PASSWORD_HASH

        if not stored_hash:
            logger.error("Admin password hash not configured")
            flash("관리자 계정이 설정되지 않았습니다.", "error")
            return render_template("admin/login.html")

        try:
            if verify_password(stored_hash, password):
                session["is_admin"] = True
                session["admin_last_activity"] = datetime.utcnow()
                session.permanent = True  # 브라우저 종료시까지 세션 유지

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


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("index"))
