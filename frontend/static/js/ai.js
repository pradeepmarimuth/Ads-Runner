document.addEventListener('DOMContentLoaded', () => {
  fetchLinkLogs();
});

// ===================================================
// SLOGANS GENERATOR
// ===================================================
async function generateSlogans(event) {
  event.preventDefault();

  const productInput = document.getElementById('product');
  const submitBtn = document.getElementById('slogan-submit-btn');
  const output = document.getElementById('slogan-output');

  if (!productInput || !productInput.value.trim()) return;
  const productName = productInput.value.trim();

  submitBtn.disabled = true;
  output.innerHTML = `
    <div class="animate-pulse flex items-center justify-center p-6 text-xs text-purple-400 font-mono">
      Synthesizing slogans matrix...
    </div>
  `;

  try {
    const response = await fetch('/api/generate-caption', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productName })
    });

    if (!response.ok) throw new Error('API server returned error');
    const result = await response.json();
    const { captions = [] } = result;

    if (captions.length === 0) {
      output.innerHTML = `<p class="text-xs text-slate-500 font-mono text-center">No slogans created.</p>`;
      return;
    }

    output.innerHTML = captions.map(c => `
      <div class="p-3 bg-slate-950 border border-slate-850 hover:border-purple-500/25 rounded-lg flex items-center justify-between gap-3 group">
        <span class="text-xs text-slate-300 font-medium">${c}</span>
        <button onclick="copyToClipboard('${c.replace(/'/g, "\\'")}', this)" class="p-1.5 hover:bg-slate-900 border border-slate-800 rounded-md text-slate-500 hover:text-purple-400 shrink-0">
          <i data-lucide="copy" class="h-3.5 w-3.5"></i>
        </button>
      </div>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error('Slogan generation error:', err);
    output.innerHTML = `<p class="text-xs text-red-400 font-mono">Failed to contact AI generator.</p>`;
  } finally {
    submitBtn.disabled = false;
  }
}

// ===================================================
// HASHTAGS GENERATOR
// ===================================================
async function generateHashtags(event) {
  event.preventDefault();

  const keywordInput = document.getElementById('hashtag-keyword');
  const submitBtn = document.getElementById('hashtag-submit-btn');
  const output = document.getElementById('hashtag-output');

  if (!keywordInput || !keywordInput.value.trim()) return;
  const keyword = keywordInput.value.trim();

  submitBtn.disabled = true;
  output.innerHTML = `
    <div class="animate-pulse flex items-center justify-center p-3 text-xs text-pink-400 font-mono w-full">
      Synthesizing hashtags...
    </div>
  `;

  try {
    const response = await fetch('/api/generate-hashtags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword })
    });

    if (!response.ok) throw new Error('API server returned error');
    const result = await response.json();
    const { hashtags = [] } = result;

    if (hashtags.length === 0) {
      output.innerHTML = `<span class="text-xs text-slate-500 font-mono">No hashtags generated.</span>`;
      return;
    }

    output.innerHTML = hashtags.map(tag => `
      <span onclick="copyToClipboard('${tag}', this)" class="cursor-pointer inline-flex items-center gap-1 px-3 py-1 bg-pink-950/20 hover:bg-pink-950/40 text-pink-300 border border-pink-500/20 hover:border-pink-500/40 rounded-full text-xs font-mono transition-colors">
        ${tag}
        <i data-lucide="copy" class="h-2.5 w-2.5 opacity-60"></i>
      </span>
    `).join('');

    lucide.createIcons();
  } catch (err) {
    console.error('Hashtag creation error:', err);
    output.innerHTML = `<span class="text-xs text-red-400 font-mono">Connection error.</span>`;
  } finally {
    submitBtn.disabled = false;
  }
}

// ===================================================
// AD LINK ANALYZER
// ===================================================
async function runLinkAnalyzer(event) {
  event.preventDefault();

  const urlInput = document.getElementById('analyzer-url');
  const submitBtn = document.getElementById('analyzer-submit-btn');
  const placeholder = document.getElementById('analyzer-placeholder');
  const panel = document.getElementById('analyzer-result-panel');

  if (!urlInput || !urlInput.value.trim()) return;
  const adLink = urlInput.value.trim();

  submitBtn.disabled = true;
  submitBtn.innerHTML = `
    <div class="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
    <span>Analyzing...</span>
  `;

  placeholder.innerHTML = `
    <i data-lucide="cpu" class="h-6 w-6 text-cyan-400 animate-spin mb-2"></i>
    <span class="text-xs text-cyan-400 font-semibold animate-pulse">Running Scraper Engine...</span>
    <span class="text-[10px] text-slate-500 mt-0.5">Extracting elements & engagement metrics</span>
  `;
  placeholder.classList.remove('hidden');
  panel.classList.add('hidden');
  lucide.createIcons();

  try {
    const response = await fetch('/api/analyze-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ adLink })
    });

    if (!response.ok) throw new Error('API analysis failed');
    const result = await response.json();
    const { log } = result;

    // Load results
    const insights = log.analysis_result || {};
    
    document.getElementById('result-ctr').innerText = insights.predicted_ctr || 'N/A';
    document.getElementById('result-eng').innerText = insights.estimated_engagement || 'N/A';
    document.getElementById('result-verdict').innerText = insights.verdict || '';
    
    const tagsContainer = document.getElementById('result-hashtags');
    if (insights.hashtags) {
      tagsContainer.innerHTML = insights.hashtags.map(t => `
        <span class="inline-flex px-2 py-0.5 bg-cyan-950/30 text-cyan-300 border border-cyan-500/10 rounded font-mono text-[10px]">${t}</span>
      `).join('');
    } else {
      tagsContainer.innerHTML = '';
    }

    placeholder.classList.add('hidden');
    panel.classList.remove('hidden');

    // Reset input
    urlInput.value = '';

    // Refresh logs table
    await fetchLinkLogs();

  } catch (err) {
    console.error('Analyzer error:', err);
    alert('Scraper execution error. Please check server console.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `
      <i data-lucide="cpu" class="h-4 w-4"></i>
      <span>Analyze URL</span>
    `;
    lucide.createIcons();
  }
}

async function fetchLinkLogs() {
  const tbody = document.getElementById('logs-table-body');
  if (!tbody) return;

  try {
    const response = await fetch('/api/campaign-logs');
    if (!response.ok) throw new Error('Failed to load log ledger');

    const logs = await response.json();

    if (logs.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="py-8 text-center text-slate-500 font-mono">
            Url scraper log indexes empty. Submit links to initialize telemetry database files.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = logs.map(l => {
      const insights = l.analysis_result || {};
      const tags = insights.hashtags ? insights.hashtags.join(', ') : 'N/A';
      return `
        <tr class="hover:bg-slate-800/20 transition-colors">
          <td class="py-4 px-6 font-mono text-[10px] text-slate-500">${l.timestamp}</td>
          <td class="py-4 px-6 max-w-xs truncate text-cyan-400 font-mono text-xs cursor-pointer select-all" title="${l.ad_link}">${l.ad_link}</td>
          <td class="py-4 px-6 text-right font-mono text-xs text-white">${insights.predicted_ctr || 'N/A'}</td>
          <td class="py-4 px-6 text-right font-mono text-xs text-white">${insights.estimated_engagement || 'N/A'}</td>
          <td class="py-4 px-6 text-xs text-slate-450 font-mono">${tags}</td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    console.error('Log loading error:', err);
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="py-8 text-center text-red-400 font-mono">
          Scraper logs sync failure.
        </td>
      </tr>
    `;
  }
}

// Global copy-to-clipboard action
function copyToClipboard(text, buttonElement) {
  navigator.clipboard.writeText(text).then(() => {
    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = `<i data-lucide="check" class="h-3.5 w-3.5 text-emerald-400"></i>`;
    lucide.createIcons();
    
    setTimeout(() => {
      buttonElement.innerHTML = originalHTML;
      lucide.createIcons();
    }, 2000);
  }).catch(err => console.error('Copy failed:', err));
}

// ===================================================
// MARKDOWN FORMATTING FOR AI RESPONSES
// ===================================================
function formatMarkdown(text) {
  // Escape HTML first
  let formatted = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // Format bold text **text** or __text__
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
  formatted = formatted.replace(/__(.+?)__/g, '<strong class="text-white font-semibold">$1</strong>');
  
  // Format section headers (text followed by colon or lines starting with ##)
  formatted = formatted.replace(/^## (.+)$/gm, '<div class="text-sm font-bold text-cyan-400 mt-3 mb-1.5">$1</div>');
  formatted = formatted.replace(/^### (.+)$/gm, '<div class="text-xs font-bold text-cyan-300 mt-2 mb-1">$1</div>');
  formatted = formatted.replace(/^([A-Z][A-Za-z\s&]+):$/gm, '<div class="text-xs font-bold text-cyan-400 mt-2 mb-1">$1:</div>');
  
  // Format bullet points
  formatted = formatted.replace(/^[•\-\*]\s+(.+)$/gm, '<div class="ml-3 my-1 flex items-start gap-2"><span class="text-cyan-400 mt-0.5">•</span><span class="flex-1">$1</span></div>');
  
  // Format numbered lists
  formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="ml-3 my-1 flex items-start gap-2"><span class="text-cyan-400 font-semibold">$1.</span><span class="flex-1">$2</span></div>');
  
  // Format emojis with slight spacing
  formatted = formatted.replace(/([\u{1F300}-\u{1F9FF}])/gu, '<span class="inline-block mx-0.5">$1</span>');
  
  // Format line breaks (double newline = paragraph break)
  formatted = formatted.replace(/\n\n/g, '</p><p class="mt-2">');
  formatted = formatted.replace(/\n/g, '<br>');
  
  // Wrap in paragraph
  formatted = '<p>' + formatted + '</p>';
  
  // Format inline code `code`
  formatted = formatted.replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-slate-800 text-cyan-300 rounded text-[10px] font-mono">$1</code>');
  
  return formatted;
}

// ===================================================
// AI MARKETING CHATBOT
// ===================================================
function setChatPrompt(text) {
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.value = text;
    chatInput.focus();
  }
}

async function sendChatMessage(event) {
  event.preventDefault();

  const chatInput = document.getElementById('chat-input');
  const chatSubmitBtn = document.getElementById('chat-submit-btn');
  const chatMessagesContainer = document.getElementById('chat-messages-container');

  if (!chatInput || !chatInput.value.trim()) return;
  const userMsgText = chatInput.value.trim();

  // Reset input field
  chatInput.value = '';

  // Append user message
  const userMessageHTML = `
    <div class="flex items-start gap-3 justify-end">
      <div class="bg-purple-950/30 border border-purple-500/20 text-slate-200 rounded-lg px-3.5 py-2 text-xs leading-relaxed max-w-[80%] text-left">
        ${userMsgText}
      </div>
      <div class="h-7 w-7 bg-purple-950/40 border border-purple-500/20 text-purple-400 rounded-lg flex items-center justify-center font-bold text-[10px] font-mono shrink-0">ME</div>
    </div>
  `;
  chatMessagesContainer.insertAdjacentHTML('beforeend', userMessageHTML);
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

  // Disable button and add animation indicator
  chatSubmitBtn.disabled = true;
  const originalBtnHTML = chatSubmitBtn.innerHTML;
  chatSubmitBtn.innerHTML = `
    <div class="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
    <span>Thinking...</span>
  `;

  // Append typing placeholder
  const typingId = 'typing-' + Date.now();
  const typingHTML = `
    <div id="${typingId}" class="flex items-start gap-3">
      <div class="h-7 w-7 bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 rounded-lg flex items-center justify-center font-bold text-[10px] font-mono shrink-0">AI</div>
      <div class="bg-cyan-950/20 border border-cyan-500/10 text-slate-400 rounded-lg px-3.5 py-2 text-xs leading-relaxed max-w-[80%] animate-pulse">
        Formulating marketing response...
      </div>
    </div>
  `;
  chatMessagesContainer.insertAdjacentHTML('beforeend', typingHTML);
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  lucide.createIcons();

  try {
    const response = await fetch('/api/ai-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsgText })
    });

    if (!response.ok) throw new Error('API server returned error');
    const result = await response.json();
    const botResponseText = result.response || 'No response compiled.';

    // Remove typing indicator
    const typingIndicator = document.getElementById(typingId);
    if (typingIndicator) typingIndicator.remove();

    // Format the AI response for better display
    const formattedResponse = formatMarkdown(botResponseText);
    
    // Append AI response
    const aiMessageHTML = `
      <div class="flex items-start gap-3">
        <div class="h-7 w-7 bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 rounded-lg flex items-center justify-center font-bold text-[10px] font-mono shrink-0">AI</div>
        <div class="bg-cyan-950/20 border border-cyan-500/10 text-slate-300 rounded-lg px-3.5 py-2.5 text-xs leading-relaxed max-w-[90%] chat-response">
          ${formattedResponse}
          <div class="mt-2 pt-2 border-t border-cyan-500/10 flex items-center gap-2">
            <span class="text-[8px] px-1.5 py-0.5 bg-cyan-950 text-cyan-300 rounded font-mono border border-cyan-500/10 uppercase tracking-widest">${result.ai_source || 'AI'}</span>
            <button type="button" onclick="copyToClipboard(\`${botResponseText.replace(/`/g, "\\`").replace(/'/g, "\\'")}\`, this)" class="text-[9px] text-slate-500 hover:text-cyan-400 transition-colors flex items-center gap-0.5">
              <i data-lucide="copy" class="h-2.5 w-2.5"></i> Copy
            </button>
          </div>
        </div>
      </div>
    `;
    chatMessagesContainer.insertAdjacentHTML('beforeend', aiMessageHTML);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    lucide.createIcons();

  } catch (err) {
    console.error('Chat error:', err);
    const typingIndicator = document.getElementById(typingId);
    if (typingIndicator) typingIndicator.remove();

    const errMessageHTML = `
      <div class="flex items-start gap-3">
        <div class="h-7 w-7 bg-red-950/40 border border-red-500/20 text-red-400 rounded-lg flex items-center justify-center font-bold text-[10px] font-mono shrink-0">ERR</div>
        <div class="bg-red-950/20 border border-red-500/10 text-red-400 rounded-lg px-3.5 py-2 text-xs leading-relaxed max-w-[80%] font-mono">
          AI chat node connection fault. Check server console output.
        </div>
      </div>
    `;
    chatMessagesContainer.insertAdjacentHTML('beforeend', errMessageHTML);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    lucide.createIcons();
  } finally {
    chatSubmitBtn.disabled = false;
    chatSubmitBtn.innerHTML = originalBtnHTML;
    lucide.createIcons();
  }
}

async function clearChatHistory() {
  const chatMessagesContainer = document.getElementById('chat-messages-container');
  if (!chatMessagesContainer) return;
  
  if (!confirm('Are you sure you want to clear the conversation history?')) return;

  try {
    const response = await fetch('/api/ai-chat/clear', { method: 'POST' });
    if (!response.ok) throw new Error('Clear request failed');

    // Reset container with enhanced initial greeting message
    chatMessagesContainer.innerHTML = `
      <div class="flex items-start gap-3">
        <div class="h-7 w-7 bg-cyan-950/40 border border-cyan-500/20 text-cyan-400 rounded-lg flex items-center justify-center font-bold text-[10px] font-mono shrink-0">AI</div>
        <div class="bg-cyan-950/20 border border-cyan-500/10 text-slate-350 rounded-lg px-3.5 py-2 text-xs leading-relaxed max-w-[90%]">
          Hello! I am your <strong>AI Marketing Assistant</strong> powered by local <strong>Ollama</strong> (model: <code class="px-1 bg-slate-800 text-cyan-300 rounded text-[10px]">qwen2.5:0.5b</code>).<br><br>
          I can provide <strong>comprehensive, detailed answers</strong> about:<br>
          • Marketing strategies and campaign planning<br>
          • Ad optimization and performance analysis<br>
          • Content creation and copywriting<br>
          • Platform-specific best practices<br>
          • Your campaign data and metrics<br><br>
          Ask me anything - I'll provide detailed, well-structured responses!
        </div>
      </div>
    `;
    lucide.createIcons();
  } catch (err) {
    console.error('Clear chat error:', err);
    alert('Failed to clear chat memory.');
  }
}
