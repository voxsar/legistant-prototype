const form = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const messages = document.getElementById('messages');
const historyList = document.getElementById('history');

let history = [];

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  addMessage('user', question);
  questionInput.value = '';

  const response = await fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ question })
  });

  const data = await response.json();
  addMessage('assistant', data.answer);

  // Save to local history
  history.push({ question, answer: data.answer });
  updateHistory();
});

function addMessage(role, content) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.textContent = content;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

function updateHistory() {
  historyList.innerHTML = '';
  history.forEach((item, index) => {
    const li = document.createElement('li');
    li.textContent = item.question;
    li.onclick = () => showHistory(index);
    historyList.appendChild(li);
  });
}

function showHistory(index) {
  messages.innerHTML = '';
  addMessage('user', history[index].question);
  addMessage('assistant', history[index].answer);
}
