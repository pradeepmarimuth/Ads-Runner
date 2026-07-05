// network.js — Discovery page for Influencers and Ad Publishers

const ROLE_COLORS = {Influencer:'purple',AdPublisher:'cyan',Customer:'emerald',Admin:'pink'};

function avatarEl(u) {
  if (u.avatar_url) return `<img src="${u.avatar_url}" class="h-16 w-16 rounded-full object-cover border-2 border-slate-700 mx-auto" onerror="this.style.display='none'">`;
  const c = ROLE_COLORS[u.role] || 'slate';
  return `<div class="h-16 w-16 rounded-full bg-gradient-to-tr from-${c}-600 to-${c}-400 flex items-center justify-center text-white font-bold text-2xl mx-auto">${(u.name||'?')[0]}</div>`;
}

function roleBadge(u) {
  const c = ROLE_COLORS[u.role] || 'slate';
  return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-mono border bg-${c}-950/40 text-${c}-300 border-${c}-500/20">${u.role}</span>`;
}

function connectBtn(u) {
  if (u.conn_status === 'accepted') {
    return `<button onclick="doConnect(${u.id},'cancel',this)" class="flex-1 py-2 bg-emerald-950/30 border border-emerald-500/25 text-emerald-300 rounded-lg text-xs font-semibold transition-all hover:border-emerald-500/50">✓ Connected</button>`;
  }
  if (u.conn_status === 'pending' && u.conn_is_mine) {
    return `<button onclick="doConnect(${u.id},'cancel',this)" class="flex-1 py-2 bg-slate-800 border border-slate-700 text-slate-400 rounded-lg text-xs font-semibold transition-all">Pending...</button>`;
  }
  if (u.conn_status === 'pending' && !u.conn_is_mine) {
    return `<button onclick="doConnect(${u.id},'accept',this)" class="flex-1 py-2 bg-purple-900/30 border border-purple-500/25 text-purple-300 rounded-lg text-xs font-semibold transition-all hover:border-purple-500/50">Accept</button>`;
  }
  return `<button onclick="doConnect(${u.id},'request',this)" class="flex-1 py-2 bg-slate-800 border border-slate-700 hover:border-purple-500/30 text-slate-400 hover:text-purple-400 rounded-lg text-xs font-semibold transition-all">+ Connect</button>`;
}

async function loadNetwork(role) {
  // Update tab styles
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.className = 'tab-btn px-5 py-2 rounded-xl text-sm font-semibold border border-slate-700 text-slate-400 hover:border-cyan-500/30 hover:text-cyan-400 transition-all';
  });
  const activeTab = document.getElementById(`tab-${role}`);
  if (activeTab) activeTab.className = 'tab-btn px-5 py-2 rounded-xl text-sm font-semibold border border-cyan-500/30 bg-slate-800 text-cyan-400 transition-all';

  const grid = document.getElementById('network-grid');
  grid.innerHTML = '<div class="col-span-full"><div class="animate-pulse grid grid-cols-3 gap-5"><div class="h-52 bg-slate-800/50 rounded-2xl"></div><div class="h-52 bg-slate-800/50 rounded-2xl"></div><div class="h-52 bg-slate-800/50 rounded-2xl"></div></div></div>';

  try {
    const url = role === 'all' ? '/api/network' : `/api/network?role=${role}`;
    const res  = await fetch(url);
    const users = await res.json();

    if (!users.length) {
      grid.innerHTML = `<div class="col-span-full text-center py-16 text-slate-500">
        <p class="text-sm font-mono">No users found in this category yet.</p>
      </div>`;
      return;
    }

    grid.innerHTML = users.map(u => `
      <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 hover:-translate-y-1 transition-all backdrop-blur-sm shadow-xl flex flex-col items-center text-center gap-3">
        <a href="/profile/${u.id}" class="block">
          ${avatarEl(u)}
        </a>
        <div class="min-w-0 w-full">
          <a href="/profile/${u.id}" class="block font-bold text-white hover:text-cyan-400 transition-colors text-sm truncate">${u.name}</a>
          <p class="text-slate-400 text-xs mt-0.5 truncate">${u.tagline || ''}</p>
          <div class="flex justify-center mt-2">${roleBadge(u)}</div>
          ${u.location ? `<p class="text-slate-600 text-[10px] mt-1">📍 ${u.location}</p>` : ''}
          <p class="text-slate-600 text-[10px] mt-0.5">${u.post_count} posts</p>
        </div>
        <div class="flex gap-2 w-full mt-2">
          ${connectBtn(u)}
          <a href="/messages/${u.id}" class="flex-1 py-2 bg-gradient-to-r from-cyan-900/40 to-blue-900/40 border border-cyan-500/20 hover:border-cyan-500/40 text-cyan-400 rounded-lg text-xs font-semibold transition-all text-center">💬 Msg</a>
        </div>
      </div>
    `).join('');
  } catch(e) {
    grid.innerHTML = `<div class="col-span-full text-center py-16 text-red-400 text-sm font-mono">Failed to load network.</div>`;
  }
}

async function doConnect(uid, action, btn) {
  try {
    const res  = await fetch(`/api/connect/${uid}`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({action})
    });
    const data = await res.json();
    // Reload network to refresh states
    const activeRole = document.querySelector('.tab-btn[class*="text-cyan-400"]')?.id?.replace('tab-','') || 'all';
    await loadNetwork(activeRole);
  } catch(e) {}
}

// Load all on init
loadNetwork('all');
