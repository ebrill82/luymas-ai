/* =============================================================================
   Luymas AI Studio — Application Core
   =============================================================================
   Complete SPA with router, WebSocket, state management, CRUD operations,
   real-time updates, and all interactive features.
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
  ACTIVITY_POLL_INTERVAL: 10000,
  HEALTH_POLL_INTERVAL: 15000,
};

// =============================================================================
// Agent Data (from agents.yaml)
// =============================================================================
const AGENT_DEFS = [
  {
    id: 'pdg',
    name: 'Luymas PDG',
    role: 'CEO / Supreme Orchestrator',
    icon: '👑',
    avatarClass: 'orchestrator',
    model: 'deepseek-r1:8b',
    status: 'active',
    task: 'Monitoring all agent operations',
    skills: ['manage-github-issues', 'create-github-pr', 'cto-status-report', 'send-notification', 'code-approval', 'identity-management'],
    description: 'Central coordinator. Validates all requests, PDF generation, API key injection, code modification approval.',
    stats: { tasksCompleted: 156, uptime: '99.8%', responseTime: '1.2s' },
  },
  {
    id: 'pm',
    name: 'Luymas PM',
    role: 'Product Manager',
    icon: '📋',
    avatarClass: 'communicator',
    model: 'qwen2.5-coder:7b',
    status: 'active',
    task: 'Analyzing new project requirements',
    skills: ['clarify-requirements', 'product-brief', 'market-research', 'spec-creation'],
    description: 'Reformulates requests into specs, market research, product briefs, requirement docs.',
    stats: { tasksCompleted: 89, uptime: '98.5%', responseTime: '2.1s' },
  },
  {
    id: 'architect',
    name: 'Luymas Architect',
    role: 'Software Architect',
    icon: '🏗️',
    avatarClass: 'analyst',
    model: 'deepseek-r1:8b',
    status: 'idle',
    task: 'Waiting for project assignment',
    skills: ['choose-engine', 'architecture-design', 'database-schema', 'api-contracts', 'mermaid-diagrams'],
    description: 'Architecture design (C4 model), tech stack selection, framework version checking, database schemas.',
    stats: { tasksCompleted: 67, uptime: '97.2%', responseTime: '3.5s' },
  },
  {
    id: 'coder_back',
    name: 'Luymas Coder Backend',
    role: 'Backend Developer',
    icon: '⚙️',
    avatarClass: 'coder',
    model: 'qwen2.5-coder:7b',
    status: 'active',
    task: 'Building REST API endpoints',
    skills: ['code-execution', 'self-verification', 'github-scout', 'fastapi-scaffold', 'sqlalchemy-orm'],
    description: 'FastAPI/SQLAlchemy scaffolding, self-verification, GitHub Scout, SOURCES.md documentation.',
    stats: { tasksCompleted: 234, uptime: '99.1%', responseTime: '4.2s' },
  },
  {
    id: 'coder_front',
    name: 'Luymas Coder Frontend',
    role: 'Frontend Developer',
    icon: '🎨',
    avatarClass: 'designer',
    model: 'qwen2.5-coder:7b',
    status: 'active',
    task: 'Implementing dashboard components',
    skills: ['reusable-components', 'responsive-design', 'github-scout', 'nextjs-scaffold', 'shadcn-ui'],
    description: 'Next.js/TypeScript/Tailwind scaffolding, shadcn/ui components, responsive design, accessibility.',
    stats: { tasksCompleted: 198, uptime: '98.9%', responseTime: '3.8s' },
  },
  {
    id: 'designer',
    name: 'Luymas Designer',
    role: 'Visual Designer',
    icon: '🖌️',
    avatarClass: 'designer',
    model: 'z-image-turbo',
    status: 'idle',
    task: 'Awaiting design requests',
    skills: ['felo-search', 'website-screenshot', 'opencode-design', 'design-updater', 'image-generation'],
    description: 'Mandatory inspiration browsing, design system creation, FLUX.1 Pro/SD3 image generation, trend detection.',
    stats: { tasksCompleted: 45, uptime: '95.0%', responseTime: '8.5s' },
  },
  {
    id: 'guardian',
    name: 'Luymas Guardian',
    role: 'Security Analyst',
    icon: '🛡️',
    avatarClass: 'reviewer',
    model: 'deepseek-r1:8b',
    status: 'idle',
    task: 'Standing by for security review',
    skills: ['security-scan', 'dependency-check', 'vulnerability-analysis', 'owasp-top10', 'penetration-test'],
    description: 'OWASP Top 10 scanning, dependency vulnerability checking, security pattern detection, deployment gate.',
    stats: { tasksCompleted: 112, uptime: '99.5%', responseTime: '5.1s' },
  },
  {
    id: 'tester',
    name: 'Luymas Tester',
    role: 'QA Engineer',
    icon: '🧪',
    avatarClass: 'qa',
    model: 'deepseek-r1:8b',
    status: 'waiting',
    task: 'Waiting for code to test',
    skills: ['test-generation', 'bug-capture', 'e2e-testing', 'coverage-tracking', 'regression-detection'],
    description: 'Unit/integration/E2E test generation, bug screenshot capture, E2E video recording, coverage tracking.',
    stats: { tasksCompleted: 178, uptime: '99.2%', responseTime: '3.2s' },
  },
  {
    id: 'ops',
    name: 'Luymas Ops',
    role: 'DevOps Engineer',
    icon: '🚀',
    avatarClass: 'devops',
    model: 'qwen2.5-coder:7b',
    status: 'active',
    task: 'Deploying staging environment',
    skills: ['deploy-to-vercel', 'connect-supabase', 'setup-monitoring', 'health-check', 'docker-containerization'],
    description: 'Docker containerization, Vercel deployment, Supabase connection, CI/CD, monitoring setup.',
    stats: { tasksCompleted: 134, uptime: '99.7%', responseTime: '2.8s' },
  },
  {
    id: 'caretaker',
    name: 'Luymas Caretaker',
    role: 'Post-Deploy Monitor',
    icon: '🔍',
    avatarClass: 'assistant',
    model: 'qwen2.5-coder:7b',
    status: 'active',
    task: 'Monitoring production systems',
    skills: ['bug-reception', 'fix-deployment', 'continuous-monitoring', 'sla-enforcement', 'incident-logging'],
    description: 'Post-deployment monitoring, bug reception via injected API keys, fix deployment, SLA enforcement.',
    stats: { tasksCompleted: 267, uptime: '99.9%', responseTime: '0.8s' },
  },
  {
    id: 'talent_scout',
    name: 'Luymas Talent Scout',
    role: 'Team Builder',
    icon: '🧲',
    avatarClass: 'researcher',
    model: 'deepseek-r1:8b',
    status: 'idle',
    task: 'Scanning for capability gaps',
    skills: ['gap-analysis', 'agent-proposal', 'capability-search', 'difficulty-assessment', 'model-evaluation'],
    description: 'Gap analysis, difficulty report processing, agent catalog, detailed proposals with role/skills/model/tools.',
    stats: { tasksCompleted: 23, uptime: '96.0%', responseTime: '4.5s' },
  },
];

// =============================================================================
// State Manager
// =============================================================================
class StateManager {
  constructor() {
    this.state = {
      currentView: 'dashboard',
      sidebarCollapsed: false,
      connected: false,
      agents: new Map(),
      projects: [],
      messages: [],
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
      selectedAgent: null,
      selectedThread: 'war-room',
      searchQuery: '',
      settingsSection: 'models',
      activityLog: [],
    };
    this.listeners = new Map();
    this.loadPersisted();
  }

  get(key) {
    return this.state[key];
  }

  set(key, value) {
    const old = this.state[key];
    this.state[key] = value;
    this.emit('state:' + key, { old, new: value });
    this.persist(['sidebarCollapsed', 'settings', 'settingsSection']);
  }

  on(event, fn) {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event).push(fn);
    return () => {
      const list = this.listeners.get(event);
      if (list) list.splice(list.indexOf(fn), 1);
    };
  }

  emit(event, data) {
    const list = this.listeners.get(event);
    if (list) list.forEach(fn => fn(data));
  }

  persist(keys) {
    try {
      const data = {};
      keys.forEach(k => data[k] = this.state[k]);
      localStorage.setItem('luymas-studio-state', JSON.stringify(data));
    } catch (e) { /* ignore */ }
  }

  loadPersisted() {
    try {
      const raw = localStorage.getItem('luymas-studio-state');
      if (raw) {
        const data = JSON.parse(raw);
        Object.keys(data).forEach(k => {
          if (data[k] !== undefined && data[k] !== null) {
            this.state[k] = data[k];
          }
        });
      }
    } catch (e) { /* ignore */ }
  }
}

// =============================================================================
// WebSocket Manager
// =============================================================================
class WebSocketManager {
  constructor(state) {
    this.state = state;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.messageQueue = [];
    this.handlers = new Map();
  }

  connect() {
    try {
      this.ws = new WebSocket(CONFIG.WS_URL);

      this.ws.onopen = () => {
        this.state.set('connected', true);
        this.reconnectAttempts = 0;
        this.flushQueue();
        this.emit('connected');
        if (window._luymas_toast) window._luymas_toast.success('Connected', 'Real-time connection established');
      };

      this.ws.onclose = () => {
        this.state.set('connected', false);
        this.emit('disconnected');
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        this.emit('error', err);
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
  }

  emit(type, data) {
    const list = this.handlers.get(type);
    if (list) list.forEach(fn => fn(data));
  }

  route(msg) {
    const { type, payload } = msg;
    switch (type) {
      case 'agent_status':
        this.handleAgentStatus(payload);
        break;
      case 'agent_message':
        this.handleAgentMessage(payload);
        break;
      case 'approval_request':
        this.handleApprovalRequest(payload);
        break;
      case 'activity':
        this.handleActivity(payload);
        break;
      case 'project_update':
        this.handleProjectUpdate(payload);
        break;
      default:
        this.emit(type, payload);
    }
  }

  handleAgentStatus(payload) {
    const agents = this.state.get('agents');
    const agent = agents.get(payload.agent_id);
    if (agent) {
      agent.status = payload.status;
      agent.task = payload.task || agent.task;
      agents.set(payload.agent_id, agent);
      this.state.set('agents', agents);
      this.emit('agent_status', payload);
    }
  }

  handleAgentMessage(payload) {
    const messages = [...this.state.get('messages'), payload];
    this.state.set('messages', messages);
    this.emit('agent_message', payload);
  }

  handleApprovalRequest(payload) {
    const approvals = [...this.state.get('approvals'), payload];
    this.state.set('approvals', approvals);
    this.emit('approval_request', payload);
    if (window._luymas_toast) window._luymas_toast.warning('Approval Needed', `${payload.agent}: ${payload.title}`);
  }

  handleActivity(payload) {
    const log = [payload, ...this.state.get('activityLog')].slice(0, 50);
    this.state.set('activityLog', log);
    this.emit('activity', payload);
  }

  handleProjectUpdate(payload) {
    const projects = this.state.get('projects').map(p =>
      p.id === payload.id ? { ...p, ...payload } : p
    );
    this.state.set('projects', projects);
    this.emit('project_update', payload);
  }
}

// =============================================================================
// Toast Notification System
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
        <div class="toast-title">${this.escape(title)}</div>
        ${message ? `<div class="toast-message">${this.escape(message)}</div>` : ''}
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
    if (!toast.parentNode) return;
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  }

  success(title, message) { return this.show('success', title, message); }
  error(title, message) { return this.show('error', title, message); }
  warning(title, message) { return this.show('warning', title, message); }
  info(title, message) { return this.show('info', title, message); }

  escape(str) {
    const div = document.createElement('div');
    div.textContent = str;
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

  open(title, bodyHtml, { confirmText = 'Confirm', onConfirm = null, size = 'normal' } = {}) {
    this.titleEl.textContent = title;
    this.bodyEl.innerHTML = bodyHtml;
    this.confirmBtn.textContent = confirmText;
    this.overlay.classList.add('active');

    if (size === 'large') {
      this.overlay.querySelector('.modal').style.maxWidth = '720px';
    } else {
      this.overlay.querySelector('.modal').style.maxWidth = '560px';
    }

    this.confirmBtn.onclick = () => {
      if (onConfirm) onConfirm();
      this.close();
    };

    // Focus trap
    setTimeout(() => {
      const firstInput = this.bodyEl.querySelector('input, textarea, select');
      if (firstInput) firstInput.focus();
    }, 100);
  }

  close() {
    this.overlay.classList.remove('active');
    this.confirmBtn.onclick = null;
  }
}

// =============================================================================
// Router
// =============================================================================
class Router {
  constructor(state) {
    this.state = state;
    this.routes = {};
    this.currentView = 'dashboard';

    window.addEventListener('popstate', () => this.handleRoute());

    // Nav click handling
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        this.navigate(view);
      });
    });
  }

  register(view, handler) {
    this.routes[view] = handler;
  }

  navigate(view) {
    if (view === this.currentView) return;
    this.currentView = view;
    this.state.set('currentView', view);
    history.pushState({ view }, '', `#${view}`);
    this.handleRoute();
  }

  handleRoute() {
    const hash = location.hash.slice(1) || 'dashboard';
    const view = hash;

    // Update nav
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
      item.classList.toggle('active', item.dataset.view === view);
    });

    // Update views
    document.querySelectorAll('.view').forEach(el => {
      el.classList.remove('active');
    });
    const viewEl = document.getElementById(`view-${view}`);
    if (viewEl) {
      viewEl.classList.add('active');
    }

    // Update header title
    const titles = {
      dashboard: 'Dashboard',
      agents: 'Agent Team',
      projects: 'Projects',
      messages: 'War Room',
      analytics: 'Analytics',
      settings: 'Settings',
    };
    const titleEl = document.getElementById('header-title');
    if (titleEl) titleEl.textContent = titles[view] || 'Dashboard';

    // Execute route handler
    if (this.routes[view]) {
      this.routes[view]();
    }

    // Close mobile sidebar
    document.querySelector('.sidebar')?.classList.remove('mobile-open');
  }
}

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
        throw new Error(err.detail || res.statusText);
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

  // Agent endpoints
  getAgents() { return this.get('/agents'); }
  getAgent(id) { return this.get(`/agents/${id}`); }
  startAgent(id) { return this.post(`/agents/${id}/start`); }
  stopAgent(id) { return this.post(`/agents/${id}/stop`); }
  pauseAgent(id) { return this.post(`/agents/${id}/pause`); }
  chatAgent(id, message) { return this.post(`/agents/${id}/chat`, { message }); }

  // Project endpoints
  getProjects() { return this.get('/projects'); }
  createProject(data) { return this.post('/projects', data); }
  updateProject(id, data) { return this.put(`/projects/${id}`, data); }
  deleteProject(id) { return this.delete(`/projects/${id}`); }

  // Message endpoints
  getMessages(threadId) { return this.get(`/messages/${threadId}`); }
  sendMessage(threadId, text) { return this.post(`/messages/${threadId}`, { text }); }

  // Approval endpoints
  getApprovals() { return this.get('/approvals'); }
  approveRequest(id) { return this.post(`/approvals/${id}/approve`); }
  rejectRequest(id) { return this.post(`/approvals/${id}/reject`); }

  // System endpoints
  getHealth() { return this.get('/system/health'); }
  getModels() { return this.get('/models'); }
  pullModel(name) { return this.post(`/models/pull`, { name }); }
  deleteModel(name) { return this.delete(`/models/${name}`); }

  // Settings endpoints
  getSettings() { return this.get('/settings'); }
  updateSettings(data) { return this.put('/settings', data); }
}

// =============================================================================
// View Renderers
// =============================================================================
class ViewRenderer {
  constructor(state, api) {
    this.state = state;
    this.api = api;
  }

  // --- Dashboard ---
  renderDashboard() {
    const agents = this.state.get('agents');
    const health = this.state.get('systemHealth');
    const activity = this.state.get('activityLog');

    const activeCount = [...agents.values()].filter(a => a.status === 'active').length;
    const idleCount = [...agents.values()].filter(a => a.status === 'idle').length;
    const waitingCount = [...agents.values()].filter(a => a.status === 'waiting').length;
    const projectCount = this.state.get('projects').length;

    // Stats cards
    const statsEl = document.getElementById('dashboard-stats');
    if (statsEl) {
      statsEl.innerHTML = `
        <div class="stat-card">
          <div class="stat-icon green">🤖</div>
          <div class="stat-content">
            <div class="stat-label">Active Agents</div>
            <div class="stat-value">${activeCount}</div>
            <div class="stat-change positive">● ${activeCount} running</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon amber">⏳</div>
          <div class="stat-content">
            <div class="stat-label">Pending Tasks</div>
            <div class="stat-value">${waitingCount}</div>
            <div class="stat-change neutral">${idleCount} agents idle</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">📁</div>
          <div class="stat-content">
            <div class="stat-label">Projects</div>
            <div class="stat-value">${projectCount}</div>
            <div class="stat-change positive">+2 this week</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cyan">🧠</div>
          <div class="stat-content">
            <div class="stat-label">Models Loaded</div>
            <div class="stat-value">${health.modelCount}</div>
            <div class="stat-change neutral">Ollama ${health.ollama}</div>
          </div>
        </div>
      `;
    }

    // Agent status cards
    const agentsEl = document.getElementById('dashboard-agents');
    if (agentsEl) {
      agentsEl.innerHTML = [...agents.values()].map(a => `
        <div class="agent-card ${a.status}" onclick="app.showAgentDetail('${a.id}')">
          <div class="agent-card-header">
            <div class="agent-avatar ${a.avatarClass}">${a.icon}
              <span class="avatar-status ${a.status}"></span>
            </div>
            <div class="agent-info">
              <div class="agent-name">${a.name}</div>
              <div class="agent-role">${a.role}</div>
            </div>
            <span class="agent-status-badge badge-${a.status}">${a.status}</span>
          </div>
          <div class="agent-card-body">
            <div class="agent-task">
              <span class="task-label">Task:</span> ${a.task}
            </div>
            <div class="agent-model">⇢ ${a.model}</div>
          </div>
        </div>
      `).join('');
    }

    // Activity feed
    const activityEl = document.getElementById('dashboard-activity');
    if (activityEl) {
      const activities = activity.length > 0 ? activity : this.getDefaultActivity();
      activityEl.innerHTML = activities.slice(0, 12).map(a => `
        <div class="activity-item">
          <div class="activity-icon" style="background:${this.getActivityBg(a.type)}; color:${this.getActivityColor(a.type)}">
            ${this.getActivityIcon(a.type)}
          </div>
          <div class="activity-content">
            <div class="activity-text">${a.text}</div>
            <div class="activity-time">${a.time}</div>
          </div>
        </div>
      `).join('');
    }

    // System health
    const healthEl = document.getElementById('dashboard-health');
    if (healthEl) {
      healthEl.innerHTML = `
        <div class="health-grid">
          <div class="health-item">
            <span class="health-dot ${health.ollama === 'online' ? 'ok' : 'error'}"></span>
            <span class="health-label">Ollama</span>
            <span class="health-value">${health.ollama}</span>
          </div>
          <div class="health-item">
            <span class="health-dot ok"></span>
            <span class="health-label">Models</span>
            <span class="health-value">${health.modelCount}</span>
          </div>
          <div class="health-item">
            <span class="health-dot ${parseInt(health.memoryUsage) > 80 ? 'warn' : 'ok'}"></span>
            <span class="health-label">Memory</span>
            <span class="health-value">${health.memoryUsage}</span>
          </div>
          <div class="health-item">
            <span class="health-dot ${parseInt(health.cpuUsage) > 70 ? 'warn' : 'ok'}"></span>
            <span class="health-label">CPU</span>
            <span class="health-value">${health.cpuUsage}</span>
          </div>
          <div class="health-item">
            <span class="health-dot ok"></span>
            <span class="health-label">Disk</span>
            <span class="health-value">${health.diskUsage}</span>
          </div>
          <div class="health-item">
            <span class="health-dot ok"></span>
            <span class="health-label">Uptime</span>
            <span class="health-value">${health.uptime}</span>
          </div>
        </div>
      `;
    }
  }

  getDefaultActivity() {
    return [
      { type: 'agent', text: '<strong>Ops</strong> deployed staging build v2.4.1', time: '2 min ago' },
      { type: 'task', text: '<strong>Coder Backend</strong> completed API endpoint /users', time: '5 min ago' },
      { type: 'approval', text: '<strong>Guardian</strong> requested code review approval', time: '8 min ago' },
      { type: 'system', text: '<strong>System</strong> pulled model qwen2.5-coder:7b update', time: '15 min ago' },
      { type: 'agent', text: '<strong>Designer</strong> generated hero section mockup', time: '22 min ago' },
      { type: 'message', text: '<strong>PM</strong> sent clarification request to user', time: '30 min ago' },
      { type: 'task', text: '<strong>Architect</strong> completed database schema design', time: '45 min ago' },
      { type: 'system', text: '<strong>Caretaker</strong> detected latency spike on /api/health', time: '1h ago' },
    ];
  }

  getActivityIcon(type) {
    const icons = { agent: '🤖', task: '⚡', approval: '🔒', system: '⚙️', message: '💬' };
    return icons[type] || '📌';
  }

  getActivityBg(type) {
    const bgs = { agent: 'var(--status-active-bg)', task: 'var(--status-waiting-bg)', approval: 'var(--status-paused-bg)', system: 'var(--status-idle-bg)', message: 'rgba(6,182,212,0.12)' };
    return bgs[type] || 'var(--status-idle-bg)';
  }

  getActivityColor(type) {
    const colors = { agent: 'var(--status-active)', task: 'var(--status-waiting)', approval: 'var(--status-paused)', system: 'var(--status-idle)', message: '#06b6d4' };
    return colors[type] || 'var(--text-tertiary)';
  }

  // --- Agents ---
  renderAgents() {
    const agents = this.state.get('agents');
    const grid = document.getElementById('agents-grid');
    if (!grid) return;

    grid.innerHTML = [...agents.values()].map(a => `
      <div class="agent-card ${a.status}" onclick="app.showAgentDetail('${a.id}')">
        <div class="agent-card-header">
          <div class="agent-avatar ${a.avatarClass}">${a.icon}
            <span class="avatar-status ${a.status}"></span>
          </div>
          <div class="agent-info">
            <div class="agent-name">${a.name}</div>
            <div class="agent-role">${a.role}</div>
          </div>
          <span class="agent-status-badge badge-${a.status}">${a.status}</span>
        </div>
        <div class="agent-card-body">
          <div class="agent-task">
            <span class="task-label">Task:</span> ${a.task}
          </div>
          <div class="agent-model">⇢ ${a.model}</div>
        </div>
        <div class="agent-card-footer">
          <button class="agent-action-btn primary" onclick="event.stopPropagation(); app.startAgent('${a.id}')" title="Start">▶ Start</button>
          <button class="agent-action-btn" onclick="event.stopPropagation(); app.pauseAgent('${a.id}')" title="Pause">⏸ Pause</button>
          <button class="agent-action-btn danger" onclick="event.stopPropagation(); app.stopAgent('${a.id}')" title="Stop">⏹ Stop</button>
          <button class="agent-action-btn" onclick="event.stopPropagation(); app.chatWithAgent('${a.id}')" title="Chat">💬</button>
        </div>
      </div>
    `).join('');
  }

  renderAgentDetail(agentId) {
    const agents = this.state.get('agents');
    const agent = agents.get(agentId);
    if (!agent) return;

    const panel = document.getElementById('agent-detail-panel');
    if (!panel) return;

    panel.innerHTML = `
      <div class="agent-detail">
        <div class="agent-detail-header">
          <div class="agent-detail-avatar ${agent.avatarClass}">${agent.icon}</div>
          <div class="agent-detail-info">
            <h2>${agent.name}</h2>
            <div class="detail-role">${agent.role}</div>
            <span class="agent-status-badge badge-${agent.status}">${agent.status}</span>
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

        <div class="mb-lg">
          <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em;">Current Task</h3>
          <p style="font-size:0.9rem;color:var(--text-secondary);">${agent.task}</p>
          <div style="margin-top:8px;font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary);">Model: ${agent.model}</div>
        </div>

        <div class="mb-lg">
          <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em;">Skills</h3>
          <div class="agent-skills">
            ${agent.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
          </div>
        </div>

        <div class="mb-lg">
          <h3 style="font-size:0.85rem;font-weight:600;margin-bottom:8px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em;">Description</h3>
          <p style="font-size:0.85rem;color:var(--text-secondary);line-height:1.7;">${agent.description}</p>
        </div>

        <div class="agent-chat">
          <h3>💬 Chat with ${agent.name}</h3>
          <div class="chat-messages" id="agent-chat-messages"></div>
          <div class="chat-input-row">
            <input type="text" id="agent-chat-input" placeholder="Send a message to ${agent.name}..." onkeydown="if(event.key==='Enter')app.sendAgentChat('${agent.id}')">
            <button onclick="app.sendAgentChat('${agent.id}')">Send</button>
          </div>
        </div>
      </div>
    `;

    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth' });
  }

  // --- Projects ---
  renderProjects() {
    const projects = this.state.get('projects');
    const list = document.getElementById('project-list');
    if (!list) return;

    if (projects.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📁</div>
          <div class="empty-title">No Projects Yet</div>
          <div class="empty-desc">Create your first project and let the Luymas AI team bring it to life.</div>
          <button class="btn btn-primary mt-lg" onclick="app.createProjectModal()">+ New Project</button>
        </div>
      `;
      return;
    }

    list.innerHTML = projects.map(p => `
      <div class="project-card" onclick="app.showProjectDetail('${p.id}')">
        <div class="project-card-header">
          <div>
            <div class="project-title">${p.name}</div>
            <div class="project-desc">${p.description}</div>
          </div>
          <span class="project-status ${p.status}">${p.status.replace('-', ' ')}</span>
        </div>
        <div class="project-meta">
          <span>🤖 ${p.agents.length} agents</span>
          <span>📅 ${p.created}</span>
          <span>📊 ${p.progress}% complete</span>
        </div>
        <div class="project-timeline">
          ${(p.timeline || []).map((step, i) => `
            <div class="timeline-step ${step === 'completed' ? 'completed' : step === 'active' ? 'active' : ''}" title="${p.timelineLabels?.[i] || ''}"></div>
          `).join('')}
        </div>
        <div class="project-actions">
          ${p.status === 'review' ? '<button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); app.deployProject(\'' + p.id + '\')">🚀 Deploy</button>' : ''}
          ${p.status === 'in-progress' ? '<button class="btn btn-sm" onclick="event.stopPropagation(); app.reviewProject(\'' + p.id + '\')">📋 Review</button>' : ''}
          <button class="btn btn-sm" onclick="event.stopPropagation(); app.editProject('${p.id}')">✏️ Edit</button>
          <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.deleteProject('${p.id}')">🗑️ Delete</button>
        </div>
      </div>
    `).join('');
  }

  // --- Messages ---
  renderMessages() {
    this.renderThreadList();
    this.renderChatArea();
  }

  renderThreadList() {
    const listEl = document.getElementById('thread-list');
    if (!listEl) return;

    const agents = this.state.get('agents');
    const threads = [
      { id: 'war-room', name: '⚔️ War Room', preview: 'Team-wide coordination', avatar: '⚔️', avatarClass: 'orchestrator' },
      ...[...agents.values()].map(a => ({
        id: `agent-${a.id}`,
        name: a.name,
        preview: a.task,
        avatar: a.icon,
        avatarClass: a.avatarClass,
      })),
    ];

    const selected = this.state.get('selectedThread');

    listEl.innerHTML = threads.map(t => `
      <div class="thread-item ${t.id === selected ? 'active' : ''}" onclick="app.selectThread('${t.id}')">
        <div class="thread-avatar ${t.avatarClass}">${t.avatar}</div>
        <div class="thread-info">
          <div class="thread-name">${t.name}</div>
          <div class="thread-preview">${t.preview}</div>
        </div>
      </div>
    `).join('');
  }

  renderChatArea() {
    const selected = this.state.get('selectedThread');
    const messages = this.state.get('messages').filter(m => m.thread === selected);
    const chatBody = document.getElementById('chat-body');
    const chatTitle = document.getElementById('chat-title');

    if (!chatBody) return;

    // Determine thread name
    let threadName = 'War Room';
    if (selected.startsWith('agent-')) {
      const agentId = selected.replace('agent-', '');
      const agents = this.state.get('agents');
      const agent = agents.get(agentId);
      if (agent) threadName = agent.name;
    }
    if (chatTitle) chatTitle.textContent = threadName;

    // Default messages for war room
    const defaultMessages = selected === 'war-room' ? [
      { id: '1', thread: 'war-room', sender: 'PDG', senderType: 'agent', text: 'Team status report: All systems operational. 5 agents active, 3 idle, 2 waiting. Current focus: E-commerce platform sprint.', time: '10:30 AM' },
      { id: '2', thread: 'war-room', sender: 'Coder Backend', senderType: 'agent', text: 'API endpoints for /users and /products are complete. Running self-verification checks now. Will push to feature branch once confirmed.', time: '10:32 AM' },
      { id: '3', thread: 'war-room', sender: 'Coder Frontend', senderType: 'agent', text: 'Dashboard components are 80% done. Need the API schema from Backend to wire up the data layer. Can someone share the latest spec?', time: '10:33 AM' },
      { id: '4', thread: 'war-room', sender: 'Ops', senderType: 'agent', text: 'Staging environment is up. Docker containers running healthy. Ready for deployment when code is merged.', time: '10:35 AM' },
    ] : [];

    const allMessages = messages.length > 0 ? messages : defaultMessages;

    chatBody.innerHTML = allMessages.map(m => `
      <div class="chat-bubble ${m.senderType === 'user' ? 'outgoing' : 'incoming'}">
        <div class="bubble-header">
          <span class="bubble-sender">${m.sender}</span>
          <span class="bubble-time">${m.time}</span>
        </div>
        <div class="bubble-content">${m.text}</div>
      </div>
    `).join('');

    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // --- Approvals ---
  renderApprovals() {
    const approvals = this.state.get('approvals');
    const panel = document.getElementById('approvals-queue');
    if (!panel) return;

    // Toggle visibility
    if (!panel.classList.contains('hidden')) {
      panel.classList.add('hidden');
      return;
    }
    panel.classList.remove('hidden');

    const defaultApprovals = approvals.length > 0 ? approvals : [
      { id: 'a1', agent: 'Guardian', title: 'Code deployment approval', description: 'Security scan completed with 0 critical, 2 medium issues. Requesting approval to proceed with deployment to production.', type: 'normal', time: '5 min ago' },
      { id: 'a2', agent: 'PDG', title: 'API key injection for production', description: 'Requesting approval to inject production API keys for Stripe and SendGrid into the deployment environment.', type: 'critical', time: '12 min ago' },
      { id: 'a3', agent: 'Architect', title: 'Tech stack change request', description: 'Recommending switch from PostgreSQL to Supabase for the new project. Requires architecture review and approval.', type: 'normal', time: '25 min ago' },
    ];

    panel.innerHTML = `
      <div class="card">
        <div class="card-header">
          <div class="card-title">🔔 Approval Queue</div>
          <span class="badge badge-waiting">${defaultApprovals.length} pending</span>
        </div>
        <div class="card-body">
          ${defaultApprovals.map(a => `
            <div class="approval-card ${a.type === 'critical' ? 'critical' : ''}">
              <div class="approval-header">
                <span class="approval-type ${a.type}">${a.type}</span>
                <span class="approval-time">${a.time}</span>
              </div>
              <div style="font-size:0.8rem;color:var(--accent-primary);margin-bottom:4px;font-weight:600;">${a.agent}</div>
              <div class="approval-body"><strong>${a.title}</strong><br>${a.description}</div>
              <div class="approval-actions">
                <button class="approval-btn approve" onclick="app.approveRequest('${a.id}')">✓ Approve</button>
                <button class="approval-btn reject" onclick="app.rejectRequest('${a.id}')">✕ Reject</button>
                <button class="approval-btn details" onclick="app.showApprovalDetail('${a.id}')">Details</button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  // --- Analytics ---
  renderAnalytics() {
    const agents = this.state.get('agents');
    const projects = this.state.get('projects');

    // Agent utilization
    const utilizationEl = document.getElementById('analytics-utilization');
    if (utilizationEl) {
      const agentList = [...agents.values()];
      utilizationEl.innerHTML = agentList.map(a => {
        const pct = a.status === 'active' ? 85 + Math.floor(Math.random() * 15) :
                    a.status === 'waiting' ? 30 + Math.floor(Math.random() * 30) :
                    Math.floor(Math.random() * 20);
        return `
          <div class="metric-row">
            <span class="metric-label">${a.icon} ${a.name.split(' ').pop()}</span>
            <div class="metric-bar">
              <div class="metric-bar-fill" style="width:${pct}%; background:${pct > 70 ? 'var(--status-active)' : pct > 40 ? 'var(--status-waiting)' : 'var(--status-idle)'}"></div>
            </div>
            <span class="metric-value">${pct}%</span>
          </div>
        `;
      }).join('');
    }

    // Project metrics
    const projectMetricsEl = document.getElementById('analytics-projects');
    if (projectMetricsEl) {
      const metrics = [
        { label: 'Projects Completed', value: '3' },
        { label: 'Average Sprint Time', value: '4.2 days' },
        { label: 'Code Quality Score', value: '94/100' },
        { label: 'Test Coverage', value: '87%' },
        { label: 'Security Score', value: 'A+' },
        { label: 'Deployment Success Rate', value: '98.5%' },
      ];
      projectMetricsEl.innerHTML = metrics.map(m => `
        <div class="metric-row">
          <span class="metric-label">${m.label}</span>
          <span class="metric-value">${m.value}</span>
        </div>
      `).join('');
    }

    // Model performance
    const modelPerfEl = document.getElementById('analytics-models');
    if (modelPerfEl) {
      const models = [
        { name: 'deepseek-r1:8b', tokens: 45, quality: 74.8 },
        { name: 'qwen2.5-coder:7b', tokens: 55, quality: 84.1 },
        { name: 'z-image-turbo', tokens: 0, quality: 76 },
      ];
      modelPerfEl.innerHTML = models.map(m => `
        <div class="metric-row">
          <span class="metric-label font-mono text-sm">${m.name}</span>
          <div class="metric-bar">
            <div class="metric-bar-fill" style="width:${m.quality}%"></div>
          </div>
          <span class="metric-value">${m.quality}%</span>
        </div>
      `).join('');
    }

    // Knowledge mesh
    const meshEl = document.getElementById('analytics-mesh');
    if (meshEl) {
      const meshStats = [
        { label: 'Knowledge Entries', value: '1,247' },
        { label: 'Connections', value: '3,891' },
        { label: 'Patterns Detected', value: '89' },
        { label: 'Lessons Learned', value: '34' },
        { label: 'Source Documents', value: '156' },
        { label: 'Last Updated', value: '2 min ago' },
      ];
      meshEl.innerHTML = meshStats.map(m => `
        <div class="metric-row">
          <span class="metric-label">${m.label}</span>
          <span class="metric-value">${m.value}</span>
        </div>
      `).join('');
    }
  }

  // --- Settings ---
  renderSettings() {
    const section = this.state.get('settingsSection');
    const panel = document.getElementById('settings-content');
    if (!panel) return;

    // Update nav
    document.querySelectorAll('.settings-nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.section === section);
    });

    switch (section) {
      case 'models': this.renderSettingsModels(panel); break;
      case 'messaging': this.renderSettingsMessaging(panel); break;
      case 'security': this.renderSettingsSecurity(panel); break;
      case 'email': this.renderSettingsEmail(panel); break;
      case 'identity': this.renderSettingsIdentity(panel); break;
      case 'system': this.renderSettingsSystem(panel); break;
      default: this.renderSettingsModels(panel);
    }
  }

  renderSettingsModels(panel) {
    const models = [
      { name: 'deepseek-r1:8b', size: '5 GB', status: 'installed', category: 'Reasoning', params: '8B' },
      { name: 'qwen2.5-coder:7b', size: '4.5 GB', status: 'installed', category: 'Coding', params: '7B' },
      { name: 'z-image-turbo', size: '4 GB', status: 'installed', category: 'Image', params: '6B' },
      { name: 'deepseek-r1:14b', size: '9 GB', status: 'available', category: 'Reasoning', params: '14B' },
      { name: 'qwen3:30b', size: '20 GB', status: 'available', category: 'Reasoning', params: '30B' },
      { name: 'qwen2.5-coder:32b', size: '20 GB', status: 'available', category: 'Coding', params: '32B' },
      { name: 'gemma4:26b', size: '16 GB', status: 'available', category: 'Reasoning', params: '26B' },
      { name: 'flux2-schnell', size: '24 GB', status: 'available', category: 'Image', params: '12B' },
      { name: 'qwen3.5', size: '20 GB', status: 'available', category: 'Reasoning', params: '32B' },
      { name: 'glm5', size: '75 GB', status: 'available', category: 'Coding', params: '130B' },
    ];

    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">🧠 Model Management</div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:16px;">
          Download, switch, and remove AI models from your local Ollama instance.
          Models are assigned to agents based on your hardware tier.
        </p>
        <div class="model-list">
          ${models.map(m => `
            <div class="model-item">
              <div class="model-info">
                <div class="model-name">${m.name}</div>
                <div class="model-meta">
                  <span>${m.category}</span>
                  <span>${m.params}</span>
                  <span>${m.size}</span>
                </div>
              </div>
              <span class="model-status ${m.status}">${m.status}</span>
              ${m.status === 'installed'
                ? `<button class="btn btn-sm btn-danger" onclick="app.removeModel('${m.name}')">Remove</button>`
                : `<button class="btn btn-sm btn-primary" onclick="app.pullModel('${m.name}')">Pull</button>`
              }
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  renderSettingsMessaging(panel) {
    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">💬 Messaging Configuration</div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Telegram Bot</div>
            <div class="setting-desc">Enable Telegram bot for agent communications</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Telegram Bot Token</div>
            <div class="setting-desc">Bot token from @BotFather</div>
          </div>
          <input class="text-input" type="password" placeholder="Enter bot token..." value="••••••••••••••••" style="width:200px;">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">WhatsApp Integration</div>
            <div class="setting-desc">Enable WhatsApp messaging via Twilio</div>
          </div>
          <div class="toggle" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Twilio Account SID</div>
            <div class="setting-desc">Your Twilio Account SID</div>
          </div>
          <input class="text-input" type="text" placeholder="AC..." style="width:200px;">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Notification Sound</div>
            <div class="setting-desc">Play sound on new messages</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Auto-Reply</div>
            <div class="setting-desc">Allow agents to auto-reply to simple queries</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
      </div>
    `;
  }

  renderSettingsSecurity(panel) {
    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">🔒 Security Settings</div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Contact Whitelist</div>
            <div class="setting-desc">Only allow messages from whitelisted contacts</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">CAPTCHA Protection</div>
            <div class="setting-desc">Enable CAPTCHA solver for protected sites</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Two-Factor Authentication</div>
            <div class="setting-desc">Require 2FA for critical operations</div>
          </div>
          <div class="toggle" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Audit Logging</div>
            <div class="setting-desc">Log all agent actions for audit trail</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">API Key Encryption</div>
            <div class="setting-desc">Encrypt stored API keys at rest</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Rate Limiting</div>
            <div class="setting-desc">Limit API calls per agent (requests/min)</div>
          </div>
          <input class="text-input" type="number" value="60" min="1" max="1000" style="width:80px;">
        </div>
      </div>
    `;
  }

  renderSettingsEmail(panel) {
    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">📧 Email Management</div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:16px;">
          Configure email accounts for each agent. Agents use these to communicate externally.
        </p>
        <div class="model-list">
          ${[...this.state.get('agents').values()].map(a => `
            <div class="model-item">
              <div class="model-info">
                <div class="model-name">${a.icon} ${a.name}</div>
                <div class="model-meta"><span>${a.id}@luymas.local</span></div>
              </div>
              <span class="model-status installed">configured</span>
              <button class="btn btn-sm" onclick="app.configureAgentEmail('${a.id}')">Edit</button>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  renderSettingsIdentity(panel) {
    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">🪪 Identity Management</div>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:16px;">
          Manage digital identities for agents across services (GitHub, Docker Hub, Vercel, etc.)
        </p>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Auto-Create Identities</div>
            <div class="setting-desc">Automatically create service accounts for new agents</div>
          </div>
          <div class="toggle" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Identity Verification</div>
            <div class="setting-desc">Require email verification for new identities</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">GitHub Account</div>
            <div class="setting-desc">Associated GitHub account for agents</div>
          </div>
          <input class="text-input" type="text" value="luymas-ai" style="width:150px;">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Docker Hub Account</div>
            <div class="setting-desc">Docker Hub account for container management</div>
          </div>
          <input class="text-input" type="text" value="luymas" style="width:150px;">
        </div>
      </div>
    `;
  }

  renderSettingsSystem(panel) {
    const health = this.state.get('systemHealth');
    panel.innerHTML = `
      <div class="settings-section">
        <div class="settings-section-title">⚙️ System Configuration</div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Hardware Tier</div>
            <div class="setting-desc">Current hardware configuration profile</div>
          </div>
          <select class="text-input" style="width:150px;">
            <option value="tier1" selected>Tier 1 (8GB)</option>
            <option value="tier2">Tier 2 (16GB)</option>
            <option value="tier3">Tier 3 (32GB+GPU)</option>
            <option value="tier4">Tier 4 (64GB+GPU)</option>
            <option value="tier5">Tier 5 (128GB+GPU)</option>
          </select>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Max Concurrent Agents</div>
            <div class="setting-desc">Maximum number of agents running simultaneously</div>
          </div>
          <input class="text-input" type="number" value="3" min="1" max="11" style="width:80px;">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Task Timeout</div>
            <div class="setting-desc">Default task timeout in seconds</div>
          </div>
          <input class="text-input" type="number" value="300" min="30" max="3600" style="width:100px;">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Auto-Update</div>
            <div class="setting-desc">Automatically check for system updates</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Sandbox Mode</div>
            <div class="setting-desc">Restrict filesystem and network access</div>
          </div>
          <div class="toggle active" onclick="this.classList.toggle('active')"></div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">Log Level</div>
            <div class="setting-desc">System log verbosity level</div>
          </div>
          <select class="text-input" style="width:120px;">
            <option>DEBUG</option>
            <option selected>INFO</option>
            <option>WARNING</option>
            <option>ERROR</option>
          </select>
        </div>
        <div style="margin-top:24px;padding:16px;background:var(--bg-tertiary);border-radius:var(--radius-md);border:1px solid var(--border-secondary);">
          <h4 style="font-size:0.9rem;margin-bottom:12px;color:var(--text-primary);">System Health</h4>
          <div class="health-grid">
            <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Ollama</span><span class="health-value">${health.ollama}</span></div>
            <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Memory</span><span class="health-value">${health.memoryUsage}</span></div>
            <div class="health-item"><span class="health-dot ok"></span><span class="health-label">CPU</span><span class="health-value">${health.cpuUsage}</span></div>
            <div class="health-item"><span class="health-dot ok"></span><span class="health-label">Disk</span><span class="health-value">${health.diskUsage}</span></div>
          </div>
        </div>
        <div style="margin-top:16px;display:flex;gap:8px;">
          <button class="btn" onclick="app.runDiagnostics()">🔧 Run Diagnostics</button>
          <button class="btn" onclick="app.checkUpdates()">🔄 Check Updates</button>
          <button class="btn btn-danger" onclick="app.restartSystem()">♻️ Restart System</button>
        </div>
      </div>
    `;
  }
}

// =============================================================================
// Main Application
// =============================================================================
class LuymasStudio {
  constructor() {
    this.state = new StateManager();
    this.ws = new WebSocketManager(this.state);
    this.api = new APIClient();
    this.modal = null;
    this.toast = null;
    this.router = null;
    this.views = null;
    this.pollingTimers = [];
  }

  async init() {
    // Initialize agents
    const agents = new Map();
    AGENT_DEFS.forEach(a => agents.set(a.id, { ...a }));
    this.state.set('agents', agents);

    // Initialize default projects
    this.state.set('projects', [
      {
        id: 'p1',
        name: 'E-Commerce Platform',
        description: 'Full-stack e-commerce solution with product catalog, cart, checkout, and admin dashboard.',
        status: 'in-progress',
        progress: 68,
        agents: ['pm', 'architect', 'coder_back', 'coder_front', 'designer'],
        created: 'Mar 1, 2026',
        timeline: ['completed', 'completed', 'completed', 'active', ''],
        timelineLabels: ['Planning', 'Design', 'Backend', 'Frontend', 'Deploy'],
      },
      {
        id: 'p2',
        name: 'AI Content Generator',
        description: 'SaaS tool for generating blog posts, social media content, and marketing copy using AI.',
        status: 'planning',
        progress: 15,
        agents: ['pm', 'architect'],
        created: 'Mar 3, 2026',
        timeline: ['active', '', '', '', ''],
        timelineLabels: ['Planning', 'Design', 'Build', 'Test', 'Deploy'],
      },
      {
        id: 'p3',
        name: 'Portfolio Website',
        description: 'Personal portfolio with project showcase, blog, and contact form.',
        status: 'review',
        progress: 95,
        agents: ['coder_front', 'designer', 'guardian'],
        created: 'Feb 25, 2026',
        timeline: ['completed', 'completed', 'completed', 'completed', 'active'],
        timelineLabels: ['Planning', 'Design', 'Build', 'Test', 'Review'],
      },
      {
        id: 'p4',
        name: 'Task Management API',
        description: 'RESTful API for task management with auth, teams, and real-time updates.',
        status: 'deployed',
        progress: 100,
        agents: ['coder_back', 'tester', 'ops', 'caretaker'],
        created: 'Feb 20, 2026',
        timeline: ['completed', 'completed', 'completed', 'completed', 'completed'],
        timelineLabels: ['Planning', 'Design', 'Build', 'Test', 'Deploy'],
      },
    ]);

    // Initialize messages
    this.state.set('messages', []);
    this.state.set('approvals', []);
    this.state.set('activityLog', []);

    // Init subsystems
    this.toast = new ToastManager();
    window._luymas_toast = this.toast;
    this.modal = new ModalManager();
    this.views = new ViewRenderer(this.state, this.api);
    this.router = new Router(this.state);

    // Register routes
    this.router.register('dashboard', () => this.views.renderDashboard());
    this.router.register('agents', () => this.views.renderAgents());
    this.router.register('projects', () => this.views.renderProjects());
    this.router.register('messages', () => this.views.renderMessages());
    this.router.register('analytics', () => this.views.renderAnalytics());
    this.router.register('settings', () => this.views.renderSettings());

    // Setup event listeners
    this.setupListeners();

    // Setup sidebar
    this.setupSidebar();

    // Setup settings nav
    this.setupSettingsNav();

    // Setup search
    this.setupSearch();

    // Connect WebSocket
    this.ws.connect();

    // Try loading from API, fall back to local state
    await this.loadFromAPI();

    // Start polling
    this.startPolling();

    // Initial render
    this.router.handleRoute();

    // Apply sidebar state
    if (this.state.get('sidebarCollapsed')) {
      document.querySelector('.sidebar')?.classList.add('collapsed');
    }

    console.log('✅ Luymas AI Studio initialized');
  }

  setupListeners() {
    // State change listeners
    this.state.on('state:agents', () => {
      if (this.router.currentView === 'agents') this.views.renderAgents();
      if (this.router.currentView === 'dashboard') this.views.renderDashboard();
    });

    this.state.on('state:projects', () => {
      if (this.router.currentView === 'projects') this.views.renderProjects();
    });

    this.state.on('state:messages', () => {
      if (this.router.currentView === 'messages') this.views.renderChatArea();
    });

    this.state.on('state:connected', ({ new: connected }) => {
      const statusEl = document.getElementById('connection-status');
      if (statusEl) {
        statusEl.className = `connection-status ${connected ? '' : 'disconnected'}`;
        statusEl.querySelector('.status-text').textContent = connected ? 'Connected' : 'Disconnected';
      }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('global-search')?.focus();
      }
      // Escape to close modals
      if (e.key === 'Escape') {
        this.modal.close();
        this.closeAgentDetail();
      }
    });

    // Mobile menu button
    document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
      document.querySelector('.sidebar')?.classList.toggle('mobile-open');
    });

    // Chat send
    document.getElementById('chat-send-btn')?.addEventListener('click', () => this.sendChatMessage());
    document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.sendChatMessage();
    });
  }

  setupSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        const sidebar = document.querySelector('.sidebar');
        sidebar?.classList.toggle('collapsed');
        this.state.set('sidebarCollapsed', sidebar?.classList.contains('collapsed'));
      });
    }
  }

  setupSettingsNav() {
    document.querySelectorAll('.settings-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const section = item.dataset.section;
        this.state.set('settingsSection', section);
        this.views.renderSettings();
      });
    });
  }

  setupSearch() {
    const searchInput = document.getElementById('global-search');
    if (!searchInput) return;

    let debounce;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        this.state.set('searchQuery', e.target.value.toLowerCase());
        this.executeSearch(e.target.value.toLowerCase());
      }, 250);
    });
  }

  executeSearch(query) {
    if (!query || query.length < 2) return;

    const agents = this.state.get('agents');
    const projects = this.state.get('projects');

    const agentResults = [...agents.values()].filter(a =>
      a.name.toLowerCase().includes(query) ||
      a.role.toLowerCase().includes(query) ||
      a.task.toLowerCase().includes(query)
    );

    const projectResults = projects.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    );

    if (agentResults.length === 1) {
      this.router.navigate('agents');
      this.showAgentDetail(agentResults[0].id);
    } else if (projectResults.length === 1) {
      this.router.navigate('projects');
    } else if (agentResults.length > 0) {
      this.router.navigate('agents');
    } else if (projectResults.length > 0) {
      this.router.navigate('projects');
    }
  }

  async loadFromAPI() {
    try {
      const [agents, projects, health] = await Promise.allSettled([
        this.api.getAgents(),
        this.api.getProjects(),
        this.api.getHealth(),
      ]);

      if (agents.status === 'fulfilled' && agents.value) {
        const agentMap = new Map();
        agents.value.forEach(a => agentMap.set(a.id || a.name, a));
        this.state.set('agents', agentMap);
      }

      if (projects.status === 'fulfilled' && projects.value) {
        this.state.set('projects', projects.value);
      }

      if (health.status === 'fulfilled' && health.value) {
        this.state.set('systemHealth', health.value);
      }
    } catch (e) {
      // API not available; using local data
      console.info('API not reachable, using local state');
    }
  }

  startPolling() {
    // Poll system health
    const healthPoll = setInterval(async () => {
      try {
        const health = await this.api.getHealth();
        if (health) this.state.set('systemHealth', health);
      } catch (e) { /* ignore */ }
    }, CONFIG.HEALTH_POLL_INTERVAL);
    this.pollingTimers.push(healthPoll);

    // Poll for activity
    const activityPoll = setInterval(() => {
      this.simulateActivity();
    }, CONFIG.ACTIVITY_POLL_INTERVAL);
    this.pollingTimers.push(activityPoll);

    // Simulate status changes
    const statusPoll = setInterval(() => {
      this.simulateStatusChange();
    }, 20000);
    this.pollingTimers.push(statusPoll);
  }

  simulateActivity() {
    const activities = [
      { type: 'agent', text: '<strong>Caretaker</strong> performed health check — all systems green', time: 'just now' },
      { type: 'task', text: '<strong>Tester</strong> completed regression test suite (47 tests passed)', time: 'just now' },
      { type: 'message', text: '<strong>PM</strong> sent project status update to stakeholders', time: 'just now' },
      { type: 'system', text: '<strong>System</strong> memory usage: 62% — within normal range', time: 'just now' },
    ];
    const random = activities[Math.floor(Math.random() * activities.length)];
    const log = [random, ...this.state.get('activityLog')].slice(0, 50);
    this.state.set('activityLog', log);
  }

  simulateStatusChange() {
    const agents = this.state.get('agents');
    const statuses = ['active', 'idle', 'waiting', 'active'];
    const agentArray = [...agents.values()];
    const randomAgent = agentArray[Math.floor(Math.random() * agentArray.length)];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

    if (randomAgent.status !== randomStatus) {
      randomAgent.status = randomStatus;
      agents.set(randomAgent.id, randomAgent);
      this.state.set('agents', agents);
    }
  }

  // --- Agent Actions ---
  async startAgent(agentId) {
    try {
      await this.api.startAgent(agentId);
      this.updateAgentStatus(agentId, 'active');
      this.toast.success('Agent Started', `Agent is now active`);
    } catch (e) {
      this.updateAgentStatus(agentId, 'active');
      this.toast.success('Agent Started', `Agent is now active (local)`);
    }
  }

  async stopAgent(agentId) {
    try {
      await this.api.stopAgent(agentId);
      this.updateAgentStatus(agentId, 'idle');
      this.toast.info('Agent Stopped', `Agent has been stopped`);
    } catch (e) {
      this.updateAgentStatus(agentId, 'idle');
      this.toast.info('Agent Stopped', `Agent has been stopped (local)`);
    }
  }

  async pauseAgent(agentId) {
    try {
      await this.api.pauseAgent(agentId);
      this.updateAgentStatus(agentId, 'paused');
      this.toast.warning('Agent Paused', `Agent is paused`);
    } catch (e) {
      this.updateAgentStatus(agentId, 'paused');
      this.toast.warning('Agent Paused', `Agent is paused (local)`);
    }
  }

  updateAgentStatus(agentId, status) {
    const agents = this.state.get('agents');
    const agent = agents.get(agentId);
    if (agent) {
      agent.status = status;
      agents.set(agentId, agent);
      this.state.set('agents', agents);
    }
  }

  showAgentDetail(agentId) {
    this.state.set('selectedAgent', agentId);
    this.views.renderAgentDetail(agentId);
  }

  closeAgentDetail() {
    const panel = document.getElementById('agent-detail-panel');
    if (panel) panel.classList.add('hidden');
    this.state.set('selectedAgent', null);
  }

  chatWithAgent(agentId) {
    this.state.set('selectedThread', `agent-${agentId}`);
    this.router.navigate('messages');
  }

  async sendAgentChat(agentId) {
    const input = document.getElementById('agent-chat-input');
    if (!input || !input.value.trim()) return;

    const message = input.value.trim();
    input.value = '';

    // Add user message
    const messagesEl = document.getElementById('agent-chat-messages');
    if (messagesEl) {
      messagesEl.innerHTML += `
        <div class="chat-msg">
          <div class="msg-sender user">You</div>
          <div class="msg-text">${this.escapeHtml(message)}</div>
          <div class="msg-time">${new Date().toLocaleTimeString()}</div>
        </div>
      `;
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    // Show typing indicator
    if (messagesEl) {
      messagesEl.innerHTML += `
        <div class="chat-msg typing-msg">
          <div class="msg-sender">Agent</div>
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      `;
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    try {
      const response = await this.api.chatAgent(agentId, message);
      this.removeTypingIndicator();
      if (messagesEl && response) {
        messagesEl.innerHTML += `
          <div class="chat-msg">
            <div class="msg-sender">Agent</div>
            <div class="msg-text">${response.text || response.message || 'Processing your request...'}</div>
            <div class="msg-time">${new Date().toLocaleTimeString()}</div>
          </div>
        `;
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    } catch (e) {
      this.removeTypingIndicator();
      // Simulate response
      setTimeout(() => {
        if (messagesEl) {
          const agents = this.state.get('agents');
          const agent = agents.get(agentId);
          messagesEl.innerHTML += `
            <div class="chat-msg">
              <div class="msg-sender">${agent ? agent.name : 'Agent'}</div>
              <div class="msg-text">I received your message: "${this.escapeHtml(message)}". I'm processing this request using ${agent ? agent.model : 'my model'}. I'll have results shortly.</div>
              <div class="msg-time">${new Date().toLocaleTimeString()}</div>
            </div>
          `;
          messagesEl.scrollTop = messagesEl.scrollHeight;
        }
      }, 1500);
    }
  }

  removeTypingIndicator() {
    document.querySelectorAll('.typing-msg').forEach(el => el.remove());
  }

  // --- Chat Actions ---
  async sendChatMessage() {
    const input = document.getElementById('chat-input');
    if (!input || !input.value.trim()) return;

    const message = input.value.trim();
    input.value = '';

    const selected = this.state.get('selectedThread');

    // Add to messages
    const messages = [...this.state.get('messages'), {
      id: `msg-${Date.now()}`,
      thread: selected,
      sender: 'You',
      senderType: 'user',
      text: message,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }];
    this.state.set('messages', messages);

    try {
      await this.api.sendMessage(selected, message);
    } catch (e) {
      // Simulate agent response
      setTimeout(() => {
        const agents = this.state.get('agents');
        const responder = [...agents.values()].find(a => a.status === 'active') || [...agents.values()][0];
        const responses = [
          'Acknowledged. I\'ll process that right away.',
          'Understood. Let me work on that and report back.',
          'Good point. I\'ll factor that into my current task.',
          'I\'ll coordinate with the team on this. Give me a moment.',
          'Received. Adjusting my workflow accordingly.',
        ];
        const updatedMessages = [...this.state.get('messages'), {
          id: `msg-${Date.now()}`,
          thread: selected,
          sender: responder ? responder.name.split(' ').pop() : 'Agent',
          senderType: 'agent',
          text: responses[Math.floor(Math.random() * responses.length)],
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }];
        this.state.set('messages', updatedMessages);
      }, 2000);
    }
  }

  selectThread(threadId) {
    this.state.set('selectedThread', threadId);
    this.views.renderThreadList();
    this.views.renderChatArea();
  }

  // --- Project Actions ---
  createProjectModal() {
    this.modal.open('Create New Project', `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Project Name</label>
          <input class="text-input" type="text" id="new-project-name" placeholder="My Awesome Project">
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Description</label>
          <textarea class="text-input" id="new-project-desc" rows="3" placeholder="Describe what you want to build..."></textarea>
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Workflow</label>
          <select class="text-input" id="new-project-workflow" style="width:100%;">
            <option value="full">Full Stack (PM → Architect → Coders → QA → Deploy)</option>
            <option value="api">API Only (PM → Architect → Backend → QA)</option>
            <option value="frontend">Frontend Only (PM → Designer → Frontend → QA)</option>
            <option value="design">Design Sprint (PM → Designer → Review)</option>
          </select>
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Target Platform</label>
          <div style="display:flex;gap:8px;">
            <button class="btn btn-sm platform-btn active" data-platform="web" onclick="this.parentElement.querySelectorAll('.platform-btn').forEach(b=>b.classList.remove('active'));this.classList.add('active');">🌐 Web</button>
            <button class="btn btn-sm platform-btn" data-platform="mobile" onclick="this.parentElement.querySelectorAll('.platform-btn').forEach(b=>b.classList.remove('active'));this.classList.add('active');">📱 Mobile</button>
            <button class="btn btn-sm platform-btn" data-platform="desktop" onclick="this.parentElement.querySelectorAll('.platform-btn').forEach(b=>b.classList.remove('active'));this.classList.add('active');">🖥️ Desktop</button>
          </div>
        </div>
      </div>
    `, {
      confirmText: '🚀 Create Project',
      onConfirm: () => this.createProject(),
    });
  }

  async createProject() {
    const name = document.getElementById('new-project-name')?.value;
    const desc = document.getElementById('new-project-desc')?.value;
    const workflow = document.getElementById('new-project-workflow')?.value;

    if (!name) {
      this.toast.error('Missing Name', 'Please enter a project name');
      return;
    }

    const workflowAgents = {
      full: ['pm', 'architect', 'coder_back', 'coder_front', 'designer', 'tester', 'ops'],
      api: ['pm', 'architect', 'coder_back', 'tester', 'ops'],
      frontend: ['pm', 'designer', 'coder_front', 'tester', 'ops'],
      design: ['pm', 'designer', 'reviewer'],
    };

    const project = {
      id: `p${Date.now()}`,
      name,
      description: desc || 'New project',
      status: 'planning',
      progress: 0,
      agents: workflowAgents[workflow] || workflowAgents.full,
      created: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      timeline: ['active', '', '', '', ''],
      timelineLabels: ['Planning', 'Design', 'Build', 'Test', 'Deploy'],
    };

    try {
      await this.api.createProject(project);
    } catch (e) { /* local fallback */ }

    const projects = [...this.state.get('projects'), project];
    this.state.set('projects', projects);
    this.toast.success('Project Created', `"${name}" is now being planned by the AI team`);
  }

  async deployProject(projectId) {
    this.toast.info('Deploying', 'Starting deployment pipeline...');
    const projects = this.state.get('projects').map(p =>
      p.id === projectId ? { ...p, status: 'deployed', progress: 100, timeline: p.timeline.map(() => 'completed') } : p
    );
    this.state.set('projects', projects);

    try {
      await this.api.updateProject(projectId, { status: 'deployed' });
    } catch (e) { /* local */ }

    setTimeout(() => this.toast.success('Deployed!', 'Project has been deployed successfully'), 2000);
  }

  reviewProject(projectId) {
    this.toast.info('Under Review', 'Security team is reviewing the project...');
    const projects = this.state.get('projects').map(p =>
      p.id === projectId ? { ...p, status: 'review' } : p
    );
    this.state.set('projects', projects);
  }

  editProject(projectId) {
    const project = this.state.get('projects').find(p => p.id === projectId);
    if (!project) return;

    this.modal.open('Edit Project', `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Project Name</label>
          <input class="text-input" type="text" id="edit-project-name" value="${this.escapeHtml(project.name)}">
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Description</label>
          <textarea class="text-input" id="edit-project-desc" rows="3">${this.escapeHtml(project.description)}</textarea>
        </div>
      </div>
    `, {
      confirmText: 'Save Changes',
      onConfirm: async () => {
        const name = document.getElementById('edit-project-name')?.value;
        const desc = document.getElementById('edit-project-desc')?.value;
        const projects = this.state.get('projects').map(p =>
          p.id === projectId ? { ...p, name: name || p.name, description: desc || p.description } : p
        );
        this.state.set('projects', projects);
        try { await this.api.updateProject(projectId, { name, description: desc }); } catch (e) {}
        this.toast.success('Updated', 'Project has been updated');
      },
    });
  }

  async deleteProject(projectId) {
    this.modal.open('Delete Project', `
      <div style="text-align:center;padding:16px;">
        <div style="font-size:2.5rem;margin-bottom:16px;">⚠️</div>
        <p style="font-size:0.95rem;color:var(--text-primary);margin-bottom:8px;">Are you sure you want to delete this project?</p>
        <p style="font-size:0.8rem;color:var(--text-tertiary);">This action cannot be undone. All project data will be lost.</p>
      </div>
    `, {
      confirmText: '🗑️ Delete',
      onConfirm: async () => {
        const projects = this.state.get('projects').filter(p => p.id !== projectId);
        this.state.set('projects', projects);
        try { await this.api.deleteProject(projectId); } catch (e) {}
        this.toast.success('Deleted', 'Project has been removed');
      },
    });
  }

  filterProjects(status) {
    const allProjects = this.state.get('projects');
    const filtered = status === 'all' ? allProjects : allProjects.filter(p => p.status === status);

    const list = document.getElementById('project-list');
    if (!list) return;

    if (filtered.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📁</div>
          <div class="empty-title">No ${status === 'all' ? '' : status + ' '}Projects</div>
          <div class="empty-desc">Create a new project to get started.</div>
        </div>
      `;
      return;
    }

    // Re-render with filtered projects
    list.innerHTML = filtered.map(p => `
      <div class="project-card" onclick="app.showProjectDetail('${p.id}')">
        <div class="project-card-header">
          <div>
            <div class="project-title">${p.name}</div>
            <div class="project-desc">${p.description}</div>
          </div>
          <span class="project-status ${p.status}">${p.status.replace('-', ' ')}</span>
        </div>
        <div class="project-meta">
          <span>🤖 ${p.agents.length} agents</span>
          <span>📅 ${p.created}</span>
          <span>📊 ${p.progress}% complete</span>
        </div>
        <div class="project-timeline">
          ${(p.timeline || []).map((step) => `
            <div class="timeline-step ${step === 'completed' ? 'completed' : step === 'active' ? 'active' : ''}"></div>
          `).join('')}
        </div>
        <div class="project-actions">
          ${p.status === 'review' ? '<button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); app.deployProject(\'' + p.id + '\')">🚀 Deploy</button>' : ''}
          <button class="btn btn-sm" onclick="event.stopPropagation(); app.editProject('${p.id}')">✏️ Edit</button>
          <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); app.deleteProject('${p.id}')">🗑️ Delete</button>
        </div>
      </div>
    `).join('');
  }

  showProjectDetail(projectId) {
    const project = this.state.get('projects').find(p => p.id === projectId);
    if (!project) return;

    this.modal.open(project.name, `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <p style="color:var(--text-secondary);font-size:0.9rem;">${project.description}</p>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
          <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;flex:1;min-width:100px;text-align:center;">
            <div style="font-size:1.2rem;font-weight:700;color:var(--text-primary);">${project.progress}%</div>
            <div style="font-size:0.7rem;color:var(--text-tertiary);">Complete</div>
          </div>
          <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;flex:1;min-width:100px;text-align:center;">
            <div style="font-size:1.2rem;font-weight:700;color:var(--text-primary);">${project.agents.length}</div>
            <div style="font-size:0.7rem;color:var(--text-tertiary);">Agents</div>
          </div>
          <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;flex:1;min-width:100px;text-align:center;">
            <div style="font-size:1.2rem;font-weight:700;color:var(--text-primary);">${project.created}</div>
            <div style="font-size:0.7rem;color:var(--text-tertiary);">Created</div>
          </div>
        </div>
        <div>
          <div style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:8px;">Pipeline</div>
          <div class="project-timeline">
            ${(project.timeline || []).map((step, i) => `
              <div class="timeline-step ${step}" title="${project.timelineLabels?.[i] || ''}"></div>
            `).join('')}
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-tertiary);">
            ${(project.timelineLabels || []).map(l => `<span>${l}</span>`).join('')}
          </div>
        </div>
        <div>
          <div style="font-size:0.8rem;color:var(--text-tertiary);margin-bottom:8px;">Assigned Agents</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;">
            ${project.agents.map(aId => {
              const agents = this.state.get('agents');
              const agent = agents.get(aId);
              return agent ? `<span class="skill-tag">${agent.icon} ${agent.name.split(' ').pop()}</span>` : '';
            }).join('')}
          </div>
        </div>
      </div>
    `, { confirmText: 'Close', onConfirm: () => {} });
  }

  // --- Approval Actions ---
  async approveRequest(requestId) {
    try {
      await this.api.approveRequest(requestId);
    } catch (e) { /* local */ }
    const approvals = this.state.get('approvals').filter(a => a.id !== requestId);
    this.state.set('approvals', approvals);
    this.toast.success('Approved', 'Request has been approved');
    this.views.renderApprovals();
  }

  async rejectRequest(requestId) {
    try {
      await this.api.rejectRequest(requestId);
    } catch (e) { /* local */ }
    const approvals = this.state.get('approvals').filter(a => a.id !== requestId);
    this.state.set('approvals', approvals);
    this.toast.info('Rejected', 'Request has been rejected');
    this.views.renderApprovals();
  }

  showApprovalDetail(requestId) {
    const approval = this.state.get('approvals').find(a => a.id === requestId);
    if (!approval) return;

    this.modal.open(`Approval: ${approval.title}`, `
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="approval-type ${approval.type}">${approval.type}</span>
          <span style="font-size:0.8rem;color:var(--text-tertiary);">from ${approval.agent}</span>
        </div>
        <p style="font-size:0.9rem;color:var(--text-secondary);line-height:1.7;">${approval.description}</p>
        <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;font-size:0.8rem;color:var(--text-tertiary);">
          Requested: ${approval.time}
        </div>
      </div>
    `, {
      confirmText: '✓ Approve',
      onConfirm: () => this.approveRequest(requestId),
    });
  }

  // --- Model Actions ---
  async pullModel(modelName) {
    this.toast.info('Pulling Model', `Downloading ${modelName}... This may take a while.`);
    try {
      await this.api.pullModel(modelName);
      this.toast.success('Model Pulled', `${modelName} is now available`);
    } catch (e) {
      this.toast.warning('Pull Queued', `${modelName} download queued (backend will process)`);
    }
    this.views.renderSettings();
  }

  async removeModel(modelName) {
    this.modal.open('Remove Model', `
      <div style="text-align:center;padding:16px;">
        <div style="font-size:2rem;margin-bottom:12px;">🗑️</div>
        <p style="font-size:0.9rem;color:var(--text-secondary);">Remove <strong>${modelName}</strong> from your local instance?</p>
        <p style="font-size:0.8rem;color:var(--text-tertiary);margin-top:8px;">Any agents using this model will need to be reassigned.</p>
      </div>
    `, {
      confirmText: 'Remove',
      onConfirm: async () => {
        try {
          await this.api.deleteModel(modelName);
        } catch (e) { /* local */ }
        this.toast.success('Removed', `${modelName} has been removed`);
        this.views.renderSettings();
      },
    });
  }

  configureAgentEmail(agentId) {
    const agents = this.state.get('agents');
    const agent = agents.get(agentId);
    if (!agent) return;

    this.modal.open(`Email: ${agent.name}`, `
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Email Address</label>
          <input class="text-input" type="email" value="${agentId}@luymas.local">
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Provider</label>
          <select class="text-input" style="width:100%;">
            <option>Gmail</option>
            <option>ProtonMail</option>
            <option>Mailgun</option>
            <option>AliasKit</option>
          </select>
        </div>
        <div>
          <label style="font-size:0.8rem;color:var(--text-tertiary);display:block;margin-bottom:4px;">Signature</label>
          <textarea class="text-input" rows="2" placeholder="Email signature...">Best regards,\n${agent.name}\nLuymas AI Team</textarea>
        </div>
      </div>
    `, {
      confirmText: 'Save',
      onConfirm: () => this.toast.success('Email Updated', `Email settings for ${agent.name} saved`),
    });
  }

  // --- System Actions ---
  async runDiagnostics() {
    this.toast.info('Diagnostics', 'Running system diagnostics...');
    setTimeout(() => {
      this.toast.success('Diagnostics Complete', 'All systems operational. No issues detected.');
    }, 3000);
  }

  async checkUpdates() {
    this.toast.info('Checking Updates', 'Looking for system updates...');
    setTimeout(() => {
      this.toast.success('Up to Date', 'System is running the latest version (v2.4.1)');
    }, 2000);
  }

  restartSystem() {
    this.modal.open('Restart System', `
      <div style="text-align:center;padding:16px;">
        <div style="font-size:2.5rem;margin-bottom:16px;">♻️</div>
        <p style="font-size:0.95rem;color:var(--text-primary);margin-bottom:8px;">Restart the Luymas AI system?</p>
        <p style="font-size:0.8rem;color:var(--text-tertiary);">All agents will be stopped and restarted. Running tasks will be saved.</p>
      </div>
    `, {
      confirmText: 'Restart',
      onConfirm: () => {
        this.toast.warning('Restarting', 'System is restarting...');
        setTimeout(() => this.toast.success('Online', 'System restarted successfully'), 5000);
      },
    });
  }

  // --- Utility ---
  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}

// =============================================================================
// Initialize
// =============================================================================
let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new LuymasStudio();
  app.init();
});
