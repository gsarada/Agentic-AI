const words = [
  'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix',
  'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf', 'vingt'
];

const scoreEl = document.getElementById('score');
const streakEl = document.getElementById('streak');
const levelEl = document.getElementById('level');
const timeEl = document.getElementById('time');
const numberEl = document.getElementById('number');
const wordHintEl = document.getElementById('wordHint');
const choicesEl = document.getElementById('choices');
const feedbackEl = document.getElementById('feedback');
const startBtn = document.getElementById('startBtn');

let score = 0;
let streak = 0;
let level = 1;
let current = 0;
let timer = null;
let timeLeft = 0;
let active = false;

function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}

function setFeedback(text, kind = '') {
  feedbackEl.textContent = text;
  feedbackEl.className = `feedback ${kind}`;
}

function updateHUD() {
  scoreEl.textContent = score;
  streakEl.textContent = streak;
  levelEl.textContent = level;
  timeEl.textContent = timeLeft;
}

function stopTimer() {
  clearInterval(timer);
  timer = null;
}

function nextRound() {
  current = Math.floor(Math.random() * 20) + 1;
  const correctWord = words[current - 1];
  const pool = [correctWord];
  while (pool.length < 4) {
    const candidate = words[Math.floor(Math.random() * words.length)];
    if (!pool.includes(candidate)) pool.push(candidate);
  }
  shuffle(pool);

  numberEl.textContent = current;
  wordHintEl.textContent = `“${correctWord}”`;
  choicesEl.innerHTML = '';

  pool.forEach(word => {
    const button = document.createElement('button');
    button.className = 'choice';
    button.textContent = word;
    button.addEventListener('click', () => choose(word, button, correctWord));
    choicesEl.appendChild(button);
  });

  timeLeft = Math.max(4, 8 - Math.floor((level - 1) / 2));
  updateHUD();
  stopTimer();
  timer = setInterval(() => {
    timeLeft -= 1;
    updateHUD();
    if (timeLeft <= 0) {
      stopTimer();
      active = false;
      streak = 0;
      updateHUD();
      setFeedback(`Too slow — ${current} is ${correctWord}.`, 'bad');
      startBtn.textContent = 'Play again';
      lockChoices(true);
    }
  }, 1000);
}

function lockChoices(lock) {
  document.querySelectorAll('.choice').forEach(btn => { btn.disabled = lock; });
}

function choose(word, button, correctWord) {
  if (!active) return;
  stopTimer();
  lockChoices(true);
  const buttons = [...document.querySelectorAll('.choice')];
  if (word === correctWord) {
    button.classList.add('correct');
    score += 10 + level;
    streak += 1;
    if (streak % 3 === 0) level += 1;
    setFeedback(`Correct! ${current} = ${correctWord}.`, 'good');
  } else {
    button.classList.add('wrong');
    buttons.find(btn => btn.textContent === correctWord)?.classList.add('correct');
    streak = 0;
    score = Math.max(0, score - 3);
    setFeedback(`Not quite — ${current} is ${correctWord}.`, 'bad');
  }
  updateHUD();
  startBtn.textContent = 'Next round';
  setTimeout(() => {
    if (active) {
      lockChoices(false);
      nextRound();
    }
  }, 800);
}

function startGame() {
  score = 0;
  streak = 0;
  level = 1;
  active = true;
  startBtn.textContent = 'Restart';
  lockChoices(false);
  setFeedback('Listen for the clue and pick the French word.', '');
  updateHUD();
  nextRound();
}

startBtn.addEventListener('click', startGame);
updateHUD();
setFeedback('Press Start to begin.');
