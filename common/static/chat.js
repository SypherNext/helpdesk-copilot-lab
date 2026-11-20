// The chat page. User text is always added with textContent. The assistant's
// answer arrives as HTML built by the server (render.py), so whether it is
// safe depends on the server, which is the point of lesson 11.
const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('message');

function addBubble(kind, text) {
  const bubble = document.createElement('div');
  bubble.className = `bubble ${kind}`;
  bubble.textContent = text;
  messages.appendChild(bubble);
  return bubble;
}

function describeToolCalls(toolCalls) {
  return toolCalls.map((call) => `${call.name}(${JSON.stringify(call.arguments)})`).join(', ');
}

function showAnswer(data) {
  const bubble = addBubble('bot', '');
  bubble.innerHTML = data.html;
  if (data.blocked) addBubble('note', `Blocked by a check: ${data.blocked}`);
  if (data.tool_calls.length) addBubble('note', `Tools used: ${describeToolCalls(data.tool_calls)}`);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addBubble('user', text);
  input.value = '';
  const waiting = addBubble('note', 'Thinking...');
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  });
  waiting.remove();
  if (!response.ok) {
    addBubble('note', `The server answered ${response.status}.`);
    return;
  }
  showAnswer(await response.json());
  messages.scrollTop = messages.scrollHeight;
});

fetch('/api/info').then((response) => response.json()).then((info) => {
  const banner = document.getElementById('banner');
  banner.textContent = info.app === 'vulnerable' ? 'VULNERABLE practice app' : 'Fixed app';
  banner.classList.add(info.app);
  document.getElementById('customer').textContent = `Signed in as ${info.customer} (${info.customer_id})`;
});
