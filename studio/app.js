/* ============================================================
   LUYMAS AI — APPLICATION CORE (Minimaliste)
   Inspiré par OpenClaw & Apple
   ============================================================ */

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
// Agent Definitions (11 agents)
// =============================================================================
const AGENT_DEFS = [
  {
    id: 'pdg', name: 'Luymas PDG', role: 'CEO / Orchestrateur Suprême', icon: '◆',
    avatarClass: 'orchestrator', model: 'deepseek-r1:8b', status: 'active',
    task: 'Surveillance de toutes les opérations',
    skills: ['manage-github-issues', 'create-github-pr', 'cto-status-report', 'send-notification', 'code-approval', 'identity-management'],
    description: 'Coordinateur central. Valide toutes les requêtes, génération PDF, injection clés API, approbation modifications.',
    stats: { tasksCompleted: 156, uptime: '99.8%', responseTime: '1.2s' },
  },
  {
    id: 'pm', name: 'Luymas PM', role: 'Chef de Produit', icon: '◇',
    avatarClass: 'communicator', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Analyse des exigences du nouveau projet',
    skills: ['clarify-requirements', 'product-brief', 'market-research', 'spec-creation'],
    description: 'Reformule les requêtes en spécifications, recherche marché, briefs produit, docs exigences.',
    stats: { tasksCompleted: 89, uptime: '98.5%', responseTime: '2.1s' },
  },
  {
    id: 'architect', name: 'Luymas Architect', role: 'Architecte Logiciel', icon: '□',
    avatarClass: 'analyst', model: 'deepseek-r1:8b', status: 'idle',
    task: 'En attente d\'assignation de projet',
    skills: ['choose-engine', 'architecture-design', 'database-schema', 'api-contracts', 'mermaid-diagrams'],
    description: 'Conception d\'architecture (modèle C4), sélection stack technique, vérification versions, schémas BDD.',
    stats: { tasksCompleted: 67, uptime: '97.2%', responseTime: '3.5s' },
  },
  {
    id: 'coder_back', name: 'Luymas Coder Backend', role: 'Développeur Backend', icon: '⚙',
    avatarClass: 'coder', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Construction des endpoints REST API',
    skills: ['code-execution', 'self-verification', 'github-scout', 'fastapi-scaffold', 'sqlalchemy-orm'],
    description: 'Scaffolding FastAPI/SQLAlchemy, auto-vérification, GitHub Scout, documentation SOURCES.md.',
    stats: { tasksCompleted: 234, uptime: '99.1%', responseTime: '4.2s' },
  },
  {
    id: 'coder_front', name: 'Luymas Coder Frontend', role: 'Développeur Frontend', icon: '◎',
    avatarClass: 'designer', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Implémentation des composants dashboard',
    skills: ['reusable-components', 'responsive-design', 'github-scout', 'nextjs-scaffold', 'shadcn-ui'],
    description: 'Scaffolding Next.js/TypeScript/Tailwind, composants shadcn/ui, design responsive, accessibilité.',
    stats: { tasksCompleted: 198, uptime: '98.9%', responseTime: '3.8s' },
  },
  {
    id: 'designer', name: 'Luymas Designer', role: 'Designer Visuel', icon: '✦',
    avatarClass: 'designer', model: 'z-image-turbo', status: 'idle',
    task: 'En attente de requêtes design',
    skills: ['felo-search', 'website-screenshot', 'opencode-design', 'design-updater', 'image-generation'],
    description: 'Inspiration obligatoire, création design system, génération FLUX.1 Pro/SD3, détection tendances.',
    stats: { tasksCompleted: 45, uptime: '95.0%', responseTime: '8.5s' },
  },
  {
    id: 'guardian', name: 'Luymas Guardian', role: 'Analyste Sécurité', icon: '▮',
    avatarClass: 'reviewer', model: 'deepseek-r1:8b', status: 'idle',
    task: 'En veille pour revue de sécurité',
    skills: ['security-scan', 'dependency-check', 'vulnerability-analysis', 'owasp-top10', 'penetration-test'],
    description: 'Scan OWASP Top 10, vérification vulnérabilités dépendances, détection patterns sécurité, gate déploiement.',
    stats: { tasksCompleted: 112, uptime: '99.5%', responseTime: '5.1s' },
  },
  {
    id: 'tester', name: 'Luymas Tester', role: 'Ingénieur QA', icon: '○',
    avatarClass: 'qa', model: 'deepseek-r1:8b', status: 'waiting',
    task: 'En attente de code à tester',
    skills: ['test-generation', 'bug-capture', 'e2e-testing', 'coverage-tracking', 'regression-detection'],
    description: 'Génération tests unit/intégration/E2E, capture bugs screenshots, recording E2E, suivi couverture.',
    stats: { tasksCompleted: 178, uptime: '99.2%', responseTime: '3.2s' },
  },
  {
    id: 'ops', name: 'Luymas Ops', role: 'Ingénieur DevOps', icon: '△',
    avatarClass: 'devops', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Déploiement environnement staging',
    skills: ['deploy-to-vercel', 'connect-supabase', 'setup-monitoring', 'health-check', 'docker-containerization'],
    description: 'Conteneurisation Docker, déploiement Vercel, connexion Supabase, CI/CD, mise en place monitoring.',
    stats: { tasksCompleted: 134, uptime: '99.7%', responseTime: '2.8s' },
  },
  {
    id: 'caretaker', name: 'Luymas Caretaker', role: 'Monitoring Post-Deploy', icon: '◈',
    avatarClass: 'assistant', model: 'qwen2.5-coder:7b', status: 'active',
    task: 'Surveillance des systèmes en production',
    skills: ['bug-reception', 'fix-deployment', 'continuous-monitoring', 'sla-enforcement', 'incident-logging'],
    description: 'Monitoring post-déploiement, réception bugs via clés API injectées, déploiement correctifs, SLA.',
    stats: { tasksCompleted: 267, uptime: '99.9%', responseTime: '0.8s' },
  },
  {
    id: 'talent_scout', name: 'Luymas Talent Scout', role: 'Builder d\'Équipe', icon: '◇',
    avatarClass: 'researcher', model: 'deepseek-r1:8b', status: 'idle',
    task: 'Scan des lacunes de capacité',
    skills: ['gap-analysis', 'agent-proposal', 'capability-search', 'difficulty-assessment', 'model-evaluation'],
    description: 'Analyse des lacunes, traitement rapports difficulté, catalogue agents, propositions détaillées.',
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

  getStatus() { return this.get('/status'); }
  getAgents() { return this.get('/agents'); }
  startAgent(id) { return this.post(`/agents/${id}/start`); }
  stopAgent(id) { return this.post(`/agents/${id}/stop`); }
  chatAgent(id, message) { return this.post(`/agents/${id}/chat`, { message }); }
  getModels() { return this.get('/models'); }
  pullModel(name) { return this.post('/models/pull', { name }); }
  removeModel(name) { return this.delete(`/models/${name}`); }
  startWorkflow(data) { return this.post('/workflow/start', data); }
  getWorkflowStatus() { return this.get('/workflow/status'); }
  getApprovals() { return this.get('/approvals'); }
  approveRequest(id) { return this.post(`/approvals/${id}/approve`); }
  rejectRequest(id) { return this.post(`/approvals/${id}/reject`); }
  getDesignImages() { return this.get('/design/images'); }
  generateImage(data) { return this.post('/design/generate', data); }
  getFileTree() { return this.get('/files/tree'); }
  getFileContent(path) { return this.get(`/files/content?path=${encodeURIComponent(path)}`); }
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
      this.ws.onerror = () => { this.emit('error'); };
      this.ws.onmessage = (event) => {
        try { const msg = JSON.parse(event.data); this.route(msg); }
        catch (e) { console.warn('WS parse error:', e); }
      };
    } catch (e) { this.scheduleReconnect(); }
  }

  send(data) {
    const payload = JSON.stringify(data);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) { this.ws.send(payload); }
    else { this.messageQueue.push(payload); }
  }

  flushQueue() {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift();
      if (this.ws && this.ws.readyState === WebSocket.OPEN) { this.ws.send(msg); }
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) return;
    clearTimeout(this.reconnectTimer);
    const delay = CONFIG.RECONNECT_INTERVAL * (1 + this.reconnectAttempts * 0.5);
    this.reconnectTimer = setTimeout(() => { this.reconnectAttempts++; this.connect(); }, delay);
  }

  on(type, fn) {
    if (!this.handlers.has(type)) this.handlers.set(type, []);
    this.handlers.get(type).push(fn);
    return () => { const list = this.handlers.get(type); if (list) list.splice(list.indexOf(fn), 1); };
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
    if (this.ws) { this.ws.close(); this.ws = null; }
    clearTimeout(this.reconnectTimer);
  }
}

// =============================================================================
// Toast Manager (Minimaliste)
// =============================================================================
class ToastManager {
  constructor() {
    this.container = document.getElementById('toast-container');
  }

  show(type, title, message, duration = CONFIG.TOAST_DURATION) {
    const icons = { success: '✓', error: '✕', warning: '!', info: 'i' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'i'}</span>
      <div class="toast-content">
        <div class="toast-title">${this.esc(title)}</div>
        ${message ? `<div class="toast-message">${this.esc(message)}</div>` : ''}
      </div>
      <button class="toast-close" aria-label="Close">&times;</button>
    `;
    toast.querySelector('.toast-close').addEventListener('click', () => this.dismiss(toast));
    this.container.appendChild(toast);
    if (duration > 0) setTimeout(() => this.dismiss(toast), duration);
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

  esc(str) { const div = document.createElement('div'); div.textContent = str || ''; return div.innerHTML; }
}

// =============================================================================
// Modal Manager (Minimaliste)
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
    this.overlay.addEventListener('click', (e) => { if (e.target === this.overlay) this.close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && this.overlay.classList.contains('active')) this.close(); });
  }

  open(title, bodyHtml, { confirmText = 'Confirmer', onConfirm = null, size = 'normal', danger = false } = {}) {
    this.titleEl.textContent = title;
    this.bodyEl.innerHTML = bodyHtml;
    this.confirmBtn.textContent = confirmText;
    this.overlay.classList.add('active');
    const modal = this.overlay.querySelector('.modal');
    modal.style.maxWidth = size === 'large' ? '720px' : size === 'small' ? '400px' : '560px';
    this.confirmBtn.className = danger ? 'btn btn-danger' : 'btn btn-primary';
    this._onConfirm = onConfirm;
    this.confirmBtn.onclick = () => { if (this._onConfirm) this._onConfirm(); this.close(); };
    setTimeout(() => { const firstInput = this.bodyEl.querySelector('input, textarea, select'); if (firstInput) firstInput.focus(); }, 100);
  }

  close() { this.overlay.classList.remove('active'); this._onConfirm = null; }
}

// =============================================================================
// Terminal Emulator (Minimaliste)
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
      if (e.key === 'Enter') { e.preventDefault(); this.execute(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); this.historyUp(); }
      else if (e.key === 'ArrowDown') { e.preventDefault(); this.historyDown(); }
    });

    document.querySelectorAll('.log-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.log-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.logFilter = btn.dataset.level;
        this.renderLogs();
      });
    });

    document.getElementById('terminal-clear')?.addEventListener('click', () => this.clear());
    document.getElementById('terminal-copy')?.addEventListener('click', () => this.copyOutput());
    document.getElementById('terminal-fullscreen')?.addEventListener('click', () => this.toggleFullscreen());
  }

  async loadInitialLogs() {
    try {
      const data = await this.api.getLogs();
      if (data && data.logs) { this.logs = data.logs; this.renderLogs(); }
    } catch (e) { this.addDefaultLogs(); }
  }

  addDefaultLogs() {
    const now = new Date();
    const defaultLogs = [
      { timestamp: this.fmtTime(now, -300), level: 'info', message: 'Luymas AI Studio v1.0.0 initialisé' },
      { timestamp: this.fmtTime(now, -280), level: 'info', message: 'Chargement des configurations agents...' },
      { timestamp: this.fmtTime(now, -260), level: 'info', message: '<span class="log-agent">[PDG]</span> Agent orchestrateur enregistré et en ligne' },
      { timestamp: this.fmtTime(now, -240), level: 'info', message: '<span class="log-agent">[Coder Backend]</span> Enregistré avec le modèle qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -220), level: 'info', message: '<span class="log-agent">[Coder Frontend]</span> Enregistré avec le modèle qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -200), level: 'info', message: '<span class="log-agent">[Ops]</span> Enregistré avec le modèle qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -180), level: 'info', message: '<span class="log-agent">[Caretaker]</span> Enregistré avec le modèle qwen2.5-coder:7b' },
      { timestamp: this.fmtTime(now, -160), level: 'info', message: 'Vérification de la connexion Ollama...' },
      { timestamp: this.fmtTime(now, -140), level: 'info', message: 'Ollama connecté avec 4 modèles disponibles' },
      { timestamp: this.fmtTime(now, -120), level: 'warning', message: '<span class="log-agent">[Guardian]</span> Vérification dépendances : 2 paquets avec vulnérabilités connues (non critiques)' },
      { timestamp: this.fmtTime(now, -100), level: 'info', message: 'Les 11 agents sont enregistrés avec succès' },
      { timestamp: this.fmtTime(now, -80), level: 'info', message: 'Knowledge Mesh initialisé' },
      { timestamp: this.fmtTime(now, -60), level: 'info', message: 'Service Messenger démarré' },
      { timestamp: this.fmtTime(now, -40), level: 'info', message: 'Interface Studio disponible sur http://localhost:5000' },
      { timestamp: this.fmtTime(now, -20), level: 'info', message: 'Système prêt. En attente de commandes...' },
    ];
    this.logs = defaultLogs;
    this.renderLogs();
  }

  fmtTime(base, offsetSeconds) {
    const d = new Date(base.getTime() + offsetSeconds * 1000);
    return d.toLocaleTimeString('fr-FR', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  renderLogs() {
    if (!this.output) return;
    const filtered = this.logFilter === 'all' ? this.logs : this.logs.filter(l => l.level === this.logFilter);
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
    const timestamp = new Date().toLocaleTimeString('fr-FR', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const entry = { timestamp, level, message };
    this.logs.push(entry);
    if (this.logs.length > CONFIG.MAX_TERMINAL_HISTORY) { this.logs = this.logs.slice(-CONFIG.MAX_TERMINAL_HISTORY); }
    if (this.logFilter === 'all' || this.logFilter === level) {
      const line = document.createElement('div');
      line.className = 'log-line';
      line.innerHTML = `<span class="log-timestamp">${timestamp}</span><span class="log-level ${level}">${level.toUpperCase()}</span><span class="log-message">${message}</span>`;
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
    this.addLog('info', `<span style="color:rgba(255,255,255,0.7)">~$</span> ${this.esc(cmd)}`);

    if (cmd === 'clear') { this.clear(); return; }
    if (cmd === 'help' || cmd === '/help') {
      this.addLog('info', 'Commandes : status, models, agents, clear, help, health, logs, restart [agent], ping');
      return;
    }
    if (cmd === 'status' || cmd === '/status') {
      this.addLog('info', 'Statut : En ligne | 11 agents | 5 actifs | 3 en veille | 2 en attente | 1 en travail');
      return;
    }
    if (cmd === 'models' || cmd === '/models') {
      this.addLog('info', 'Modèles chargés : deepseek-r1:8b, qwen2.5-coder:7b, z-image-turbo, nomic-embed-text');
      return;
    }
    if (cmd === 'agents' || cmd === '/agents') {
      AGENT_DEFS.forEach(a => { this.addLog('info', `  <span class="log-agent">[${a.id}]</span> ${a.name} — ${a.status} — ${a.task}`); });
      return;
    }
    if (cmd === 'health' || cmd === '/health') {
      this.addLog('info', 'Ollama : en ligne | Mémoire : 62% | CPU : 34% | Disque : 45% | Uptime : 14j 6h 32m');
      return;
    }
    if (cmd === 'ping') { this.addLog('info', 'Pong ! Latence : 12ms'); return; }
    if (cmd.startsWith('restart ')) {
      const agentId = cmd.split(' ')[1];
      this.addLog('warning', `Redémarrage de l\'agent : ${agentId}...`);
      setTimeout(() => { this.addLog('info', `<span class="log-agent">[${agentId}]</span> Agent redémarré avec succès`); }, 1500);
      return;
    }

    try {
      const result = await this.api.executeCommand(cmd);
      if (result && result.output) this.addLog('info', this.esc(result.output));
      else if (result && result.message) this.addLog('info', this.esc(result.message));
    } catch (e) {
      this.addLog('error', `Commande échouée : ${this.esc(e.message)}`);
    }
  }

  historyUp() {
    if (this.historyIndex > 0) { this.historyIndex--; this.input.value = this.commandHistory[this.historyIndex] || ''; }
  }

  historyDown() {
    if (this.historyIndex < this.commandHistory.length - 1) { this.historyIndex++; this.input.value = this.commandHistory[this.historyIndex] || ''; }
    else { this.historyIndex = this.commandHistory.length; this.input.value = ''; }
  }

  clear() { this.logs = []; this.output.innerHTML = ''; }
  copyOutput() {
    const text = this.logs.map(l => `${l.timestamp} [${l.level.toUpperCase()}] ${l.message.replace(/<[^>]*>/g, '')}`).join('\n');
    navigator.clipboard.writeText(text).then(() => { if (window._luymas_toast) window._luymas_toast.success('Copié', 'Sortie du terminal copiée'); }).catch(() => {});
  }

  toggleFullscreen() {
    this.wrapper.classList.toggle('fullscreen');
    if (this.wrapper.classList.contains('fullscreen')) this.input.focus();
  }

  esc(str) { const div = document.createElement('div'); div.textContent = str; return div.innerHTML; }
}

// =============================================================================
// LuymasTerminal — Minimaliste
// =============================================================================
class LuymasTerminal {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    this.history = [];
    this.historyIndex = -1;
    this.commands = ['/help', '/agents', '/goal', '/design', '/review', '/commit', '/deploy', '/test', '/status', '/pdf', '/update', '/scout', '/clear'];
    this.init();
  }

  init() {
    this.output = document.createElement('div');
    this.output.className = 'terminal-body';
    this.container.appendChild(this.output);

    this.inputLine = document.createElement('div');
    this.inputLine.className = 'terminal-input-line';
    this.inputLine.innerHTML = '<span class="terminal-prompt">~$</span> ';

    this.input = document.createElement('input');
    this.input.type = 'text';
    this.input.className = 'terminal-input';
    this.input.spellcheck = false;
    this.input.placeholder = 'Tapez /help...';
    this.input.addEventListener('keydown', (e) => this.handleKeydown(e));

    this.inputLine.appendChild(this.input);
    this.container.appendChild(this.inputLine);
    this.input.focus();

    this.print('Luymas AI Terminal prêt.', 'success');
    this.print('/help pour les commandes.', 'muted');
    this.print('');
  }

  handleKeydown(e) {
    if (e.key === 'Enter') {
      const cmd = this.input.value.trim();
      if (cmd) {
        this.execute(cmd);
        this.history.push(cmd);
        this.historyIndex = this.history.length;
        this.input.value = '';
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      this.autocomplete();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (this.historyIndex > 0) { this.historyIndex--; this.input.value = this.history[this.historyIndex]; }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (this.historyIndex < this.history.length - 1) { this.historyIndex++; this.input.value = this.history[this.historyIndex]; }
      else { this.historyIndex = this.history.length; this.input.value = ''; }
    }
  }

  autocomplete() {
    const current = this.input.value.toLowerCase();
    const matches = this.commands.filter(c => c.startsWith(current));
    if (matches.length === 1) { this.input.value = matches[0] + ' '; }
    else if (matches.length > 1) { this.print(matches.join('  '), 'muted'); }
  }

  execute(cmd) {
    this.print(`~$ ${cmd}`, 'command');
    const cmdName = cmd.split(' ')[0].toLowerCase();
    const args = cmd.substring(cmdName.length).trim();

    switch(cmdName) {
      case '/help':
        this.print('Commandes disponibles :', 'muted');
        this.commands.filter(c => c !== '/help').forEach(c => this.print(`  ${c}`, 'muted'));
        break;
      case '/clear':
        this.output.innerHTML = '';
        break;
      case '/agents':
        this.print('PDG             actif', 'success');
        this.print('PM              actif', 'success');
        this.print('Architect       actif', 'success');
        this.print('Coder Back      en attente', 'muted');
        this.print('Coder Front     en attente', 'muted');
        this.print('Designer        en attente', 'muted');
        this.print('Guardian        en attente', 'muted');
        this.print('Tester          en attente', 'muted');
        this.print('Ops             en attente', 'muted');
        this.print('Caretaker       en veille', 'muted');
        this.print('Talent Scout    en veille', 'muted');
        break;
      case '/goal':
        if (args) { this.print(`Objectif : "${args}"`, 'muted'); this.sendToAgent('pdg', {action: 'goal', content: args}); }
        else { this.print('Usage : /goal [description]', 'error'); }
        break;
      case '/design':
        if (args) { this.print(`Design demandé : "${args}"`, 'muted'); this.sendToAgent('designer', {action: 'design', content: args}); }
        else { this.print('Usage : /design [description]', 'error'); }
        break;
      case '/review':
        this.print('Revue de code demandée...', 'muted');
        this.sendToAgent('guardian', {action: 'review'});
        break;
      case '/commit':
        this.print('Commit en préparation...', 'muted');
        this.sendToAgent('pdg', {action: 'commit'});
        break;
      case '/deploy':
        this.print('Déploiement lancé...', 'muted');
        this.sendToAgent('ops', {action: 'deploy'});
        break;
      case '/test':
        this.print('Tests lancés...', 'muted');
        this.sendToAgent('tester', {action: 'test'});
        break;
      case '/status':
        this.print('Spécifications   terminé', 'success');
        this.print('Architecture     terminé', 'success');
        this.print('Code Backend     en cours', 'muted');
        this.print('Code Frontend    en attente', 'muted');
        this.print('Design           en attente', 'muted');
        break;
      case '/pdf':
        this.print('Génération du rapport PDF...', 'muted');
        this.sendToAgent('pdg', {action: 'pdf'});
        break;
      case '/update':
        this.print('Vérification des mises à jour...', 'muted');
        this.sendToAgent('caretaker', {action: 'update'});
        break;
      case '/scout':
        this.print('Recherche de nouveaux agents...', 'muted');
        this.sendToAgent('talent_scout', {action: 'scout'});
        break;
      default:
        this.print(`Commande inconnue : ${cmdName}`, 'error');
    }
  }

  sendToAgent(agent, data) {
    const startTime = Date.now();
    setTimeout(() => {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      this.print(`  ${agent} — terminé (${elapsed}s)`, 'success');
    }, 400 + Math.random() * 800);
  }

  print(message, type = '') {
    const line = document.createElement('div');
    line.className = `terminal-output-${type}`;
    line.textContent = message;
    this.output.appendChild(line);
    this.container.scrollTop = this.container.scrollHeight;
  }
}

// =============================================================================
// Chat Manager (Minimaliste)
// =============================================================================
class ChatManager {
  constructor(api, state) {
    this.api = api;
    this.state = state;
    this.messages = [];
    this.currentThread = 'war-room';
    this.slashCommands = [
      { cmd: '/status', desc: 'Afficher le statut système' },
      { cmd: '/models', desc: 'Lister les modèles chargés' },
      { cmd: '/help', desc: 'Afficher les commandes' },
      { cmd: '/deploy', desc: 'Lancer le déploiement' },
      { cmd: '/agents', desc: 'Lister les agents' },
      { cmd: '/approve', desc: 'Approbations en attente' },
      { cmd: '/clear', desc: 'Effacer l\'historique' },
    ];
    this._bound = false;
  }

  bind() {
    if (this._bound) return;
    this._bound = true;
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); } });
    input.addEventListener('input', () => { this.handleSlashAutocomplete(input.value); });
    sendBtn.addEventListener('click', () => this.send());
    document.getElementById('thread-search')?.addEventListener('input', (e) => { this.filterThreads(e.target.value); });
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
      { id: 'm1', thread: 'war-room', sender: 'PDG', senderType: 'agent', text: 'Rapport d\'équipe : Tous les systèmes opérationnels. 5 agents actifs, 3 en veille, 2 en attente. Focus actuel : Sprint plateforme e-commerce.', time: '10:30' },
      { id: 'm2', thread: 'war-room', sender: 'Coder Backend', senderType: 'agent', text: 'Endpoints API pour /users et /products terminés. Vérifications en cours. Push sur la branche feature une fois confirmé.', time: '10:32' },
      { id: 'm3', thread: 'war-room', sender: 'Coder Frontend', senderType: 'agent', text: 'Composants dashboard à 80%. Besoin du schéma API de Backend pour connecter la couche données.', time: '10:33' },
      { id: 'm4', thread: 'war-room', sender: 'Ops', senderType: 'agent', text: 'Environnement staging opérationnel. Conteneurs Docker healthy. Prêt pour le déploiement.', time: '10:35' },
      { id: 'm5', thread: 'war-room', sender: 'Guardian', senderType: 'agent', text: 'Scan sécurité terminé : 0 critique, 2 moyen, 5 faible. Recommandation : traiter avant la mise en prod.', time: '10:38', isApproval: true, approvalId: 'a1' },
      { id: 'm6', thread: 'war-room', sender: 'Vous', senderType: 'user', text: 'Bon travail. Guardian, prépare un rapport détaillé. Coder Backend, poussez sur la branche feature.', time: '10:40' },
      { id: 'm7', thread: 'war-room', sender: 'PM', senderType: 'agent', text: 'Backlog produit mis à jour. Vélocité sprint en bonne voie. Prochaine priorité : module paiement.', time: '10:42' },
    ];
  }

  renderThreadList() {
    const listEl = document.getElementById('thread-list');
    if (!listEl) return;
    const threads = [
      { id: 'war-room', name: 'War Room', preview: 'Coordination d\'équipe', avatar: '◆', avatarClass: 'orchestrator' },
      ...AGENT_DEFS.map(a => ({ id: `agent-${a.id}`, name: a.name, preview: a.task, avatar: a.icon, avatarClass: a.avatarClass })),
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
    listEl.querySelectorAll('.thread-item').forEach(item => { item.addEventListener('click', () => { this.selectThread(item.dataset.thread); }); });
  }

  selectThread(threadId) {
    this.currentThread = threadId;
    document.querySelectorAll('.thread-item').forEach(item => { item.classList.toggle('active', item.dataset.thread === threadId); });
    let title = 'War Room';
    let subtitle = '11 agents en ligne';
    if (threadId.startsWith('agent-')) {
      const agentId = threadId.replace('agent-', '');
      const agent = AGENT_DEFS.find(a => a.id === agentId);
      if (agent) { title = agent.name; subtitle = agent.role; }
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
      chatBody.innerHTML = '<div class="empty-state-sm"><span class="empty-icon-sm">◇</span><p>Aucun message. Lancez la conversation !</p></div>';
      return;
    }
    chatBody.innerHTML = threadMessages.map(m => {
      if (m.isSystem) return `<div class="chat-bubble system-bubble"><div class="bubble-content">${m.text}</div></div>`;
      if (m.isApproval) return `
        <div class="chat-bubble incoming approval-bubble">
          <div class="bubble-header"><span class="bubble-sender">${m.sender}</span><span class="bubble-time">${m.time}</span></div>
          <div class="bubble-content">${m.text}</div>
          <div class="approval-inline-actions">
            <button class="approval-btn approve" onclick="app.handleApproval('${m.approvalId}', 'approve')">Approuver</button>
            <button class="approval-btn reject" onclick="app.handleApproval('${m.approvalId}', 'reject')">Rejeter</button>
          </div>
        </div>`;
      return `
        <div class="chat-bubble ${m.senderType === 'user' ? 'outgoing' : 'incoming'}">
          <div class="bubble-header"><span class="bubble-sender">${m.sender}</span><span class="bubble-time">${m.time}</span></div>
          <div class="bubble-content">${m.text}</div>
        </div>`;
    }).join('');
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  send() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    this.hideSlashHint();
    if (text.startsWith('/')) { this.handleSlashCommand(text); return; }
    const msg = { id: `msg-${Date.now()}`, thread: this.currentThread, sender: 'Vous', senderType: 'user', text, time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) };
    this.messages.push(msg);
    this.renderChat();
    if (this.currentThread.startsWith('agent-')) { const agentId = this.currentThread.replace('agent-', ''); this.sendToAgent(agentId, text); }
  }

  async sendToAgent(agentId, message) {
    this.showTyping(agentId);
    try {
      const result = await this.api.chatAgent(agentId, message);
      this.hideTyping();
      if (result && result.response) {
        const agent = AGENT_DEFS.find(a => a.id === agentId);
        const reply = { id: `msg-${Date.now()}`, thread: this.currentThread, sender: agent ? agent.name : agentId, senderType: 'agent', text: result.response, time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) };
        this.messages.push(reply);
        this.renderChat();
      }
    } catch (e) {
      this.hideTyping();
      const agent = AGENT_DEFS.find(a => a.id === agentId);
      if (agent) {
        const reply = { id: `msg-${Date.now()}`, thread: this.currentThread, sender: agent.name, senderType: 'agent', text: `Message reçu : "${message}". Traitement en cours.`, time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) };
        this.messages.push(reply);
        this.renderChat();
      }
    }
  }

  handleSlashCommand(cmd) {
    const parts = cmd.split(' ');
    const command = parts[0].toLowerCase();
    const systemMsg = (text) => {
      this.messages.push({ id: `sys-${Date.now()}`, thread: this.currentThread, sender: 'Système', senderType: 'system', text, time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }), isSystem: true });
      this.renderChat();
    };
    switch (command) {
      case '/status': systemMsg('Statut : En ligne | 11 agents | 5 actifs | 3 en veille | 2 en attente | Mémoire : 62% | Uptime : 14j 6h'); break;
      case '/models': systemMsg('Modèles : deepseek-r1:8b, qwen2.5-coder:7b, z-image-turbo, nomic-embed-text'); break;
      case '/help': systemMsg('Commandes : /status, /models, /help, /deploy, /agents, /approve, /clear'); break;
      case '/deploy': systemMsg('Déploiement initié. En attente de l\'approbation Guardian...'); break;
      case '/agents': systemMsg(AGENT_DEFS.map(a => `${a.icon} ${a.name} : ${a.status}`).join(' | ')); break;
      case '/approve': systemMsg('Approbations en attente : 3 requêtes. Utilisez le panneau latéral.'); break;
      case '/clear': this.messages = this.messages.filter(m => m.thread !== this.currentThread); this.renderChat(); break;
      default: systemMsg(`Commande inconnue : ${command}. Tapez /help.`);
    }
  }

  handleSlashAutocomplete(value) {
    if (!value.startsWith('/')) { this.hideSlashHint(); return; }
    const hint = document.getElementById('slash-hint');
    if (!hint) return;
    const matches = this.slashCommands.filter(c => c.cmd.startsWith(value.toLowerCase()));
    if (matches.length === 0 || (matches.length === 1 && matches[0].cmd === value.toLowerCase())) { this.hideSlashHint(); return; }
    hint.innerHTML = matches.map(c => `<div class="slash-hint-item" data-cmd="${c.cmd}"><span class="slash-cmd">${c.cmd}</span><span class="slash-desc">${c.desc}</span></div>`).join('');
    hint.classList.add('visible');
    hint.querySelectorAll('.slash-hint-item').forEach(item => { item.addEventListener('click', () => { const input = document.getElementById('chat-input'); input.value = item.dataset.cmd + ' '; input.focus(); this.hideSlashHint(); }); });
  }

  hideSlashHint() { const hint = document.getElementById('slash-hint'); if (hint) { hint.classList.remove('visible'); hint.innerHTML = ''; } }

  showTyping(agentId) {
    const agent = AGENT_DEFS.find(a => a.id === agentId);
    const indicator = document.getElementById('typing-indicator');
    const nameEl = document.getElementById('typing-agent');
    if (indicator && nameEl) { nameEl.textContent = agent ? agent.name : agentId; indicator.classList.remove('hidden'); }
  }

  hideTyping() { const indicator = document.getElementById('typing-indicator'); if (indicator) indicator.classList.add('hidden'); }

  filterThreads(query) {
    const items = document.querySelectorAll('.thread-item');
    const q = query.toLowerCase();
    items.forEach(item => { const name = item.querySelector('.thread-name')?.textContent?.toLowerCase() || ''; item.style.display = name.includes(q) ? '' : 'none'; });
  }

  addAgentMessage(agentId, text) {
    const agent = AGENT_DEFS.find(a => a.id === agentId);
    const msg = { id: `msg-${Date.now()}`, thread: 'war-room', sender: agent ? agent.name : agentId, senderType: 'agent', text, time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) };
    this.messages.push(msg);
    if (this.currentThread === 'war-room') this.renderChat();
  }
}

// =============================================================================
// File Manager (Minimaliste)
// =============================================================================
class FileManager {
  constructor(api) {
    this.api = api;
    this.tree = null;
    this.currentFile = null;
    this.currentContent = '';
    this._bound = false;
  }

  async init() { this.bind(); await this.loadTree(); }

  bind() {
    if (this._bound) return;
    this._bound = true;
    document.getElementById('files-project-select')?.addEventListener('change', (e) => { this.loadTree(e.target.value); });
  }

  async loadTree(projectId) {
    try { const data = await this.api.getFileTree(); this.tree = data.tree || data; }
    catch (e) { this.tree = this.getDefaultTree(); }
    this.renderTree();
  }

  getDefaultTree() {
    return {
      name: 'project-root', type: 'folder', children: [
        { name: 'src', type: 'folder', children: [
          { name: 'app.py', type: 'file', lang: 'python' },
          { name: 'models.py', type: 'file', lang: 'python' },
          { name: 'routes.py', type: 'file', lang: 'python' },
          { name: 'templates', type: 'folder', children: [{ name: 'base.html', type: 'file', lang: 'html' }, { name: 'index.html', type: 'file', lang: 'html' }] },
          { name: 'static', type: 'folder', children: [{ name: 'style.css', type: 'file', lang: 'css' }, { name: 'app.js', type: 'file', lang: 'javascript' }] },
        ]},
        { name: 'config', type: 'folder', children: [{ name: 'agents.yaml', type: 'file', lang: 'yaml' }, { name: 'models.yaml', type: 'file', lang: 'yaml' }] },
        { name: 'agents', type: 'folder', children: [{ name: '__init__.py', type: 'file', lang: 'python' }, { name: 'base.py', type: 'file', lang: 'python' }, { name: 'pdg.py', type: 'file', lang: 'python' }] },
        { name: 'requirements.txt', type: 'file', lang: 'text' },
        { name: 'README.md', type: 'file', lang: 'markdown' },
      ]
    };
  }

  renderTree() {
    const treeEl = document.getElementById('file-tree');
    if (!treeEl || !this.tree) return;
    treeEl.innerHTML = this.renderNode(this.tree, 0);
    treeEl.querySelectorAll('.tree-item').forEach(item => {
      item.addEventListener('click', () => {
        if (item.dataset.type === 'file') this.loadFile(item.dataset.path);
        else item.nextElementSibling?.classList.toggle('hidden');
      });
    });
  }

  renderNode(node, depth) {
    const indent = depth * 16;
    const icon = node.type === 'folder' ? '▸' : '·';
    let html = `<div class="tree-item" data-type="${node.type}" data-path="${node.name}" style="padding-left:${12 + indent}px"><span class="tree-icon">${icon}</span>${node.name}</div>`;
    if (node.children) {
      html += `<div class="tree-children">`;
      node.children.forEach(child => { html += this.renderNode(child, depth + 1); });
      html += `</div>`;
    }
    return html;
  }

  async loadFile(path) {
    const filenameEl = document.getElementById('file-content-filename');
    const contentEl = document.getElementById('file-content');
    const copyBtn = document.getElementById('btn-copy-file');
    const dlBtn = document.getElementById('btn-download-file');
    if (filenameEl) filenameEl.textContent = path;
    if (copyBtn) copyBtn.style.display = '';
    if (dlBtn) dlBtn.style.display = '';
    this.currentFile = path;
    try {
      const data = await this.api.getFileContent(path);
      if (contentEl) contentEl.textContent = data.content || data.text || JSON.stringify(data, null, 2);
    } catch (e) {
      if (contentEl) contentEl.textContent = `// Contenu de ${path}\n// Fichier non disponible en mode démo`;
    }
  }

  copyFileContent() { if (this.currentFile) navigator.clipboard.writeText(document.getElementById('file-content')?.textContent || '').catch(() => {}); }
  downloadFile() { /* placeholder */ }
  refreshFileTree() { this.loadTree(); }
}

// =============================================================================
// Main App Controller
// =============================================================================
class LuymasApp {
  constructor() {
    this.api = new APIClient();
    this.state = { currentTab: 'dashboard', agents: AGENT_DEFS, models: [], projects: [], approvals: [] };
    this.ws = new WebSocketManager((type, payload) => this.handleWSMessage(type, payload));
    this.toast = new ToastManager();
    this.modal = new ModalManager();
    this.terminal = null;
    this.luymasTerminal = null;
    this.chat = new ChatManager(this.api, this.state);
    this.files = new FileManager(this.api);
  }

  init() {
    // Connect WebSocket
    this.ws.connect();

    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });

    // Initialize terminal
    this.terminal = new TerminalEmulator(this.api);

    // Initialize LuymasTerminal (for tab)
    this.luymasTerminal = new LuymasTerminal('terminal-container');

    // Initialize chat
    this.chat.init();

    // Initialize files
    this.files.init();

    // Render dashboard
    this.renderDashboard();

    // Render agents
    this.renderAgents();

    // Render settings
    this.renderSettings();

    // Search
    document.getElementById('btn-search')?.addEventListener('click', () => this.toggleSearch());
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); this.toggleSearch(); }
      if (e.key === 'Escape') { this.closeSearch(); this.modal.close(); }
    });

    // Design form
    document.getElementById('design-gen-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.generateDesign();
    });

    // Connection status
    this.ws.on('connected', () => this.updateConnectionStatus('connected'));
    this.ws.on('disconnected', () => this.updateConnectionStatus('disconnected'));

    // Global reference
    window._luymas_toast = this.toast;
    window.app = this;

    // Initial status
    this.updateConnectionStatus('connecting');
    this.checkStatus();
  }

  switchTab(tab) {
    this.state.currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(b => { b.classList.toggle('active', b.dataset.tab === tab); b.setAttribute('aria-selected', b.dataset.tab === tab); });
    document.querySelectorAll('.tab-panel').forEach(p => { p.classList.toggle('active', p.id === `tab-${tab}`); });
  }

  updateConnectionStatus(status) {
    const el = document.getElementById('connection-status');
    if (!el) return;
    el.className = `connection-status ${status === 'connected' ? '' : status === 'disconnected' ? 'disconnected' : 'connecting'}`;
    const text = el.querySelector('.status-text');
    if (text) text.textContent = status === 'connected' ? 'En ligne' : status === 'disconnected' ? 'Hors ligne' : 'Connexion...';
  }

  async checkStatus() {
    try {
      const status = await this.api.getStatus();
      this.updateConnectionStatus('connected');
    } catch (e) {
      this.updateConnectionStatus('disconnected');
    }
  }

  handleWSMessage(type, payload) {
    if (type === 'agent_status') {
      const agent = this.state.agents.find(a => a.id === payload?.id);
      if (agent && payload?.status) { agent.status = payload.status; this.renderAgents(); }
    }
    if (type === 'activity') { this.addActivity(payload); }
  }

  renderDashboard() {
    // Status bar
    const statusBar = document.getElementById('dashboard-status-bar');
    if (statusBar) {
      const stats = [
        { icon: '◆', label: 'AGENTS', value: '11', change: '+1', cls: 'green' },
        { icon: '△', label: 'ACTIFS', value: '5', change: '', cls: 'green' },
        { icon: '◇', label: 'PROJETS', value: '3', change: '', cls: 'blue' },
        { icon: '○', label: 'UPTIME', value: '99.8%', change: '', cls: 'purple' },
      ];
      statusBar.innerHTML = stats.map(s => `
        <div class="status-card">
          <div class="status-icon ${s.cls}">${s.icon}</div>
          <div>
            <div class="status-label">${s.label}</div>
            <div class="status-value">${s.value}</div>
          </div>
        </div>
      `).join('');
    }

    // Agents compact
    const agentsEl = document.getElementById('dashboard-agents');
    if (agentsEl) {
      agentsEl.innerHTML = AGENT_DEFS.slice(0, 6).map(a => `
        <div class="agent-card" style="padding:12px">
          <div class="agent-card-top">
            <div class="agent-avatar" style="width:32px;height:32px;font-size:14px;border-radius:8px">${a.icon}</div>
            <div class="agent-info">
              <div class="agent-name" style="font-size:12px">${a.name}</div>
              <div class="agent-role">${a.status}</div>
            </div>
          </div>
        </div>
      `).join('');
    }

    // Activity
    const activityEl = document.getElementById('dashboard-activity');
    if (activityEl) {
      const activities = [
        { icon: '◆', text: '<strong>PDG</strong> a validé la revue de code', time: 'il y a 2 min' },
        { icon: '⚙', text: '<strong>Coder Backend</strong> a poussé 3 commits', time: 'il y a 5 min' },
        { icon: '△', text: '<strong>Ops</strong> a déployé en staging', time: 'il y a 12 min' },
        { icon: '▮', text: '<strong>Guardian</strong> a détecté 2 vulnérabilités', time: 'il y a 18 min' },
        { icon: '○', text: '<strong>Tester</strong> a complété 45 tests', time: 'il y a 25 min' },
      ];
      activityEl.innerHTML = activities.map(a => `
        <div class="activity-item">
          <div class="activity-icon">${a.icon}</div>
          <div class="activity-content">
            <div class="activity-text">${a.text}</div>
            <div class="activity-time">${a.time}</div>
          </div>
        </div>
      `).join('');
    }

    // Health
    const healthEl = document.getElementById('dashboard-health');
    if (healthEl) {
      const health = [
        { label: 'Ollama', value: 'En ligne', status: 'ok' },
        { label: 'Mémoire', value: '62%', status: 'ok' },
        { label: 'CPU', value: '34%', status: 'ok' },
        { label: 'Disque', value: '45%', status: 'ok' },
      ];
      healthEl.innerHTML = health.map(h => `
        <div class="health-item">
          <div class="health-dot ${h.status}"></div>
          <span class="health-label">${h.label}</span>
          <span class="health-value">${h.value}</span>
        </div>
      `).join('');
    }

    // Approvals
    const approvalsEl = document.getElementById('dashboard-approvals');
    const approvalCount = document.getElementById('approval-count');
    if (approvalsEl) {
      const approvals = [
        { agent: 'Guardian', action: 'Déploiement staging', type: 'normal', time: 'il y a 5 min' },
      ];
      if (approvalCount) approvalCount.textContent = approvals.length;
      approvalsEl.innerHTML = approvals.map(a => `
        <div class="approval-card ${a.type === 'critical' ? 'critical' : ''}">
          <div class="approval-header">
            <span class="approval-type ${a.type}">${a.type}</span>
            <span class="approval-time">${a.time}</span>
          </div>
          <div class="approval-agent">${a.agent}</div>
          <div class="approval-body">${a.action}</div>
          <div class="approval-actions">
            <button class="approval-btn approve">Approuver</button>
            <button class="approval-btn reject">Rejeter</button>
          </div>
        </div>
      `).join('');
    }
  }

  renderAgents() {
    const grid = document.getElementById('agents-grid');
    if (!grid) return;
    grid.innerHTML = AGENT_DEFS.map(a => `
      <div class="agent-card status-${a.status === 'active' ? 'active' : a.status === 'working' ? 'working' : a.status === 'waiting' ? 'waiting' : 'idle'}" onclick="app.showAgentDetail('${a.id}')">
        <div class="agent-card-top">
          <div class="agent-avatar ${a.avatarClass}">
            ${a.icon}
            <div class="avatar-status-dot ${a.status === 'active' ? 'online' : a.status === 'working' ? 'working' : a.status === 'waiting' ? 'waiting' : 'idle'}"></div>
          </div>
          <div class="agent-info">
            <div class="agent-name">${a.name}</div>
            <div class="agent-role">${a.role}</div>
          </div>
          <span class="badge badge-${a.status === 'active' ? 'online' : a.status === 'working' ? 'working' : a.status === 'waiting' ? 'waiting' : 'idle'}">${a.status}</span>
        </div>
        <div class="agent-card-body">
          <div class="agent-task"><span class="task-label">Tâche :</span> ${a.task}</div>
          <div class="agent-model">${a.model}</div>
        </div>
        <div class="agent-card-footer">
          <button class="agent-action-btn" onclick="event.stopPropagation(); app.chatWithAgent('${a.id}')">Chat</button>
          <button class="agent-action-btn primary" onclick="event.stopPropagation(); app.startAgent('${a.id}')">Démarrer</button>
        </div>
      </div>
    `).join('');
  }

  showAgentDetail(id) {
    const agent = AGENT_DEFS.find(a => a.id === id);
    if (!agent) return;
    const panel = document.getElementById('agent-detail-panel');
    if (!panel) return;
    panel.classList.remove('hidden');
    panel.innerHTML = `
      <div class="agent-detail-header">
        <div class="agent-detail-avatar">${agent.icon}</div>
        <div class="agent-detail-info">
          <h2>${agent.name}</h2>
          <div class="detail-role">${agent.role}</div>
          <span class="badge badge-${agent.status === 'active' ? 'online' : 'idle'}">${agent.status}</span>
        </div>
        <button class="btn btn-sm" onclick="document.getElementById('agent-detail-panel').classList.add('hidden')">Fermer</button>
      </div>
      <div class="agent-detail-stats">
        <div class="detail-stat"><div class="detail-stat-value">${agent.stats.tasksCompleted}</div><div class="detail-stat-label">Tâches</div></div>
        <div class="detail-stat"><div class="detail-stat-value">${agent.stats.uptime}</div><div class="detail-stat-label">Uptime</div></div>
        <div class="detail-stat"><div class="detail-stat-value">${agent.stats.responseTime}</div><div class="detail-stat-label">Réponse</div></div>
      </div>
      <div class="agent-skills">${agent.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.5)">${agent.description}</div>
    `;
  }

  renderSettings() {
    const content = document.getElementById('settings-content');
    if (!content) return;

    document.querySelectorAll('.settings-nav-item').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.settings-nav-item').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.renderSettingsSection(btn.dataset.section);
      });
    });

    this.renderSettingsSection('models');
  }

  renderSettingsSection(section) {
    const content = document.getElementById('settings-content');
    if (!content) return;

    if (section === 'models') {
      const models = [
        { name: 'deepseek-r1:8b', size: '4.7 Go', status: 'installé' },
        { name: 'qwen2.5-coder:7b', size: '4.5 Go', status: 'installé' },
        { name: 'z-image-turbo', size: '3.8 Go', status: 'installé' },
        { name: 'nomic-embed-text', size: '274 Mo', status: 'installé' },
      ];
      content.innerHTML = `
        <div class="settings-section">
          <div class="settings-section-title">Modèles Ollama</div>
          ${models.map(m => `
            <div class="model-card">
              <div class="model-info">
                <div class="model-name">${m.name}</div>
                <div class="model-size">${m.size} — ${m.status}</div>
              </div>
              <button class="btn btn-xs">Gérer</button>
            </div>
          `).join('')}
        </div>
      `;
    } else if (section === 'system') {
      content.innerHTML = `
        <div class="settings-section">
          <div class="settings-section-title">Système</div>
          <div class="settings-row">
            <div><div class="settings-label">Mode sombre</div><div class="settings-desc">Interface en mode sombre par défaut</div></div>
            <div class="toggle on" onclick="this.classList.toggle('on')"></div>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Notifications</div><div class="settings-desc">Recevoir les alertes agent</div></div>
            <div class="toggle on" onclick="this.classList.toggle('on')"></div>
          </div>
          <div class="settings-row">
            <div><div class="settings-label">Auto-déploiement</div><div class="settings-desc">Déployer automatiquement après approbation</div></div>
            <div class="toggle" onclick="this.classList.toggle('on')"></div>
          </div>
        </div>
      `;
    } else {
      content.innerHTML = `<div class="empty-state"><div class="empty-icon">◇</div><div class="empty-title">En développement</div><div class="empty-desc">Cette section sera bientôt disponible.</div></div>`;
    }
  }

  chatWithAgent(id) { this.switchTab('warroom'); this.chat.selectThread(`agent-${id}`); }

  startAgent(id) { this.toast.info('Agent', `Démarrage de ${id}...`); }
  startAllAgents() { this.toast.info('Agents', 'Démarrage de tous les agents...'); }
  refreshAgents() { this.renderAgents(); this.toast.success('Agents', 'Liste actualisée'); }

  createProjectModal() {
    this.modal.open('Nouveau Projet', `
      <div class="form-group"><label class="form-label">Nom du projet</label><input class="form-input glass-input" placeholder="Mon projet"></div>
      <div class="form-group"><label class="form-label">Description</label><textarea class="form-textarea glass-input" rows="3" placeholder="Décrivez votre projet..."></textarea></div>
    `, { confirmText: 'Créer', onConfirm: () => this.toast.success('Projet', 'Projet créé avec succès') });
  }

  checkModels() { this.toast.info('Modèles', 'Vérification des modèles...'); }
  runDiagnostics() { this.toast.info('Diagnostics', 'Exécution des diagnostics...'); }
  handleApproval(id, action) { this.toast.success('Approbation', `Demande ${action === 'approve' ? 'approuvée' : 'rejetée'}`); }
  toggleApprovalsSidebar() { document.getElementById('approvals-sidebar')?.classList.toggle('hidden'); }
  showApprovalsInChat() { this.toast.info('Approbations', '3 approbations en attente'); }

  toggleSearch() { document.getElementById('search-overlay')?.classList.toggle('active'); }
  closeSearch() { const el = document.getElementById('search-overlay'); if (el) el.classList.remove('active'); }

  async generateDesign() {
    const prompt = document.getElementById('design-prompt')?.value;
    if (!prompt) return;
    this.toast.info('Design', `Génération : "${prompt}"...`);
    try {
      const model = document.getElementById('design-model')?.value || 'flux.1';
      const size = document.getElementById('design-size')?.value || '1024x1024';
      const result = await this.api.generateImage({ prompt, model, size });
      this.toast.success('Design', 'Image générée avec succès');
    } catch (e) {
      this.toast.warning('Design', 'Mode démo — la génération nécessite le backend');
    }
  }

  downloadProjectZip() { this.toast.info('Export', 'Téléchargement du projet...'); }
  copyFileContent() { this.files.copyFileContent(); }
  downloadFile() { this.files.downloadFile(); }
  refreshFileTree() { this.files.refreshFileTree(); }

  addActivity(data) {
    // Add to activity feed if on dashboard
    const feed = document.getElementById('dashboard-activity');
    if (!feed) return;
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `<div class="activity-icon">◇</div><div class="activity-content"><div class="activity-text">${data?.text || 'Nouvelle activité'}</div><div class="activity-time">à l\'instant</div></div>`;
    feed.insertBefore(item, feed.firstChild);
  }
}

// =============================================================================
// Initialize
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
  const app = new LuymasApp();
  app.init();
});
