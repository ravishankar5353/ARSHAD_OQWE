// Utility: Flash fadeout
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(f => {
            f.style.opacity = '0';
            setTimeout(() => f.remove(), 300);
        });
    }, 4000);
});

// ------------- CHART.JS RENDERING -------------
// Global Chart.js Font config
Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#a0aab2';
Chart.defaults.font.family = "'Outfit', sans-serif";

// 1. Admin Category Pie Chart
if (document.getElementById('categoryChart') && window.categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: window.categoryData.map(d => d.label),
            datasets: [{
                data: window.categoryData.map(d => d.count),
                backgroundColor: [
                    'rgba(79, 172, 254, 0.7)',
                    'rgba(0, 242, 254, 0.7)',
                    'rgba(176, 106, 179, 0.7)',
                    'rgba(69, 104, 220, 0.7)'
                ],
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            cutout: '70%'
        }
    });
}

// 2. User/Reports Progress Line Chart
if (document.getElementById('progressChart') && window.progressData) {
    const ctx = document.getElementById('progressChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: window.progressData.map(d => d.date),
            datasets: [{
                label: 'Assessment Score',
                data: window.progressData.map(d => d.score),
                borderColor: '#00f2fe',
                backgroundColor: 'rgba(0, 242, 254, 0.1)',
                borderWidth: 3,
                tension: 0.4, // Smooth curves
                fill: true,
                pointBackgroundColor: '#4facfe',
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ------------- QUIZ EXECUTION LOGIC -------------
if (document.getElementById('questionText') && window.quizData) {
    
    const quizState = {
        questions: window.quizData,
        currentIndex: 0,
        answers: {}, // map of { question_id : "A/B/C/D" }
        timeLimit: 60,
        timeLeft: 60,
        timerInterval: null
    };

    // DOM Elements
    const elQNum = document.getElementById('currentQNum');
    const elQText = document.getElementById('questionText');
    const elGrid = document.getElementById('optionsGrid');
    const elProgress = document.getElementById('progressFill');
    const elPrev = document.getElementById('prevBtn');
    const elNext = document.getElementById('nextBtn');
    const elSubmit = document.getElementById('submitBtn');
    
    const elTimeText = document.getElementById('timeText');
    const elTimerCircle = document.getElementById('timerCircle');

    function initQuiz() {
        if(quizState.questions.length === 0) return;
        renderQuestion();
        startTimer();
    }

    function renderQuestion() {
        const q = quizState.questions[quizState.currentIndex];
        
        elQNum.textContent = quizState.currentIndex + 1;
        elQText.textContent = q.question_text;
        
        // Progress bar
        const pct = ((quizState.currentIndex) / quizState.questions.length) * 100;
        elProgress.style.width = `${pct}%`;

        // Nav Buttons
        elPrev.disabled = quizState.currentIndex === 0;
        
        if (quizState.currentIndex === quizState.questions.length - 1) {
            elNext.classList.add('hidden');
            elSubmit.classList.remove('hidden');
        } else {
            elNext.classList.remove('hidden');
            elSubmit.classList.add('hidden');
        }

        // Render Options
        elGrid.innerHTML = '';
        const options = [
            { key: 'A', text: q.option_a },
            { key: 'B', text: q.option_b },
            { key: 'C', text: q.option_c },
            { key: 'D', text: q.option_d }
        ];

        const savedAns = quizState.answers[q.id];

        options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = `option-btn ${savedAns === opt.key ? 'selected' : ''}`;
            btn.textContent = `${opt.key}. ${opt.text}`;
            btn.onclick = () => selectOption(q.id, opt.key);
            elGrid.appendChild(btn);
        });
    }

    function selectOption(qId, key) {
        quizState.answers[qId] = key;
        renderQuestion(); // re-render to highlight selection
    }

    // Export navigation methods to global scope for HTML onclick
    window.nextQuestion = () => {
        if(quizState.currentIndex < quizState.questions.length - 1) {
            quizState.currentIndex++;
            renderQuestion();
        }
    };

    window.prevQuestion = () => {
        if(quizState.currentIndex > 0) {
            quizState.currentIndex--;
            renderQuestion();
        }
    };

    function startTimer() {
        quizState.timerInterval = setInterval(() => {
            quizState.timeLeft--;
            elTimeText.textContent = quizState.timeLeft;
            
            // Circular animation calculation (157 is empirical circumference of r=25 SVG)
            const fraction = quizState.timeLeft / quizState.timeLimit;
            const offset = 157 - (fraction * 157);
            elTimerCircle.style.strokeDashoffset = offset;
            
            if (quizState.timeLeft <= 10) {
                elTimeText.classList.add('text-danger');
            }

            if (quizState.timeLeft <= 0) {
                clearInterval(quizState.timerInterval);
                window.submitQuiz(true); // Auto submit trigger
            }
        }, 1000);
    }

    window.submitQuiz = (isAuto = false) => {
        if (!isAuto && !confirm("Finalize answers and submit sequence?")) return;
        
        clearInterval(quizState.timerInterval);
        
        // Evaluate logic
        let correctCount = 0;
        quizState.questions.forEach(q => {
            if (quizState.answers[q.id] === q.correct_option) {
                correctCount++;
            }
        });
        
        const total = quizState.questions.length;
        const incorrectCount = total - correctCount;
        const timeSpent = quizState.timeLimit - quizState.timeLeft;

        const payload = {
            score: correctCount,
            total: total,
            correct: correctCount,
            incorrect: incorrectCount,
            time_spent: timeSpent
        };

        // Post to backend API
        fetch('/quiz/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(res => res.json())
          .then(data => {
            if(data.status === 'success') {
                window.location.href = "/reports"; // redirect to analytical breakdown
            }
        }).catch(err => {
            alert("Error saving result.");
            console.error(err);
        });
    };

    // Bootstrap
    initQuiz();
}
