# WhoRUCoffee (후얼유유커피)

당신의 커피 성향을 알아보는 테스트

## 프로젝트 소개

WhoRUCoffee는 사용자의 커피 취향과 라이프스타일을 분석하여 8가지 커피 성향 중 하나를 추천해주는 웹 서비스입니다. OpenAI의 GPT를 활용하여 사용자의 응답을 분석하고, 개인화된 결과를 제공합니다.

### 커피 성향 유형
- 진성 한국인
- 유러피안 커피 애호가
- 프리미엄 탐험가
- 가성비 실속파
- 카페인 러버
- 소셜 커피러
- 헬시 드링커
- 라이트 컨슈머

## 기술 스택

### Frontend
- HTML5
- CSS3
- JavaScript
- Flask Templates

### Backend
- Python 3.9+
- Flask 3.0.0
- OpenAI API

### 배포
- Vercel

## 주요 기능

1. **맞춤형 질문**
   - 사용자의 커피 취향
   - 라이프스타일
   - 소비 패턴
   - 카페 이용 습관

2. **AI 기반 분석**
   - OpenAI GPT 모델 활용
   - 응답 패턴 분석
   - 성향 매칭 알고리즘

3. **결과 페이지**
   - 개인화된 커피 성향 프로필
   - 상세한 특징 설명
   - 맞춤형 추천사항
   - 애니메이션 효과

## 프로젝트 구조
whorubean/
├── api/
│ └── index.py # 메인 애플리케이션 로직
├── static/
│ ├── css/
│ │ ├── style.css # 공통 스타일
│ │ └── result.css # 결과 페이지 스타일
│ ├── img/
│ │ └── types/ # 성향별 이미지
│ └── js/
│ └── script.js # 프론트엔드 로직
├── templates/
│ ├── base.html # 기본 템플릿
│ ├── index.html # 메인 페이지
│ ├── question.html # 질문 페이지
│ └── results/ # 결과 템플릿
├── requirements.txt # 의존성 패키지
└── vercel.json # Vercel 설정

## 설치 및 실행 방법

1. 저장소 클론
``` bash
git clone https://github.com/username/whorubean.git
cd whorubean
```

2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate # Linux/Mac
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
```

.env 파일 생성
OPENAI_API_KEY=your_api_key
FLASK_SECRET_KEY=your_secret_key

5. 개발 서버 실행
```bash
flask run
```

6. 배포
```bash
vercel --prod
```

## 커밋 규칙

- 커밋 메시지는 영어로 작성
- 커밋 메시지는 최대한 한 줄로 작성

## 기여 방법
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스
MIT License

