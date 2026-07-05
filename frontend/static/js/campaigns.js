// Local stores for fetched campaigns
let allCampaigns = [];
let filteredCampaigns = [];
let activeFilter = 'All';
let sortField = 'date';
let sortDirection = 'desc';

document.addEventListener('DOMContentLoaded', () => {
  fetchCampaignLogs();
  
  const refreshBtn = document.getElementById('refresh-logs');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', fetchCampaignLogs);
  }
});

async function fetchCampaignLogs() {
  const refreshBtn = document.getElementById('refresh-logs');
  const refreshIcon = document.getElementById('refresh-icon');
  
  if (refreshIcon) refreshIcon.classList.add('animate-spin');
  if (refreshBtn) refreshBtn.disabled = true;

  try {
    const response = await fetch('/api/campaigns');
    if (!response.ok) throw new Error('API server returned error');
    
    allCampaigns = await response.json();
    applyFilterAndSort();
  } catch (err) {
    console.error('Error fetching logs:', err);
    document.getElementById('table-body').innerHTML = `
      <tr>
        <td colspan="8" class="py-8 text-center text-red-400 font-mono">
          Failed to fetch campaign logs. Verify database server is online.
        </td>
      </tr>
    `;
  } finally {
    if (refreshIcon) refreshIcon.classList.remove('animate-spin');
    if (refreshBtn) refreshBtn.disabled = false;
  }
}

// Triggered by dropdown onchange
function applyPlatformFilter() {
  const filterSelect = document.getElementById('platform-select-filter');
  if (!filterSelect) return;
  
  activeFilter = filterSelect.value;
  applyFilterAndSort();
}

function sortData(field) {
  if (sortField === field) {
    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
  } else {
    sortField = field;
    sortDirection = 'desc';
  }
  applyFilterAndSort();
}

function applyFilterAndSort() {
  // 1. Filter
  if (activeFilter === 'All') {
    filteredCampaigns = [...allCampaigns];
  } else {
    filteredCampaigns = allCampaigns.filter(c => c.platform === activeFilter);
  }

  // 2. Sort
  filteredCampaigns.sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (sortField === 'roi') {
      aVal = a.spend > 0 ? (a.revenue - a.spend) / a.spend : 0;
      bVal = b.spend > 0 ? (b.revenue - b.spend) / b.spend : 0;
    }

    if (sortField === 'status') {
      // Sort status alphabetically
      const getStatus = (x) => x.revenue > x.spend ? 'Profit' : (x.revenue < x.spend ? 'Loss' : 'Average');
      aVal = getStatus(a);
      bVal = getStatus(b);
    }

    if (sortField === 'date') {
      aVal = new Date(a.date).getTime();
      bVal = new Date(b.date).getTime();
    }

    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  renderTable();
}

// Formatting utilities
const formatNumber = (num) => new Intl.NumberFormat('en-US').format(num);
const formatCurrency = (num) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);

// Render campaigns tbody
function renderTable() {
  const tbody = document.getElementById('table-body');
  if (!tbody) return;

  if (filteredCampaigns.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="py-8 text-center text-slate-500 font-mono">
          No telemetry files matching criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filteredCampaigns.map(camp => {
    // Platform icons and badges
    let platformBadge = 'bg-blue-950/40 text-blue-300 border-blue-500/20';
    let iconClass = 'globe';
    let iconColor = 'text-blue-400';

    if (camp.platform === 'Instagram') {
      platformBadge = 'bg-pink-950/40 text-pink-300 border-pink-500/20';
      iconClass = 'camera';
      iconColor = 'text-pink-400';
    } else if (camp.platform === 'YouTube') {
      platformBadge = 'bg-red-950/40 text-red-300 border-red-500/20';
      iconClass = 'video';
      iconColor = 'text-red-500';
    }

    // Dynamic campaign Profit/Loss status logic
    let statusText = 'Average';
    let statusBadge = 'bg-slate-950/40 text-slate-350 border-slate-700/30';
    let statusIcon = 'dot';
    
    if (camp.revenue > camp.spend) {
      statusText = 'Profit';
      statusBadge = 'bg-emerald-950/40 text-emerald-300 border-emerald-500/20';
      statusIcon = 'trending-up';
    } else if (camp.revenue < camp.spend) {
      statusText = 'Loss';
      statusBadge = 'bg-red-950/40 text-red-300 border-red-500/20';
      statusIcon = 'trending-down';
    }

    const formattedDate = new Date(camp.date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC'
    });

    return `
      <tr class="hover:bg-slate-800/20 transition-colors">
        <td class="py-4 px-6 font-mono text-xs text-slate-400">${formattedDate}</td>
        <td class="py-4 px-6 font-semibold text-slate-200">${camp.name}</td>
        <td class="py-4 px-6">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${platformBadge}">
            <i data-lucide="${iconClass}" class="h-3.5 w-3.5 ${iconColor}"></i>
            ${camp.platform}
          </span>
        </td>
        <td class="py-4 px-6 text-right font-mono text-cyan-400">${formatNumber(camp.clicks)}</td>
        <td class="py-4 px-6 text-right font-mono text-pink-400">${formatNumber(camp.conversions)}</td>
        <td class="py-4 px-6 text-right font-mono text-slate-450">${formatCurrency(camp.spend)}</td>
        <td class="py-4 px-6 text-right font-mono text-emerald-400 font-bold">${formatCurrency(camp.revenue)}</td>
        <td class="py-4 px-6 text-right">
          <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded border text-xs font-mono ${statusBadge}">
            <i data-lucide="${statusIcon}" class="h-3 w-3"></i>
            ${statusText}
          </span>
        </td>
      </tr>
    `;
  }).join('');

  lucide.createIcons();
}

function toggleCampaignModal(show) {
  const modal = document.getElementById('campaign-modal');
  const panel = document.getElementById('modal-panel');
  const errorBox = document.getElementById('modal-error');
  const form = document.getElementById('campaign-form');

  if (!modal || !panel) return;

  if (show) {
    if (errorBox) errorBox.classList.add('hidden');
    if (form) form.reset();
    
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('modal-date');
    if (dateInput) dateInput.value = today;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
      panel.classList.remove('scale-95', 'opacity-0');
      panel.classList.add('scale-100', 'opacity-100');
    }, 50);
  } else {
    panel.classList.remove('scale-100', 'opacity-100');
    panel.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
      modal.classList.remove('flex');
      modal.classList.add('hidden');
    }, 300);
  }
}

async function submitNewCampaign(event) {
  event.preventDefault();

  const submitBtn = document.getElementById('modal-submit-btn');
  const errorBox = document.getElementById('modal-error');
  
  if (errorBox) errorBox.classList.add('hidden');
  if (submitBtn) submitBtn.disabled = true;

  const payload = {
    name: document.getElementById('modal-name').value,
    platform: document.getElementById('modal-platform').value,
    date: document.getElementById('modal-date').value,
    clicks: parseInt(document.getElementById('modal-clicks').value, 10),
    conversions: parseInt(document.getElementById('modal-conversions').value, 10),
    spend: parseFloat(document.getElementById('modal-spend').value),
    revenue: parseFloat(document.getElementById('modal-revenue').value)
  };

  try {
    const response = await fetch('/api/campaigns', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || 'Server failed to save campaign.');
    }

    toggleCampaignModal(false);
    await fetchCampaignLogs();

  } catch (err) {
    console.error('Launch failed:', err);
    if (errorBox) {
      errorBox.innerText = `Quantum Core Rejection: ${err.message}`;
      errorBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
}
