/**
 * chatbot.js — AI chatbot widget.
 * Floating button + chat window with history.
 */

const Chatbot = (() => {
  let isOpen = false;
  let conversationHistory = [];

  // Welcome message
  const WELCOME_MSG = "👋 Hi! I'm Adarsh's AI assistant. Ask me about his skills, projects, education, or how to get in touch!";

  function init() {
    _render();
    _bindEvents();
    // Show welcome message after short delay
    setTimeout(() => _appendBotMessage(WELCOME_MSG), 800);
  }

  function _render() {
    const html = `
      <!-- Chatbot Bubble -->
      <button class="chat-bubble-btn" id="chat-bubble-btn" aria-label="Open chat assistant" title="Chat with AI Assistant">
        <span id="chat-bubble-icon">💬</span>
      </button>

      <!-- Chat Window -->
      <div class="chat-window" id="chat-window" role="dialog" aria-label="AI Chat Assistant">
        <div class="chat-header">
          <div class="chat-header-info">
            <div class="chat-avatar">🤖</div>
            <div>
              <div class="chat-title">AI Assistant</div>
              <div class="chat-status">● Online — asks about Adarsh's work</div>
            </div>
          </div>
          <button class="chat-close" id="chat-close-btn" aria-label="Close chat">✕</button>
        </div>

        <div class="chat-messages" id="chat-messages"></div>

        <div class="chat-input-area">
          <textarea
            class="chat-input"
            id="chat-input"
            placeholder="Ask me anything..."
            rows="1"
            aria-label="Chat message input"
          ></textarea>
          <button class="chat-send-btn" id="chat-send-btn" aria-label="Send message">➤</button>
        </div>
      </div>
    `;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    document.body.appendChild(wrapper);
  }

  function _bindEvents() {
    // Toggle button
    document.getElementById('chat-bubble-btn').addEventListener('click', _toggle);
    document.getElementById('chat-close-btn').addEventListener('click', _close);

    // Send button
    document.getElementById('chat-send-btn').addEventListener('click', _sendMessage);

    // Enter to send (Shift+Enter for newline)
    const input = document.getElementById('chat-input');
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        _sendMessage();
      }
    });

    // Auto-resize textarea
    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      const win = document.getElementById('chat-window');
      const btn = document.getElementById('chat-bubble-btn');
      if (isOpen && win && !win.contains(e.target) && !btn.contains(e.target)) {
        _close();
      }
    });
  }

  function _toggle() {
    isOpen ? _close() : _open();
  }

  function _open() {
    isOpen = true;
    document.getElementById('chat-window').classList.add('open');
    document.getElementById('chat-bubble-icon').textContent = '✕';
    document.getElementById('chat-input').focus();
  }

  function _close() {
    isOpen = false;
    document.getElementById('chat-window').classList.remove('open');
    document.getElementById('chat-bubble-icon').textContent = '💬';
  }

  async function _sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Display user message
    _appendUserMessage(message);
    input.value = '';
    input.style.height = 'auto';

    // Add to history
    conversationHistory.push({ role: 'user', content: message });

    // Show typing indicator
    const typingId = _showTyping();

    try {
      const data = await API.chat.send(message, conversationHistory.slice(-6));
      const response = data.response || "I didn't catch that, can you rephrase?";

      // Add bot response to history
      conversationHistory.push({ role: 'assistant', content: response });

      // Remove typing and show response
      _hideTyping(typingId);
      _appendBotMessage(response);

    } catch (err) {
      _hideTyping(typingId);
      _appendBotMessage("Sorry, I'm having trouble connecting right now. Please try again! 🔄");
    }
  }

  function _appendUserMessage(text) {
    _appendMessage(text, 'user');
  }

  function _appendBotMessage(text) {
    _appendMessage(text, 'bot');
  }

  function _appendMessage(text, type) {
    const container = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.className = `chat-msg ${type}`;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
  }

  function _showTyping() {
    const container = document.getElementById('chat-messages');
    const id = 'typing-' + Date.now();
    const el = document.createElement('div');
    el.id = id;
    el.className = 'typing-indicator';
    el.innerHTML = `
      <div class="typing-text">Adarsh Typing</div>
      <div class="typing-dots">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
    return id;
  }

  function _hideTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  return { init };
})();

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', Chatbot.init);
