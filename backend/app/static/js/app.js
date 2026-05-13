/**
 * UniGestión HR Platform - Main JavaScript
 * Handles authentication, API calls, and UI interactions.
 */

const API_BASE = '';

// --- Auth Utilities ---

function getToken() {
    return localStorage.getItem('hr_token');
}

function getUser() {
    const user = localStorage.getItem('hr_user');
    return user ? JSON.parse(user) : null;
}

function setAuth(token, user) {
    localStorage.setItem('hr_token', token);
    localStorage.setItem('hr_user', JSON.stringify(user));
}

function clearAuth() {
    localStorage.removeItem('hr_token');
    localStorage.removeItem('hr_user');
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    clearAuth();
    window.location.href = '/login';
}

function requireAuth(allowedRoles = []) {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return false;
    }
    const user = getUser();
    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// --- API Utilities ---

async function apiCall(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            clearAuth();
            window.location.href = '/login';
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error en la solicitud');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// --- UI Utilities ---

function showAlert(message, type = 'success', container = 'alert-container') {
    const alertDiv = document.getElementById(container);
    if (!alertDiv) return;

    alertDiv.innerHTML = `
        <div class="alert alert-${type} alert-custom alert-dismissible fade show" role="alert">
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    setTimeout(() => {
        const alert = alertDiv.querySelector('.alert');
        if (alert) alert.remove();
    }, 5000);
}

function showLoading(buttonEl) {
    buttonEl.disabled = true;
    buttonEl.dataset.originalText = buttonEl.innerHTML;
    buttonEl.innerHTML = '<span class="loading-spinner"></span>';
}

function hideLoading(buttonEl) {
    buttonEl.disabled = false;
    buttonEl.innerHTML = buttonEl.dataset.originalText || 'Enviar';
}

function formatDate(dateStr) {
    if (!dateStr || dateStr === 'None') return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(amount);
}

function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge-status badge-pending">Pendiente</span>',
        'approved': '<span class="badge-status badge-approved">Aprobado</span>',
        'rejected': '<span class="badge-status badge-rejected">Rechazado</span>',
        'completed': '<span class="badge-status badge-completed">Completado</span>',
        'in_progress': '<span class="badge-status badge-pending">En Progreso</span>'
    };
    return badges[status] || `<span class="badge-status">${status}</span>`;
}

function getUserInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

// --- Navigation ---

function setActiveNav(sectionId) {
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
    if (activeLink) activeLink.classList.add('active');
}

function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    const target = document.getElementById(sectionId);
    if (target) target.style.display = 'block';
    setActiveNav(sectionId);
}
