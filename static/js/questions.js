const questions = [
    {
        title: "주로 커피를 어디서 마시나요?",
        subtitle: "해당하는 항목을 모두 선택해주세요.",
        options: ["프랜차이즈 카페", "로스터리/스페셜티 카페", "집", "회사/학교", "테이크아웃"],
        values: ["franchise", "specialty", "home", "work", "takeout"]
    },
    {
        title: "가장 자주 마시는 커피 종류는?",
        subtitle: "자주 마시는 메뉴를 모두 선택해주세요.",
        options: ["아메리카노", "에스프레소", "라떼/카푸치노", "콜드브루", "핸드드립", "캡슐/인스턴트"],
        values: ["americano", "espresso", "latte", "coldbrew", "handdrip", "instant"]
    },
    {
        title: "선호하는 원두 특성은?",
        subtitle: "선호하는 특성을 모두 선택해주세요.",
        options: ["깔끔한 산미", "진한 바디감", "균형잡힌 맛", "고소/달콤함", "강렬한 쓴맛", "특별히 없음"],
        values: ["acidity", "body", "balance", "sweet", "bitter", "none"]
    },
    {
        title: "하루 평균 커피 소비량은?",
        subtitle: "가장 가까운 것을 선택해주세요.",
        options: ["1잔 이하", "2~3잔", "4잔 이상"],
        values: ["low", "medium", "high"]
    },
    {
        title: "커피 구입 시 가장 중요하게 생각하는 요소는?",
        subtitle: "중요하게 생각하는 요소를 모두 선택해주세요.",
        options: ["원두 품질", "가성비", "브랜드 신뢰도", "접근성/편의성", "건강/영양", "분위기/트렌드"],
        values: ["quality", "value", "brand", "convenience", "health", "trend"]
    },
    {
        title: "새로운 커피를 접할 때 당신은?",
        subtitle: "가장 가까운 것을 선택해주세요.",
        options: ["적극적으로 새로운 메뉴를 시도한다", "리뷰를 보고 신중하게 선택한다", "익숙한 메뉴를 고수한다"],
        values: ["adventurous", "careful", "conservative"]
    },
    {
        title: "커피를 마시는 주된 목적은?",
        subtitle: "가장 중요한 이유를 선택해주세요.",
        options: ["에너지 충전", "커피 맛과 향 즐기기", "휴식/힐링", "사교/비즈니스", "습관적으로"],
        values: ["energy", "taste", "relaxation", "social", "habit"]
    },
    {
        title: "선호하는 로스팅 정도는?",
        subtitle: "가장 선호하는 것을 선택해주세요.",
        options: ["라이트 로스트 (산미와 과일향)", "미디엄 로스트 (균형잡힌 맛)", "다크 로스트 (진하고 쓴맛)", "특별히 고려하지 않음"],
        values: ["light", "medium", "dark", "none"]
    }
]; 