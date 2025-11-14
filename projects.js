// Jared Consulting Projects SPA
// LocalStorage-backed project manager with hash routing

(function(){
  'use strict';

  const LS_KEY = 'jc_projects_v1';
  const $app = document.getElementById('app');
  const $year = document.getElementById('year');
  if ($year) $year.textContent = String(new Date().getFullYear());

  // Utilities
  const fmt = new Intl.NumberFormat(undefined, { style:'currency', currency:'USD', maximumFractionDigits: 0});
  const byId = (id) => document.getElementById(id);
  const el = (tag, attrs={}, children=[]) => {
    const n = document.createElement(tag);
    Object.entries(attrs).forEach(([k,v])=>{
      if (k === 'class') n.className = v; else if (k === 'html') n.innerHTML = v; else n.setAttribute(k, v);
    });
    children.forEach(c=> n.appendChild(c));
    return n;
  };

  // Data model
  function uid(){ return Math.random().toString(36).slice(2,10); }

  function load(){
    try{ return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); }
    catch{ return []; }
  }
  function save(items){ localStorage.setItem(LS_KEY, JSON.stringify(items)); }
  function all(){ return load().sort((a,b)=> (b.updatedAt||0) - (a.updatedAt||0)); }
  function get(id){ return all().find(p=> p.id === id) || null; }
  function upsert(project){
    const list = load();
    const idx = list.findIndex(p=> p.id === project.id);
    project.updatedAt = Date.now();
    if (idx >= 0) list[idx] = project; else list.push(project);
    save(list);
    return project;
  }
  function remove(id){ save(load().filter(p=> p.id !== id)); }

  // Router
  const routes = {
    '#/dashboard': renderDashboard,
    '#/projects': renderList,
    '#/new': renderFormNew,
  };
  window.addEventListener('hashchange', onRoute);
  window.addEventListener('DOMContentLoaded', onRoute);
  if (!location.hash) location.hash = '#/dashboard';

  function onRoute(){
    const hash = location.hash;
    if (hash.startsWith('#/project/')) return renderDetail(hash.split('/')[2]);
    if (hash.startsWith('#/edit/')) return renderFormEdit(hash.split('/')[2]);
    const fn = routes[hash] || renderNotFound;
    fn();
  }

  // Views
  function renderNotFound(){
    $app.innerHTML = '<div class="section"><h2>Not found</h2><p class="helper">The page you requested does not exist.</p></div>';
  }

  function renderDashboard(){
    const items = all();
    const total = items.length;
    const active = items.filter(p=> p.status === 'active').length;
    const paused = items.filter(p=> p.status === 'paused').length;
    const closed = items.filter(p=> p.status === 'closed').length;
    const budget = items.reduce((s,p)=> s + (Number(p.budget)||0), 0);
    const upcoming = items
      .filter(p=> p.endDate)
      .sort((a,b)=> new Date(a.endDate) - new Date(b.endDate))
      .slice(0,5);

    $app.innerHTML = '';
    const wrap = el('div', {class:'cards'});

    wrap.appendChild(cardMetric('Total Projects', String(total)));
    wrap.appendChild(cardMetric('Active', String(active)));
    wrap.appendChild(cardMetric('Paused', String(paused)));
    wrap.appendChild(cardMetric('Closed', String(closed)));
    wrap.appendChild(cardMetric('Budget (sum)', fmt.format(budget)));

    const upcomingList = el('div', {class:'section'});
    upcomingList.appendChild(el('h2', {html:'Upcoming Deadlines'}));
    if (upcoming.length === 0) {
      upcomingList.appendChild(el('p', {class:'helper', html:'No upcoming deadlines.'}));
    } else {
      const table = el('table', {class:'table'});
      table.innerHTML = '<thead><tr><th>Project</th><th>Client</th><th>Due</th><th>Status</th></tr></thead>';
      const tb = el('tbody');
      upcoming.forEach(p=>{
        const tr = el('tr');
        tr.appendChild(tdLink(p.name, `#/project/${p.id}`));
        tr.appendChild(el('td', {html: escapeHtml(p.client||'—')}));
        tr.appendChild(el('td', {html: p.endDate||'—'}));
        tr.appendChild(el('td', {html: badge(p.status)}));
        tb.appendChild(tr);
      });
      table.appendChild(tb);
      upcomingList.appendChild(table);
    }

    $app.appendChild(wrap);
    $app.appendChild(upcomingList);
  }

  function renderList(){
    const items = all();
    const section = el('div', {class:'section'});
    section.appendChild(el('h2', {html:'Projects'}));
    const actions = el('div', {class:'actions'});
    actions.appendChild(linkBtn('#/new', '+ New Project', 'btn btn-primary'));
    section.appendChild(actions);

    const table = el('table', {class:'table'});
    table.innerHTML = '<thead><tr><th>Name</th><th>Client</th><th>Status</th><th>Budget</th><th>Dates</th><th></th></tr></thead>';
    const tb = el('tbody');
    if (items.length === 0) {
      const tr = el('tr');
      const td = el('td', {html:'No projects yet.', class:'helper'}); td.colSpan = 6; tr.appendChild(td);
      tb.appendChild(tr);
    } else {
      items.forEach(p=>{
        const tr = el('tr');
        tr.appendChild(tdLink(p.name, `#/project/${p.id}`));
        tr.appendChild(el('td', {html: escapeHtml(p.client||'—')}));
        tr.appendChild(el('td', {html: badge(p.status)}));
        const bud = Number(p.budget)||0; tr.appendChild(el('td', {html: bud ? fmt.format(bud) : '—'}));
        const dates = [p.startDate||'', p.endDate||''].filter(Boolean).join(' → ');
        tr.appendChild(el('td', {html: dates || '—'}));
        const actions = el('td');
        actions.appendChild(linkBtn(`#/edit/${p.id}`, 'Edit', 'btn btn-ghost small'));
        actions.appendChild(btn('Delete', 'btn small', ()=>{ if (confirm(`Delete "${p.name}"?`)){ remove(p.id); renderList(); }}));
        tr.appendChild(actions);
        tb.appendChild(tr);
      });
    }
    table.appendChild(tb);
    section.appendChild(table);
    $app.innerHTML = '';
    $app.appendChild(section);
  }

  function renderDetail(id){
    const p = get(id);
    if (!p) { return renderNotFound(); }
    const section = el('div', {class:'section'});
    section.appendChild(el('h2', {html: escapeHtml(p.name)}));

    const meta = el('div');
    meta.innerHTML = `
      <p><strong>Client:</strong> ${escapeHtml(p.client||'—')}</p>
      <p><strong>Status:</strong> ${badge(p.status)}</p>
      <p><strong>Budget:</strong> ${p.budget ? fmt.format(Number(p.budget)) : '—'}</p>
      <p><strong>Dates:</strong> ${(p.startDate||'—')} → ${(p.endDate||'—')}</p>
    `;
    section.appendChild(meta);

    section.appendChild(el('h3', {html:'Description'}));
    section.appendChild(el('p', {class:'helper', html: escapeHtml(p.description||'—')}));

    const actions = el('div', {class:'actions'});
    actions.appendChild(linkBtn(`#/edit/${p.id}`, 'Edit Project', 'btn btn-primary'));
    actions.appendChild(linkBtn('#/projects', 'Back to List', 'btn btn-ghost'));
    section.appendChild(actions);

    $app.innerHTML = '';
    $app.appendChild(section);
  }

  function renderFormNew(){ renderForm({ id: uid(), name:'', client:'', status:'prospect', budget:'', startDate:'', endDate:'', description:'' }, 'Create Project'); }
  function renderFormEdit(id){ const p = get(id); if (!p) return renderNotFound(); renderForm(p, 'Save Changes'); }

  function renderForm(state, cta){
    $app.innerHTML = '';
    const section = el('div', {class:'section'});
    section.appendChild(el('h2', {html: state.id ? 'Edit Project' : 'New Project'}));

    const form = el('form', {class:'form', id:'projForm'});
    form.innerHTML = `
      <div class="row">
        <div class="field">
          <label for="name">Project name</label>
          <input id="name" name="name" type="text" required placeholder="e.g., AI Roadmap" value="${escapeAttr(state.name)}" />
          <small class="helper" id="err-name"></small>
        </div>
        <div class="field">
          <label for="client">Client</label>
          <input id="client" name="client" type="text" placeholder="e.g., Acme Corp" value="${escapeAttr(state.client)}" />
        </div>
      </div>
      <div class="row">
        <div class="field">
          <label for="status">Status</label>
          <select id="status" name="status">
            ${['prospect','active','paused','closed'].map(s=>`<option value="${s}" ${state.status===s?'selected':''}>${cap(s)}</option>`).join('')}
          </select>
        </div>
        <div class="field">
          <label for="budget">Budget (USD)</label>
          <input id="budget" name="budget" type="number" min="0" step="1000" placeholder="50000" value="${escapeAttr(state.budget)}" />
        </div>
      </div>
      <div class="row">
        <div class="field">
          <label for="startDate">Start date</label>
          <input id="startDate" name="startDate" type="date" value="${escapeAttr(state.startDate)}" />
        </div>
        <div class="field">
          <label for="endDate">End date</label>
          <input id="endDate" name="endDate" type="date" value="${escapeAttr(state.endDate)}" />
        </div>
      </div>
      <div class="field">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="6" placeholder="Project goals, scope, and deliverables">${escapeHtml(state.description||'')}</textarea>
      </div>
      <div class="actions">
        <button type="submit" class="btn btn-primary">${cta}</button>
        <a href="#/projects" class="btn btn-ghost">Cancel</a>
      </div>
    `;

    form.addEventListener('submit', (e)=>{
      e.preventDefault();
      const data = formToObj(new FormData(form));
      // Validation
      let ok = true;
      const nameErr = byId('err-name');
      nameErr.textContent = '';
      if (!data.name || String(data.name).trim().length < 3){
        nameErr.textContent = 'Name must be at least 3 characters.'; ok = false;
      }
      if (!ok) return;
      // Normalize
      const item = {
        id: state.id || uid(),
        name: String(data.name).trim(),
        client: String(data.client||'').trim(),
        status: String(data.status||'prospect'),
        budget: data.budget !== '' ? Number(data.budget) : '',
        startDate: data.startDate || '',
        endDate: data.endDate || '',
        description: String(data.description||'').trim(),
        createdAt: state.createdAt || Date.now(),
      };
      upsert(item);
      location.hash = `#/project/${item.id}`;
    });

    section.appendChild(form);
    $app.appendChild(section);
  }

  // Helpers
  function cardMetric(title, value){
    const c = el('div', {class:'card'});
    c.appendChild(el('div', {class:'helper', html:title}));
    c.appendChild(el('div', {class:'metric', html:value}));
    return c;
  }
  function linkBtn(href, text, cls){ const a = el('a', {href, class: cls||'btn', html: escapeHtml(text)}); return a; }
  function btn(text, cls, onClick){ const b = el('button', {type:'button', class: cls||'btn', html: escapeHtml(text)}); b.addEventListener('click', onClick); return b; }
  function tdLink(text, href){ const td = el('td'); const a = el('a', {href, html: escapeHtml(text)}); a.className=''; td.appendChild(a); return td; }
  function badge(status){ const cls = `badge ${status}`; return `<span class="${cls}">${cap(status||'—')}</span>`; }
  function cap(s){ return (s||'').charAt(0).toUpperCase() + (s||'').slice(1); }
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c])); }
  function escapeAttr(s){ return escapeHtml(s).replace(/"/g, '&quot;'); }
  function formToObj(fd){ return Object.fromEntries(fd.entries()); }

})();
