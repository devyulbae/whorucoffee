import os
import sys

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
import json
import logging
from dotenv import load_dotenv
from prompts.coffee_personality_prompt import COFFEE_TYPES
from utils.llm_handler import analyze_coffee_personality

# 로깅 설정
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# Flask 앱 생성
flask_app = Flask(__name__, 
    static_folder='../static',    
    template_folder='../templates'
)

# 기본 설정
flask_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# 유형 이름 매핑
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

@flask_app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return jsonify(error=str(e)), 500

@flask_app.route('/question')
def question():
    return render_template("question.html")

@flask_app.route('/analyze', methods=['POST'])
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
        coffee_type = result.get('type', '')
        
        if not coffee_type:
            return render_template('error.html', 
                               error_message="커피 유형을 결정할 수 없습니다.")
        
        template_name = TYPE_MAPPING.get(coffee_type, 'default')
        result['image'] = f"{template_name}.jpeg"
        
        template_path = f'results/{template_name}.html'
        return render_template(template_path, type_info=result)
            
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        return render_template('error.html', 
                           error_message=f"결과를 처리하는 중 오류가 발생했습니다: {str(e)}")

@flask_app.route('/result')
def result():
    type_name = request.args.get("type", "진성 한국인")
    template = f"results/{TYPE_MAPPING.get(type_name, 'korean_authentic')}.html"
    return render_template(template, type_info=COFFEE_TYPES[type_name], type=type_name)

# Vercel Serverless Function handler
def app(environ, start_response):
    return flask_app(environ, start_response)

# Local development server
if __name__ == "__main__":
    flask_app.run(debug=True)