// profile.js — Load profile posts and handle connect actions

async function loadProfilePosts() {
  const el = document.getElementById('profile-posts');
  if (!el) return;
  try {
    const res   = await fetch('/api/posts');
    const posts = (await res.json()).filter(p => p.user_id === PROFILE_ID);

    if (!posts.length) {
      el.innerHTML = `<p class="text-sm text-slate-500 font-mono text-center py-4">No posts yet.</p>`;
      return;
    }

    el.innerHTML = posts.slice(0, 6).map(p => `
      <div class="p-4 bg-slate-950/50 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors">
        <p class="text-sm text-slate-300 leading-relaxed">${escHtml(p.content)}</p>
        ${p.image_url ? `<div class="mt-2 rounded-lg overflow-hidden max-h-48"><img src="${p.image_url}" class="w-full object-cover max-h-48" loading="lazy" onerror="this.parentElement.style.display='none'"></div>` : ''}
        <div class="flex items-center gap-4 mt-3 pt-2 border-t border-slate-800/50">
          <span class="text-[11px] text-slate-600">${formatTime(p.timestamp)}</span>
          <span class="text-[11px] text-slate-600 flex items-center gap-1">❤️ ${p.likes_count}</span>
        </div>
      </div>
    `).join('');
  } catch(e) {
    el.innerHTML = `<p class="text-xs text-red-400 font-mono">Failed to load posts.</p>`;
  }
}

async function handleConnect(action) {
  if (typeof PROFILE_ID === 'undefined') return;
  try {
    const res  = await fetch(`/api/connect/${PROFILE_ID}`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({action})
    });
    if (res.ok) location.reload();
  } catch(e) {}
}

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'});
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

loadProfilePosts();
