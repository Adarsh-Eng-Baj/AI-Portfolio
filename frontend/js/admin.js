/**
 * admin.js — Admin dashboard logic.
 * Handles auth guard, sections, analytics charts, CRUD operations.
 */

// ─────────────────────────────────────────────
// Auth Guard — redirect non-admin users
// ─────────────────────────────────────────────
if (!Auth.isLoggedIn()) {
  window.location.href = '/admin/login.html';
}

// ─────────────────────────────────────────────
// State
// ─────────────────────────────────────────────
let currentSection = 'overview';
let allProjects = [];
let allMessages = [];
let allBlogPosts = [];
let visitsChart = null;
let deviceChart = null;

// ─────────────────────────────────────────────
// Initialization
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await loadAdminUser();
  await loadOverview();
  await loadMessages(); // pre-load for badge

  // Analytics day selector
  document.getElementById('analytics-days')?.addEventListener('change', () => loadOverview());

  // Logout
  document.getElementById('logout-btn').addEventListener('click', () => {
    Auth.removeToken();
    SuccessAnim.show({
      title: 'Logged Out',
      subtitle: 'You have been successfully logged out.',
      badge: 'Session Ended',
      autoClose: 1500
    });
    setTimeout(() => window.location.href = '/admin/login.html', 1500);
  });

  // Change Password Form
  document.getElementById('change-pwd-form')?.addEventListener('submit', handlePasswordChange);
});

// ─────────────────────────────────────────────
// Load current admin user info
// ─────────────────────────────────────────────
async function loadAdminUser() {
  try {
    const { user } = await API.auth.me();
    if (document.getElementById('admin-name')) {
      document.getElementById('admin-name').textContent = user.name;
    }
    if (document.getElementById('topbar-name')) {
      document.getElementById('topbar-name').textContent = user.name.split(' ')[0];
    }
  } catch (_) {
    Auth.removeToken();
    window.location.href = '/admin/login.html';
  }
}

// ─────────────────────────────────────────────
// Section Switching
// ─────────────────────────────────────────────
function switchSection(section, linkEl) {
  // Hide all sections
  document.querySelectorAll('[id^="section-"]').forEach(s => s.style.display = 'none');
  // Remove active from all links
  document.querySelectorAll('.dash-nav-link').forEach(l => l.classList.remove('active'));

  // Show selected section
  document.getElementById(`section-${section}`).style.display = 'block';
  if (linkEl) linkEl.classList.add('active');

  currentSection = section;

  // Lazy-load section data
  if (section === 'projects')  loadProjects();
  if (section === 'messages')  loadMessages();
  if (section === 'analytics') loadPageAnalytics();
  if (section === 'blog')      loadBlogPosts();
}

// ─────────────────────────────────────────────
// OVERVIEW — Analytics Summary
// ─────────────────────────────────────────────
async function loadOverview() {
  const days = parseInt(document.getElementById('analytics-days')?.value || 30);

  try {
    const [analyticsRes, projectsRes, contactRes] = await Promise.all([
      API.analytics.summary(days),
      API.projects.list(),
      API.contact.list({ unread: true }),
    ]);

    // Stat cards
    document.getElementById('stat-visits').textContent    = analyticsRes.summary.total_visits.toLocaleString();
    document.getElementById('stat-sessions').textContent  = analyticsRes.summary.unique_sessions.toLocaleString();
    document.getElementById('stat-messages').textContent  = contactRes.unread_count || 0;
    document.getElementById('stat-projects').textContent  = projectsRes.total;

    // Unread badge in sidebar
    const badge = document.getElementById('unread-badge');
    if (contactRes.unread_count > 0) {
      badge.textContent = contactRes.unread_count;
      badge.style.display = 'inline-block';
    }

    // Top pages table
    const tbody = document.getElementById('top-pages-tbody');
    tbody.innerHTML = analyticsRes.top_pages.slice(0, 8).map((p, i) => `
      <tr>
        <td><span class="badge badge-purple">${i + 1}</span></td>
        <td style="font-family:var(--font-mono);font-size:var(--text-sm);">${p.page}</td>
        <td><strong>${p.visits}</strong></td>
      </tr>`
    ).join('') || '<tr><td colspan="3" style="text-align:center;color:var(--clr-text-muted);">No data yet</td></tr>';

    // Charts
    renderVisitsChart(analyticsRes.daily_visits);
    renderDeviceChart(analyticsRes.device_breakdown);

  } catch (err) {
    console.warn('Analytics error:', err.message);
    // Show zeros on error (backend might not have data yet)
    ['stat-visits','stat-sessions','stat-messages','stat-projects'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = '0';
    });
  }
}

function renderVisitsChart(dailyData) {
  const ctx = document.getElementById('visits-chart')?.getContext('2d');
  if (!ctx) return;

  if (visitsChart) visitsChart.destroy();

  const labels = (dailyData || []).map(d => {
    const dt = new Date(d.date);
    return dt.toLocaleDateString('en', { month: 'short', day: 'numeric' });
  });
  const data = (dailyData || []).map(d => d.visits);

  visitsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Visits',
        data,
        borderColor: '#7c3aed',
        backgroundColor: 'rgba(124,58,237,0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#7c3aed',
        pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b', precision: 0 }, beginAtZero: true },
      }
    }
  });
}

function renderDeviceChart(deviceData) {
  const ctx = document.getElementById('device-chart')?.getContext('2d');
  if (!ctx) return;

  if (deviceChart) deviceChart.destroy();

  const labels = Object.keys(deviceData || { desktop: 1 });
  const data   = Object.values(deviceData || { desktop: 1 });
  const colors = ['#7c3aed','#06b6d4','#10b981'];

  deviceChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 0 }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } }
      },
      cutout: '65%',
    }
  });
}

// ─────────────────────────────────────────────
// PROJECTS — CRUD
// ─────────────────────────────────────────────
async function loadProjects() {
  const tbody = document.getElementById('projects-tbody');
  try {
    const { projects } = await API.projects.list();
    allProjects = projects;

    if (!projects.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:var(--space-xl);color:var(--clr-text-muted);">No projects yet. Add one! 🚀</td></tr>';
      return;
    }

    tbody.innerHTML = projects.map(p => `
      <tr>
        <td>
          <div style="font-weight:600;">${p.title}</div>
          <div style="font-size:var(--text-xs);color:var(--clr-text-muted);">${truncate(p.description, 60)}</div>
        </td>
        <td><span class="badge badge-purple">${p.category}</span></td>
        <td><span class="badge ${p.status === 'completed' ? 'badge-green' : p.status === 'in-progress' ? 'badge-orange' : 'badge-blue'}">${p.status}</span></td>
        <td>${p.featured ? '⭐ Yes' : '—'}</td>
        <td style="font-size:var(--text-xs);color:var(--clr-text-muted);">${formatDate(p.created_at)}</td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-ghost btn-sm" onclick="editProject(${p.id})">✏️</button>
            <button class="btn btn-outline btn-sm" style="border-color:rgba(239,68,68,0.4);color:var(--clr-red);" onclick="deleteProject(${p.id},'${p.title.replace(/'/g,'\\')}')">🗑️</button>
          </div>
        </td>
      </tr>`
    ).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-xl);color:var(--clr-red);">${err.message}</td></tr>`;
  }
}

function openProjectModal(projectId = null) {
  document.getElementById('project-form').reset();
  document.getElementById('proj-id').value = '';
  document.getElementById('proj-modal-title').textContent = 'Add New Project';
  document.getElementById('proj-save-text').textContent = 'Save Project';
  document.getElementById('proj-modal-overlay').classList.add('open');
}

function editProject(id) {
  const p = allProjects.find(p => p.id === id);
  if (!p) return;

  document.getElementById('proj-id').value       = p.id;
  document.getElementById('proj-title').value     = p.title;
  document.getElementById('proj-desc').value      = p.description || '';
  document.getElementById('proj-long-desc').value = p.long_description || '';
  document.getElementById('proj-tech').value      = (p.tech_stack || []).join(', ');
  document.getElementById('proj-github').value    = p.github_url || '';
  document.getElementById('proj-demo').value      = p.demo_url || '';
  document.getElementById('proj-image').value     = p.image_url || '';
  document.getElementById('proj-featured').checked = p.featured;
  document.getElementById('proj-category').value  = p.category || 'AI/ML';
  document.getElementById('proj-status').value    = p.status || 'completed';

  document.getElementById('proj-modal-title').textContent = 'Edit Project';
  document.getElementById('proj-save-text').textContent = 'Update Project';
  document.getElementById('proj-modal-overlay').classList.add('open');
}

function closeProjectModal() {
  document.getElementById('proj-modal-overlay').classList.remove('open');
}

async function saveProject() {
  const id = document.getElementById('proj-id').value;
  const title = document.getElementById('proj-title').value.trim();

  if (!title) {
    Toast.error('Validation', 'Project title is required.');
    return;
  }

  const saveBtn     = document.getElementById('proj-save-btn');
  const saveText    = document.getElementById('proj-save-text');
  const saveSpinner = document.getElementById('proj-save-spinner');
  saveBtn.disabled  = true;
  saveText.style.display   = 'none';
  saveSpinner.style.display = 'block';

  const data = {
    title,
    description:      document.getElementById('proj-desc').value.trim(),
    long_description: document.getElementById('proj-long-desc').value.trim(),
    tech_stack:       document.getElementById('proj-tech').value.trim(),
    github_url:       document.getElementById('proj-github').value.trim(),
    demo_url:         document.getElementById('proj-demo').value.trim(),
    image_url:        document.getElementById('proj-image').value.trim(),
    category:         document.getElementById('proj-category').value,
    status:           document.getElementById('proj-status').value,
    featured:         document.getElementById('proj-featured').checked,
  };

  try {
    if (id) {
      await API.projects.update(id, data);
      Toast.success('Updated! ✅', `"${title}" has been updated.`);
    } else {
      await API.projects.create(data);
      Toast.success('Created! 🚀', `"${title}" has been added.`);
    }
    closeProjectModal();
    await loadProjects();
  } catch (err) {
    Toast.error('Save Failed', err.message);
  } finally {
    saveBtn.disabled = false;
    saveText.style.display   = 'block';
    saveSpinner.style.display = 'none';
  }
}

async function deleteProject(id, title) {
  if (!confirm(`Delete project "${title}"? This cannot be undone.`)) return;
  try {
    await API.projects.delete(id);
    Toast.success('Deleted', `"${title}" has been removed.`);
    await loadProjects();
  } catch (err) {
    Toast.error('Delete Failed', err.message);
  }
}

// ─────────────────────────────────────────────
// MESSAGES
// ─────────────────────────────────────────────
async function loadMessages() {
  const container = document.getElementById('messages-list');
  const unreadOnly = document.getElementById('unread-filter')?.checked || false;

  try {
    const { messages, unread_count } = await API.contact.list({ unread: unreadOnly });
    allMessages = messages;

    // Update unread badge
    const badge = document.getElementById('unread-badge');
    if (badge) {
      badge.textContent = unread_count;
      badge.style.display = unread_count > 0 ? 'inline-block' : 'none';
    }
    document.getElementById('stat-messages').textContent = unread_count;

    if (!container) return;

    if (!messages.length) {
      container.innerHTML = `
        <div style="text-align:center;padding:var(--space-3xl);">
          <p style="font-size:2.5rem;">📭</p>
          <h3>No messages yet</h3>
          <p style="color:var(--clr-text-muted);">Messages from your contact form will appear here.</p>
        </div>`;
      return;
    }

    container.innerHTML = messages.map(m => `
      <div class="card" style="padding:var(--space-xl);cursor:pointer;border-left:3px solid ${m.is_read ? 'transparent' : 'var(--clr-purple)'};"
           onclick="viewMessage(${m.id})">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:var(--space-sm);">
          <div>
            <span style="font-weight:700;">${m.name}</span>
            <span style="color:var(--clr-text-muted);font-size:var(--text-sm);margin-left:8px;">&lt;${m.email}&gt;</span>
          </div>
          <div style="display:flex;align-items:center;gap:var(--space-sm);">
            ${!m.is_read ? '<span class="badge badge-purple">New</span>' : ''}
            <span style="font-size:var(--text-xs);color:var(--clr-text-dim);">${formatDate(m.created_at)}</span>
          </div>
        </div>
        <div style="font-weight:600;font-size:var(--text-sm);margin-bottom:4px;">${m.subject || 'No Subject'}</div>
        <p style="font-size:var(--text-sm);color:var(--clr-text-muted);">${truncate(m.message, 120)}</p>
      </div>`
    ).join('');

  } catch (err) {
    if (container) container.innerHTML = `
      <div style="text-align:center;padding:var(--space-2xl);color:var(--clr-red);">
        Failed to load messages: ${err.message}
      </div>`;
  }
}

async function viewMessage(id) {
  const msg = allMessages.find(m => m.id === id);
  if (!msg) return;

  document.getElementById('msg-modal-body').innerHTML = `
    <div style="margin-bottom:var(--space-lg);">
      <div style="display:flex;gap:var(--space-lg);flex-wrap:wrap;margin-bottom:var(--space-md);">
        <div><div style="font-size:var(--text-xs);color:var(--clr-text-muted);">FROM</div><strong>${msg.name}</strong> &lt;${msg.email}&gt;</div>
        <div><div style="font-size:var(--text-xs);color:var(--clr-text-muted);">DATE</div>${formatDate(msg.created_at)}</div>
        <div><div style="font-size:var(--text-xs);color:var(--clr-text-muted);">SUBJECT</div>${msg.subject || '—'}</div>
      </div>
      <div style="background:var(--clr-surface2);border-radius:var(--radius-md);padding:var(--space-lg);white-space:pre-wrap;font-size:var(--text-sm);">
        ${msg.message}
      </div>
    </div>`;

  document.getElementById('msg-modal-footer').innerHTML = `
    <button class="btn btn-ghost" onclick="closeMsgModal()">Close</button>
    ${!msg.is_read ? `<button class="btn btn-outline" onclick="markMsgRead(${msg.id})">✅ Mark as Read</button>` : ''}
    <button class="btn btn-outline" style="border-color:rgba(239,68,68,0.4);color:var(--clr-red);" onclick="deleteMessage(${msg.id})">🗑️ Delete</button>
    <a href="mailto:${msg.email}?subject=Re: ${encodeURIComponent(msg.subject || '')}" class="btn btn-primary">📧 Reply</a>`;

  document.getElementById('msg-modal-overlay').classList.add('open');

  // Auto-mark as read
  if (!msg.is_read) await markMsgRead(msg.id, false);
}

function closeMsgModal() {
  document.getElementById('msg-modal-overlay').classList.remove('open');
}

async function markMsgRead(id, reload = true) {
  try {
    await API.contact.markRead(id);
    const msg = allMessages.find(m => m.id === id);
    if (msg) msg.is_read = true;
    if (reload) {
      closeMsgModal();
      loadMessages();
    }
  } catch (err) {
    Toast.error('Error', err.message);
  }
}

async function deleteMessage(id) {
  if (!confirm('Delete this message permanently?')) return;
  try {
    await API.contact.delete(id);
    Toast.success('Deleted', 'Message removed.');
    closeMsgModal();
    loadMessages();
  } catch (err) {
    Toast.error('Error', err.message);
  }
}

// ─────────────────────────────────────────────
// PAGE ANALYTICS
// ─────────────────────────────────────────────
async function loadPageAnalytics() {
  const tbody = document.getElementById('pages-analytics-tbody');
  try {
    const { pages } = await API.analytics.pages();
    tbody.innerHTML = pages.map(p => `
      <tr>
        <td style="font-family:var(--font-mono);font-size:var(--text-sm);">${p.page}</td>
        <td><strong>${p.visits}</strong></td>
        <td>${p.avg_duration}s</td>
      </tr>`
    ).join('') || '<tr><td colspan="3" style="text-align:center;color:var(--clr-text-muted);">No data yet</td></tr>';
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:var(--clr-red);">${err.message}</td></tr>`;
  }
}

// Modal close on overlay click
document.addEventListener('click', e => {
  if (e.target.id === 'proj-modal-overlay') closeProjectModal();
  if (e.target.id === 'msg-modal-overlay')  closeMsgModal();
  if (e.target.id === 'blog-modal-overlay') closeBlogModal();
});

// ─────────────────────────────────────────────
// BLOG POSTS — CRUD
// ─────────────────────────────────────────────
async function loadBlogPosts() {
  const tbody = document.getElementById('blog-tbody');
  try {
    const { posts } = await API.blog.list({ all: true });
    allBlogPosts = posts;

    if (!posts.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:var(--space-xl);color:var(--clr-text-muted);">No blog posts yet. Write your first one! ✍️</td></tr>';
      return;
    }

    tbody.innerHTML = posts.map(p => `
      <tr>
        <td>
          <div style="font-weight:600;">${p.title}</div>
          <div style="font-size:var(--text-xs);color:var(--clr-text-muted);">${truncate(p.excerpt || '', 60)}</div>
        </td>
        <td><span class="badge badge-purple">${p.category}</span></td>
        <td><span class="badge ${p.is_published ? 'badge-green' : 'badge-orange'}">${p.is_published ? 'Published' : 'Draft'}</span></td>
        <td>👁 ${p.views}</td>
        <td>⏱ ${p.read_time}m</td>
        <td>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-ghost btn-sm" onclick="editBlogPost(${p.id})">✏️</button>
            <button class="btn btn-outline btn-sm" style="border-color:rgba(239,68,68,0.4);color:var(--clr-red);" onclick="deleteBlogPost(${p.id},'${p.title.replace(/'/g,"\\'")}')">🗑️</button>
          </div>
        </td>
      </tr>`
    ).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-xl);color:var(--clr-red);">${err.message}</td></tr>`;
  }
}

function openBlogModal() {
  document.getElementById('blog-form').reset();
  document.getElementById('blog-id').value = '';
  document.getElementById('blog-modal-title').textContent = 'New Blog Post';
  document.getElementById('blog-save-text').textContent = 'Save Post';
  document.getElementById('blog-modal-overlay').classList.add('open');
}

function editBlogPost(id) {
  const p = allBlogPosts.find(p => p.id === id);
  if (!p) return;

  document.getElementById('blog-id').value        = p.id;
  document.getElementById('blog-title').value     = p.title;
  document.getElementById('blog-excerpt').value   = p.excerpt || '';
  document.getElementById('blog-content').value   = p.content || '';
  document.getElementById('blog-category').value  = p.category || 'General';
  document.getElementById('blog-read-time').value = p.read_time || 5;
  document.getElementById('blog-tags').value      = (p.tags || []).join(', ');
  document.getElementById('blog-cover').value     = p.cover_image || '';
  document.getElementById('blog-published').checked = p.is_published;

  document.getElementById('blog-modal-title').textContent = 'Edit Blog Post';
  document.getElementById('blog-save-text').textContent = 'Update Post';
  document.getElementById('blog-modal-overlay').classList.add('open');
}

function closeBlogModal() {
  document.getElementById('blog-modal-overlay').classList.remove('open');
}

async function saveBlogPost() {
  const id    = document.getElementById('blog-id').value;
  const title = document.getElementById('blog-title').value.trim();
  const content = document.getElementById('blog-content').value.trim();

  if (!title || !content) {
    Toast.error('Validation', 'Title and content are required.');
    return;
  }

  const saveBtn     = document.getElementById('blog-save-btn');
  const saveText    = document.getElementById('blog-save-text');
  const saveSpinner = document.getElementById('blog-save-spinner');
  saveBtn.disabled  = true;
  saveText.style.display   = 'none';
  saveSpinner.style.display = 'block';

  const data = {
    title,
    excerpt:      document.getElementById('blog-excerpt').value.trim(),
    content,
    category:     document.getElementById('blog-category').value,
    read_time:    parseInt(document.getElementById('blog-read-time').value) || 5,
    tags:         document.getElementById('blog-tags').value.trim(),
    cover_image:  document.getElementById('blog-cover').value.trim(),
    is_published: document.getElementById('blog-published').checked,
  };

  try {
    if (id) {
      await API.blog.update(id, data);
      Toast.success('Updated! ✅', `"${title}" has been updated.`);
    } else {
      await API.blog.create(data);
      Toast.success('Published! 🚀', `"${title}" has been created.`);
    }
    closeBlogModal();
    await loadBlogPosts();
  } catch (err) {
    Toast.error('Save Failed', err.message);
  } finally {
    saveBtn.disabled = false;
    saveText.style.display   = 'block';
    saveSpinner.style.display = 'none';
  }
}

async function deleteBlogPost(id, title) {
  if (!confirm(`Delete blog post "${title}"? This cannot be undone.`)) return;
  try {
    await API.blog.delete(id);
    Toast.success('Deleted', `"${title}" has been removed.`);
    await loadBlogPosts();
  } catch (err) {
    Toast.error('Delete Failed', err.message);
  }
}

// ─────────────────────────────────────────────
// SETTINGS — Change Password
// ─────────────────────────────────────────────
async function handlePasswordChange(e) {
  e.preventDefault();

  const currentPass = document.getElementById('current-password').value;
  const newPass     = document.getElementById('new-password').value;
  const confirmPass = document.getElementById('confirm-password').value;

  if (newPass !== confirmPass) {
    Toast.error('Validation Error', 'New passwords do not match.');
    return;
  }

  const btn = document.getElementById('change-pwd-btn');
  const text = document.getElementById('change-pwd-text');
  const spinner = document.getElementById('change-pwd-spinner');

  btn.disabled = true;
  text.style.display = 'none';
  spinner.style.display = 'block';

  try {
    const res = await API.auth.changePassword(currentPass, newPass);
    
    SuccessAnim.show({
      title: 'Password Changed! 🔐',
      subtitle: res.message || 'Identity verified and security updated.',
      badge: 'High Security',
      autoClose: 2000
    });

    // Logout after 2 seconds
    setTimeout(() => {
      Auth.removeToken();
      window.location.href = '/admin/login.html';
    }, 2000);

  } catch (err) {
    Toast.error('Change Failed', err.message || 'Check your current password.');
    btn.disabled = false;
    text.style.display = 'block';
    spinner.style.display = 'none';
  }
}
