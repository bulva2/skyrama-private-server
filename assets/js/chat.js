let chatBox, toggle, sendBtn, input, messages, charCount;
let collapsed = false;
let lastMessageTime = 0;
const RATE_LIMIT_MS = 5000; // 2 seconds

/**
 * Append a message to the chat UI
 * @param {string} text - Content
 * @param {string} who - Sender username
 * @param {string} created_at - Timestamp
 */
function appendMsg(text, who, created_at) {
    const el = document.createElement('div');
    el.className = 'mb-1';
    el.style.fontSize = '10px';

    const timestamp = document.createElement('timestamp');
    timestamp.textContent = '[' + created_at + '] ';
    el.appendChild(timestamp);

    const username = document.createElement('username');
    if (who === 'System') {
        username.style.color = 'red';
    } else if (who === 'You') {
        username.style.color = 'blue';
    }
    username.textContent = who + ': ';
    el.appendChild(username);

    const span = document.createElement('span');
    span.textContent = text;
    span.style.fontWeight = 'normal';
    el.appendChild(span);

    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
}

async function send() {
    const txt = input.value.trim();
    if (!txt) return;

    // Just a backup to ease up the server
    const now = Date.now();
    if (now - lastMessageTime < RATE_LIMIT_MS) {
        const remaining = Math.ceil((RATE_LIMIT_MS - (now - lastMessageTime)) / 1000);
        appendMsg(`Slow down manager! Wait ${remaining}s before sending another message!`, 'System', 'Now');
        return;
    }

    lastMessageTime = now;

    const dateNow = new Date();
    const timestamp = `${dateNow.getDate()}.${dateNow.getMonth() + 1}. ${dateNow.getHours()}:${dateNow.getMinutes().toString().padStart(2, '0')}`;
    
    appendMsg(txt, 'You', timestamp);
    input.value = '';
    charCount.textContent = '0/200';

    try {
        const response = await fetch('/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: txt })
        });

        
        if (response.ok) {
            await loadMessages();
        } else {
            const error = await response.json();
            console.error('[send] Error response:', error);
            appendMsg(error.message || 'Error sending message.', 'System', timestamp);
        }
    } catch (error) {
        console.error('[send] Catch error:', error);
        appendMsg('Failed to send message.', 'System', timestamp);
    }
}

async function loadMessages() {
    try {
        const response = await fetch('/chat/messages');
        if (!response.ok) {
            throw new Error('Failed to load messages');
        }
        const data = await response.json();
        if (Array.isArray(data.messages)) {
            messages.innerHTML = '';
            data.messages.forEach(msg => {
                appendMsg(msg.text, msg.user, msg.created_at);
            });
        }
    } catch (error) {
        console.error('Failed to load chat messages:', error);
    }
}

function toggleChat() {
    collapsed = !collapsed;
    if (collapsed) {
        chatBox.style.height = '48px';
        chatBox.style.width = '150px';
        messages.style.display = 'none';
        sendBtn.style.display = 'none';
        input.style.display = 'none';
        charCount.style.display = 'none';

    } else {
        chatBox.style.height = '';
        chatBox.style.width = '320px';
        messages.style.display = 'block';
        sendBtn.style.display = 'block';
        input.style.display = 'block';
        charCount.style.display = 'block';
    }
}

function initChat() {
    chatBox = document.getElementById('chatbox');
    toggle = document.getElementById('chatToggle');
    sendBtn = document.getElementById('chatSend');
    input = document.getElementById('chatInput');
    messages = document.getElementById('chatMessages');
    charCount = document.getElementById('charCount');
    
    if (!chatBox) return;
    
    toggle.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', send);
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') send();
    });
    input.addEventListener('input', function () {
        const len = input.value.length;
        charCount.textContent = len + '/200';
        charCount.style.color = len > 150 ? '#ff6b6b' : '#666';
    });

    loadMessages();
    setInterval(loadMessages, 10000);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChat);
} else {
    initChat();
}
