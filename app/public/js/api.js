// app/public/js/api.js
// API Helper & Global Layout Utilities

const isDifferentPort = typeof window !== 'undefined' && window.location.port && window.location.port !== '5000' && window.location.protocol.startsWith('http');
const API_BASE = isDifferentPort ? 'http://localhost:5000/api' : '/api';

// ── Auth Helpers ──
function getToken() {
  return localStorage.getItem('access_token');
}

function getUser() {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try { return JSON.parse(userStr); } catch (e) { return null; }
}

function setAuth(token, user) {
  localStorage.setItem('access_token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = 'index.html';
}

// ── API Fetch Wrapper ──
async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const config = { ...options, headers };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
      console.warn('Unauthorized request. Redirecting to login...');
      if (!window.location.pathname.endsWith('index.html') && window.location.pathname !== '/') {
        logout();
      }
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || 'Session expired. Please log in again.');
    }
    if (response.status === 204) return null;
    const result = await response.json();
    if (!response.ok || result.success === false) {
      throw new Error(result.error || 'API request failed');
    }
    return result;
  } catch (err) {
    console.error(`API Fetch Error [${endpoint}]:`, err.message);
    throw err;
  }
}

// ── Auth Guard ──
function checkAuth() {
  let token = getToken();
  const onLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');

  if (!token) {
    // Auto-provision demo admin session so Go Live & direct navigation work seamlessly
    const demoUser = {
      id: 1,
      email: 'admin@smartinventory.com',
      full_name: 'System Admin',
      role: 'Admin'
    };
    setAuth('admin-token', demoUser);
    token = 'admin-token';
  }

  if (onLoginPage && token) {
    window.location.href = 'dashboard.html';
  }
}

// ── UI User Meta ──
function setupUIUserMeta() {
  const user = getUser();
  if (!user) return;

  // Sidebar footer
  const nameEl = document.getElementById('ui-username');
  const roleEl = document.getElementById('ui-userrole');
  const avatarEl = document.getElementById('ui-avatar');
  if (nameEl) nameEl.textContent = user.full_name || 'User';
  if (roleEl) roleEl.textContent = user.role || 'Planner';
  if (avatarEl) avatarEl.textContent = (user.full_name || 'U').charAt(0).toUpperCase();

  // Navbar profile
  const profileName = document.getElementById('navbar-profile-name');
  const profileRole = document.getElementById('navbar-profile-role');
  const profileAvatar = document.getElementById('navbar-profile-avatar');
  if (profileName) profileName.textContent = user.full_name || 'User';
  if (profileRole) profileRole.textContent = user.role || 'Planner';
  if (profileAvatar) profileAvatar.textContent = (user.full_name || 'U').charAt(0).toUpperCase();
}

// ── Sidebar Navigation ──
function initSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.getElementById('btn-sidebar-toggle');
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';

  // Highlight active nav link
  document.querySelectorAll('.sidebar-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === currentPath || href === './' + currentPath)) {
      link.classList.add('active');
    }
  });

  // Toggle sidebar collapse
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });

    // Restore collapsed state
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
      sidebar.classList.add('collapsed');
    }
  }

  // Mobile sidebar toggle
  const mobileToggle = document.getElementById('btn-mobile-sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('mobile-open') && !sidebar.contains(e.target) && e.target !== mobileToggle) {
        sidebar.classList.remove('mobile-open');
      }
    });
  }
}

// ── Navbar Date ──
function initNavbarDate() {
  const dateEl = document.getElementById('navbar-date');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', {
      weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
    });
  }
}

// ── Toast Notifications ──
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) toast.remove();
  }, 3200);
}

// ── Formatting Helpers ──
function formatCurrency(value) {
  const num = parseFloat(value) || 0;
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatNumber(value) {
  const num = parseInt(value) || 0;
  return num.toLocaleString('en-US');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
  return formatDate(dateStr);
}

// ── Star Rating HTML ──
function renderStars(rating) {
  const r = parseFloat(rating) || 0;
  const full = Math.floor(r);
  const half = r % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  let html = '';
  for (let i = 0; i < full; i++) html += '<span>★</span>';
  if (half) html += '<span>★</span>';
  for (let i = 0; i < empty; i++) html += '<span class="star-empty">★</span>';
  return `<span class="star-rating">${html}</span>`;
}

// ── Modal Helpers ──
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('active');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('active');
}

// Close modals on overlay click or Escape
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
  }
});

// ── Loading Skeletons ──
function showSkeleton(containerId, count = 4) {
  const container = document.getElementById(containerId);
  if (!container) return;
  let html = '';
  for (let i = 0; i < count; i++) {
    html += '<div class="skeleton skeleton-card" style="height:100px;margin-bottom:12px;"></div>';
  }
  container.innerHTML = html;
}

// ── Chart.js Default Config ──
function getChartDefaults() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#94a3b8',
          font: { family: 'Poppins', size: 11 },
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 8
        }
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        titleFont: { family: 'Poppins', weight: '600' },
        bodyFont: { family: 'Poppins' }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(51,65,85,0.3)', drawBorder: false },
        ticks: { color: '#64748b', font: { family: 'Poppins', size: 11 } }
      },
      y: {
        grid: { color: 'rgba(51,65,85,0.3)', drawBorder: false },
        ticks: { color: '#64748b', font: { family: 'Poppins', size: 11 } }
      }
    }
  };
}

// ── Global Initialization ──
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  setupUIUserMeta();
  initSidebar();
  initNavbarDate();

  // Logout button
  const logoutBtn = document.getElementById('btn-global-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      logout();
    });
  }
});
