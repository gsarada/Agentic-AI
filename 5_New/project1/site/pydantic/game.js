const rounds = [
  { english: 'bread', french: 'le pain' },
  { english: 'cheese', french: 'le fromage' },
  { english: 'apple', french: 'la pomme' },
  { english: 'water', french: "l'eau" },
  { english: 'milk', french: 'le lait' },
  { english: 'coffee', french: 'le café' },
  { english: 'tea', french: 'le thé' },
  { english: 'juice', french: 'le jus' },
  { english: 'soup', french: 'la soupe' },
  { english: 'butter', french: 'le beurre' },
  { english: 'egg', french: "l'œuf" },
  { english: 'sandwich', french: 'le sandwich' }
];

const els = {
  score: document.getElementById('score'),
  streak: document.getElementById('streak'),
  level: document.getElementById('level'),
  prompt: document.getElementById('englishPrompt'),
  choices: document.getElementById('choices'),
  feedback: document.getElementById('feedback'),
  nextBtn: document.getElementById('nextBtn')
};

let score = 0, streak = 0, level = 1, locked = false, current = null;

function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
function setStats() { els.score.textContent = score; els.streak.textContent = streak; els.level.textContent = level; }

function newRound() {
  locked = false;
  els.nextBtn.disabled = true;
  els.feedback.textContent = 'Choose the correct French translation.';
  const pool = shuffle(rounds);
  current = pool[0];
  const choices = shuffle([current.french, pool[1].french, pool[2].french, pool[3].french]);
  els.prompt.textContent = current.english;
  els.choices.innerHTML = '';
  choices.forEach(choice => {
    const btn = document.createElement('button');
    btn.className = 'choice';
    btn.type = 'button';
    btn.textContent = choice;
    btn.addEventListener('click', () => choose(btn, choice));
    els.choices.appendChild(btn);
  });
}

function choose(btn, choice) {
  if (locked) return;
  locked = true;
  const buttons = [...els.choices.querySelectorAll('button')];
  const correct = choice === current.french;
  buttons.forEach(b => {
    b.disabled = true;
    if (b.textContent === current.french) b.classList.add('correct');
  });
  if (correct) {
    score += 10 * level;
    streak += 1;
    if (streak % 3 === 0) level += 1;
    els.feedback.textContent = `Correct! ${current.english} = ${current.french}.`;
    btn.classList.add('correct');
  } else {
    streak = 0;
    score = Math.max(0, score - 3);
    els.feedback.textContent = `Not quite. ${current.english} is ${current.french}.`;
    btn.classList.add('wrong');
  }
  setStats();
  els.nextBtn.disabled = false;
}

els.nextBtn.addEventListener('click', newRound);
setStats();
newRound();
