// Global instances for charts
let lineChartInstance = null;
let barChartInstance = null;

// Telemetry local states
let globalCampaigns = [];
let filteredCampaigns = [];
let activePlatformFilter = 'All';

// Formatting utilities
const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

// Page load event
document.addEventListener('DOMContentLoaded', () => {
  // Restore theme configuration
  initTheme();
  
  // Load stats and posts
  fetchDashboardTelemetry();
  fetchFeedPosts();
  
  // Sync button trigger
  const syncBtn = document.getElementById('sync-telemetry');
  if (syncBtn) {
    syncBtn.addEventListener('click', () => {
      fetchDashboardTelemetry();
      fetchFeedPosts();
    });
  }
});

// ===================================================
// THEME SWITCHING MODULE
// ===================================================
function initTheme() {
  const theme = localStorage.getItem('theme') || 'dark';
  const body = document.body;
  const themeIcon = document.getElementById('theme-icon');

  body.className = body.className.replace(/dark|light/g, '').trim();

  if (theme === 'dark') {
    body.classList.add('dark');
    document.documentElement.classList.add('dark');
    document.documentElement.classList.remove('light');
    if (themeIcon) themeIcon.setAttribute('data-lucide', 'sun');
  } else {
    body.classList.add('light');
    document.documentElement.classList.add('light');
    document.documentElement.classList.remove('dark');
    if (themeIcon) themeIcon.setAttribute('data-lucide', 'moon');
  }
  lucide.createIcons();
}

function toggleTheme() {
  const body = document.body;
  const currentTheme = body.classList.contains('dark') ? 'dark' : 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  localStorage.setItem('theme', nextTheme);
  initTheme();
}

// ===================================================
// DASHBOARD DATA ACTIONS
// ===================================================
async function fetchDashboardTelemetry() {
  const syncBtn = document.getElementById('sync-telemetry');
  const refreshIcon = document.getElementById('refresh-icon');
  
  if (refreshIcon) refreshIcon.classList.add('animate-spin');
  if (syncBtn) syncBtn.disabled = true;

  try {
    const campaignsResponse = await fetch('/api/campaigns');
    if (!campaignsResponse.ok) throw new Error('API request failed');

    globalCampaigns = await campaignsResponse.json();
    filteredCampaigns = [...globalCampaigns];

    // Read platform dropdown
    const filterSelect = document.getElementById('platform-filter');
    if (filterSelect) {
      activePlatformFilter = filterSelect.value || 'All';
    }

    calculateAndRenderDashboard();

  } catch (err) {
    console.error('Telemetry Sync Error:', err);
    alert('Database connection lost. Please verify Flask server is running.');
  } finally {
    if (refreshIcon) refreshIcon.classList.remove('animate-spin');
    if (syncBtn) syncBtn.disabled = false;
  }
}

function applyPlatformFilter() {
  const filterSelect = document.getElementById('platform-filter');
  if (!filterSelect) return;

  activePlatformFilter = filterSelect.value;
  calculateAndRenderDashboard();
}

function calculateAndRenderDashboard() {
  // Apply platform filters
  if (activePlatformFilter === 'All') {
    filteredCampaigns = [...globalCampaigns];
  } else {
    filteredCampaigns = globalCampaigns.filter(c => c.platform === activePlatformFilter);
  }

  // Calculate metrics
  let clicks = 0;
  let spend = 0.0;
  let revenue = 0.0;
  let conversions = 0;

  filteredCampaigns.forEach(c => {
    clicks += c.clicks;
    spend += c.spend;
    revenue += c.revenue;
    conversions += c.conversions;
  });

  const impressions = clicks * 30; // standard CTR simulation
  const roi = spend > 0 ? ((revenue - spend) / spend * 100) : 0.0;

  // Render KPI cards (Impressions, Clicks, Conversions, Revenue, ROI)
  renderKPICards({ clicks, spend, revenue, conversions, impressions, roi });
  
  // Render charts
  renderCharts(filteredCampaigns);
}

function renderKPICards(metrics) {
  const container = document.getElementById('kpi-container');
  if (!container) return;

  // Dynamic Insight: Highest conversions platform
  const platformConv = {};
  globalCampaigns.forEach(c => {
    platformConv[c.platform] = (platformConv[c.platform] || 0) + c.conversions;
  });

  let bestPlat = 'None';
  let maxConv = 0;
  for (const [p, val] of Object.entries(platformConv)) {
    if (val > maxConv) {
      maxConv = val;
      bestPlat = p;
    }
  }
  const insightsText = maxConv > 0 
    ? `${bestPlat} performing best with ${formatNumber(maxConv)} conversions.` 
    : 'No campaign telemetry resolved.';

  // Simulated Predictions (expected next week scale)
  let seed = metrics.revenue || 5000;
  // Deterministic random multiplier based on conversion counts
  const multiplier = 1.05 + ((metrics.conversions % 15) / 100); 
  const predictedRevenue = seed * multiplier;
  const predictedPercent = ((multiplier - 1) * 100).toFixed(1);

  const cards = [
    {
      title: 'Total Impressions',
      value: formatNumber(metrics.impressions),
      subtitle: `${metrics.impressions > 0 ? ((metrics.clicks / metrics.impressions) * 100).toFixed(2) : '0.00'}% CTR telemetry`,
      icon: 'eye',
      colorClass: 'text-purple-400',
      borderClass: 'border-purple-500/20'
    },
    {
      title: 'Total Clicks',
      value: formatNumber(metrics.clicks),
      subtitle: `${formatNumber(metrics.conversions)} total conversions`,
      icon: 'mouse-pointer-click',
      colorClass: 'text-cyan-400',
      borderClass: 'border-cyan-500/20'
    },
    {
      title: 'Total Spend',
      value: formatCurrency(metrics.spend),
      subtitle: `Revenue: ${formatCurrency(metrics.revenue)}`,
      icon: 'shopping-bag',
      colorClass: 'text-pink-400',
      borderClass: 'border-pink-500/20'
    },
    {
      title: 'Gross Return (ROI)',
      value: `${metrics.roi.toFixed(0)}%`,
      subtitle: metrics.roi > 0 ? `Net income: ${formatCurrency(metrics.revenue - metrics.spend)}` : 'Zero friction margin',
      icon: 'trending-up',
      colorClass: 'text-emerald-400',
      borderClass: 'border-emerald-500/20'
    },
    {
      title: 'Future Forecast',
      value: `+${predictedPercent}%`,
      subtitle: `Est. Revenue: ${formatCurrency(predictedRevenue)} next week`,
      icon: 'compass',
      colorClass: 'text-amber-400',
      borderClass: 'border-amber-500/20',
      isDouble: true
    },
    {
      title: 'Campaign Insights',
      value: bestPlat,
      subtitle: insightsText,
      icon: 'sparkles',
      colorClass: 'text-violet-400',
      borderClass: 'border-violet-500/20',
      isDouble: true
    }
  ];

  container.innerHTML = cards.map(c => `
    <div class="relative overflow-hidden bg-space-900 dark:bg-space-900 light:bg-slate-300/40 border border-slate-800 dark:border-slate-800 light:border-slate-300 rounded-2xl p-5 shadow-lg ${c.isDouble ? 'sm:col-span-2' : ''} border-l-4 ${c.borderClass}">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase">
            ${c.title}
          </p>
          <h3 class="text-2xl font-extrabold text-white dark:text-white light:text-slate-850 tracking-tight mt-1">
            ${c.value}
          </h3>
          <p class="text-[11px] text-slate-450 dark:text-slate-450 light:text-slate-600 font-medium mt-1">
            ${c.subtitle}
          </p>
        </div>
        <div class="p-2.5 bg-slate-950/60 dark:bg-slate-950/60 light:bg-slate-300 border border-slate-850 dark:border-slate-800 light:border-slate-350 rounded-xl ${c.colorClass}">
          <i data-lucide="${c.icon}" class="h-5 w-5"></i>
        </div>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

function renderCharts(campaigns) {
  const timeline = [...campaigns].sort((a, b) => new Date(a.date) - new Date(b.date));
  const labels = timeline.map(c => {
    const d = new Date(c.date);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
  });

  // Line Chart
  const lineCtx = document.getElementById('lineChart');
  if (lineCtx) {
    if (lineChartInstance) lineChartInstance.destroy();
    lineChartInstance = new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Clicks',
            data: timeline.map(c => c.clicks),
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.08)',
            tension: 0.35,
            fill: true,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(128, 128, 128, 0.05)' }, ticks: { color: '#94a3b8', font: { size: 9 } } },
          y: { grid: { color: 'rgba(128, 128, 128, 0.05)' }, ticks: { color: '#94a3b8', font: { size: 9 } } }
        }
      }
    });
  }

  // Bar Chart
  const platforms = ['Instagram', 'Google Ads', 'YouTube'];
  const summary = platforms.reduce((acc, p) => {
    acc[p] = { spend: 0, revenue: 0 };
    return acc;
  }, {});

  campaigns.forEach(c => {
    const platKey = c.platform === 'Google Ads' || c.platform === 'Google' ? 'Google Ads' : c.platform;
    if (summary[platKey]) {
      summary[platKey].spend += c.spend;
      summary[platKey].revenue += c.revenue;
    }
  });

  const barCtx = document.getElementById('barChart');
  if (barCtx) {
    if (barChartInstance) barChartInstance.destroy();
    barChartInstance = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: platforms,
        datasets: [
          {
            label: 'Spend ($)',
            data: platforms.map(p => summary[p].spend),
            backgroundColor: 'rgba(236, 72, 153, 0.75)',
            borderRadius: 4
          },
          {
            label: 'Revenue ($)',
            data: platforms.map(p => summary[p].revenue),
            backgroundColor: 'rgba(16, 185, 129, 0.75)',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(128, 128, 128, 0.05)' }, ticks: { color: '#94a3b8', font: { size: 9 } } },
          y: { grid: { color: 'rgba(128, 128, 128, 0.05)' }, ticks: { color: '#94a3b8', font: { size: 8 } } }
        }
      }
    });
  }
}

async function runPerformanceAudit() {
  const auditBtn = document.getElementById('run-audit-btn');
  const auditIcon = document.getElementById('audit-icon');
  const analysisText = document.getElementById('analysis-text');

  if (!auditBtn || !analysisText) return;

  if (auditIcon) auditIcon.classList.add('animate-spin');
  auditBtn.disabled = true;
  analysisText.innerText = "Analyzing live user database files... Calibrating flight matrices recommendations...";
  analysisText.className = "text-purple-400 text-xs leading-normal mt-0.5 animate-pulse";

  try {
    const response = await fetch('/api/analyze-performance', { method: 'POST' });
    if (!response.ok) throw new Error('API server returned error');

    const result = await response.json();
    analysisText.innerText = result.analysis || "Telemetry readout stable. Recommendations cataloged.";
    analysisText.className = "text-slate-200 dark:text-slate-200 light:text-slate-800 text-xs leading-normal mt-0.5";
  } catch (err) {
    console.error('Audit failed:', err);
    analysisText.innerText = "Error: Failed to fetch performance analysis. Verify database connectivity.";
    analysisText.className = "text-red-400 text-xs leading-normal mt-0.5";
  } finally {
    if (auditIcon) auditIcon.classList.remove('animate-spin');
    auditBtn.disabled = false;
  }
}

// ===================================================
// SOCIAL FEED MODULE (LinkedIn Activity)
// ===================================================
async function fetchFeedPosts() {
  const timeline = document.getElementById('feed-timeline');
  if (!timeline) return;

  try {
    const response = await fetch('/api/posts');
    if (!response.ok) throw new Error('Failed to read feed posts');

    const posts = await response.json();

    if (posts.length === 0) {
      timeline.innerHTML = `<p class="text-center text-slate-500 font-mono text-[11px] pt-12">No telemetry reports on the timeline. Share updates above!</p>`;
      return;
    }

    timeline.innerHTML = posts.map(p => `
      <div class="p-3.5 bg-slate-950/60 dark:bg-slate-950/60 light:bg-slate-350/40 border border-slate-850 dark:border-slate-800 light:border-slate-300 rounded-xl space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-200 dark:text-slate-200 light:text-slate-800 flex items-center gap-1.5">
            <i data-lucide="user" class="h-3 w-3 text-cyan-400"></i>
            ${p.username}
          </span>
          <span class="text-[9px] font-mono text-slate-500">${p.timestamp}</span>
        </div>
        <p class="text-xs text-slate-300 dark:text-slate-300 light:text-slate-700 leading-normal font-medium">
          ${p.content}
        </p>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error('Feed loading failed:', err);
    timeline.innerHTML = `<p class="text-center text-red-400 font-mono text-[11px] pt-8">Connection to pilot feed lost.</p>`;
  }
}

async function postFeedUpdate(event) {
  event.preventDefault();
  
  const feedInput = document.getElementById('feed-input');
  const submitBtn = document.getElementById('feed-submit-btn');

  if (!feedInput || !feedInput.value.trim()) return;
  const content = feedInput.value.trim();

  submitBtn.disabled = true;
  
  try {
    const response = await fetch('/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });

    if (!response.ok) throw new Error('API server post failed');

    feedInput.value = '';
    await fetchFeedPosts();
  } catch (err) {
    console.error('Feed posting failed:', err);
    alert('Failed to share update on the timeline.');
  } finally {
    submitBtn.disabled = false;
  }
}
