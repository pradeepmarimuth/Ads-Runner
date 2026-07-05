// ─── feed.js — Instagram-style feed ───────────────────────────────────────────
'use strict';

const ROLE_COLORS = {
  Influencer: 'purple',
  AdPublisher: 'cyan',
  Customer: 'emerald',
  Admin: 'pink'
};

// ── Helpers ────────────────────────────────────────────────────────────────────
function roleBadge(role) {
  const c = ROLE_COLORS[role] || 'slate';
  return `<span class="role-badge role-${c}">${role}</span>`;
}

function avatarEl(p, size = 44) {
  const c = ROLE_COLORS[p.role] || 'slate';
  const s = `width:${size}px;height:${size}px;`;
  const cls = 'ig-avatar';
  if (p.avatar_url) {
    return `<img src="${p.avatar_url}" class="${cls} border-${c}" style="${s}" onerror="this.outerHTML=initials('${(p.username||'?')[0]}','${c}',${size})">`;
  }
  return initialsEl((p.username || '?')[0], c, size);
}

function initialsEl(letter, color, size = 44) {
  return `<div class="ig-avatar ig-avatar-init av-${color}" style="width:${size}px;height:${size}px;font-size:${Math.round(size*0.4)}px">${letter.toUpperCase()}</div>`;
}

function timeAgo(ts) {
  const diff = Math.floor((Date.now() - new Date(ts + ' UTC').getTime()) / 1000);
  if (diff < 60)    return `${diff}s`;
  if (diff < 3600)  return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

// ── Reels strip ───────────────────────────────────────────────────────────────
async function loadReels() {
  try {
    const res   = await fetch('/api/posts');
    const posts = await res.json();
    const reels = posts.filter(p => p.reel_url || p.image_url);
    const el    = document.getElementById('reels-strip');
    if (!el || !reels.length) return;

    el.innerHTML = reels.slice(0, 10).map(p => {
      const c = ROLE_COLORS[p.role] || 'slate';
      const thumb = p.reel_url
        ? `<video src="${p.reel_url}" class="reel-thumb" muted loop preload="metadata"></video>`
        : `<img src="${p.image_url}" class="reel-thumb" loading="lazy">`;
      return `
        <button class="reel-item" onclick="openReelModal(${p.id})" title="${escHtml(p.username)}">
          <div class="reel-ring ring-${c}">
            <div class="reel-inner">
              ${p.avatar_url
                ? `<img src="${p.avatar_url}" class="reel-avatar">`
                : `<div class="reel-avatar reel-init av-${c}">${(p.username||'?')[0]}</div>`}
            </div>
          </div>
          <span class="reel-name">${escHtml((p.username||'').split(' ')[0])}</span>
        </button>`;
    }).join('');
  } catch(e) { console.warn('Reels load failed', e); }
}

// ── Reel modal ────────────────────────────────────────────────────────────────
window.openReelModal = function(postId) {
  const modal = document.getElementById('reel-modal');
  if (!modal) return;
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  loadReelContent(postId);
};

window.closeReelModal = function() {
  const modal = document.getElementById('reel-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  const v = document.getElementById('reel-video');
  if (v) { v.pause(); v.src = ''; }
};

async function loadReelContent(postId) {
  try {
    const res  = await fetch('/api/posts');
    const posts = await res.json();
    const p    = posts.find(x => x.id === postId);
    if (!p) return;
    const body = document.getElementById('reel-modal-body');
    const c = ROLE_COLORS[p.role] || 'slate';
    body.innerHTML = `
      <div class="reel-modal-media">
        ${p.reel_url
          ? `<video id="reel-video" src="${p.reel_url}" class="reel-modal-video" controls autoplay loop></video>`
          : p.image_url
            ? `<img src="${p.image_url}" class="reel-modal-img">`
            : `<div class="reel-modal-text">${escHtml(p.content)}</div>`
        }
        <div class="reel-overlay-info">
          <div class="flex items-center gap-2">
            ${p.avatar_url ? `<img src="${p.avatar_url}" class="h-8 w-8 rounded-full object-cover border-2 border-white/30">` : initialsEl((p.username||'?')[0], c, 32)}
            <div>
              <p class="font-bold text-white text-sm">${escHtml(p.username)}</p>
              ${p.content && p.content !== '📸' ? `<p class="text-white/70 text-xs">${escHtml(p.content.substring(0,80))}</p>` : ''}
            </div>
          </div>
        </div>
        <div class="reel-actions-side">
          <button class="reel-action-btn" onclick="likePost(${p.id}, this, true)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-7 w-7"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
            <span class="reel-action-count">${p.likes_count}</span>
          </button>
          <button class="reel-action-btn" onclick="toggleComments(${p.id})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-7 w-7"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            <span class="reel-action-count">${p.comment_count}</span>
          </button>
        </div>
      </div>`;
    // Check liked state
    fetchLikedState(p.id, body.querySelector('.reel-action-btn'));
  } catch(e) { console.warn(e); }
}

// ── Feed ──────────────────────────────────────────────────────────────────────
async function loadFeed() {
  try {
    const res   = await fetch('/api/posts');
    const posts = await res.json();
    const container = document.getElementById('feed-container');
    if (!container) return;

    if (!posts.length) {
      container.innerHTML = `
        <div class="ig-empty">
          <div class="ig-empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="h-12 w-12 text-neutral-600"><rect x="3" y="3" width="18" height="18" rx="3" ry="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
          </div>
          <p class="font-bold text-white mt-3">No posts yet</p>
          <p class="text-neutral-400 text-sm mt-1">Be the first to share!</p>
          <button onclick="openCompose('photo')" class="ig-btn-primary mt-4">Share Your First Post</button>
        </div>`;
      return;
    }

    container.innerHTML = posts.map(p => buildPostCard(p)).join('');

    // After rendering, fetch liked states for all posts
    posts.forEach(p => {
      const btn = document.getElementById(`like-btn-${p.id}`);
      if (btn) fetchLikedState(p.id, btn);
    });

  } catch(e) {
    console.error('Feed error:', e);
    const c = document.getElementById('feed-container');
    if (c) c.innerHTML = `<p class="text-center text-red-400 text-sm py-8">Failed to load feed.</p>`;
  }
}

function buildPostCard(p) {
  const hasImage   = p.image_url && p.image_url.trim();
  const hasReel    = p.reel_url  && p.reel_url.trim();
  const isCaption  = p.content && p.content !== '📸';
  const c = ROLE_COLORS[p.role] || 'slate';

  return `
    <article class="ig-post-card" id="post-${p.id}">

      <!-- ── Header ─────────────────────────────── -->
      <div class="ig-post-header">
        <a href="/profile/${p.user_id}" class="shrink-0">
          ${avatarEl(p, 42)}
        </a>
        <div class="flex-grow min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <a href="/profile/${p.user_id}" class="ig-username">${escHtml(p.username)}</a>
            ${roleBadge(p.role)}
            <span class="ig-dot">•</span>
            <span class="ig-timestamp">${timeAgo(p.timestamp)}</span>
          </div>
          ${p.tagline ? `<p class="ig-tagline truncate">${escHtml(p.tagline)}</p>` : ''}
        </div>
        <button class="ig-more-btn" onclick="showPostMenu(${p.id})" aria-label="More options">
          <svg viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5"><circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/></svg>
        </button>
      </div>

      <!-- ── Media ──────────────────────────────── -->
      ${hasReel ? `
        <div class="ig-media-wrap">
          <video src="${p.reel_url}" class="ig-media" controls muted loop preload="metadata"
            ondblclick="likePost(${p.id}, document.getElementById('like-btn-${p.id}'))"></video>
          <div class="ig-reel-badge"><svg viewBox="0 0 24 24" fill="white" class="h-4 w-4"><path d="M4 6h16M4 10h16M4 14h8m-8 4h4"/></svg> Reel</div>
        </div>` : ''}
      ${hasImage && !hasReel ? `
        <div class="ig-media-wrap">
          <img src="${p.image_url}" class="ig-media" loading="lazy"
            ondblclick="likePost(${p.id}, document.getElementById('like-btn-${p.id}'))"
            onerror="this.parentElement.style.display='none'">
        </div>` : ''}

      <!-- ── Actions ────────────────────────────── -->
      <div class="ig-actions">
        <div class="ig-actions-left">
          <!-- Like -->
          <button id="like-btn-${p.id}" class="ig-action-btn" onclick="likePost(${p.id}, this)" aria-label="Like">
            <svg class="ig-action-icon like-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
          </button>
          <!-- Comment -->
          <button class="ig-action-btn" onclick="toggleComments(${p.id})" aria-label="Comment">
            <svg class="ig-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </button>
          <!-- Share (message) -->
          <a href="/messages/${p.user_id}" class="ig-action-btn" aria-label="Message">
            <svg class="ig-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
          </a>
        </div>
        <!-- Bookmark -->
        <button class="ig-action-btn" onclick="toggleBookmark(this)" aria-label="Save">
          <svg class="ig-action-icon bookmark-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
          </svg>
        </button>
      </div>

      <!-- ── Like count ──────────────────────────── -->
      <div class="ig-like-row">
        <span id="likes-count-${p.id}" class="ig-like-count">${p.likes_count.toLocaleString()} ${p.likes_count === 1 ? 'like' : 'likes'}</span>
      </div>

      <!-- ── Caption ────────────────────────────── -->
      ${isCaption ? `
        <div class="ig-caption">
          <a href="/profile/${p.user_id}" class="ig-caption-user">${escHtml(p.username)}</a>
          <span class="ig-caption-text">${escHtml(p.content)}</span>
        </div>` : ''}

      <!-- ── Comment preview ────────────────────── -->
      <button class="ig-view-comments" onclick="toggleComments(${p.id})">
        ${p.comment_count > 0 ? `View all ${p.comment_count} comment${p.comment_count > 1 ? 's' : ''}` : 'Add a comment...'}
      </button>

      <!-- ── Inline Comments Panel ──────────────── -->
      <div id="comments-panel-${p.id}" class="ig-comments-panel hidden">
        <div id="comments-list-${p.id}" class="ig-comments-list">
          <div class="ig-comments-loading">Loading comments...</div>
        </div>
        <div class="ig-comment-input-row">
          <div class="ig-comment-avatar-wrap">
            <!-- current user avatar injected via window.CURRENT_USER -->
          </div>
          <input type="text" id="comment-input-${p.id}"
            placeholder="Add a comment..."
            class="ig-comment-input"
            onkeydown="if(event.key==='Enter')submitComment(${p.id})"
          >
          <button onclick="submitComment(${p.id})" class="ig-comment-post-btn">Post</button>
        </div>
      </div>

    </article>`;
}

// ── Like toggle ────────────────────────────────────────────────────────────────
window.likePost = async function(postId, btn) {
  if (!btn) btn = document.getElementById(`like-btn-${postId}`);
  if (!btn) return;
  const wasLiked = btn.classList.contains('liked');
  // Optimistic UI
  toggleLikedUI(btn, !wasLiked);
  updateLikeCount(postId, !wasLiked);

  try {
    const res  = await fetch(`/api/posts/${postId}/like`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) { toggleLikedUI(btn, wasLiked); return; }
    const countEl = document.getElementById(`likes-count-${postId}`);
    if (countEl) {
      const n = data.likes_count;
      countEl.textContent = `${n.toLocaleString()} ${n === 1 ? 'like' : 'likes'}`;
    }
    toggleLikedUI(btn, data.liked);
  } catch(e) {
    toggleLikedUI(btn, wasLiked); // revert on error
  }
};

function toggleLikedUI(btn, liked) {
  const icon = btn.querySelector('.like-icon');
  if (liked) {
    btn.classList.add('liked');
    if (icon) { icon.setAttribute('fill', '#ef4444'); icon.setAttribute('stroke', '#ef4444'); }
    btn.classList.add('like-pop');
    setTimeout(() => btn.classList.remove('like-pop'), 300);
  } else {
    btn.classList.remove('liked');
    if (icon) { icon.setAttribute('fill', 'none'); icon.setAttribute('stroke', 'currentColor'); }
  }
}

function updateLikeCount(postId, increment) {
  const el = document.getElementById(`likes-count-${postId}`);
  if (!el) return;
  const current = parseInt(el.textContent) || 0;
  const n = increment ? current + 1 : Math.max(0, current - 1);
  el.textContent = `${n.toLocaleString()} ${n === 1 ? 'like' : 'likes'}`;
}

async function fetchLikedState(postId, btn) {
  if (!btn) btn = document.getElementById(`like-btn-${postId}`);
  if (!btn) return;
  try {
    const res  = await fetch(`/api/posts/${postId}/liked`);
    const data = await res.json();
    toggleLikedUI(btn, data.liked);
  } catch(e) {}
}

// ── Bookmark toggle ────────────────────────────────────────────────────────────
window.toggleBookmark = function(btn) {
  const icon = btn.querySelector('.bookmark-icon');
  const saved = btn.classList.toggle('bookmarked');
  if (icon) {
    icon.setAttribute('fill', saved ? 'currentColor' : 'none');
  }
};

// ── Comments ──────────────────────────────────────────────────────────────────
window.toggleComments = async function(postId) {
  const panel = document.getElementById(`comments-panel-${postId}`);
  if (!panel) return;
  const isHidden = panel.classList.contains('hidden');
  panel.classList.toggle('hidden', !isHidden);
  if (isHidden) {
    await loadComments(postId);
    const input = document.getElementById(`comment-input-${postId}`);
    if (input) input.focus();
  }
};

async function loadComments(postId) {
  const list = document.getElementById(`comments-list-${postId}`);
  if (!list) return;
  try {
    const res      = await fetch(`/api/posts/${postId}/comments`);
    const comments = await res.json();
    if (!comments.length) {
      list.innerHTML = `<p class="ig-no-comments">No comments yet. Be the first!</p>`;
      return;
    }
    list.innerHTML = comments.map(c => buildCommentEl(c)).join('');
  } catch(e) {
    list.innerHTML = `<p class="text-red-400 text-xs px-4 py-2">Failed to load comments.</p>`;
  }
}

function buildCommentEl(c) {
  const col = ROLE_COLORS[c.role] || 'slate';
  const av = c.avatar_url
    ? `<img src="${c.avatar_url}" class="ig-comment-avatar border-${col}">`
    : `<div class="ig-comment-avatar ig-comment-av-init av-${col}">${(c.username||'?')[0]}</div>`;
  return `
    <div class="ig-comment-item">
      <a href="/profile/${c.user_id}" class="shrink-0">${av}</a>
      <div class="flex-grow min-w-0">
        <span class="ig-comment-user">${escHtml(c.username)}</span>
        <span class="ig-comment-body">${escHtml(c.content)}</span>
        <div class="ig-comment-meta">${timeAgo(c.timestamp)}</div>
      </div>
    </div>`;
}

window.submitComment = async function(postId) {
  const input = document.getElementById(`comment-input-${postId}`);
  if (!input) return;
  const content = input.value.trim();
  if (!content) { input.focus(); return; }
  input.disabled = true;

  try {
    const res  = await fetch(`/api/posts/${postId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    const data = await res.json();
    if (!res.ok) { alert(data.message); input.disabled = false; return; }
    input.value = '';
    // Append new comment without full reload
    const list = document.getElementById(`comments-list-${postId}`);
    if (list) {
      const noC = list.querySelector('.ig-no-comments');
      if (noC) noC.remove();
      const el = document.createElement('div');
      el.innerHTML = buildCommentEl(data);
      list.appendChild(el.firstElementChild);
      list.scrollTop = list.scrollHeight;
    }
    // Update comment count in preview button
    const viewBtn = document.querySelector(`#post-${postId} .ig-view-comments`);
    if (viewBtn) {
      const match = viewBtn.textContent.match(/\d+/);
      const n = match ? parseInt(match[0]) + 1 : 1;
      viewBtn.textContent = `View all ${n} comment${n > 1 ? 's' : ''}`;
    }
  } catch(e) { alert('Failed to post comment.'); }
  input.disabled = false;
  input.focus();
};

// ── Suggestions sidebar ───────────────────────────────────────────────────────
async function loadSuggestions() {
  try {
    const res   = await fetch('/api/network');
    const users = await res.json();
    const el    = document.getElementById('suggestions-list');
    if (!el) return;
    const list = users.filter(u => !u.conn_status).slice(0, 5);
    if (!list.length) { el.innerHTML = `<p class="text-xs text-neutral-500">No suggestions yet.</p>`; return; }
    el.innerHTML = list.map(u => {
      const c = ROLE_COLORS[u.role] || 'slate';
      const av = u.avatar_url
        ? `<img src="${u.avatar_url}" class="ig-sugg-avatar border-${c}">`
        : `<div class="ig-sugg-avatar ig-sugg-init av-${c}">${(u.name||'?')[0]}</div>`;
      return `
        <div class="ig-sugg-item">
          <a href="/profile/${u.id}" class="shrink-0">${av}</a>
          <div class="min-w-0 flex-grow">
            <a href="/profile/${u.id}" class="ig-sugg-name truncate block">${escHtml(u.name)}</a>
            <p class="ig-sugg-role truncate">${u.tagline || u.role}</p>
          </div>
          <button onclick="followUser(${u.id}, this)" class="ig-follow-btn">Follow</button>
        </div>`;
    }).join('');
  } catch(e) {}
}

window.followUser = async function(uid, btn) {
  try {
    await fetch(`/api/connect/${uid}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'request' })
    });
    btn.textContent = 'Requested';
    btn.disabled = true;
    btn.classList.add('requested');
  } catch(e) {}
};

// ── Post menu (stub) ──────────────────────────────────────────────────────────
window.showPostMenu = function(postId) {
  // Placeholder — can extend with report/copy link etc.
};

// ── Init ──────────────────────────────────────────────────────────────────────
loadReels();
loadFeed();
loadSuggestions();
