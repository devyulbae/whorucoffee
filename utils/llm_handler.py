import os
import json
import google.generativeai as genai
from typing import Dict, List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Gemini API 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def analyze_coffee_personality(answers: Dict[str, List[str]]) -> Dict:
    """
    사용자의 답변을 분석하여 커피 성향을 판단합니다.
    """
    # 답변을 문자열로 포맷팅
    formatted_answers = "\n".join(
        [
            f"질문: {question}\n답변: {', '.join(answer)}"
            for question, answer in answers.items()
        ]
    )

    prompt = f"""
당신은 커피 전문가입니다. 사용자의 답변을 분석하여 가장 적합한 커피 성향을 판단해주세요.

다음 중 하나의 타입으로만 분류해야 합니다:
- 진성 한국인
- 유러피안 커피 애호가
- 프리미엄 탐험가
- 가성비 실속파
- 카페인 러버
- 소셜 커피러
- 헬시 드링커
- 라이트 컨슈머

사용자의 답변:
{formatted_answers}

다음 JSON 형식으로 정확하게 응답해주세요:
{{
    "type": "위 타입 중 하나",
    "characteristics": [
        "사용자의 특징 1",
        "사용자의 특징 2",
        "사용자의 특징 3"
    ],
    "recommendations": [
        "맞춤 추천 1",
        "맞춤 추천 2",
        "맞춤 추천 3"
    ]
}}
"""

    try:
        print("Prompt:", prompt)  # 디버깅용

        # 동기 방식으로 API 호출
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        response_text = response.text

        print("Raw response:", response_text)  # 디버깅용

        # 응답에서 JSON 부분만 추출
        try:
            # JSON 시작/끝 위치 찾기
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]

            result = json.loads(json_str)

            # 필수 필드 검증
            if not all(
                k in result for k in ["type", "characteristics", "recommendations"]
            ):
                raise ValueError("Missing required fields in response")

            # 타입 검증
            valid_types = [
                "진성 한국인",
                "유러피안 커피 애호가",
                "프리미엄 탐험가",
                "가성비 실속파",
                "카페인 러버",
                "소셜 커피러",
                "헬시 드링커",
                "라이트 컨슈머",
            ]
            if result["type"] not in valid_types:
                raise ValueError(f"Invalid type: {result['type']}")

            print("Parsed result:", result)  # 디버깅용

            return {"success": True, "result": result}

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            return {"success": False, "error": "응답을 파싱할 수 없습니다."}

    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return {"success": False, "error": str(e)}
