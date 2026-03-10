// ── Flash auto-dismiss ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(f => {
            f.style.opacity = '0';
            f.style.transition = 'opacity 0.4s';
            setTimeout(() => f.remove(), 400);
        });
    }, 4000);
});

// ── Chart.js Global Config ──────────────────────────────────────────────────
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#8892a4';
    Chart.defaults.font.family = "'Outfit', sans-serif";

    // Admin – Category Donut Chart
    if (document.getElementById('categoryChart') && window.categoryData) {
        new Chart(document.getElementById('categoryChart').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: window.categoryData.map(d => d.label),
                datasets: [{
                    data: window.categoryData.map(d => d.count),
                    backgroundColor: [
                        'rgba(79,172,254,0.75)',
                        'rgba(0,242,254,0.75)',
                        'rgba(176,106,179,0.75)',
                        'rgba(246,79,139,0.75)',
                        'rgba(0,230,118,0.75)'
                    ],
                    borderColor: 'rgba(255,255,255,0.08)',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                cutout: '68%'
            }
        });
    }

    // Reports – Score Progression Line Chart
    if (document.getElementById('progressChart') && window.progressData) {
        new Chart(document.getElementById('progressChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: window.progressData.map(d => d.date),
                datasets: [{
                    label: 'Score',
                    data: window.progressData.map(d => d.score),
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0,242,254,0.08)',
                    borderWidth: 3,
                    tension: 0.45,
                    fill: true,
                    pointBackgroundColor: '#4facfe',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 9
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

// ── Quiz Execution Logic ────────────────────────────────────────────────────
if (document.getElementById('questionText') && window.quizData) {

    const TIMER_MAX    = 30;        // 30 seconds limit per AOQRWE question
    const CIRCUMFER   = 182.2;      // 2π × r=29

    const quizState = {
        questions:     window.quizData,
        currentIndex:  0,
        answers:       {},           // { question_id: "A"|"B"|"C"|"D" }
        timeLeft:      TIMER_MAX,
        timerInterval: null,
        startTime:     Date.now()
    };

    window._quizAnswers = quizState.answers;

    // DOM refs
    const elQNum     = document.getElementById('currentQNum');
    const elQText    = document.getElementById('questionText');
    const elGrid     = document.getElementById('optionsGrid');
    const elProgress = document.getElementById('progressFill');
    const elPrev     = document.getElementById('prevBtn');
    const elNext     = document.getElementById('nextBtn');
    const elSubmit   = document.getElementById('submitBtn');
    const elTimeText = document.getElementById('timeText');
    const elTimerSVG = document.getElementById('timerSVG');
    const elTimerCircle = document.getElementById('timerCircle');
    const elAnswered = document.getElementById('answeredCount');
    const elUnanswered = document.getElementById('unansweredCount');

    // ── Timer ────────────────────────────────────────────────────────────────
    function startTimer() {
        clearInterval(quizState.timerInterval);
        quizState.timeLeft = TIMER_MAX;
        updateTimerUI();

        quizState.timerInterval = setInterval(() => {
            quizState.timeLeft--;
            updateTimerUI();

            if (quizState.timeLeft <= 0) {
                clearInterval(quizState.timerInterval);
                autoAdvance();
            }
        }, 1000);
    }

    function updateTimerUI() {
        const t = quizState.timeLeft;
        const fraction = t / TIMER_MAX;
        const offset   = CIRCUMFER - fraction * CIRCUMFER;

        if (elTimerCircle) elTimerCircle.style.strokeDashoffset = offset;
        if (elTimeText) elTimeText.textContent = t;

        // Colour transitions
        if (elTimerSVG) {
            elTimerSVG.className  = 'circular-timer';
            if (t <= 5) {
                elTimerSVG.className += ' danger';
                if (elTimeText) elTimeText.className = 'time-text danger';
            } else if (t <= 15) {
                elTimerSVG.className += ' warn';
                if (elTimeText) elTimeText.className = 'time-text warn';
            } else {
                if (elTimeText) elTimeText.className = 'time-text';
            }
        }
    }

    function autoAdvance() {
        if (quizState.currentIndex < quizState.questions.length - 1) {
            quizState.currentIndex++;
            renderQuestion();
            startTimer();
        } else {
            window.submitQuiz(); 
        }
    }

    // ── Render ────────────────────────────────────────────────────────────────
    function renderQuestion() {
        const q = quizState.questions[quizState.currentIndex];

        if (elQNum) elQNum.textContent = quizState.currentIndex + 1;
        if (elQText) elQText.textContent = q.question_text;

        // Progress bar
        const pct = (quizState.currentIndex / quizState.questions.length) * 100;
        if (elProgress) elProgress.style.width = `${pct}%`;

        // Answered counter
        updateStats();

        // Nav buttons
        if (elPrev) elPrev.disabled = quizState.currentIndex === 0;
        const isLast = quizState.currentIndex === quizState.questions.length - 1;
        if (elNext) elNext.classList.toggle('hidden', isLast);
        if (elSubmit) elSubmit.classList.toggle('hidden', !isLast);

        // Update dot grid
        document.querySelectorAll('.q-dot').forEach((dot, idx) => {
            dot.classList.remove('active');
            if(idx === quizState.currentIndex) dot.classList.add('active');
            const qid = quizState.questions[idx].id;
            if(quizState.answers[qid]) dot.classList.add('answered');
        });

        // Option TILES
        const letters = ['A', 'B', 'C', 'D'];
        const opts = [q.option_a, q.option_b, q.option_c, q.option_d];
        const saved = quizState.answers[q.id];

        if (elGrid) {
            elGrid.innerHTML = '';
            opts.forEach((text, i) => {
                const key  = letters[i];
                const tile = document.createElement('button');
                tile.className = `option-tile${saved === key ? ' selected' : ''}`;
                tile.id = `opt-${key}`;
                tile.innerHTML = `
                    <span class="tile-letter">${key}</span>
                    <span class="tile-text">${text}</span>
                `;
                tile.addEventListener('click', () => selectOption(q.id, key));
                elGrid.appendChild(tile);
            });
        }
    }

    function updateStats() {
        const answeredCount = Object.keys(quizState.answers).length;
        if (elAnswered) elAnswered.textContent = answeredCount;
        if (elUnanswered) elUnanswered.textContent = quizState.questions.length - answeredCount;
    }

    function selectOption(qId, key) {
        quizState.answers[qId] = key;
        document.querySelectorAll('.option-tile').forEach(t => t.classList.remove('selected'));
        const picked = document.getElementById(`opt-${key}`);
        if (picked) picked.classList.add('selected');
        
        // Mark dot answered
        const dot = document.getElementById(`q-dot-${quizState.currentIndex}`);
        if(dot) dot.classList.add('answered');
        
        updateStats();
    }

    // ── Navigation ────────────────────────────────────────────────────────────
    window.nextQuestion = () => {
        if (quizState.currentIndex < quizState.questions.length - 1) {
            quizState.currentIndex++;
            renderQuestion();
            startTimer();
        }
    };

    window.prevQuestion = () => {
        if (quizState.currentIndex > 0) {
            quizState.currentIndex--;
            renderQuestion();
            startTimer();
        }
    };

    window.jumpToQuestion = (index) => {
        quizState.currentIndex = index;
        renderQuestion();
        startTimer();
    };

    // ── Submit ────────────────────────────────────────────────────────────────
    window.submitQuiz = () => {
        const modal = document.getElementById('submitModal');
        if (modal) modal.classList.add('hidden');

        clearInterval(quizState.timerInterval);

        let correct = 0;
        const answersPayload = [];

        quizState.questions.forEach(q => {
            const selected = quizState.answers[q.id] || null;
            if (selected === q.correct_option) correct++;
            answersPayload.push({ question_id: q.id, selected });
        });

        const total     = quizState.questions.length;
        const incorrect = total - correct;
        const timeSpent = Math.round((Date.now() - quizState.startTime) / 1000);

        const btn = document.getElementById('confirmSubmitBtn');
        if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing AOQRWE...'; }

        fetch('/quiz/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                score: correct, total, correct, incorrect,
                time_spent: timeSpent,
                category: document.body.dataset.category || 'General',
                answers: answersPayload
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') window.location.href = '/reports';
        })
        .catch(err => {
            alert('AOQRWE Network Error. Please contact admin.');
            if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-check"></i> Retry Submit'; }
            console.error(err);
        });
    };

    // ── Bootstrap ─────────────────────────────────────────────────────────────
    renderQuestion();
    startTimer();
}
