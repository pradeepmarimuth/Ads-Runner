// messages.js — Chat inbox + real-time polling chat thread

const ROLE_COLORS = {Influencer:'purple',AdPublisher:'cyan',Customer:'emerald',Admin:'pink'};
let pollInterval = null;

function avatarEl(partner) {
  if (partner.partner_avatar)
    return `<img src="${partner.partner_avatar}" class="h-10 w-10 rounded-full object-cover border border-slate-700 shrink-0" onerror="this.style.display='none'">`;
  const c = ROLE_COLORS[partner.partner_role] || 'slate';
  return `<div class="h-10 w-10 rounded-full bg-gradient-to-tr from-${c}-600 to-${c}-400 flex items-center justify-center text-white font-bold shrink-0">${(partner.partner_name||'?')[0]}</div>`;
}

async function loadInbox() {
  const el = document.getElementById('inbox-list');
  if (!el) return;
  try {
    const res    = await fetch('/api/messages/inbox');
    const convos = await res.json();

    if (!convos.length) {
      el.innerHTML = `<div class="p-6 text-center">
        <p class="text-xs text-slate-600 font-mono">No messages yet.<br>Start a conversation from the <a href="/network" class="text-cyan-400 hover:underline">Network</a>.</p>
      </div>`;
      return;
    }

    el.innerHTML = convos.map(c => `
      <a href="/messages/${c.partner_id}" class="flex items-center gap-3 p-4 hover:bg-slate-800/40 transition-colors ${CHAT_USER_ID === c.partner_id ? 'bg-slate-800/60 border-l-2 border-cyan-500' : ''}">
        ${avatarEl(c)}
        <div class="min-w-0 flex-grow">
          <div class="flex justify-between items-center">
            <p class="text-sm font-bold text-white truncate">${c.partner_name}</p>
            <span class="text-[10px] text-slate-600 shrink-0 ml-2">${c.last_ts}</span>
          </div>
          <p class="text-xs text-slate-500 truncate mt-0.5">${c.last_message || '...'}</p>
        </div>
        ${c.unread > 0 ? `<span class="shrink-0 h-5 min-w-[20px] px-1.5 bg-cyan-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">${c.unread}</span>` : ''}
      </a>
    `).join('');
  } catch(e) {}
}

async function loadMessages() {
  if (!CHAT_USER_ID) return;
  const container = document.getElementById('chat-messages');
  if (!container) return;

  try {
    const res   = await fetch(`/api/messages/${CHAT_USER_ID}`);
    const msgs  = await res.json();
    const wasAtBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 50;

    if (!msgs.length) {
      container.innerHTML = `<div class="flex justify-center py-8">
        <span class="text-[11px] font-mono text-slate-600 px-4 py-2 bg-slate-900/60 rounded-full border border-slate-800">Start the conversation below 👇</span>
      </div>`;
      return;
    }

    container.innerHTML = msgs.map(m => {
      const isMe = m.sender_id === MY_ID;
      return `
        <div class="flex ${isMe ? 'justify-end' : 'justify-start'}">
          <div class="msg-bubble px-4 py-3 rounded-2xl text-sm leading-relaxed shadow
            ${isMe
              ? 'bg-gradient-to-br from-cyan-700 to-blue-700 text-white rounded-br-sm'
              : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-bl-sm'}">
            <p>${escHtml(m.content)}</p>
            <p class="text-[9px] mt-1 opacity-60 ${isMe ? 'text-right' : ''}">${m.timestamp.slice(11,16)}</p>
          </div>
        </div>`;
    }).join('');

    // Auto-scroll to bottom only if already near bottom
    if (wasAtBottom || container.scrollTop === 0) {
      container.scrollTop = container.scrollHeight;
    }

    // Refresh inbox badge counts
    loadInbox();
  } catch(e) {}
}

async function sendMessage() {
  const input   = document.getElementById('msg-input');
  const content = input?.value?.trim();
  if (!content || !CHAT_USER_ID) return;

  try {
    const res = await fetch(`/api/messages/${CHAT_USER_ID}`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({content})
    });
    if (res.ok) {
      input.value = '';
      await loadMessages();
    }
  } catch(e) {}
}

function handleMsgKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Init
loadInbox();
if (CHAT_USER_ID) {
  loadMessages();
  // Poll every 3 seconds for new messages
  pollInterval = setInterval(loadMessages, 3000);
}
