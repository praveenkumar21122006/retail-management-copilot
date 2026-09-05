const answerArea = document.querySelector('#answer-area');
const questionInput = document.querySelector('#question-input');
const askButton = document.querySelector('#ask-button');

function renderDashboard(data) {
  document.querySelector('.sync-card strong').textContent = 'Data synced';
  document.querySelector('.sync-card span:not(.status-dot)').textContent = data.syncedAt;
  document.querySelector('.copilot-foot').innerHTML = `<span class="source-dot"></span> Grounded in <strong>${data.stores} stores</strong> · ${data.products} products`;
}

function renderAnswer(answer, message) {
  if (!answer) {
    answerArea.innerHTML = `<div class="answer-content"><span class="answer-label">No confident answer</span><h3>I don't have enough data for that yet.</h3><p>${message || 'The available retail data does not support this question.'}</p><div class="recommendation"><strong>Try asking</strong>Which products might run out, what is overstocked, or how did Matcha Starter Kit perform this month?</div><p class="assumption">No estimate made. The available data does not support this question.</p></div>`;
    return;
  }
  const rows = answer.rows.map(([label, value]) => `<tr><td>${label}</td><td>${value}</td></tr>`).join('');
  answerArea.innerHTML = `<div class="answer-content"><span class="answer-label">Evidence-backed answer</span><h3>${answer.title}</h3><p>${answer.body}</p><table class="answer-table"><thead><tr><th>Measure</th><th>Value</th></tr></thead><tbody>${rows}</tbody></table><div class="recommendation"><strong>Recommended next step</strong>${answer.recommendation}</div><p class="assumption">${answer.assumption}</p></div>`;
}

async function loadDashboard() {
  try {
    const response = await fetch('/api/dashboard');
    if (!response.ok) throw new Error('Dashboard request failed');
    renderDashboard(await response.json());
  } catch {
    document.querySelector('.sync-card strong').textContent = 'Backend offline';
    document.querySelector('.sync-card span:not(.status-dot)').textContent = 'Start server.py on port 3000';
  }
}

async function ask(question) {
  const value = question || questionInput.value.trim();
  if (!value) return;
  questionInput.value = value;
  askButton.classList.add('asking');
  try {
    const response = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: value }) });
    if (!response.ok) throw new Error('Question request failed');
    const result = await response.json();
    renderAnswer(result.answer, result.message);
  } catch {
    renderAnswer(null, 'The Python backend is not reachable. Start it with `python3 server.py` and try again.');
  } finally {
    askButton.classList.remove('asking');
  }
}

document.querySelectorAll('[data-question]').forEach((button) => button.addEventListener('click', () => ask(button.dataset.question)));
askButton.addEventListener('click', () => ask());
questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); ask(); }
});
document.querySelector('.refresh-btn').addEventListener('click', (event) => {
  loadDashboard();
  event.currentTarget.textContent = '✓';
  setTimeout(() => { event.currentTarget.textContent = '↻'; }, 1000);
});
loadDashboard();
