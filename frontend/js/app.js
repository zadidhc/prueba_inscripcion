// Interacción y lógica de presentación de la interfaz de usuario
document.addEventListener('DOMContentLoaded', () => {
  // Elementos DOM
  const navButtons = document.querySelectorAll('.nav-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const alertBox = document.getElementById('global-alert');

  // Elementos de Autenticación
  const authSection = document.getElementById('auth-section');
  const userInfo = document.getElementById('user-info');
  const userDisplay = document.getElementById('user-display');
  const btnOpenLogin = document.getElementById('btn-open-login');
  const btnLogout = document.getElementById('btn-logout');
  const modalLogin = document.getElementById('modal-login');
  const btnCloseLogin = document.getElementById('btn-close-login');
  const btnCancelLogin = document.getElementById('btn-cancel-login');
  const formLogin = document.getElementById('form-login');

  // Navegación por rol
  const navAtt = document.getElementById('nav-att');
  const navEvents = document.getElementById('nav-events');
  const navDash = document.getElementById('nav-dash');

  // Modal Inscripción
  const modalRegister = document.getElementById('modal-register');
  const btnCloseRegister = document.getElementById('btn-close-register');
  const btnCancelRegister = document.getElementById('btn-cancel-register');
  const formRegister = document.getElementById('form-register-participant');

  // Modal Gestión de Eventos
  const modalEvent = document.getElementById('modal-event');
  const modalEventTitle = document.getElementById('modal-event-title');
  const btnCloseEventModal = document.getElementById('btn-close-event-modal');
  const btnCancelEventModal = document.getElementById('btn-cancel-event-modal');
  const btnOpenCreateEvent = document.getElementById('btn-open-create-event');
  const formEventManage = document.getElementById('form-event-manage');

  // Asistencia
  const attEventSelect = document.getElementById('att-event-select');
  const attSessionSelect = document.getElementById('att-session-select');
  const formMarkAttendance = document.getElementById('form-mark-attendance');
  const btnSubmitAtt = document.getElementById('btn-submit-att');
  const btnRefreshAtt = document.getElementById('btn-refresh-att');

  // Dashboard & Refresh
  const btnRefreshMetrics = document.getElementById('btn-refresh-metrics');
  const btnRefreshPublic = document.getElementById('btn-refresh-public');

  // Búsqueda
  const formSearchParticipant = document.getElementById('form-search-participant');

  // Funciones de Notificación
  function showAlert(message, type = 'success', duration = 5000) {
    alertBox.className = `alert alert-${type}`;
    alertBox.innerHTML = `
      <span>${message}</span>
      <button style="background:none; border:none; color:inherit; font-weight:700; cursor:pointer;" onclick="this.parentElement.style.display='none'">&times;</button>
    `;
    alertBox.style.display = 'flex';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
      alertBox.style.display = 'none';
    }, duration);
  }

  // Control de Pestañas
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      if (!targetTab) return;

      navButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(t => t.classList.remove('active'));

      btn.classList.add('active');
      const activeEl = document.getElementById(targetTab);
      if (activeEl) activeEl.classList.add('active');

      if (targetTab === 'tab-public') loadPublicEvents();
      if (targetTab === 'tab-admin-events') loadAdminEvents();
      if (targetTab === 'tab-attendance') loadAttendanceEventsDropdown();
      if (targetTab === 'tab-dashboard') loadDashboardMetrics();
    });
  });

  // Manejo de Sesión / Roles
  function updateAuthUI() {
    const user = api.getUser();
    if (user) {
      authSection.style.display = 'none';
      userInfo.style.display = 'flex';
      userDisplay.innerHTML = `<strong>${user.full_name}</strong> (${user.role.toUpperCase()})`;

      navAtt.style.display = 'inline-block';
      if (user.role === 'admin') {
        navEvents.style.display = 'inline-block';
        navDash.style.display = 'inline-block';
      } else {
        navEvents.style.display = 'none';
        navDash.style.display = 'none';
      }
    } else {
      authSection.style.display = 'block';
      userInfo.style.display = 'none';
      navAtt.style.display = 'none';
      navEvents.style.display = 'none';
      navDash.style.display = 'none';
    }
  }

  window.addEventListener('auth-expired', () => {
    updateAuthUI();
    showAlert('Su sesión ha expirado. Inicie sesión nuevamente.', 'danger');
  });

  // Eventos de Autenticación
  btnOpenLogin.addEventListener('click', () => { modalLogin.style.display = 'flex'; });
  btnCloseLogin.addEventListener('click', () => { modalLogin.style.display = 'none'; });
  btnCancelLogin.addEventListener('click', () => { modalLogin.style.display = 'none'; });

  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value;
    try {
      await api.login(u, p);
      modalLogin.style.display = 'none';
      formLogin.reset();
      updateAuthUI();
      showAlert('Inicio de sesión exitoso. Bienvenido al sistema.', 'success');
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  });

  btnLogout.addEventListener('click', () => {
    api.removeToken();
    updateAuthUI();
    document.querySelector('[data-tab="tab-public"]').click();
    showAlert('Sesión cerrada correctamente.', 'success');
  });

  // ================= 1. EVENTOS PÚBLICOS =================
  async function loadPublicEvents() {
    const tbody = document.querySelector('#table-public-events tbody');
    tbody.innerHTML = `<tr><td colspan="7"><div class="loading-state"><div class="spinner"></div> Cargando catálogo de eventos...</div></td></tr>`;
    try {
      const events = await api.getEvents();
      if (!events || events.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7">
              <div class="empty-state">
                <div class="empty-state-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                  </svg>
                </div>
                <h3>No hay eventos disponibles actualmente</h3>
                <p>Las inscripciones para futuros eventos académicos se publicarán en esta sección. Inicie sesión como Administrador para registrar nuevos eventos.</p>
              </div>
            </td>
          </tr>`;
        return;
      }
      tbody.innerHTML = '';
      events.forEach(ev => {
        const tr = document.createElement('tr');
        const formattedDate = new Date(ev.start_time).toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' });
        const isFull = ev.active_registrations_count >= ev.max_capacity;
        const isOpen = ev.status === 'ABIERTA' && !isFull;

        tr.innerHTML = `
          <td><span style="font-family:monospace; font-weight:700; color:var(--text-muted);">#${ev.id}</span></td>
          <td>
            <div style="font-weight:700; color:var(--text-heading); font-size:0.95rem;">${ev.title}</div>
            <div style="color:var(--text-muted); font-size:0.825rem; margin-top:2px;">${ev.description}</div>
          </td>
          <td style="white-space:nowrap; color:var(--navy-800); font-weight:500;">${formattedDate}</td>
          <td><span style="display:inline-flex; align-items:center; gap:0.3rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>${ev.location}</span></td>
          <td><strong>${ev.max_capacity}</strong> cupos</td>
          <td>
            <span style="font-weight:600;">${ev.active_registrations_count} / ${ev.max_capacity}</span>
            ${isFull ? '<span class="badge badge-closed" style="margin-left:0.35rem;">Agotado</span>' : ''}
          </td>
          <td style="text-align: right; white-space:nowrap;">
            ${isOpen ? `<button class="btn btn-primary btn-sm btn-register" data-id="${ev.id}" data-title="${encodeURIComponent(ev.title)}">Inscribirme</button>` : `<span class="badge badge-closed">${ev.status === 'CERRADA' ? 'Cerrado' : 'Sin Cupos'}</span>`}
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.querySelectorAll('.btn-register').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-id');
          const title = decodeURIComponent(btn.getAttribute('data-title'));
          openRegisterModal(id, title);
        });
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state" style="color:var(--rose-700);"><p>Error al cargar eventos: ${err.message}</p></div></td></tr>`;
    }
  }

  if (btnRefreshPublic) {
    btnRefreshPublic.addEventListener('click', loadPublicEvents);
  }

  // ================= 2. INSCRIPCIÓN DE PARTICIPANTE =================
  function openRegisterModal(eventId, eventTitle) {
    document.getElementById('reg-event-id').value = eventId;
    document.getElementById('reg-event-title').value = eventTitle;
    formRegister.reset();
    document.getElementById('reg-event-id').value = eventId;
    document.getElementById('reg-event-title').value = eventTitle;
    modalRegister.style.display = 'flex';
  }

  btnCloseRegister.addEventListener('click', () => { modalRegister.style.display = 'none'; });
  btnCancelRegister.addEventListener('click', () => { modalRegister.style.display = 'none'; });

  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      event_id: parseInt(document.getElementById('reg-event-id').value),
      document_id: document.getElementById('reg-doc').value.trim(),
      full_name: document.getElementById('reg-name').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      participant_type: document.getElementById('reg-type').value
    };

    try {
      const res = await api.createRegistration(payload);
      modalRegister.style.display = 'none';
      showAlert(`Inscripción registrada correctamente. Código oficial de registro: <strong>${res.code}</strong>`, 'success', 9000);
      loadPublicEvents();
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  });

  // ================= 3. CONSULTAR INSCRIPCIÓN Y CERTIFICADOS =================
  formSearchParticipant.addEventListener('submit', async (e) => {
    e.preventDefault();
    const doc = document.getElementById('search-doc').value.trim();
    if (!doc) return;

    const resultsContainer = document.getElementById('search-results');
    const tbody = document.querySelector('#table-search-results tbody');
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-state"><div class="spinner"></div> Buscando inscripciones para el documento...</div></td></tr>`;
    resultsContainer.style.display = 'block';

    try {
      const regs = await api.getRegistrations({ document_id: doc });
      if (!regs || regs.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6">
              <div class="empty-state">
                <h3>No se encontraron inscripciones</h3>
                <p>No existen registros activos asociados al documento de identidad <strong>"${doc}"</strong>. Verifique el número ingresado o realice su inscripción en el catálogo de eventos.</p>
              </div>
            </td>
          </tr>`;
        return;
      }

      tbody.innerHTML = '';
      for (const r of regs) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong style="font-family:monospace; color:var(--primary);">${r.code}</strong></td>
          <td><strong>${r.event_title}</strong></td>
          <td>${r.full_name}</td>
          <td><span class="badge badge-type">${r.participant_type}</span></td>
          <td><span class="badge ${r.status === 'INSCRITO' ? 'badge-active' : 'badge-cancelled'}">${r.status}</span></td>
          <td style="text-align: right;">
            <button class="btn btn-outline btn-sm btn-download-cert" data-id="${r.id}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
              Descargar PDF
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      }

      document.querySelectorAll('.btn-download-cert').forEach(btn => {
        btn.addEventListener('click', async () => {
          const regId = btn.getAttribute('data-id');
          try {
            btn.textContent = 'Generando...';
            btn.disabled = true;
            const blob = await api.downloadCertificate(regId);
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `Certificado_Inscripcion_${regId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);
            showAlert('Certificado PDF descargado con éxito.', 'success');
          } catch (err) {
            showAlert(`Certificado no disponible: ${err.message}`, 'danger');
          } finally {
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Descargar PDF`;
            btn.disabled = false;
          }
        });
      });

    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state" style="color:var(--rose-700);"><p>${err.message}</p></div></td></tr>`;
    }
  });

  // ================= 4. GESTIÓN DE EVENTOS (ADMIN) =================
  async function loadAdminEvents() {
    const tbody = document.querySelector('#table-admin-events tbody');
    tbody.innerHTML = `<tr><td colspan="8"><div class="loading-state"><div class="spinner"></div> Cargando inventario de eventos...</div></td></tr>`;
    try {
      const events = await api.getEvents();
      if (!events || events.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8">
              <div class="empty-state">
                <h3>No hay eventos registrados en la base de datos</h3>
                <p>Presione el botón "+ Registrar Evento" para crear el primer evento del ciclo académico.</p>
              </div>
            </td>
          </tr>`;
        return;
      }
      tbody.innerHTML = '';
      events.forEach(ev => {
        const tr = document.createElement('tr');
        const formattedDate = new Date(ev.start_time).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' });
        tr.innerHTML = `
          <td><span style="font-family:monospace; font-weight:700;">#${ev.id}</span></td>
          <td><strong>${ev.title}</strong></td>
          <td>${formattedDate}</td>
          <td>${ev.location}</td>
          <td><strong>${ev.max_capacity}</strong> cupos</td>
          <td>${ev.active_registrations_count}</td>
          <td>
            <span class="badge ${ev.status === 'ABIERTA' ? 'badge-open' : 'badge-closed'}">${ev.status}</span>
          </td>
          <td style="text-align: right; white-space:nowrap;">
            <button class="btn btn-outline btn-sm btn-edit-event" data-id="${ev.id}">Editar</button>
            <button class="btn ${ev.status === 'ABIERTA' ? 'btn-danger' : 'btn-secondary'} btn-sm btn-toggle-status" data-id="${ev.id}" data-status="${ev.status}">
              ${ev.status === 'ABIERTA' ? 'Cerrar' : 'Habilitar'}
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.querySelectorAll('.btn-edit-event').forEach(btn => {
        btn.addEventListener('click', () => openEditEventModal(btn.getAttribute('data-id')));
      });

      document.querySelectorAll('.btn-toggle-status').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.getAttribute('data-id');
          const currentStatus = btn.getAttribute('data-status');
          const newStatus = currentStatus === 'ABIERTA' ? 'CERRADA' : 'ABIERTA';
          try {
            await api.updateEvent(id, { status: newStatus });
            showAlert(`El evento #${id} ahora tiene inscripciones: ${newStatus}`, 'success');
            loadAdminEvents();
          } catch (err) {
            showAlert(err.message, 'danger');
          }
        });
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state" style="color:var(--rose-700);"><p>${err.message}</p></div></td></tr>`;
    }
  }

  btnOpenCreateEvent.addEventListener('click', () => {
    formEventManage.reset();
    document.getElementById('manage-event-id').value = '';
    modalEventTitle.textContent = 'Nuevo Evento Académico';
    modalEvent.style.display = 'flex';
  });

  async function openEditEventModal(id) {
    try {
      const ev = await api.getEvent(id);
      document.getElementById('manage-event-id').value = ev.id;
      document.getElementById('ev-title').value = ev.title;
      document.getElementById('ev-desc').value = ev.description;
      document.getElementById('ev-date').value = ev.start_time.slice(0, 16);
      document.getElementById('ev-capacity').value = ev.max_capacity;
      document.getElementById('ev-location').value = ev.location;
      document.getElementById('ev-status').value = ev.status;
      modalEventTitle.textContent = `Editar Evento #${ev.id}`;
      modalEvent.style.display = 'flex';
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  }

  btnCloseEventModal.addEventListener('click', () => { modalEvent.style.display = 'none'; });
  btnCancelEventModal.addEventListener('click', () => { modalEvent.style.display = 'none'; });

  formEventManage.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('manage-event-id').value;
    const payload = {
      title: document.getElementById('ev-title').value.trim(),
      description: document.getElementById('ev-desc').value.trim(),
      start_time: new Date(document.getElementById('ev-date').value).toISOString(),
      max_capacity: parseInt(document.getElementById('ev-capacity').value),
      location: document.getElementById('ev-location').value.trim(),
      status: document.getElementById('ev-status').value
    };

    try {
      if (id) {
        await api.updateEvent(id, payload);
        showAlert('Evento académico actualizado correctamente.', 'success');
      } else {
        await api.createEvent(payload);
        showAlert('Evento registrado exitosamente con su sesión obligatoria inicial.', 'success');
      }
      modalEvent.style.display = 'none';
      loadAdminEvents();
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  });

  // ================= 5. ASISTENCIA =================
  async function loadAttendanceEventsDropdown() {
    try {
      const events = await api.getEvents();
      attEventSelect.innerHTML = '<option value="">Seleccione un evento académico...</option>';
      events.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.id;
        opt.textContent = `#${e.id} — ${e.title}`;
        attEventSelect.appendChild(opt);
      });
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  }

  attEventSelect.addEventListener('change', async () => {
    const eventId = attEventSelect.value;
    if (!eventId) {
      attSessionSelect.innerHTML = '<option value="">Primero elija un evento</option>';
      attSessionSelect.disabled = true;
      btnSubmitAtt.disabled = true;
      document.querySelector('#table-attendance-matrix tbody').innerHTML = `
        <tr><td colspan="8"><div class="empty-state"><p>Seleccione un evento académico para visualizar el control de asistencia.</p></div></td></tr>`;
      return;
    }

    try {
      const eventDetail = await api.getEvent(eventId);
      attSessionSelect.innerHTML = '';
      if (!eventDetail.sessions || eventDetail.sessions.length === 0) {
        attSessionSelect.innerHTML = '<option value="">No hay sesiones programadas</option>';
        attSessionSelect.disabled = true;
        btnSubmitAtt.disabled = true;
      } else {
        eventDetail.sessions.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s.id;
          opt.textContent = `${s.title} ${s.is_mandatory ? '(Obligatoria)' : ''}`;
          attSessionSelect.appendChild(opt);
        });
        attSessionSelect.disabled = false;
        btnSubmitAtt.disabled = false;
      }
      loadAttendanceMatrix(eventId);
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  });

  async function loadAttendanceMatrix(eventId) {
    const tbody = document.querySelector('#table-attendance-matrix tbody');
    tbody.innerHTML = `<tr><td colspan="8"><div class="loading-state"><div class="spinner"></div> Cargando registros de asistencia...</div></td></tr>`;
    try {
      const matrix = await api.getEventAttendances(eventId);
      if (!matrix || matrix.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8">
              <div class="empty-state">
                <h3>No hay participantes inscritos en este evento</h3>
                <p>Cuando los estudiantes o docentes se inscriban a este evento académico, aparecerán listados aquí para el control de asistencia.</p>
              </div>
            </td>
          </tr>`;
        return;
      }
      tbody.innerHTML = '';
      matrix.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong style="font-family:monospace;">${p.code}</strong></td>
          <td>${p.document_id}</td>
          <td><strong>${p.full_name}</strong></td>
          <td><span class="badge badge-type">${p.participant_type}</span></td>
          <td><span class="badge ${p.status === 'INSCRITO' ? 'badge-active' : 'badge-cancelled'}">${p.status}</span></td>
          <td><strong>${p.attended_sessions}</strong> / ${p.total_mandatory_sessions}</td>
          <td>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span style="font-weight:700;">${p.attendance_percentage}%</span>
            </div>
          </td>
          <td style="text-align: right;">
            ${p.is_eligible_certificate ? '<span class="badge badge-open">ELEGIBLE</span>' : '<span class="badge badge-closed">NO ELEGIBLE</span>'}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state" style="color:var(--rose-700);"><p>${err.message}</p></div></td></tr>`;
    }
  }

  formMarkAttendance.addEventListener('submit', async (e) => {
    e.preventDefault();
    const sessionId = attSessionSelect.value;
    const docId = document.getElementById('att-doc').value.trim();
    if (!sessionId || !docId) return;

    try {
      const res = await api.recordAttendance(sessionId, docId);
      showAlert(`Asistencia registrada exitosamente para: <strong>${res.participant_name}</strong> (DNI: ${res.document_id})`, 'success');
      document.getElementById('att-doc').value = '';
      loadAttendanceMatrix(attEventSelect.value);
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  });

  btnRefreshAtt.addEventListener('click', () => {
    if (attEventSelect.value) {
      loadAttendanceMatrix(attEventSelect.value);
    }
  });

  // ================= 6. PANEL Y REPORTES (ADMIN) =================
  async function loadDashboardMetrics() {
    try {
      const metrics = await api.getMetrics();
      document.getElementById('metric-total-events').textContent = metrics.total_events;
      document.getElementById('metric-open-events').textContent = metrics.open_events;
      document.getElementById('metric-total-regs').textContent = metrics.total_registrations;
      document.getElementById('metric-total-atts').textContent = metrics.total_attendances;
      document.getElementById('metric-total-certs').textContent = metrics.total_eligible_certificates;

      const tbody = document.querySelector('#table-summary-events tbody');
      if (!metrics.events_summary || metrics.events_summary.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6">
              <div class="empty-state">
                <h3>Sin eventos para reportar</h3>
                <p>Las estadísticas se actualizarán automáticamente conforme se registren eventos y participantes.</p>
              </div>
            </td>
          </tr>`;
        return;
      }

      tbody.innerHTML = '';
      metrics.events_summary.forEach(e => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><span style="font-family:monospace; font-weight:700;">#${e.event_id}</span></td>
          <td><strong>${e.title}</strong></td>
          <td>${e.capacity} cupos</td>
          <td>${e.registrations} participantes</td>
          <td>${e.attendances} asistencias</td>
          <td><span class="badge ${e.status === 'ABIERTA' ? 'badge-open' : 'badge-closed'}">${e.status}</span></td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      showAlert(err.message, 'danger');
    }
  }

  btnRefreshMetrics.addEventListener('click', loadDashboardMetrics);

  // Inicialización
  updateAuthUI();
  loadPublicEvents();
});
