class QuestionManager {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.totalQuestions = questions.length;
        
        // 저장된 답변 확인
        const savedAnswers = this.loadAnswers();
        const savedProgress = this.loadProgress();
        
        if (savedAnswers && Object.keys(savedAnswers).length > 0) {
            this.showRecoveryAlert();
        } else {
            this.initializeQuestions();
        }
        
        // 생성자에서 beforeunload 핸들러를 인스턴스 메서드로 저장
        this.beforeUnloadHandler = (e) => {
            if (Object.keys(this.answers).length > 0) {
                e.preventDefault();
                e.returnValue = '';
            }
        };
        window.addEventListener('beforeunload', this.beforeUnloadHandler);
    }
    
    showRecoveryAlert() {
        const alert = document.getElementById('recovery-alert');
        alert.style.display = 'block';
    }
    
    continueProgress() {
        this.answers = this.loadAnswers() || {};
        this.currentQuestion = this.loadProgress() || 0;
        document.getElementById('recovery-alert').style.display = 'none';
        this.initializeQuestions();
    }
    
    startNew() {
        this.clearProgress();
        document.getElementById('recovery-alert').style.display = 'none';
        this.initializeQuestions();
    }
    
    initializeQuestions() {
        this.initializeEventListeners();
        this.showQuestion(this.currentQuestion);
    }
    
    // 진행상황 저장
    saveProgress() {
        localStorage.setItem('currentQuestion', this.currentQuestion);
        localStorage.setItem('answers', JSON.stringify(this.answers));
    }
    
    // 진행상황 불러오기
    loadProgress() {
        return parseInt(localStorage.getItem('currentQuestion')) || 0;
    }
    
    // 답변 불러오기
    loadAnswers() {
        const savedAnswers = localStorage.getItem('answers');
        return savedAnswers ? JSON.parse(savedAnswers) : {};
    }
    
    // 진행상황 초기화
    clearProgress() {
        localStorage.removeItem('currentQuestion');
        localStorage.removeItem('answers');
    }
    
    initializeEventListeners() {
        document.getElementById('nextBtn').addEventListener('click', () => this.nextQuestion());
        document.getElementById('prevBtn').addEventListener('click', () => this.prevQuestion());
    }
    
    showQuestion(index) {
        const question = questions[index];
        const container = document.querySelector('.question-card');
        
        container.innerHTML = this.generateQuestionHTML(question);
        this.updateProgress();
        this.updateNavigationButtons();
        
        // 이전 답변이 있다면 선택 상태 복원
        if (this.answers[question.title]) {
            this.answers[question.title].forEach(answer => {
                const option = container.querySelector(`[data-value="${answer}"]`);
                if (option) option.classList.add('selected');
            });
        }
        
        // 옵션 클릭 이벤트 설정
        container.querySelectorAll('.option-item').forEach(option => {
            option.addEventListener('click', () => this.toggleOption(option, question));
        });
    }
    
    generateQuestionHTML(question) {
        return `
            <h2 class="question-title">${question.title}</h2>
            ${question.subtitle ? `<p class="question-subtitle">${question.subtitle}</p>` : ''}
            <div class="options-grid">
                ${question.options.map((option, index) => `
                    <div class="option-item" data-value="${question.values[index]}">
                        ${option}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    toggleOption(option, question) {
        if (!this.answers[question.title]) {
            this.answers[question.title] = [];
        }
        
        const value = option.dataset.value;
        
        if (question.subtitle?.includes('모두 선택')) {
            // 다중 선택 가능
            if (option.classList.contains('selected')) {
                option.classList.remove('selected');
                this.answers[question.title] = this.answers[question.title]
                    .filter(item => item !== value);
            } else {
                option.classList.add('selected');
                if (!this.answers[question.title].includes(value)) {
                    this.answers[question.title].push(value);
                }
            }
        } else {
            // 단일 선택만 가능
            const allOptions = document.querySelectorAll('.option-item');
            allOptions.forEach(item => {
                item.classList.remove('selected');
            });
            option.classList.add('selected');
            this.answers[question.title] = [value];
        }
        
        this.saveProgress();
    }
    
    updateProgress() {
        const progress = ((this.currentQuestion + 1) / this.totalQuestions) * 100;
        document.querySelector('.progress-fill').style.width = `${progress}%`;
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        prevBtn.style.display = this.currentQuestion === 0 ? 'none' : 'block';
        nextBtn.textContent = this.currentQuestion === this.totalQuestions - 1 ? '결과 보기' : '다음';
    }
    
    nextQuestion() {
        const currentAnswers = this.answers[questions[this.currentQuestion].title];
        if (!currentAnswers || currentAnswers.length === 0) {
            alert('답변을 선택해주세요.');
            return;
        }
        
        if (this.currentQuestion === this.totalQuestions - 1) {
            // 마지막 질문이면 결과 제출 전 저장 데이터 삭제
            this.clearProgress();
            this.submitAnswers();
        } else {
            this.currentQuestion++;
            this.saveProgress();
            this.showQuestion(this.currentQuestion);
        }
    }
    
    prevQuestion() {
        if (this.currentQuestion > 0) {
            this.currentQuestion--;
            this.saveProgress();
            this.showQuestion(this.currentQuestion);
        }
    }
    
    submitAnswers() {
        // 페이지 이탈 전 localStorage 초기화
        this.clearProgress();
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/analyze';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'answers';
        input.value = JSON.stringify(this.answers);
        
        form.appendChild(input);
        document.body.appendChild(form);
        
        // beforeunload 이벤트 리스너 제거
        window.removeEventListener('beforeunload', this.beforeUnloadHandler);
        
        form.submit();
    }
}

// 페이지 로드 시
document.addEventListener('DOMContentLoaded', () => {
    const manager = new QuestionManager();
    
    // 복구 관련 버튼 이벤트 리스너 추가
    document.querySelector('.recovery-actions .btn-primary')
        ?.addEventListener('click', () => manager.continueProgress());
    document.querySelector('.recovery-actions .btn-outline')
        ?.addEventListener('click', () => manager.startNew());
}); 