// active tab indicator
let activeTab = 'users';

document.addEventListener('DOMContentLoaded', () => {
  fetchAdminTelemetry();
});

function switchTab(tabId) {
  activeTab = tabId;
  
  // Hide all tab contents
  const contents = document.querySelectorAll('.tab-content');
  contents.forEach(content => content.classList.add('hidden'));
  
  // Show target tab content
  const targetContent = document.getElementById(`tab-${tabId}-content`);
  if (targetContent) targetContent.classList.remove('hidden');

  // Clear focus state on all nav buttons
  const buttons = document.querySelectorAll('aside nav button');
  buttons.forEach(btn => {
    btn.className = "w-full flex items-center space-x-3 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800/40 border border-transparent transition-all duration-200";
  });

  // Highlight active button
  const activeBtn = document.getElementById(`btn-${tabId}`);
  if (activeBtn) {
    activeBtn.className = "w-full flex items-center space-x-3 px-4 py-2.5 rounded-xl text-sm font-semibold border border-pink-500/20 bg-slate-800/85 text-pink-400 transition-all duration-200";
  }
}

async function fetchAdminTelemetry() {
  const refreshBtn = document.getElementById('refresh-admin-btn');
  const refreshIcon = document.getElementById('refresh-icon');

  if (refreshIcon) refreshIcon.classList.add('animate-spin');
  if (refreshBtn) refreshBtn.disabled = true;

  try {
    const response = await fetch('/api/admin/data');
    if (!response.ok) throw new Error('Failed to load admin directories');

    const data = await response.json();
    
    renderUsers(data.users || []);
    renderGlobalCampaigns(data.campaigns || []);
    renderGlobalLogs(data.logs || []);

  } catch (err) {
    console.error('Admin loading failed:', err);
    alert('Access Denied or Database connection lost.');
  } finally {
    if (refreshIcon) refreshIcon.classList.remove('animate-spin');
    if (refreshBtn) refreshBtn.disabled = false;
  }
}

function renderUsers(users) {
  const tbody = document.getElementById('users-table-body');
  if (!tbody) return;

  if (users.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500 font-mono">No nodes registered.</td></tr>`;
    return;
  }

  tbody.innerHTML = users.map(user => `
    <tr class="hover:bg-slate-800/20 transition-colors">
      <td class="py-4 px-6 font-mono text-xs text-slate-400">Node-#00${user.id}</td>
      <td class="py-4 px-6 font-semibold text-slate-200">${user.name}</td>
      <td class="py-4 px-6 text-slate-450">${user.email}</td>
      <td class="py-4 px-6">
        <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-mono border ${
          user.role === 'Admin' 
            ? 'bg-pink-950/40 text-pink-300 border-pink-500/20' 
            : 'bg-cyan-950/40 text-cyan-300 border-cyan-500/20'
        }">${user.role}</span>
      </td>
    </tr>
  `).join('');
}

function renderGlobalCampaigns(campaigns) {
  const tbody = document.getElementById('campaigns-table-body');
  if (!tbody) return;

  if (campaigns.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-500 font-mono">No active campaigns.</td></tr>`;
    return;
  }

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  tbody.innerHTML = campaigns.map(c => `
    <tr class="hover:bg-slate-800/20 transition-colors">
      <td class="py-4 px-6 font-mono text-xs text-slate-400">Node-#00${c.user_id}</td>
      <td class="py-4 px-6 font-semibold text-slate-200">${c.name}</td>
      <td class="py-4 px-6 font-mono text-xs text-slate-400">${c.platform}</td>
      <td class="py-4 px-6 text-right font-mono text-cyan-400">${c.clicks}</td>
      <td class="py-4 px-6 text-right font-mono text-pink-400">${c.conversions}</td>
      <td class="py-4 px-6 text-right font-mono text-slate-450">${formatCurrency(c.spend)}</td>
      <td class="py-4 px-6 text-right font-mono text-emerald-400 font-bold">${formatCurrency(c.revenue)}</td>
    </tr>
  `).join('');
}

function renderGlobalLogs(logs) {
  const tbody = document.getElementById('logs-table-body');
  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-500 font-mono">No scraper link analytics logs found.</td></tr>`;
    return;
  }

  tbody.innerHTML = logs.map(log => {
    let resultObj = log.analysis_result || {};
    if (typeof resultObj === 'string') {
      try { resultObj = json.parse(resultObj); } catch(e) {}
    }

    const ctr = resultObj.predicted_ctr || 'N/A';
    const eng = resultObj.estimated_engagement || 'N/A';
    const hashtags = resultObj.hashtags ? resultObj.hashtags.join(', ') : 'N/A';

    return `
      <tr class="hover:bg-slate-800/20 transition-colors">
        <td class="py-4 px-6 font-mono text-xs text-slate-400">Node-#00${log.user_id}</td>
        <td class="py-4 px-6 max-w-xs truncate text-cyan-400 underline font-mono text-xs cursor-pointer" onclick="window.open('${log.ad_link}', '_blank')">${log.ad_link}</td>
        <td class="py-4 px-6 font-mono text-xs text-slate-200">${ctr}</td>
        <td class="py-4 px-6 font-mono text-xs text-slate-200">${eng}</td>
        <td class="py-4 px-6 text-xs text-slate-400 font-mono">${hashtags}</td>
        <td class="py-4 px-6 font-mono text-[10px] text-slate-500">${log.timestamp}</td>
      </tr>
    `;
  }).join('');
}
