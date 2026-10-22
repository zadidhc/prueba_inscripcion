// Cliente de comunicación HTTP con la API FastAPI
const API_BASE = '/api/v1';

const api = {
  getToken() {
    return localStorage.getItem('token');
  },

  setToken(token) {
    localStorage.setItem('token', token);
  },

  removeToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = options.headers || {};
    
    if (!headers['Content-Type'] && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      this.removeToken();
      window.dispatchEvent(new CustomEvent('auth-expired'));
      throw new Error('Sesión expirada o no autorizada. Inicie sesión nuevamente.');
    }

    // Para descarga de PDF
    if (response.headers.get('content-type')?.includes('application/pdf')) {
      if (!response.ok) {
        throw new Error('Error al generar el certificado PDF.');
      }
      return await response.blob();
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const message = data?.detail || 'Ocurrió un error en la solicitud.';
      throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
    }

    return data;
  },

  // Auth
  async login(username, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(res.access_token);
    this.setUser(res.user);
    return res.user;
  },

  async getMe() {
    return await this.request('/auth/me');
  },

  // Events
  async getEvents(status = null) {
    const query = status ? `?status=${status}` : '';
    return await this.request(`/events${query}`);
  },

  async getEvent(id) {
    return await this.request(`/events/${id}`);
  },

  async createEvent(data) {
    return await this.request('/events', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateEvent(id, data) {
    return await this.request(`/events/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async addSession(eventId, data) {
    return await this.request(`/events/${eventId}/sessions`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Registrations
  async createRegistration(data) {
    return await this.request('/registrations', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async getRegistrations(params = {}) {
    const searchParams = new URLSearchParams(params);
    return await this.request(`/registrations?${searchParams.toString()}`);
  },

  async updateRegistrationStatus(id, status) {
    return await this.request(`/registrations/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  },

  // Attendances
  async recordAttendance(sessionId, documentId) {
    return await this.request('/attendances', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, document_id: documentId })
    });
  },

  async getEventAttendances(eventId) {
    return await this.request(`/events/${eventId}/attendances`);
  },

  // Certificates
  async getEligibleParticipants(eventId) {
    return await this.request(`/events/${eventId}/certificates/eligible`);
  },

  async downloadCertificate(registrationId) {
    return await this.request(`/certificates/${registrationId}/pdf`);
  },

  // Dashboard
  async getMetrics() {
    return await this.request('/dashboard/metrics');
  }
};
