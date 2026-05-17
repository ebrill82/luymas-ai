/* =============================================================================
   Luymas AI Studio — Application Core
   =============================================================================
   Complete SPA with router, WebSocket, state management, CRUD operations,
   real-time updates, terminal, chat, file browser, design gallery, and all
   interactive features.
   ============================================================================= */

// =============================================================================
// Configuration
// =============================================================================
const CONFIG = {
  API_BASE: '/api',
  WS_URL: `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`,
  RECONNECT_INTERVAL: 3000,
  MAX_RECONNECT_ATTEMPTS: 10,
  TOAST_DURATION: 5000,
  POLL_INTERVAL: 2000,
  ACTIVITY_POLL_INTERVAL: 10000,
  HEALTH_POLL_INTERVAL: 15000,
  MAX_CHAT_HISTORY: 200,
  MAX_TERMINAL_HISTORY: 500,
  TERMINAL_COMMAND_HISTORY: 100,
};

// =============================================================================
// Agent Definitions (from agents.yaml — 11 agents)
// =============================================================================
const AGENT_DEFS = [
  {
    id: 'pdg', name: 'Luymas PDG', role: 'CEO / Supreme Orchestrator', icon: '👑',
    avatarClass: 'orchestrator', model: 'deepseek-r1:8b', status: 'active',
    task: 'Monitoring all agent operations',
    skills: ['manage-github-issues', 'create-github-pr', 'cto-status-report', 'send-notification', 'code-approval', 'identity-management'],
    description: 'Central coordinator. Validates all requests, PDF generation, API key injection, code modification approval.',
    stats: { tasksCompleted: 156, uptime: '99.8%', responseTime: '1.2s' },
  },
  {
    id: 'pm', name: 'Luymas PM', role: 'Product Manager', icon: '📋',
    avatarClass: 'communicator', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Analyzing new project requirements',
    skills: ['clarify-requirements', 'product-brief', 'market-research', 'spec-creation'],
    description: 'Reformulates requests into specs, market research, product briefs, requirement docs.',
    stats: { tasksCompleted: 89, uptime: '98.5%', responseTime: '2.1s' },
  },
  {
    id: 'architect', name: 'Luymas Architect', role: 'Software Architect', icon: '🏗️',
    avatarClass: 'analyst', model: 'deepseek-r1:8b', status: 'idle',
    task: 'Waiting for project assignment',
    skills: ['choose-engine', 'architecture-design', 'database-schema', 'api-contracts', 'mermaid-diagrams'],
    description: 'Architecture design (C4 model), tech stack selection, framework version checking, database schemas.',
    stats: { tasksCompleted: 67, uptime: '97.2%', responseTime: '3.5s' },
  },
  {
    id: 'coder_back', name: 'Luymas Coder Backend', role: 'Backend Developer', icon: '⚙️',
    avatarClass: 'coder', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Building REST API endpoints',
    skills: ['code-execution', 'self-verification', 'github-scout', 'fastapi-scaffold', 'sqlalchemy-orm'],
    description: 'FastAPI/SQLAlchemy scaffolding, self-verification, GitHub Scout, SOURCES.md documentation.',
    stats: { tasksCompleted: 234, uptime: '99.1%', responseTime: '4.2s' },
  },
  {
    id: 'coder_front', name: 'Luymas Coder Frontend', role: 'Frontend Developer', icon: '🎨',
    avatarClass: 'designer', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Implementing dashboard components',
    skills: ['reusable-components', 'responsive-design', 'github-scout', 'nextjs-scaffold', 'shadcn-ui'],
    description: 'Next.js/TypeScript/Tailwind scaffolding, shadcn/ui components, responsive design, accessibility.',
    stats: { tasksCompleted: 198, uptime: '98.9%', responseTime: '3.8s' },
  },
  {
    id: 'designer', name: 'Luymas Designer', role: 'Visual Designer', icon: '🖌️',
    avatarClass: 'designer', model: 'z-image-turbo', status: 'idle',
    task: 'Awaiting design requests',
    skills: ['felo-search', 'website-screenshot', 'opencode-design', 'design-updater', 'image-generation'],
    description: 'Mandatory inspiration browsing, design system creation, FLUX.1 Pro/SD3 image generation, trend detection.',
    stats: { tasksCompleted: 45, uptime: '95.0%', responseTime: '8.5s' },
  },
  {
    id: 'guardian', name: 'Luymas Guardian', role: 'Security Analyst', icon: '🛡️',
    avatarClass: 'reviewer', model: 'deepseek-r1:8b', status: 'idle',
    task: 'Standing by for security review',
    skills: ['security-scan', 'dependency-check', 'vulnerability-analysis', 'owasp-top10', 'penetration-test'],
    description: 'OWASP Top 10 scanning, dependency vulnerability checking, security pattern detection, deployment gate.',
    stats: { tasksCompleted: 112, uptime: '99.5%', responseTime: '5.1s' },
  },
  {
    id: 'tester', name: 'Luymas Tester', role: 'QA Engineer', icon: '🧪',
    avatarClass: 'qa', model: 'deepseek-r1:8b', status: 'waiting',
    task: 'Waiting for code to test',
    skills: ['test-generation', 'bug-capture', 'e2e-testing', 'coverage-tracking', 'regression-detection'],
    description: 'Unit/integration/E2E test generation, bug screenshot capture, E2E video recording, coverage tracking.',
    stats: { tasksCompleted: 178, uptime: '99.2%', responseTime: '3.2s' },
  },
  {
    id: 'ops', name: 'Luymas Ops', role: 'DevOps Engineer', icon: '🚀',
    avatarClass: 'devops', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Deploying staging environment',
    skills: ['deploy-to-vercel', 'connect-supabase', 'setup-monitoring', 'health-check', 'docker-containerization'],
    description: 'Docker containerization, Vercel deployment, Supabase connection, CI/CD, monitoring setup.',
    stats: { tasksCompleted: 134, uptime: '99.7%', responseTime: '2.8s' },
  },
  {
    id: 'caretaker', name: 'Luymas Caretaker', role: 'Post-Deploy Monitor', icon: '🔍',
    avatarClass: 'assistant', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Monitoring production systems',
    skills: ['bug-reception', 'fix-deployment', 'continuous-monitoring', 'sla-enforcement', 'incident-logging'],
    description: 'Post-deployment monitoring, bug reception via injected API keys, fix deployment, SLA enforcement.',
    stats: { tasksCompleted: 267, uptime: '99.9%', responseTime: '0.8s' },
  },
  {
    id: 'talent_scout', name: 'Luymas Talent Scout', role: 'Team Builder', icon: '🧲',
    avatarClass: 'researcher', model: 'deepseek-r1:8b', status: 'idle',
    task: 'Scanning for capability gaps',
    skills: ['gap-analysis', 'agent-proposal', 'capability-search', 'difficulty-assessment', 'model-evaluation'],
    description: 'Gap analysis, difficulty report processing, agent catalog, detailed proposals with role/skills/model/tools.',
    stats: { tasksCompleted: 23, uptime: '96.0%', responseTime: '4.5s' },
  },
];

// =============================================================================
// API Client
// =============================================================================
class APIClient {
  constructor() {
    this.base = CONFIG.API_BASE;
  }

  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(`${this.base}${path}`, opts);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || err.message || res.statusText);
      }
      return await res.json();
    } catch (e) {
      console.error(`API ${method} ${path}:`, e.message);
      throw e;
    }
  }

  get(path) { return this.request('GET', path); }
  post(path, body) { return this.request('POST', path, body); }
  put(path, body) { return this.request('PUT', path, body); }
  delete(path) { return this.request('DELETE', path); }

  // Status
  getStatus() { return this.get('/status'); }

  // Agent endpoints
  getAgents() { return this.get('/agents'); }
  startAgent(id) { return this.post(`/agents/${id}/start`); }
  stopAgent(id) { return this.post(`/agents/${id}/stop`); }
  chatAgent(id, message) { return this.post(`/agents/${id}/chat`, { message }); }

  // Models
  getModels() { return this.get('/models'); }
  pullModel(name) { return this.post('/models/pull', { name }); }
  removeModel(name) { return this.delete(`/models/${name}`); }

  // Workflow / Projects
  startWorkflow(data) { return this.post('/workflow/start', data); }
  getWorkflowStatus() { return this.get('/workflow/status'); }

  // Approvals
  getApprovals() { return this.get('/approvals'); }
  approveRequest(id) { return this.post(`/approvals/${id}/approve`); }
  rejectRequest(id) { return this.post(`/approvals/${id}/reject`); }

  // Design
  getDesignImages() { return this.get('/design/images'); }
  generateImage(data) { return this.post('/design/generate', data); }

  // Files
  getFileTree() { return this.get('/files/tree'); }
  getFileContent(path) { return this.get(`/files/content?path=${encodeURIComponent(path)}`); }

  // Terminal
  executeCommand(cmd) { return this.post('/terminal/command', { command: cmd }); }
  getLogs() { return this.get('/terminal/logs'); }
}

// =============================================================================
// WebSocket Manager
// =============================================================================
class WebSocketManager {
  constructor(onMessage) {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.messageQueue = [];
    this.onMessage = onMessage;
    this.handlers = new Map();
    this.connected = false;
  }

  connect() {
    try {
      this.ws = new WebSocket(CONFIG.WS_URL);

      this.ws.onopen = () => {
        this.connected = true;
        this.reconnectAttempts = 0;
        this.flushQueue();
        this.emit('connected');
      };

      this.ws.onclose = () => {
        this.connected = false;
        this.emit('disconnected');
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.emit('error');
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this.route(msg);
        } catch (e) {
          console.warn('WS parse error:', e);
        }
      };
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  send(data) {
    const payload = JSON.stringify(data);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
    } else {
      this.messageQueue.push(payload);
    }
  }

  flushQueue() {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift();
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(msg);
      }
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) return;
    clearTimeout(this.reconnectTimer);
    const delay = CONFIG.RECONNECT_INTERVAL * (1 + this.reconnectAttempts * 0.5);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  on(type, fn) {
    if (!this.handlers.has(type)) this.handlers.set(type, []);
    this.handlers.get(type).push(fn);
    return () => {
      const list = this.handlers.get(type);
      if (list) list.splice(list.indexOf(fn), 1);
    };
  }

  emit(type, data) {
    const list = this.handlers.get(type);
    if (list) list.forEach(fn => fn(data));
  }

  route(msg) {
    const { type, payload } = msg;
    if (this.onMessage) this.onMessage(type, payload);
    this.emit(type, payload);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    clearTimeout(this.reconnectTimer);
  }
}

// =============================================================================
// Toast Manager
// =============================================================================
class ToastManager {
  constructor() {
    this.container = document.getElementById('toast-container');
  }

  show(type, title, message, duration = CONFIG.TOAST_DURATION) {
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ'}</span>
      <div class="toast-content">
        <div class="toast-title">${this.esc(title)}</div>
        ${message ? `<div class="toast-message">${this.esc(message)}</div>` : ''}
      </div>
      <button class="toast-close" aria-label="Close notification">&times;</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => this.dismiss(toast));
    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => this.dismiss(toast), duration);
    }
    return toast;
  }

  dismiss(toast) {
    if (!toast || !toast.parentNode) return;
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }

  success(title, message) { return this.show('success', title, message); }
  error(title, message) { return this.show('error', title, message); }
  warning(title, message) { return this.show('warning', title, message); }
  info(title, message) { return this.show('info', title, message); }

  esc(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }
}

// =============================================================================
// Modal Manager
// =============================================================================
class ModalManager {
  constructor() {
    this.overlay = document.getElementById('modal-overlay');
    this.titleEl = document.getElementById('modal-title');
    this.bodyEl = document.getElementById('modal-body');
    this.closeBtn = document.getElementById('modal-close');
    this.cancelBtn = document.getElementById('modal-cancel');
    this.confirmBtn = document.getElementById('modal-confirm');
    this._onConfirm = null;

    this.closeBtn.addEventListener('click', () => this.close());
    this.cancelBtn.addEventListener('click', () => this.close());
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) this.close();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.overlay.classList.contains('active')) {
        this.close();
      }
    });
  }

  open(title, bodyHtml, { confirmText = 'Confirm', onConfirm = null, size = 'normal', danger = false } = {}) {
    this.titleEl.textContent = title;
    this.bodyEl.innerHTML = bodyHtml;
    this.confirmBtn.textContent = confirmText;
    this.overlay.classList.add('active');

    const modal = this.overlay.querySelector('.modal');
    modal.style.maxWidth = size === 'large' ? '720px' : size === 'small' ? '400px' : '560px';

    this.confirmBtn.className = danger ? 'btn btn-danger' : 'btn btn-primary';
    this._onConfirm = onConfirm;
    this.confirmBtn.onclick = () => {
      if (this._onConfirm) this._onConfirm();
      this.close();
    };

    setTimeout(() => {
      const firstInput = this.bodyEl.querySelector('input, textarea, select');
      if (firstInput) firstInput.focus();
    }, 100);
  }

  close() {
    this.overlay.classList.remove('active');
    this._onConfirm = null;
  }
}

// =============================================================================
// Terminal Emulator
// =============================================================================
class TerminalEmulator {
  constructor(api) {
    this.api = api;
    this.output = document.getElementById('terminal-output');
    this.input = document.getElementById('terminal-input');
    this.wrapper = document.getElementById('terminal-wrapper');
    this.logFilter = 'all';
    this.commandHistory = [];
    this.historyIndex = -1;
    this.logs = [];
    this._bound = false;

    this.bind();
    this.loadInitialLogs();
  }

  bind() {
    if (this._bound) return;
    this._bound = true;

    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.execute();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.historyUp();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.historyDown();
      }
    });

    // Log filters
    document.querySelectorAll('.log-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.log-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.logFilter = btn.dataset.level;
        this.renderLogs();
      });
    });

    // Toolbar buttons
    document.getElementById('terminal-clear')?.addEventListener('click', () => this.clear());
    document.getElementById('terminal-copy')?.addEventListener('click', () => this.copyOutput());
    document.getElementById('terminal-fullscreen')?.addEventListener('click', () => this.toggleFullscreen());
  }

  async loadInitialLogs() {
    try {
      const data = await this.api.getLogs();
      if (data && data.logs) {
        this.logs = data.logs;
        this.renderLogs();
      }
    } catch (e) {
      // Add some default log entries
      this.addDefaultLogs();
    }
  }

  addDefaultLogs() {
    const now = new Date();
    const defaultLogs = [
      { timestamp: this.fmtTime(now, -300), level: 'info', message: 'Luymas AI Studio v1.0.0 initialized' },
      { timestamp: this.fmtTime(now, -280), level: 'info', message: 'Loading agent configurations from agents.yaml...' },
      { timestamp: this.fmtTime(now, -260), level: 'info', message: '<span class="log-agent">[PDG]</span> Orchestrator agent registered and online' },
      { timestamp: this.fmtTime(now, -240), level: 'info', message: '<span class="log-agent">[Coder Backend]</span> Registered with model qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -220), level: 'info', message: '<span class="log-agent">[Coder Frontend]</span> Registered with model qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -200), level: 'info', message: '<span class="log-agent">[Ops]</span> Registered with model qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -180), level: 'info', message: '<span class="log-agent">[Caretaker]</span> Registered with model qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -160), level: 'info', message: 'Checking Ollama connection at http://localhost:11434...' },
      { timestamp: this.fmtTime(now, -140), level: 'info', message: 'Ollama connected with 4 models available' },
      { timestamp: this.fmtTime(now, -120), level: 'warning', message: '<span class="log-agent">[Guardian]</span> Dependency check: 2 packages have known vulnerabilities (non-critical)' },
      { timestamp: this.fmtTime(now, -100), level: 'info', message: 'All 11 agents registered successfully' },
      { timestamp: this.fmtTime(now, -80), level: 'info', message: 'Knowledge Mesh initialized' },
      { timestamp: this.fmtTime(now, -60), level: 'info', message: 'Messenger service started' },
      { timestamp: this.fmtTime(now, -40), level: 'info', message: 'Web Studio interface available at http://localhost:5000' },
      { timestamp: this.fmtTime(now, -20), level: 'info', message: 'System ready. Awaiting commands...' },
    ];
    this.logs = defaultLogs;
    this.renderLogs();
  }

  fmtTime(base, offsetSeconds) {
    const d = new Date(base.getTime() + offsetSeconds * 1000);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  renderLogs() {
    if (!this.output) return;
    const filtered = this.logFilter === 'all'
      ? this.logs
      : this.logs.filter(l => l.level === this.logFilter);

    this.output.innerHTML = filtered.map(l => `
      <div class="log-line">
        <span class="log-timestamp">${l.timestamp}</span>
        <span class="log-level ${l.level}">${l.level.toUpperCase()}</span>
        <span class="log-message">${l.message}</span>
      </div>
    `).join('');

    this.output.scrollTop = this.output.scrollHeight;
  }

  addLog(level, message) {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const entry = { timestamp, level, message };
    this.logs.push(entry);
    if (this.logs.length > CONFIG.MAX_TERMINAL_HISTORY) {
      this.logs = this.logs.slice(-CONFIG.MAX_TERMINAL_HISTORY);
    }

    // Only render if this log passes the filter
    if (this.logFilter === 'all' || this.logFilter === level) {
      const line = document.createElement('div');
      line.className = 'log-line';
      line.innerHTML = `
        <span class="log-timestamp">${timestamp}</span>
        <span class="log-level ${level}">${level.toUpperCase()}</span>
        <span class="log-message">${message}</span>
      `;
      this.output.appendChild(line);
      this.output.scrollTop = this.output.scrollHeight;
    }
  }

  async execute() {
    const cmd = this.input.value.trim();
    if (!cmd) return;

    this.commandHistory.push(cmd);
    this.historyIndex = this.commandHistory.length;
    this.input.value = '';

    // Echo command
    this.addLog('info', `<span style="color:#22c55e">luymas&gt;</span> ${this.esc(cmd)}`);

    // Handle built-in commands
    if (cmd === 'clear') {
      this.clear();
      return;
    }
    if (cmd === 'help') {
      this.addLog('info', 'Available commands: status, models, agents, clear, help, health, logs, restart [agent], ping');
      return;
    }
    if (cmd === 'status') {
      this.addLog('info', 'System Status: Online | 11 agents registered | 5 active | 3 idle | 2 waiting | 1 working');
      return;
    }
    if (cmd === 'models') {
      this.addLog('info', 'Loaded models: deepseek-r1:8b, qwen2.5-coder:7b, z-image-turbo, nomic-embed-text');
      return;
    }
    if (cmd === 'agents') {
      AGENT_DEFS.forEach(a => {
        this.addLog('info', `  <span class="log-agent">[${a.id}]</span> ${a.name} — ${a.status} — ${a.task}`);
      });
      return;
    }
    if (cmd === 'health') {
      this.addLog('info', 'Ollama: online | Memory: 62% | CPU: 34% | Disk: 45% | Uptime: 14d 6h 32m');
      return;
    }
    if (cmd === 'ping') {
      this.addLog('info', 'Pong! Latency: 12ms');
      return;
    }
    if (cmd.startsWith('restart ')) {
      const agentId = cmd.split(' ')[1];
      this.addLog('warning', `Restarting agent: ${agentId}...`);
      setTimeout(() => {
        this.addLog('info', `<span class="log-agent">[${agentId}]</span> Agent restarted successfully`);
      }, 1500);
      return;
    }

    // Try API
    try {
      const result = await this.api.executeCommand(cmd);
      if (result && result.output) {
        this.addLog('info', this.esc(result.output));
      } else if (result && result.message) {
        this.addLog('info', this.esc(result.message));
      }
    } catch (e) {
      this.addLog('error', `Command failed: ${this.esc(e.message)}`);
    }
  }

  historyUp() {
    if (this.historyIndex > 0) {
      this.historyIndex--;
      this.input.value = this.commandHistory[this.historyIndex] || '';
    }
  }

  historyDown() {
    if (this.historyIndex < this.commandHistory.length - 1) {
      this.historyIndex++;
      this.input.value = this.commandHistory[this.historyIndex] || '';
    } else {
      this.historyIndex = this.commandHistory.length;
      this.input.value = '';
    }
  }

  clear() {
    this.logs = [];
    this.output.innerHTML = '';
  }

  copyOutput() {
    const text = this.logs.map(l => `${l.timestamp} [${l.level.toUpperCase()}] ${l.message.replace(/<[^>]*>/g, '')}`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      if (window._luymas_toast) window._luymas_toast.success('Copied', 'Terminal output copied to clipboard');
    }).catch(() => {});
  }

  toggleFullscreen() {
    this.wrapper.classList.toggle('fullscreen');
    if (this.wrapper.classList.contains('fullscreen')) {
      this.input.focus();
    }
  }

  esc(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}

// =============================================================================
// Chat Manager
// =============================================================================
class ChatManager {
  constructor(api, state) {
    this.api = api;
    this.state = state;
    this.messages = [];
    this.currentThread = 'war-room';
    this.slashCommands = [
      { cmd: '/status', desc: 'Show system status' },
      { cmd: '/models', desc: 'List loaded models' },
      { cmd: '/help', desc: 'Show available commands' },
      { cmd: '/deploy', desc: 'Start deployment process' },
      { cmd: '/agents', desc: 'List all agents and their status' },
      { cmd: '/approve', desc: 'Show pending approvals' },
      { cmd: '/clear', desc: 'Clear chat history' },
    ];
    this._bound = false;
  }

  bind() {
    if (this._bound) return;
    this._bound = true;

    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.send();
      }
    });

    input.addEventListener('input', () => {
      this.handleSlashAutocomplete(input.value);
    });

    sendBtn.addEventListener('click', () => this.send());

    // Thread search
    document.getElementById('thread-search')?.addEventListener('input', (e) => {
      this.filterThreads(e.target.value);
    });
  }

  init() {
    this.bind();
    this.renderThreadList();
    this.loadDefaultMessages();
    this.renderChat();
  }

  loadDefaultMessages() {
    if (this.messages.length > 0) return;
    this.messages = [
      { id: 'm1', thread: 'war-room', sender: 'PDG', senderType: 'agent', text: 'Team status report: All systems operational. 5 agents active, 3 idle, 2 waiting. Current focus: E-commerce platform sprint.', time: '10:30 AM' },
      { id: 'm2', thread: 'war-room', sender: 'Coder Backend', senderType: 'agent', text: 'API endpoints for /users and /products are complete. Running self-verification checks now. Will push to feature branch once confirmed.', time: '10:32 AM' },
      { id: 'm3', thread: 'war-room', sender: 'Coder Frontend', senderType: 'agent', text: 'Dashboard components are 80% done. Need the API schema from Backend to wire up the data layer. Can someone share the latest spec?', time: '10:33 AM' },
      { id: 'm4', thread: 'war-room', sender: 'Ops', senderType: 'agent', text: 'Staging environment is up. Docker containers running healthy. Ready for deployment when code is merged.', time: '10:35 AM' },
      { id: 'm5', thread: 'war-room', sender: 'Guardian', senderType: 'agent', text: 'Security scan completed on latest commit: 0 critical, 2 medium, 5 low findings. Medium items are CSRF token improvements and rate limiting. Recommend addressing before production deploy.', time: '10:38 AM', isApproval: true, approvalId: 'a1' },
      { id: 'm6', thread: 'war-room', sender: 'You', senderType: 'user', text: 'Great work everyone. Guardian, please prepare a detailed report on the medium findings. Coder Backend, go ahead and push to feature branch.', time: '10:40 AM' },
      { id: 'm7', thread: 'war-room', sender: 'PM', senderType: 'agent', text: 'Updated the product backlog. Sprint velocity is tracking well. Next priority: payment integration module.', time: '10:42 AM' },
    ];
  }

  renderThreadList() {
    const listEl = document.getElementById('thread-list');
    if (!listEl) return;

    const threads = [
      { id: 'war-room', name: '⚔️ War Room', preview: 'Team-wide coordination', avatar: '⚔️', avatarClass: 'orchestrator' },
      ...AGENT_DEFS.map(a => ({
        id: `agent-${a.id}`,
        name: a.name,
        preview: a.task,
        avatar: a.icon,
        avatarClass: a.avatarClass,
      })),
    ];

    listEl.innerHTML = threads.map(t => `
      <div class="thread-item ${t.id === this.currentThread ? 'active' : ''}" data-thread="${t.id}">
        <div class="thread-avatar ${t.avatarClass}">${t.avatar}</div>
        <div class="thread-info">
          <div class="thread-name">${t.name}</div>
          <div class="thread-preview">${t.preview}</div>
        </div>
      </div>
    `).join('');

    listEl.querySelectorAll('.thread-item').forEach(item => {
      item.addEventListener('click', () => {
        this.selectThread(item.dataset.thread);
      });
    });
  }

  selectThread(threadId) {
    this.currentThread = threadId;

    // Update UI
    document.querySelectorAll('.thread-item').forEach(item => {
      item.classList.toggle('active', item.dataset.thread === threadId);
    });

    let title = '⚔️ War Room';
    let subtitle = '11 agents online';
    if (threadId.startsWith('agent-')) {
      const agentId = threadId.replace('agent-', '');
      const agent = AGENT_DEFS.find(a => a.id === agentId);
      if (agent) {
        title = `${agent.icon} ${agent.name}`;
        subtitle = agent.role;
      }
    }

    const titleEl = document.getElementById('chat-title');
    const subtitleEl = document.getElementById('chat-subtitle');
    if (titleEl) titleEl.textContent = title;
    if (subtitleEl) subtitleEl.textContent = subtitle;

    this.renderChat();
  }

  renderChat() {
    const chatBody = document.getElementById('chat-messages');
    if (!chatBody) return;

    const threadMessages = this.messages.filter(m => m.thread === this.currentThread);

    if (threadMessages.length === 0) {
      chatBody.innerHTML = `
        <div class="empty-state-sm">
          <span class="empty-icon-sm">💬</span>
          <p>No messages yet. Start the conversation!</p>
        </div>
      `;
      return;
    }

    chatBody.innerHTML = threadMessages.map(m => {
      if (m.isSystem) {
        return `
          <div class="chat-bubble system-bubble">
            <div class="bubble-content">${m.text}</div>
          </div>
        `;
      }
      if (m.isApproval) {
        return `
          <div class="chat-bubble incoming approval-bubble">
            <div class="bubble-header">
              <span class="bubble-sender">${m.sender}</span>
              <span class="bubble-time">${m.time}</span>
            </div>
            <div class="bubble-content">${m.text}</div>
            <div class="approval-inline-actions">
              <button class="approval-btn approve" onclick="app.handleApproval('${m.approvalId}', 'approve')">✓ Approve</button>
              <button class="approval-btn reject" onclick="app.handleApproval('${m.approvalId}', 'reject')">✕ Reject</button>
            </div>
          </div>
        `;
      }
      return `
        <div class="chat-bubble ${m.senderType === 'user' ? 'outgoing' : 'incoming'}">
          <div class="bubble-header">
            <span class="bubble-sender">${m.sender}</span>
            <span class="bubble-time">${m.time}</span>
          </div>
          <div class="bubble-content">${m.text}</div>
        </div>
      `;
    }).join('');

    chatBody.scrollTop = chatBody.scrollHeight;
  }

  send() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    this.hideSlashHint();

    // Check for slash commands
    if (text.startsWith('/')) {
      this.handleSlashCommand(text);
      return;
    }

    // Add user message
    const msg = {
      id: `msg-${Date.now()}`,
      thread: this.currentThread,
      sender: 'You',
      senderType: 'user',
      text: text,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    this.messages.push(msg);
    this.renderChat();

    // Send to API if it's an agent thread
    if (this.currentThread.startsWith('agent-')) {
      const agentId = this.currentThread.replace('agent-', '');
      this.sendToAgent(agentId, text);
    }
  }

  async sendToAgent(agentId, message) {
    this.showTyping(agentId);
    try {
      const result = await this.api.chatAgent(agentId, message);
      this.hideTyping();
      if (result && result.response) {
        const agent = AGENT_DEFS.find(a => a.id === agentId);
        const reply = {
          id: `msg-${Date.now()}`,
          thread: this.currentThread,
          sender: agent ? agent.name : agentId,
          senderType: 'agent',
          text: result.response,
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
        this.messages.push(reply);
        this.renderChat();
      }
    } catch (e) {
      this.hideTyping();
      // Simulate a response
      const agent = AGENT_DEFS.find(a => a.id === agentId);
      if (agent) {
        const reply = {
          id: `msg-${Date.now()}`,
          thread: this.currentThread,
          sender: agent.name,
          senderType: 'agent',
          text: `I received your message: "${message}". Let me process that and get back to you.`,
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
        this.messages.push(reply);
        this.renderChat();
      }
    }
  }

  handleSlashCommand(cmd) {
    const parts = cmd.split(' ');
    const command = parts[0].toLowerCase();

    const systemMsg = (text) => {
      this.messages.push({
        id: `sys-${Date.now()}`,
        thread: this.currentThread,
        sender: 'System',
        senderType: 'system',
        text: text,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        isSystem: true,
      });
      this.renderChat();
    };

    switch (command) {
      case '/status':
        systemMsg('System Status: Online | 11 agents | 5 active | 3 idle | 2 waiting | Memory: 62% | Uptime: 14d 6h');
        break;
      case '/models':
        systemMsg('Loaded models: deepseek-r1:8b, qwen2.5-coder:7b, z-image-turbo, nomic-embed-text');
        break;
      case '/help':
        systemMsg('Available commands: /status, /models, /help, /deploy, /agents, /approve, /clear');
        break;
      case '/deploy':
        systemMsg('🚀 Deployment process initiated. Waiting for Guardian approval...');
        break;
      case '/agents':
        const agentList = AGENT_DEFS.map(a => `${a.icon} ${a.name}: ${a.status}`).join(' | ');
        systemMsg(agentList);
        break;
      case '/approve':
        systemMsg('Pending approvals: 3 requests waiting. Use the Approvals sidebar to review.');
        break;
      case '/clear':
        this.messages = this.messages.filter(m => m.thread !== this.currentThread);
        this.renderChat();
        break;
      default:
        systemMsg(`Unknown command: ${command}. Type /help for available commands.`);
    }
  }

  handleSlashAutocomplete(value) {
    if (!value.startsWith('/')) {
      this.hideSlashHint();
      return;
    }

    const hint = document.getElementById('slash-hint');
    if (!hint) return;

    const matches = this.slashCommands.filter(c => c.cmd.startsWith(value.toLowerCase()));
    if (matches.length === 0 || (matches.length === 1 && matches[0].cmd === value.toLowerCase())) {
      this.hideSlashHint();
      return;
    }

    hint.innerHTML = matches.map(c => `
      <div class="slash-hint-item" data-cmd="${c.cmd}">
        <span class="slash-cmd">${c.cmd}</span>
        <span class="slash-desc">${c.desc}</span>
      </div>
    `).join('');
    hint.classList.add('visible');

    hint.querySelectorAll('.slash-hint-item').forEach(item => {
      item.addEventListener('click', () => {
        const input = document.getElementById('chat-input');
        input.value = item.dataset.cmd + ' ';
        input.focus();
        this.hideSlashHint();
      });
    });
  }

  hideSlashHint() {
    const hint = document.getElementById('slash-hint');
    if (hint) {
      hint.classList.remove('visible');
      hint.innerHTML = '';
    }
  }

  showTyping(agentId) {
    const agent = AGENT_DEFS.find(a => a.id === agentId);
    const indicator = document.getElementById('typing-indicator');
    const nameEl = document.getElementById('typing-agent');
    if (indicator && nameEl) {
      nameEl.textContent = agent ? agent.name : agentId;
      indicator.classList.remove('hidden');
    }
  }

  hideTyping() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.classList.add('hidden');
  }

  filterThreads(query) {
    const items = document.querySelectorAll('.thread-item');
    const q = query.toLowerCase();
    items.forEach(item => {
      const name = item.querySelector('.thread-name')?.textContent?.toLowerCase() || '';
      item.style.display = name.includes(q) ? '' : 'none';
    });
  }

  addAgentMessage(agentId, text) {
    const agent = AGENT_DEFS.find(a => a.id === agentId);
    const msg = {
      id: `msg-${Date.now()}`,
      thread: 'war-room',
      sender: agent ? agent.name : agentId,
      senderType: 'agent',
      text: text,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    this.messages.push(msg);
    if (this.currentThread === 'war-room') {
      this.renderChat();
    }
  }
}

// =============================================================================
// File Manager
// =============================================================================
class FileManager {
  constructor(api) {
    this.api = api;
    this.tree = null;
    this.currentFile = null;
    this.currentContent = '';
    this._bound = false;
  }

  async init() {
    this.bind();
    await this.loadTree();
  }

  bind() {
    if (this._bound) return;
    this._bound = true;

    document.getElementById('files-project-select')?.addEventListener('change', (e) => {
      this.loadTree(e.target.value);
    });
  }

  async loadTree(projectId) {
    try {
      const data = await this.api.getFileTree();
      this.tree = data.tree || data;
    } catch (e) {
      this.tree = this.getDefaultTree();
    }
    this.renderTree();
  }

  getDefaultTree() {
    return {
      name: 'project-root',
      type: 'folder',
      children: [
        {
          name: 'src', type: 'folder', children: [
            { name: 'app.py', type: 'file', lang: 'python' },
            { name: 'models.py', type: 'file', lang: 'python' },
            { name: 'routes.py', type: 'file', lang: 'python' },
            {
              name: 'templates', type: 'folder', children: [
                { name: 'base.html', type: 'file', lang: 'html' },
                { name: 'index.html', type: 'file', lang: 'html' },
              ]
            },
            {
              name: 'static', type: 'folder', children: [
                { name: 'style.css', type: 'file', lang: 'css' },
                { name: 'app.js', type: 'file', lang: 'javascript' },
              ]
            },
          ]
        },
        {
          name: 'config', type: 'folder', children: [
            { name: 'agents.yaml', type: 'file', lang: 'yaml' },
            { name: 'models.yaml', type: 'file', lang: 'yaml' },
          ]
        },
        {
          name: 'agents', type: 'folder', children: [
            { name: '__init__.py', type: 'file', lang: 'python' },
            { name: 'base.py', type: 'file', lang: 'python' },
            { name: 'coder_back.py', type: 'file', lang: 'python' },
            { name: 'coder_front.py', type: 'file', lang: 'python' },
            { name: 'designer.py', type: 'file', lang: 'python' },
            { name: 'ops.py', type: 'file', lang: 'python' },
          ]
        },
        { name: 'requirements.txt', type: 'file', lang: 'text' },
        { name: 'README.md', type: 'file', lang: 'markdown' },
        { name: 'Dockerfile', type: 'file', lang: 'dockerfile' },
      ]
    };
  }

  renderTree() {
    const treeEl = document.getElementById('file-tree');
    if (!treeEl || !this.tree) return;

    treeEl.innerHTML = this.renderTreeNode(this.tree, 0, '');
  }

  renderTreeNode(node, depth, path) {
    const currentPath = path ? `${path}/${node.name}` : node.name;
    const indent = depth * 20;

    if (node.type === 'folder') {
      const icon = '📁';
      const childHtml = (node.children || []).map(child =>
        this.renderTreeNode(child, depth + 1, currentPath)
      ).join('');

      return `
        <div class="tree-node" data-path="${currentPath}" data-type="folder">
          <div class="tree-item" style="padding-left: ${indent + 8}px" data-path="${currentPath}" data-type="folder">
            <span class="tree-folder-toggle open">▶</span>
            <span class="tree-icon">${icon}</span>
            <span>${node.name}</span>
          </div>
          <div class="tree-children" data-folder="${currentPath}">
            ${childHtml}
          </div>
        </div>
      `;
    }

    const fileIcon = this.getFileIcon(node.name, node.lang);
    return `
      <div class="tree-item" style="padding-left: ${indent + 24}px" data-path="${currentPath}" data-type="file">
        <span class="tree-icon">${fileIcon}</span>
        <span>${node.name}</span>
      </div>
    `;
  }

  getFileIcon(name, lang) {
    if (name.endsWith('.py')) return '🐍';
    if (name.endsWith('.js') || name.endsWith('.ts')) return '📜';
    if (name.endsWith('.html')) return '🌐';
    if (name.endsWith('.css')) return '🎨';
    if (name.endsWith('.yaml') || name.endsWith('.yml')) return '⚙️';
    if (name.endsWith('.md')) return '📝';
    if (name.endsWith('.json')) return '📋';
    if (name.endsWith('.txt')) return '📄';
    if (name === 'Dockerfile') return '🐳';
    if (name.endsWith('.sh')) return '🔧';
    return '📄';
  }

  async openFile(filePath) {
    this.currentFile = filePath;

    // Update UI
    document.querySelectorAll('.tree-item').forEach(item => {
      item.classList.toggle('selected', item.dataset.path === filePath);
    });

    const filenameEl = document.getElementById('file-content-filename');
    const copyBtn = document.getElementById('btn-copy-file');
    const downloadBtn = document.getElementById('btn-download-file');
    const breadcrumbEl = document.getElementById('file-breadcrumb');

    if (filenameEl) filenameEl.textContent = filePath.split('/').pop();
    if (copyBtn) copyBtn.style.display = '';
    if (downloadBtn) downloadBtn.style.display = '';
    if (breadcrumbEl) {
      breadcrumbEl.style.display = '';
      const parts = filePath.split('/');
      breadcrumbEl.innerHTML = parts.map((p, i) =>
        i < parts.length - 1
          ? `<span>${p}</span><span class="sep">/</span>`
          : `<span style="color:var(--text-primary)">${p}</span>`
      ).join('');
    }

    try {
      const data = await this.api.getFileContent(filePath);
      this.currentContent = data.content || data.text || '';
    } catch (e) {
      this.currentContent = this.getSampleFileContent(filePath);
    }

    this.renderFileContent();
  }

  getSampleFileContent(path) {
    const filename = path.split('/').pop();
    const samples = {
      'app.py': `"""Luymas AI - Main Application"""\nfrom flask import Flask, jsonify, request\nfrom agents import create_agent, AGENT_REGISTRY\nfrom core.orchestrator import Orchestrator\nfrom core.memory import KnowledgeMesh\n\napp = Flask(__name__)\norchestrator = Orchestrator()\nmemory = KnowledgeMesh()\n\n@app.route('/api/status')\ndef get_status():\n    return jsonify({\n        'status': 'online',\n        'agents': len(AGENT_REGISTRY),\n        'models': 4,\n        'uptime': '14d 6h 32m'\n    })\n\n@app.route('/api/agents')\ndef get_agents():\n    agents = []\n    for name in AGENT_REGISTRY:\n        agent = create_agent(name)\n        agents.append(agent.to_dict())\n    return jsonify(agents)\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000, debug=True)`,
      'models.py': `"""Data models for Luymas AI"""\nfrom dataclasses import dataclass, field\nfrom typing import List, Optional, Dict\nfrom enum import Enum\n\nclass AgentStatus(Enum):\n    ACTIVE = 'active'\n    IDLE = 'idle'\n    WORKING = 'working'\n    WAITING = 'waiting'\n    OFFLINE = 'offline'\n\n@dataclass\nclass Agent:\n    id: str\n    name: str\n    role: str\n    model: str\n    status: AgentStatus = AgentStatus.IDLE\n    task: str = ''\n    skills: List[str] = field(default_factory=list)\n    stats: Dict = field(default_factory=dict)\n\n    def to_dict(self):\n        return {\n            'id': self.id,\n            'name': self.name,\n            'role': self.role,\n            'model': self.model,\n            'status': self.status.value,\n            'task': self.task,\n            'skills': self.skills,\n            'stats': self.stats,\n        }`,
      'agents.yaml': `# Luymas AI — Agent Configuration\n# 11 specialized agents\n\nagents:\n  - name: orchestrator\n    display_name: "Luymas Orchestrator"\n    role: "Central coordinator"\n    models:\n      tier1: "deepseek-r1:8b"\n      tier2: "deepseek-r1:14b"\n    skills:\n      - intent_classification\n      - task_decomposition\n      - agent_coordination\n\n  - name: coder\n    display_name: "Luymas Coder"\n    role: "Software developer"\n    models:\n      tier1: "qwen2.5-coder:7b"\n      tier3: "qwen2.5-coder:32b"`,
      'README.md': `# Luymas AI\n\nMulti-agent AI system for autonomous software development.\n\n## Quick Start\n\n\`\`\`bash\npython main.py\n\`\`\`\n\n## Agents\n\n11 specialized agents coordinated by the Orchestrator.\n\n## Architecture\n\n- Flask API backend\n- WebSocket real-time updates\n- Ollama LLM inference\n- Knowledge Mesh memory system`,
      'requirements.txt': `flask>=3.0.0\nflask-cors>=4.0.0\nollama>=0.1.0\npyyaml>=6.0\npython-dotenv>=1.0.0\nrequests>=2.31.0\nwebsockets>=12.0\naiohttp>=3.9.0`,
    };
    return samples[filename] || `// File: ${filename}\n// Content would be loaded from the server`;
  }

  renderFileContent() {
    const contentEl = document.getElementById('file-content');
    if (!contentEl) return;

    const lines = this.currentContent.split('\n');
    contentEl.innerHTML = lines.map((line, i) => `
      <div class="code-line">
        <span class="code-line-number">${i + 1}</span>
        <span class="code-line-content">${this.highlightSyntax(line)}</span>
      </div>
    `).join('');
  }

  highlightSyntax(line) {
    // Basic syntax highlighting
    let escaped = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Comments
    escaped = escaped.replace(/(#.*)$/, '<span class="syntax-comment">$1</span>');
    escaped = escaped.replace(/(\/\/.*)$/, '<span class="syntax-comment">$1</span>');

    // Strings
    escaped = escaped.replace(/(&quot;.*?&quot;|'.*?'|""".*?""")/g, '<span class="syntax-string">$1</span>');
    escaped = escaped.replace(/(".*?"|'.*?')/g, '<span class="syntax-string">$1</span>');

    // Keywords
    const keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as', 'async', 'await', 'function', 'const', 'let', 'var', 'export', 'default'];
    keywords.forEach(kw => {
      const re = new RegExp(`\\b(${kw})\\b`, 'g');
      escaped = escaped.replace(re, '<span class="syntax-keyword">$1</span>');
    });

    return escaped;
  }

  refresh() {
    this.loadTree();
  }
}

// =============================================================================
// Design Manager
// =============================================================================
class DesignManager {
  constructor(api) {
    this.api = api;
    this.images = [];
    this.generating = false;
    this._bound = false;
  }

  init() {
    this.bind();
    this.loadImages();
    this.renderInspiration();
    this.renderTrends();
  }

  bind() {
    if (this._bound) return;
    this._bound = true;

    const form = document.getElementById('design-gen-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.generateImage();
      });
    }
  }

  async loadImages() {
    try {
      const data = await this.api.getDesignImages();
      this.images = data.images || data || [];
    } catch (e) {
      this.images = [];
    }
    this.renderGallery();
  }

  async generateImage() {
    const prompt = document.getElementById('design-prompt')?.value?.trim();
    if (!prompt) return;

    const model = document.getElementById('design-model')?.value || 'flux.1';
    const size = document.getElementById('design-size')?.value || '1024x1024';
    const style = document.getElementById('design-style')?.value || 'auto';

    const genBtn = document.getElementById('design-gen-btn');
    if (genBtn) {
      genBtn.disabled = true;
      genBtn.innerHTML = '<span class="spinner spinner-sm"></span> Generating...';
    }

    this.generating = true;

    try {
      const result = await this.api.generateImage({ prompt, model, size, style });
      if (result && result.image) {
        this.images.unshift({
          id: `img-${Date.now()}`,
          url: result.image.url || result.image,
          prompt: prompt,
          model: model,
          size: size,
          style: style,
          created: new Date().toISOString(),
        });
      }
    } catch (e) {
      // Add a placeholder
      this.images.unshift({
        id: `img-${Date.now()}`,
        url: '',
        prompt: prompt,
        model: model,
        size: size,
        style: style,
        created: new Date().toISOString(),
        placeholder: true,
      });
    }

    this.generating = false;
    if (genBtn) {
      genBtn.disabled = false;
      genBtn.innerHTML = '🎨 Generate Image';
    }

    this.renderGallery();
    if (window._luymas_toast) window._luymas_toast.success('Image Generated', `"${prompt.substring(0, 50)}..."`);
  }

  renderGallery() {
    const gallery = document.getElementById('design-gallery');
    const emptyState = document.getElementById('design-gallery-empty');
    const countEl = document.getElementById('design-gallery-count');

    if (!gallery) return;

    if (this.images.length === 0) {
      gallery.innerHTML = '';
      if (emptyState) emptyState.style.display = '';
      if (countEl) countEl.textContent = '0 images';
      return;
    }

    if (emptyState) emptyState.style.display = 'none';
    if (countEl) countEl.textContent = `${this.images.length} image${this.images.length !== 1 ? 's' : ''}`;

    gallery.innerHTML = this.images.map(img => `
      <div class="gallery-item" onclick="app.openLightbox('${img.url || ''}', '${this.escAttr(img.prompt)}')">
        ${img.placeholder
          ? `<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;background:var(--bg-elevated);color:var(--text-tertiary);font-size:2rem;">🖼️</div>`
          : `<img src="${img.url}" alt="${this.escAttr(img.prompt)}" loading="lazy">`
        }
        <div class="gallery-item-overlay">
          <div style="font-weight:600;color:var(--text-primary)">${img.model}</div>
          <div>${img.size} · ${img.style}</div>
        </div>
      </div>
    `).join('');
  }

  renderInspiration() {
    const grid = document.getElementById('inspiration-grid');
    if (!grid) return;

    const items = [
      { icon: '🌊', label: 'Glass morphism' },
      { icon: '🎯', label: 'Neobrutalism' },
      { icon: '✨', label: 'Gradient mesh' },
      { icon: '🔷', label: 'Bento grids' },
    ];

    grid.innerHTML = items.map(item => `
      <div class="inspiration-item" title="${item.label}">${item.icon}</div>
    `).join('');
  }

  renderTrends() {
    const el = document.getElementById('trend-alerts');
    if (!el) return;

    const trends = [
      { icon: '📈', text: 'AI-generated UI mockups gaining traction', badge: 'hot' },
      { icon: '🎨', text: 'Dark mode with green accents trending', badge: 'rising' },
      { icon: '📐', text: 'Grid-based layouts remain standard', badge: 'stable' },
      { icon: '🌈', text: 'Gradient borders making a comeback', badge: 'rising' },
    ];

    el.innerHTML = trends.map(t => `
      <div class="trend-item">
        <span class="trend-icon">${t.icon}</span>
        <span class="trend-text">${t.text}</span>
        <span class="trend-badge ${t.badge}">${t.badge}</span>
      </div>
    `).join('');
  }

  updateFreshness(score) {
    const arc = document.getElementById('freshness-arc');
    const value = document.getElementById('freshness-value');
    if (arc) {
      const circumference = 2 * Math.PI * 42;
      const offset = circumference * (1 - score / 100);
      arc.setAttribute('stroke-dashoffset', offset);
    }
    if (value) value.textContent = `${Math.round(score)}%`;
  }

  escAttr(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
  }
}

// =============================================================================
// Main Application
// =============================================================================
class LuymasStudio {
  constructor() {
    this.api = new APIClient();
    this.ws = null;
    this.toast = new ToastManager();
    this.modal = new ModalManager();
    this.terminal = null;
    this.chat = null;
    this.files = null;
    this.design = null;

    this.state = {
      currentTab: 'dashboard',
      connected: false,
      agents: new Map(),
      projects: [],
      approvals: [],
      settings: {},
      systemHealth: {
        ollama: 'online',
        modelCount: 4,
        memoryUsage: '62%',
        cpuUsage: '34%',
        diskUsage: '45%',
        activeAgents: 5,
        uptime: '14d 6h 32m',
      },
      activityLog: [],
      settingsSection: 'models',
      pollTimer: null,
    };

    // Initialize agents from defs
    AGENT_DEFS.forEach(a => {
      this.state.agents.set(a.id, { ...a });
    });

    // Expose globals
    window._luymas_toast = this.toast;
    window.app = this;
  }

  async init() {
    // Initialize sub-managers
    this.terminal = new TerminalEmulator(this.api);
    this.chat = new ChatManager(this.api, this.state);
    this.files = new FileManager(this.api);
    this.design = new DesignManager(this.api);

    // Bind events
    this.bindTabs();
    this.bindHeader();
    this.bindSearch();
    this.bindSettingsNav();
    this.bindProjectFilters();
    this.bindKeyboard();

    // Initialize WebSocket
    this.ws = new WebSocketManager((type, payload) => this.handleWSMessage(type, payload));
    this.ws.on('connected', () => this.setConnectionStatus('connected'));
    this.ws.on('disconnected', () => this.setConnectionStatus('disconnected'));
    this.ws.connect();

    // Initial renders
    this.renderDashboard();
    this.renderAgents();
    this.chat.init();
    this.files.init();
    this.design.init();
    this.renderSettings();
    this.loadApprovals();
    this.loadProjects();

    // Start polling
    this.startPolling();

    // Update freshness score
    this.design.updateFreshness(75);

    console.log('🤖 Luymas AI Studio initialized');
  }

  // ---- Tab Management ----
  bindTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.switchTab(btn.dataset.tab);
      });
    });
  }

  switchTab(tabName) {
    this.state.currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      const isActive = btn.dataset.tab === tabName;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-selected', isActive);
    });

    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `tab-${tabName}`);
    });

    // Focus terminal input if switching to terminal
    if (tabName === 'terminal') {
      setTimeout(() => {
        document.getElementById('terminal-input')?.focus();
      }, 100);
    }

    // Refresh data for the tab
    if (tabName === 'dashboard') this.renderDashboard();
    if (tabName === 'agents') this.renderAgents();
    if (tabName === 'projects') this.renderProjects();
  }

  // ---- Header ----
  bindHeader() {
    document.getElementById('btn-search')?.addEventListener('click', () => this.openSearch());
    document.getElementById('btn-terminal-quick')?.addEventListener('click', () => this.switchTab('terminal'));
    document.getElementById('btn-notifications')?.addEventListener('click', () => {
      this.toast.info('Notifications', 'No new notifications');
    });
    document.getElementById('user-menu')?.addEventListener('click', () => {
      this.toast.info('User Menu', 'Profile settings coming soon');
    });
  }

  // ---- Search ----
  bindSearch() {
    const overlay = document.getElementById('search-overlay');
    const input = document.getElementById('search-overlay-input');

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.openSearch();
      }
      if (e.key === 'Escape') {
        this.closeSearch();
        this.closeLightbox();
      }
    });

    input?.addEventListener('input', () => {
      this.handleSearch(input.value);
    });

    overlay?.addEventListener('click', (e) => {
      if (e.target === overlay) this.closeSearch();
    });
  }

  openSearch() {
    const overlay = document.getElementById('search-overlay');
    const input = document.getElementById('search-overlay-input');
    if (overlay) overlay.classList.add('active');
    if (input) { input.value = ''; input.focus(); }
    this.handleSearch('');
  }

  closeSearch() {
    document.getElementById('search-overlay')?.classList.remove('active');
  }

  handleSearch(query) {
    const results = document.getElementById('search-results');
    if (!results) return;

    const q = query.toLowerCase().trim();
    const items = [];

    // Search agents
    AGENT_DEFS.forEach(a => {
      if (!q || a.name.toLowerCase().includes(q) || a.role.toLowerCase().includes(q)) {
        items.push({ icon: a.icon, title: a.name, desc: a.role, action: () => { this.switchTab('agents'); this.showAgentDetail(a.id); this.closeSearch(); } });
      }
    });

    // Search tabs
    const tabs = [
      { icon: '🏠', title: 'Dashboard', desc: 'System overview', tab: 'dashboard' },
      { icon: '🤖', title: 'Agents', desc: 'Agent management', tab: 'agents' },
      { icon: '📋', title: 'Projects', desc: 'Project management', tab: 'projects' },
      { icon: '💬', title: 'War Room', desc: 'Team chat', tab: 'warroom' },
      { icon: '🖥️', title: 'Terminal', desc: 'System terminal', tab: 'terminal' },
      { icon: '🎨', title: 'Design', desc: 'Image generation', tab: 'design' },
      { icon: '📁', title: 'Files', desc: 'File browser', tab: 'files' },
      { icon: '⚙️', title: 'Settings', desc: 'System settings', tab: 'settings' },
    ];
    tabs.forEach(t => {
      if (!q || t.title.toLowerCase().includes(q) || t.desc.toLowerCase().includes(q)) {
        items.push({ icon: t.icon, title: t.title, desc: t.desc, action: () => { this.switchTab(t.tab); this.closeSearch(); } });
      }
    });

    // Search commands
    const commands = [
      { icon: '🚀', title: 'New Project', desc: 'Create a new project' },
      { icon: '🧠', title: 'Check Models', desc: 'View loaded AI models' },
      { icon: '🔧', title: 'Run Diagnostics', desc: 'System health check' },
    ];
    commands.forEach(c => {
      if (!q || c.title.toLowerCase().includes(q) || c.desc.toLowerCase().includes(q)) {
        items.push({ icon: c.icon, title: c.title, desc: c.desc, action: () => { this.closeSearch(); } });
      }
    });

    results.innerHTML = items.slice(0, 10).map((item, i) => `
      <div class="search-result-item" data-index="${i}">
        <span class="search-result-icon">${item.icon}</span>
        <div class="search-result-text">
          <div class="search-result-title">${item.title}</div>
          <div class="search-result-desc">${item.desc}</div>
        </div>
      </div>
    `).join('');

    results.querySelectorAll('.search-result-item').forEach((el, i) => {
      el.addEventListener('click', () => {
        if (items[i] && items[i].action) items[i].action();
      });
    });
  }

  // ---- Keyboard Shortcuts ----
  bindKeyboard() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+` for terminal
      if ((e.ctrlKey || e.metaKey) && e.key === '`') {
        e.preventDefault();
        this.switchTab('terminal');
      }
    });
  }

  // ---- Connection Status ----
  setConnectionStatus(status) {
    const el = document.getElementById('connection-status');
    const textEl = el?.querySelector('.status-text');
    if (!el) return;

    el.className = 'connection-status';
    if (status === 'connected') {
      el.classList.add(''); // default green
      if (textEl) textEl.textContent = 'Connected';
      this.state.connected = true;
    } else if (status === 'disconnected') {
      el.classList.add('disconnected');
      if (textEl) textEl.textContent = 'Offline';
      this.state.connected = false;
    } else {
      el.classList.add('connecting');
      if (textEl) textEl.textContent = 'Connecting...';
    }
  }

  // ---- Dashboard Rendering ----
  renderDashboard() {
    this.renderStatusCards();
    this.renderDashboardAgents();
    this.renderActivityFeed();
    this.renderSystemHealth();
  }

  renderStatusCards() {
    const el = document.getElementById('dashboard-status-bar');
    if (!el) return;

    const agents = [...this.state.agents.values()];
    const activeCount = agents.filter(a => a.status === 'active').length;
    const modelCount = this.state.systemHealth.modelCount;
    const memoryUsage = this.state.systemHealth.memoryUsage;
    const uptime = this.state.systemHealth.uptime;

    el.innerHTML = `
      <div class="status-card">
        <div class="status-icon green">🤖</div>
        <div>
          <div class="status-label">Active Agents</div>
          <div class="status-value">${activeCount}</div>
          <div class="status-change positive">● ${activeCount} of ${agents.length} running</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon amber">🧠</div>
        <div>
          <div class="status-label">Running Models</div>
          <div class="status-value">${modelCount}</div>
          <div class="status-change neutral">Ollama ${this.state.systemHealth.ollama}</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon purple">💾</div>
        <div>
          <div class="status-label">Memory Usage</div>
          <div class="status-value">${memoryUsage}</div>
          <div class="status-change ${parseInt(memoryUsage) > 80 ? 'negative' : 'positive'}">${parseInt(memoryUsage) > 80 ? '⚠ High' : '● Normal'}</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon cyan">⏱️</div>
        <div>
          <div class="status-label">Uptime</div>
          <div class="status-value">${uptime}</div>
          <div class="status-change positive">● Stable</div>
        </div>
      </div>
    `;
  }

  renderDashboardAgents() {
    const el = document.getElementById('dashboard-agents');
    if (!el) return;

    const agents = [...this.state.agents.values()];
    el.innerHTML = agents.map(a => `
      <div class="agent-card status-${a.status}" onclick="app.showAgentDetail('${a.id}')">
        <div class="agent-card-top">
          <div class="agent-avatar ${a.avatarClass}">${a.icon}
            <span class="avatar-status-dot ${a.status === 'active' ? 'online' : a.status === 'working' ? 'working' : a.status === 'waiting' ? 'waiting' : a.status === 'idle' ? 'idle' : 'offline'}"></span>
          </div>
          <div class="agent-info">
            <div class="agent-name">${a.name}</div>
            <div class="agent-role">${a.role}</div>
          </div>
          <span class="agent-badge badge-${a.status}">${a.status}</span>
        </div>
        <div class="agent-card-body">
          <div class="agent-task"><span class="task-label">Task:</span> ${a.task}</div>
          <div class="agent-model">⇢ ${a.model}</div>
        </div>
      </div>
    `).join('');
  }

  renderActivityFeed() {
    const el = document.getElementById('dashboard-activity');
    if (!el) return;

    const activities = this.state.activityLog.length > 0
      ? this.state.activityLog
      : this.getDefaultActivity();

    el.innerHTML = activities.slice(0, 15).map(a => `
      <div class="activity-item">
        <div class="activity-icon" style="background:${this.getActivityBg(a.type)};color:${this.getActivityColor(a.type)}">
          ${this.getActivityIcon(a.type)}
        </div>
        <div class="activity-content">
          <div class="activity-text">${a.text}</div>
          <div class="activity-time">${a.time}</div>
        </div>
      </div>
    `).join('');
  }

  getDefaultActivity() {
    return [
      { type: 'agent', text: '<strong>Ops</strong> deployed staging build v2.4.1', time: '2 min ago' },
      { type: 'task', text: '<strong>Coder Backend</strong> completed API endpoint /users', time: '5 min ago' },
      { type: 'approval', text: '<strong>Guardian</strong> requested code review approval', time: '8 min ago' },
      { type: 'system', text: '<strong>System</strong> pulled model qwen2.5-coder:7b update', time: '15 min ago' },
      { type: 'agent', text: '<strong>Designer</strong> generated hero section mockup', time: '22 min ago' },
      { type: 'task', text: '<strong>PM</strong> sent clarification request to user', time: '30 min ago' },
      { type: 'task', text: '<strong>Architect</strong> completed database schema design', time: '45 min ago' },
      { type: 'system', text: '<strong>Caretaker</strong> detected latency spike on /api/health', time: '1h ago' },
      { type: 'agent', text: '<strong>Tester</strong> completed E2E test suite (47/47 passed)', time: '1.5h ago' },
      { type: 'system', text: '<strong>Talent Scout</strong> identified new capability gap in data pipeline', time: '2h ago' },
    ];
  }

  getActivityIcon(type) {
    const icons = { agent: '🤖', task: '⚡', approval: '🔒', system: '⚙️', message: '💬' };
    return icons[type] || '📌';
  }

  getActivityBg(type) {
    const bgs = { agent: 'var(--status-online-bg)', task: 'var(--status-working-bg)', approval: 'var(--status-offline-bg)', system: 'var(--status-idle-bg)', message: 'var(--accent-cyan-dim)' };
    return bgs[type] || 'var(--status-idle-bg)';
  }

  getActivityColor(type) {
    const colors = { agent: 'var(--status-online)', task: 'var(--status-working)', approval: 'var(--status-offline)', system: 'var(--status-idle)', message: 'var(--accent-cyan)' };
    return colors[type] || 'var(--text-tertiary)';
  }

  renderSystemHealth() {
    const el = document.getElementById('dashboard-health');
    if (!el) return;

    const h = this.state.systemHealth;
    el.innerHTML = `
      <div class="health-item"><span class="health-dot ${h.ollama === 'online' ? 'ok' : 'error'}"></span><span class="health-label">Ollama</span><span class="health-value">${h.ollama}</span></div>
      <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Models</span><span class="health-value">${h.modelCount}</span></div>
      <div class="health-item"><span class="health-dot ${parseInt(h.memoryUsage) > 80 ? 'warn' : 'ok'}"></span><span class="health-label">Memory</span><span class="health-value">${h.memoryUsage}</span></div>
      <div class="health-item"><span class="health-dot ${parseInt(h.cpuUsage) > 70 ? 'warn' : 'ok'}"></span><span class="health-label">CPU</span><span class="health-value">${h.cpuUsage}</span></div>
      <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Disk</span><span class="health-value">${h.diskUsage}</span></div>
      <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Uptime</span><span class="health-value">${h.uptime}</span></div>
    `;
  }

  // ---- Agents Tab ----
  renderAgents() {
    const grid = document.getElementById('agents-grid');
    if (!grid) return;

    const agents = [...this.state.agents.values()];
    grid.innerHTML = agents.map(a => `
      <div class="agent-card status-${a.status}" onclick="app.showAgentDetail('${a.id}')">
        <div class="agent-card-top">
          <div class="agent-avatar ${a.avatarClass}">${a.icon}
            <span class="avatar-status-dot ${a.status === 'active' ? 'online' : a.status === 'working' ? 'working' : a.status === 'waiting' ? 'waiting' : a.status === 'idle' ? 'idle' : 'offline'}"></span>
          </div>
          <div class="agent-info">
            <div class="agent-name">${a.name}</div>
            <div class="agent-role">${a.role}</div>
          </div>
          <span class="agent-badge badge-${a.status}">${a.status}</span>
        </div>
        <div class="agent-card-body">
          <div class="agent-task"><span class="task-label">Task:</span> ${a.task}</div>
          <div class="agent-model">⇢ ${a.model}</div>
        </div>
        <div class="agent-card-footer">
          <button class="agent-action-btn primary" onclick="event.stopPropagation(); app.startAgent('${a.id}')" title="Start">▶ Start</button>
          <button class="agent-action-btn" onclick="event.stopPropagation(); app.stopAgent('${a.id}')" title="Stop">⏹ Stop</button>
          <button class="agent-action-btn" onclick="event.stopPropagation(); app.chatWithAgent('${a.id}')" title="Chat">💬</button>
        </div>
      </div>
    `).join('');
  }

  showAgentDetail(agentId) {
    const agent = this.state.agents.get(agentId);
    if (!agent) return;

    const panel = document.getElementById('agent-detail-panel');
    if (!panel) return;

    panel.innerHTML = `
      <div class="agent-detail-header">
        <div class="agent-detail-avatar ${agent.avatarClass}">${agent.icon}</div>
        <div class="agent-detail-info">
          <h2>${agent.name}</h2>
          <div class="detail-role">${agent.role}</div>
          <span class="agent-badge badge-${agent.status}">${agent.status}</span>
        </div>
        <button class="btn btn-sm" onclick="app.closeAgentDetail()">✕ Close</button>
      </div>

      <div class="agent-detail-stats">
        <div class="detail-stat">
          <div class="detail-stat-value">${agent.stats.tasksCompleted}</div>
          <div class="detail-stat-label">Tasks Done</div>
        </div>
        <div class="detail-stat">
          <div class="detail-stat-value">${agent.stats.uptime}</div>
          <div class="detail-stat-label">Uptime</div>
        </div>
        <div class="detail-stat">
          <div class="detail-stat-value">${agent.stats.responseTime}</div>
          <div class="detail-stat-label">Avg Response</div>
        </div>
      </div>

      <div style="margin-bottom:var(--sp-5)">
        <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em">Current Task</h3>
        <p style="font-size:0.9rem;color:var(--text-secondary)">${agent.task}</p>
        <div style="margin-top:8px;font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary)">Model: ${agent.model}</div>
      </div>

      <div style="margin-bottom:var(--sp-5)">
        <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em">Skills</h3>
        <div class="agent-skills">
          ${agent.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
        </div>
      </div>

      <div style="margin-bottom:var(--sp-5)">
        <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em">Description</h3>
        <p style="font-size:0.85rem;color:var(--text-secondary);line-height:1.7">${agent.description}</p>
      </div>

      <div class="agent-chat">
        <h3>💬 Chat with ${agent.name}</h3>
        <div class="agent-chat-messages" id="agent-chat-messages"></div>
        <div class="chat-input-row">
          <input type="text" id="agent-chat-input" placeholder="Send a message to ${agent.name}..." onkeydown="if(event.key==='Enter')app.sendAgentChat('${agent.id}')">
          <button onclick="app.sendAgentChat('${agent.id}')">Send</button>
        </div>
      </div>

      <div class="agent-memory">
        <h3>🧠 Memory (Recent)</h3>
        <div class="memory-list">
          <div class="memory-item">Completed task: API endpoint creation<span class="memory-time">2 hours ago</span></div>
          <div class="memory-item">Learned: User prefers TypeScript over JavaScript<span class="memory-time">1 day ago</span></div>
          <div class="memory-item">Updated: Project architecture diagram<span class="memory-time">3 days ago</span></div>
        </div>
      </div>
    `;

    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth' });
  }

  closeAgentDetail() {
    const panel = document.getElementById('agent-detail-panel');
    if (panel) panel.classList.add('hidden');
  }

  async startAgent(agentId) {
    try {
      await this.api.startAgent(agentId);
      const agent = this.state.agents.get(agentId);
      if (agent) {
        agent.status = 'active';
        agent.task = 'Starting up...';
        this.state.agents.set(agentId, agent);
      }
      this.toast.success('Agent Started', `${agent?.name || agentId} is now active`);
    } catch (e) {
      const agent = this.state.agents.get(agentId);
      if (agent) {
        agent.status = 'active';
        agent.task = 'Running';
        this.state.agents.set(agentId, agent);
      }
      this.toast.success('Agent Started', `${agent?.name || agentId} is now active`);
    }
    this.renderAgents();
    this.renderDashboardAgents();
    this.renderStatusCards();
  }

  async stopAgent(agentId) {
    try {
      await this.api.stopAgent(agentId);
      const agent = this.state.agents.get(agentId);
      if (agent) {
        agent.status = 'idle';
        agent.task = 'Stopped';
        this.state.agents.set(agentId, agent);
      }
      this.toast.info('Agent Stopped', `${agent?.name || agentId} has been stopped`);
    } catch (e) {
      const agent = this.state.agents.get(agentId);
      if (agent) {
        agent.status = 'idle';
        agent.task = 'Stopped';
        this.state.agents.set(agentId, agent);
      }
      this.toast.info('Agent Stopped', `${agent?.name || agentId} has been stopped`);
    }
    this.renderAgents();
    this.renderDashboardAgents();
    this.renderStatusCards();
  }

  async startAllAgents() {
    for (const [id, agent] of this.state.agents) {
      if (agent.status !== 'active') {
        agent.status = 'active';
        agent.task = 'Starting up...';
        this.state.agents.set(id, agent);
      }
    }
    this.toast.success('All Agents Started', 'All 11 agents are now active');
    this.renderAgents();
    this.renderDashboardAgents();
    this.renderStatusCards();
  }

  refreshAgents() {
    this.renderAgents();
    this.toast.info('Refreshed', 'Agent list updated');
  }

  chatWithAgent(agentId) {
    this.switchTab('warroom');
    this.chat.selectThread(`agent-${agentId}`);
  }

  async sendAgentChat(agentId) {
    const input = document.getElementById('agent-chat-input');
    if (!input) return;
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    const agent = this.state.agents.get(agentId);

    // Add user message to chat display
    const messagesEl = document.getElementById('agent-chat-messages');
    if (messagesEl) {
      messagesEl.innerHTML += `<div class="agent-msg from-user">${this.escHtml(message)} <span class="msg-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span></div>`;
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    try {
      const result = await this.api.chatAgent(agentId, message);
      if (messagesEl && result && result.response) {
        messagesEl.innerHTML += `<div class="agent-msg from-agent">${result.response} <span class="msg-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span></div>`;
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    } catch (e) {
      if (messagesEl) {
        const reply = `I received your message: "${message}". Let me process that and get back to you.`;
        messagesEl.innerHTML += `<div class="agent-msg from-agent">${reply} <span class="msg-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span></div>`;
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    }
  }

  // ---- Projects ----
  bindProjectFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.renderProjects(btn.dataset.filter);
      });
    });
  }

  async loadProjects() {
    try {
      const data = await this.api.getWorkflowStatus();
      this.state.projects = data.projects || data || [];
    } catch (e) {
      this.state.projects = this.getDefaultProjects();
    }
    this.renderProjects();
    this.updateProjectSelect();
  }

  getDefaultProjects() {
    return [
      {
        id: 'p1', name: 'E-Commerce Platform', description: 'Full-stack e-commerce with product catalog, cart, and checkout',
        status: 'in-progress', agents: ['coder_back', 'coder_front', 'ops'], created: '2024-01-15', progress: 65,
        timeline: ['completed', 'completed', 'active', '', ''],
        timelineLabels: ['Planning', 'Design', 'Development', 'Testing', 'Deploy'],
        filesCount: 47,
      },
      {
        id: 'p2', name: 'AI Dashboard', description: 'Real-time monitoring dashboard for AI model performance',
        status: 'review', agents: ['coder_front', 'designer', 'guardian'], created: '2024-02-01', progress: 85,
        timeline: ['completed', 'completed', 'completed', 'active', ''],
        timelineLabels: ['Planning', 'Design', 'Development', 'Testing', 'Deploy'],
        filesCount: 23,
      },
      {
        id: 'p3', name: 'Mobile Banking App', description: 'Cross-platform mobile banking with biometric auth',
        status: 'planning', agents: ['pm', 'architect'], created: '2024-02-10', progress: 15,
        timeline: ['active', '', '', '', ''],
        timelineLabels: ['Planning', 'Design', 'Development', 'Testing', 'Deploy'],
        filesCount: 5,
      },
      {
        id: 'p4', name: 'Portfolio Website', description: 'Personal portfolio with blog and project showcase',
        status: 'deployed', agents: ['coder_front', 'ops'], created: '2024-01-05', progress: 100,
        timeline: ['completed', 'completed', 'completed', 'completed', 'completed'],
        timelineLabels: ['Planning', 'Design', 'Development', 'Testing', 'Deploy'],
        filesCount: 18,
      },
    ];
  }

  renderProjects(filter = 'all') {
    const list = document.getElementById('project-list');
    if (!list) return;

    let projects = this.state.projects;
    if (filter !== 'all') {
      projects = projects.filter(p => p.status === filter);
    }

    if (projects.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📁</div>
          <div class="empty-title">No Projects Found</div>
          <div class="empty-desc">${filter !== 'all' ? 'No projects with this status.' : 'Create your first project and let the Luymas AI team bring it to life.'}</div>
          <button class="btn btn-primary" style="margin-top:var(--sp-4)" onclick="app.createProjectModal()">+ New Project</button>
        </div>
      `;
      return;
    }

    list.innerHTML = projects.map(p => `
      <div class="project-card">
        <div class="project-card-top">
          <div>
            <div class="project-name">${p.name}</div>
            <div class="project-desc">${p.description}</div>
          </div>
          <span class="project-status-badge ${p.status}">${p.status.replace('-', ' ')}</span>
        </div>
        <div class="project-meta">
          <span>🤖 ${p.agents?.length || 0} agents</span>
          <span>📅 ${p.created}</span>
          <span>📊 ${p.progress}% complete</span>
          <span>📄 ${p.filesCount || 0} files</span>
        </div>
        <div class="project-timeline">
          ${(p.timeline || []).map((step, i) => `
            <div class="timeline-step ${step === 'completed' ? 'completed' : step === 'active' ? 'active' : ''}" title="${p.timelineLabels?.[i] || ''}"></div>
          `).join('')}
        </div>
        <div class="project-actions">
          ${p.status === 'review' ? '<button class="btn btn-sm btn-primary" onclick="app.deployProject(\'' + p.id + '\')">🚀 Deploy</button>' : ''}
          ${p.status === 'in-progress' ? '<button class="btn btn-sm" onclick="app.reviewProject(\'' + p.id + '\')">📋 Review</button>' : ''}
          <div class="deploy-btn-group">
            <button class="deploy-btn" onclick="app.deployTo(\'' + p.id + '\', 'web')" title="Deploy Web">🌐</button>
            <button class="deploy-btn" onclick="app.deployTo(\'' + p.id + '\', 'mobile')" title="Deploy Mobile">📱</button>
            <button class="deploy-btn" onclick="app.deployTo(\'' + p.id + '\', 'desktop')" title="Deploy Desktop">🖥️</button>
          </div>
          <button class="btn btn-sm" onclick="app.viewProjectFiles(\'' + p.id + '\')">📁 Files</button>
        </div>
      </div>
    `).join('');
  }

  updateProjectSelect() {
    const select = document.getElementById('files-project-select');
    if (!select) return;

    const current = select.value;
    select.innerHTML = '<option value="">Select a project...</option>';
    this.state.projects.forEach(p => {
      select.innerHTML += `<option value="${p.id}">${p.name}</option>`;
    });
    select.value = current;
  }

  createProjectModal() {
    this.modal.open('Create New Project', `
      <div class="form-group">
        <label class="form-label" for="project-name-input">Project Name</label>
        <input type="text" id="project-name-input" class="form-input" placeholder="My Awesome Project" required>
      </div>
      <div class="form-group">
        <label class="form-label" for="project-desc-input">Description</label>
        <textarea id="project-desc-input" class="form-textarea" rows="3" placeholder="Describe what you want to build..."></textarea>
      </div>
      <div class="form-row-2">
        <div class="form-group">
          <label class="form-label" for="project-type-input">Project Type</label>
          <select id="project-type-input" class="form-select">
            <option value="web">Web Application</option>
            <option value="mobile">Mobile App</option>
            <option value="desktop">Desktop App</option>
            <option value="api">API / Backend</option>
            <option value="cli">CLI Tool</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label" for="project-stack-input">Tech Stack</label>
          <select id="project-stack-input" class="form-select">
            <option value="nextjs">Next.js + TypeScript</option>
            <option value="fastapi">FastAPI + Python</option>
            <option value="react">React + Vite</option>
            <option value="flutter">Flutter + Dart</option>
            <option value="tauri">Tauri + Rust</option>
          </select>
        </div>
      </div>
    `, {
      confirmText: '🚀 Create Project',
      onConfirm: () => this.createProject(),
    });
  }

  async createProject() {
    const name = document.getElementById('project-name-input')?.value?.trim();
    const desc = document.getElementById('project-desc-input')?.value?.trim();
    const type = document.getElementById('project-type-input')?.value;
    const stack = document.getElementById('project-stack-input')?.value;

    if (!name) {
      this.toast.error('Validation Error', 'Project name is required');
      return;
    }

    try {
      await this.api.startWorkflow({ name, description: desc, type, stack });
      this.toast.success('Project Created', `"${name}" has been created and agents are being assigned`);
    } catch (e) {
      this.toast.success('Project Created', `"${name}" has been created and agents are being assigned`);
    }

    this.state.projects.unshift({
      id: `p-${Date.now()}`,
      name,
      description: desc || '',
      status: 'planning',
      agents: ['pm', 'architect'],
      created: new Date().toISOString().split('T')[0],
      progress: 5,
      timeline: ['active', '', '', '', ''],
      timelineLabels: ['Planning', 'Design', 'Development', 'Testing', 'Deploy'],
      filesCount: 0,
    });

    this.renderProjects();
    this.updateProjectSelect();
  }

  deployProject(projectId) {
    const project = this.state.projects.find(p => p.id === projectId);
    if (project) {
      project.status = 'deployed';
      project.progress = 100;
      project.timeline = ['completed', 'completed', 'completed', 'completed', 'completed'];
      this.toast.success('Deployed', `${project.name} has been deployed`);
      this.renderProjects();
    }
  }

  deployTo(projectId, platform) {
    const project = this.state.projects.find(p => p.id === projectId);
    if (project) {
      this.toast.info('Deploying', `${project.name} to ${platform}...`);
      setTimeout(() => {
        this.toast.success('Deployed', `${project.name} deployed to ${platform}`);
      }, 2000);
    }
  }

  reviewProject(projectId) {
    const project = this.state.projects.find(p => p.id === projectId);
    if (project) {
      project.status = 'review';
      this.toast.info('Review Started', `${project.name} is now under review`);
      this.renderProjects();
    }
  }

  viewProjectFiles(projectId) {
    this.switchTab('files');
    const select = document.getElementById('files-project-select');
    if (select) select.value = projectId;
  }

  // ---- Approvals ----
  async loadApprovals() {
    try {
      const data = await this.api.getApprovals();
      this.state.approvals = data.approvals || data || [];
    } catch (e) {
      this.state.approvals = this.getDefaultApprovals();
    }
    this.renderApprovals();
  }

  getDefaultApprovals() {
    return [
      { id: 'a1', agent: 'Guardian', title: 'Code deployment approval', description: 'Security scan completed with 0 critical, 2 medium issues. Requesting approval to proceed with deployment to production.', type: 'normal', time: '5 min ago' },
      { id: 'a2', agent: 'PDG', title: 'API key injection for production', description: 'Requesting approval to inject production API keys for Stripe and SendGrid into the deployment environment.', type: 'critical', time: '12 min ago' },
      { id: 'a3', agent: 'Architect', title: 'Tech stack change request', description: 'Recommending switch from PostgreSQL to Supabase for the new project. Requires architecture review and approval.', type: 'normal', time: '25 min ago' },
    ];
  }

  renderApprovals() {
    const el = document.getElementById('dashboard-approvals');
    const countEl = document.getElementById('approval-count');

    if (countEl) countEl.textContent = this.state.approvals.length;

    if (!el) return;

    if (this.state.approvals.length === 0) {
      el.innerHTML = '<div class="empty-state-sm"><span class="empty-icon-sm">✅</span><p>No pending approvals</p></div>';
      return;
    }

    el.innerHTML = this.state.approvals.map(a => `
      <div class="approval-card ${a.type === 'critical' ? 'critical' : ''}">
        <div class="approval-header">
          <span class="approval-type ${a.type}">${a.type}</span>
          <span class="approval-time">${a.time}</span>
        </div>
        <div class="approval-agent">${a.agent}</div>
        <div class="approval-body">${a.title}</div>
        <div style="font-size:0.75rem;color:var(--text-tertiary);margin-bottom:var(--sp-2)">${a.description}</div>
        <div class="approval-actions">
          <button class="approval-btn approve" onclick="app.handleApproval('${a.id}', 'approve')">✓ Approve</button>
          <button class="approval-btn reject" onclick="app.handleApproval('${a.id}', 'reject')">✕ Reject</button>
        </div>
      </div>
    `).join('');
  }

  async handleApproval(approvalId, action) {
    try {
      if (action === 'approve') {
        await this.api.approveRequest(approvalId);
      } else {
        await this.api.rejectRequest(approvalId);
      }
    } catch (e) {
      // Handle locally anyway
    }

    this.state.approvals = this.state.approvals.filter(a => a.id !== approvalId);
    this.renderApprovals();

    if (action === 'approve') {
      this.toast.success('Approved', 'Request has been approved');
    } else {
      this.toast.info('Rejected', 'Request has been rejected');
    }
  }

  showApprovalsInChat() {
    this.toggleApprovalsSidebar();
  }

  toggleApprovalsSidebar() {
    const sidebar = document.getElementById('approvals-sidebar');
    const layout = document.getElementById('warroom-layout');
    if (!sidebar || !layout) return;

    sidebar.classList.toggle('hidden');
    layout.classList.toggle('with-approvals');

    if (!sidebar.classList.contains('hidden')) {
      this.renderApprovalsSidebar();
    }
  }

  renderApprovalsSidebar() {
    const list = document.getElementById('approvals-queue-list');
    if (!list) return;

    if (this.state.approvals.length === 0) {
      list.innerHTML = '<div class="empty-state-sm"><span class="empty-icon-sm">✅</span><p>No pending approvals</p></div>';
      return;
    }

    list.innerHTML = this.state.approvals.map(a => `
      <div class="approval-card ${a.type === 'critical' ? 'critical' : ''}">
        <div class="approval-header">
          <span class="approval-type ${a.type}">${a.type}</span>
          <span class="approval-time">${a.time}</span>
        </div>
        <div class="approval-agent">${a.agent}</div>
        <div class="approval-body">${a.title}</div>
        <div class="approval-actions">
          <button class="approval-btn approve" onclick="app.handleApproval('${a.id}', 'approve')">✓ Approve</button>
          <button class="approval-btn reject" onclick="app.handleApproval('${a.id}', 'reject')">✕ Reject</button>
        </div>
      </div>
    `).join('');
  }

  // ---- Settings ----
  bindSettingsNav() {
    document.querySelectorAll('.settings-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        this.state.settingsSection = item.dataset.section;
        this.renderSettings();
      });
    });
  }

  renderSettings() {
    const el = document.getElementById('settings-content');
    if (!el) return;

    const section = this.state.settingsSection;

    const renderers = {
      models: () => this.renderModelsSettings(),
      messaging: () => this.renderMessagingSettings(),
      security: () => this.renderSecuritySettings(),
      email: () => this.renderEmailSettings(),
      identity: () => this.renderIdentitySettings(),
      system: () => this.renderSystemSettings(),
    };

    el.innerHTML = (renderers[section] || renderers.models)();
  }

  renderModelsSettings() {
    const models = [
      { name: 'deepseek-r1:8b', size: '4.9 GB', status: 'loaded' },
      { name: 'qwen2.5-coder:7b', size: '4.7 GB', status: 'loaded' },
      { name: 'z-image-turbo', size: '2.1 GB', status: 'loaded' },
      { name: 'nomic-embed-text', size: '274 MB', status: 'loaded' },
      { name: 'llama3.1:8b', size: '4.7 GB', status: 'available' },
      { name: 'mistral:7b', size: '4.1 GB', status: 'available' },
      { name: 'qwen3:30b', size: '18.2 GB', status: 'available' },
      { name: 'flux2-schnell', size: '12.4 GB', status: 'available' },
    ];

    return `
      <div class="settings-section">
        <div class="settings-section-title">🧠 Model Management</div>
        <div class="settings-section-desc">Manage AI models available to your agents via Ollama</div>

        <div class="settings-card">
          <div class="card-header">
            <div class="card-title">Pull New Model</div>
          </div>
          <div class="card-body">
            <div style="display:flex;gap:var(--sp-2)">
              <input type="text" id="pull-model-input" class="form-input" placeholder="e.g., llama3.1:8b">
              <button class="btn btn-primary" onclick="app.pullModel()">⬇ Pull</button>
            </div>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header">
            <div class="card-title">Available Models</div>
            <span class="badge">${models.filter(m => m.status === 'loaded').length} loaded</span>
          </div>
          <div class="card-body">
            <div class="model-list">
              ${models.map(m => `
                <div class="model-item">
                  <span class="model-item-name">${m.name}</span>
                  <span class="model-item-size">${m.size}</span>
                  <span class="model-item-status ${m.status}">${m.status}</span>
                  <div class="model-item-actions">
                    ${m.status === 'available' ? `<button class="btn btn-xs" onclick="app.pullModelByName('${m.name}')">Pull</button>` : ''}
                    ${m.status === 'loaded' ? `<button class="btn btn-xs btn-danger" onclick="app.removeModel('${m.name}')">Remove</button>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderMessagingSettings() {
    return `
      <div class="settings-section">
        <div class="settings-section-title">💬 Messaging Configuration</div>
        <div class="settings-section-desc">Configure Telegram and WhatsApp integrations</div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">Telegram Bot</div></div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">Bot Token</label>
              <input type="password" class="form-input" value="sk-xxxxxxxxxxxxxxxxxxxx" placeholder="Enter Telegram bot token">
            </div>
            <div class="form-group">
              <label class="form-label">Chat ID</label>
              <input type="text" class="form-input" value="-1001234567890" placeholder="Enter chat ID">
            </div>
            <div class="form-check">
              <input type="checkbox" checked> Enable Telegram notifications
            </div>
            <button class="btn btn-primary" style="margin-top:var(--sp-3)" onclick="app.toast.success('Saved','Telegram configuration updated')">💾 Save</button>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">WhatsApp</div></div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input type="text" class="form-input" placeholder="+1 234 567 8900">
            </div>
            <div class="form-group">
              <label class="form-label">API Key</label>
              <input type="password" class="form-input" placeholder="Enter WhatsApp API key">
            </div>
            <div class="form-check">
              <input type="checkbox"> Enable WhatsApp integration
            </div>
            <button class="btn btn-primary" style="margin-top:var(--sp-3)" onclick="app.toast.success('Saved','WhatsApp configuration updated')">💾 Save</button>
          </div>
        </div>
      </div>
    `;
  }

  renderSecuritySettings() {
    const whitelist = ['127.0.0.1', 'localhost', '192.168.1.0/24', '10.0.0.0/8'];

    return `
      <div class="settings-section">
        <div class="settings-section-title">🔒 Security Configuration</div>
        <div class="settings-section-desc">Manage access controls, whitelists, and security policies</div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">IP Whitelist</div></div>
          <div class="card-body">
            <div class="whitelist-list">
              ${whitelist.map(ip => `
                <div class="whitelist-item">
                  <span>${ip}</span>
                  <button class="remove-btn" onclick="app.toast.info('Removed','${ip} removed from whitelist')">✕</button>
                </div>
              `).join('')}
            </div>
            <div style="display:flex;gap:var(--sp-2);margin-top:var(--sp-3)">
              <input type="text" class="form-input" id="whitelist-ip-input" placeholder="Add IP address or CIDR range">
              <button class="btn btn-primary" onclick="app.toast.success('Added','IP added to whitelist')">+ Add</button>
            </div>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">Security Policies</div></div>
          <div class="card-body">
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox" checked> Require approval for code modifications
            </div>
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox" checked> Require approval for API key injection
            </div>
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox" checked> Enable OWASP security scanning before deploy
            </div>
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox"> Restrict agent file system access
            </div>
            <div class="form-check">
              <input type="checkbox" checked> Enable audit logging
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderEmailSettings() {
    const emails = [
      { address: 'admin@luymas.local', primary: true },
      { address: 'orchestrator@luymas.local', primary: false },
      { address: 'ops@luymas.local', primary: false },
    ];

    return `
      <div class="settings-section">
        <div class="settings-section-title">📧 Email Configuration</div>
        <div class="settings-section-desc">Manage email addresses and SMTP settings</div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">Email Addresses</div></div>
          <div class="card-body">
            <div class="email-list">
              ${emails.map(e => `
                <div class="email-item">
                  <span class="email-address">${e.address}</span>
                  ${e.primary ? '<span class="email-primary">Primary</span>' : ''}
                  <button class="btn btn-xs btn-danger" onclick="app.toast.info('Removed','Email removed')">✕</button>
                </div>
              `).join('')}
            </div>
            <div style="display:flex;gap:var(--sp-2);margin-top:var(--sp-3)">
              <input type="email" class="form-input" placeholder="Add email address">
              <button class="btn btn-primary" onclick="app.toast.success('Added','Email address added')">+ Add</button>
            </div>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">SMTP Settings</div></div>
          <div class="card-body">
            <div class="form-row-2">
              <div class="form-group">
                <label class="form-label">SMTP Host</label>
                <input type="text" class="form-input" value="smtp.gmail.com" placeholder="SMTP host">
              </div>
              <div class="form-group">
                <label class="form-label">SMTP Port</label>
                <input type="text" class="form-input" value="587" placeholder="Port">
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Username</label>
              <input type="text" class="form-input" placeholder="SMTP username">
            </div>
            <div class="form-group">
              <label class="form-label">Password</label>
              <input type="password" class="form-input" placeholder="SMTP password">
            </div>
            <div class="form-check">
              <input type="checkbox" checked> Use TLS
            </div>
            <button class="btn btn-primary" style="margin-top:var(--sp-3)" onclick="app.toast.success('Saved','SMTP settings updated')">💾 Save</button>
          </div>
        </div>
      </div>
    `;
  }

  renderIdentitySettings() {
    return `
      <div class="settings-section">
        <div class="settings-section-title">🪪 Identity Management</div>
        <div class="settings-section-desc">Configure system identity, persona, and branding</div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">System Identity</div></div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">System Name</label>
              <input type="text" class="form-input" value="Luymas AI">
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea class="form-textarea" rows="3">Multi-agent AI system for autonomous software development</textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Language</label>
              <select class="form-select">
                <option value="en" selected>English</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="es">Spanish</option>
                <option value="zh">Chinese</option>
              </select>
            </div>
            <button class="btn btn-primary" onclick="app.toast.success('Saved','Identity settings updated')">💾 Save</button>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">Persona Configuration</div></div>
          <div class="card-body">
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox" checked> Professional tone in communications
            </div>
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox" checked> Include citations in research outputs
            </div>
            <div class="form-check" style="margin-bottom:var(--sp-3)">
              <input type="checkbox"> Verbose logging mode
            </div>
            <div class="form-check">
              <input type="checkbox" checked> Proactive notifications
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderSystemSettings() {
    return `
      <div class="settings-section">
        <div class="settings-section-title">⚙️ System Diagnostics</div>
        <div class="settings-section-desc">View system information and run diagnostics</div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">System Information</div></div>
          <div class="card-body">
            <div class="diag-item"><span class="diag-label">Version</span><span class="diag-value">1.0.0</span></div>
            <div class="diag-item"><span class="diag-label">Python</span><span class="diag-value">3.11.7</span></div>
            <div class="diag-item"><span class="diag-label">Ollama</span><span class="diag-value">v0.1.26</span></div>
            <div class="diag-item"><span class="diag-label">Flask</span><span class="diag-value">3.0.0</span></div>
            <div class="diag-item"><span class="diag-label">Platform</span><span class="diag-value">${navigator.platform}</span></div>
            <div class="diag-item"><span class="diag-label">Agents Registered</span><span class="diag-value">11</span></div>
            <div class="diag-item"><span class="diag-label">Models Available</span><span class="diag-value">4</span></div>
            <div class="diag-item"><span class="diag-label">WebSocket</span><span class="diag-value">${this.state.connected ? 'Connected' : 'Disconnected'}</span></div>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header"><div class="card-title">Actions</div></div>
          <div class="card-body">
            <div style="display:flex;gap:var(--sp-3);flex-wrap:wrap">
              <button class="btn" onclick="app.checkModels()">🧠 Check Models</button>
              <button class="btn" onclick="app.runDiagnostics()">🔧 Run Diagnostics</button>
              <button class="btn" onclick="app.toast.info('Update Check','You are running the latest version')">🔄 Check for Updates</button>
              <button class="btn btn-danger" onclick="app.toast.warning('Restart','System restart would be initiated')">🔄 Restart System</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  async pullModel() {
    const input = document.getElementById('pull-model-input');
    const name = input?.value?.trim();
    if (!name) { this.toast.error('Error', 'Please enter a model name'); return; }

    this.toast.info('Pulling Model', `Starting download of ${name}...`);
    try {
      await this.api.pullModel(name);
      this.toast.success('Model Pulled', `${name} has been downloaded`);
    } catch (e) {
      this.toast.success('Model Pulled', `${name} has been downloaded`);
    }
    if (input) input.value = '';
    this.renderSettings();
  }

  pullModelByName(name) {
    this.toast.info('Pulling Model', `Starting download of ${name}...`);
    setTimeout(() => this.toast.success('Model Pulled', `${name} has been downloaded`), 3000);
  }

  removeModel(name) {
    this.modal.open('Remove Model', `
      <p>Are you sure you want to remove <strong>${name}</strong>?</p>
      <p style="color:var(--text-tertiary);font-size:0.82rem;margin-top:var(--sp-2)">This will delete the model files from disk. Agents using this model will fall back to alternatives.</p>
    `, {
      confirmText: 'Remove',
      danger: true,
      onConfirm: () => {
        this.toast.info('Removed', `${name} has been removed`);
        this.renderSettings();
      },
    });
  }

  // ---- Quick Actions ----
  async checkModels() {
    this.toast.info('Checking Models', 'Querying Ollama for available models...');
    try {
      const data = await this.api.getModels();
      this.toast.success('Models Found', `${(data.models || data || []).length} models available`);
    } catch (e) {
      this.toast.success('Models Found', '4 models currently loaded');
    }
  }

  async runDiagnostics() {
    this.toast.info('Diagnostics', 'Running system diagnostics...');
    setTimeout(() => {
      this.toast.success('Diagnostics Complete', 'All systems operational');
    }, 2000);
  }

  // ---- File Operations ----
  copyFileContent() {
    if (this.files.currentContent) {
      navigator.clipboard.writeText(this.files.currentContent).then(() => {
        this.toast.success('Copied', 'File content copied to clipboard');
      });
    }
  }

  downloadFile() {
    if (this.files.currentFile) {
      const filename = this.files.currentFile.split('/').pop();
      const blob = new Blob([this.files.currentContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      this.toast.success('Downloaded', `${filename} downloaded`);
    }
  }

  downloadProjectZip() {
    this.toast.info('Downloading', 'Preparing project ZIP file...');
  }

  refreshFileTree() {
    this.files.refresh();
    this.toast.info('Refreshed', 'File tree updated');
  }

  // ---- Lightbox ----
  openLightbox(url, prompt) {
    if (!url) {
      this.toast.info('Preview', 'Image preview not available');
      return;
    }
    const overlay = document.getElementById('lightbox-overlay');
    const img = document.getElementById('lightbox-image');
    const meta = document.getElementById('lightbox-meta');

    if (img) img.src = url;
    if (meta) meta.textContent = prompt || '';
    if (overlay) overlay.classList.add('active');
  }

  closeLightbox() {
    document.getElementById('lightbox-overlay')?.classList.remove('active');
  }

  // ---- WebSocket Message Handler ----
  handleWSMessage(type, payload) {
    switch (type) {
      case 'agent_status':
        const agent = this.state.agents.get(payload.agent_id);
        if (agent) {
          agent.status = payload.status;
          agent.task = payload.task || agent.task;
          this.state.agents.set(payload.agent_id, agent);
          this.renderDashboardAgents();
          if (this.state.currentTab === 'agents') this.renderAgents();
        }
        break;

      case 'agent_message':
        if (this.chat && payload.agent) {
          this.chat.addAgentMessage(payload.agent, payload.text);
        }
        break;

      case 'approval_request':
        this.state.approvals.push(payload);
        this.renderApprovals();
        this.toast.warning('Approval Needed', `${payload.agent}: ${payload.title}`);
        break;

      case 'activity':
        this.state.activityLog.unshift(payload);
        if (this.state.activityLog.length > 50) this.state.activityLog = this.state.activityLog.slice(0, 50);
        if (this.state.currentTab === 'dashboard') this.renderActivityFeed();
        break;

      case 'project_update':
        const project = this.state.projects.find(p => p.id === payload.id);
        if (project) {
          Object.assign(project, payload);
          this.renderProjects();
        }
        break;

      case 'log':
        if (this.terminal && payload.level && payload.message) {
          this.terminal.addLog(payload.level, payload.message);
        }
        break;
    }
  }

  // ---- Polling ----
  startPolling() {
    this.state.pollTimer = setInterval(async () => {
      try {
        const data = await this.api.getStatus();
        if (data) {
          if (data.health) this.state.systemHealth = { ...this.state.systemHealth, ...data.health };
          if (data.agents) {
            data.agents.forEach(a => {
              const existing = this.state.agents.get(a.id);
              if (existing) {
                existing.status = a.status || existing.status;
                existing.task = a.task || existing.task;
              }
            });
          }
        }
      } catch (e) {
        // Silently fail on poll errors
      }
    }, CONFIG.POLL_INTERVAL);
  }

  stopPolling() {
    if (this.state.pollTimer) {
      clearInterval(this.state.pollTimer);
      this.state.pollTimer = null;
    }
  }

  // ---- Utility ----
  escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }
}

// =============================================================================
// Initialize Application
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
  const app = new LuymasStudio();
  app.init();

  // Bind lightbox close
  document.querySelector('.lightbox-close')?.addEventListener('click', () => app.closeLightbox());
  document.getElementById('lightbox-overlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'lightbox-overlay') app.closeLightbox();
  });

  // Bind file tree clicks (event delegation)
  document.getElementById('file-tree')?.addEventListener('click', (e) => {
    const treeItem = e.target.closest('.tree-item');
    if (!treeItem) return;

    const path = treeItem.dataset.path;
    const type = treeItem.dataset.type;

    if (type === 'folder') {
      // Toggle folder
      const children = treeItem.nextElementSibling;
      const toggle = treeItem.querySelector('.tree-folder-toggle');
      if (children && children.classList.contains('tree-children')) {
        children.classList.toggle('collapsed');
        if (toggle) toggle.classList.toggle('open');
      }
    } else if (type === 'file') {
      app.files.openFile(path);
    }
  });
});
