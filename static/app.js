// ── Constants ──────────────────────────────────────────────────────────────

const SPORT_COLORS = {
  Run:          '#fc4c02',
  Ride:         '#4fc3f7',
  Hike:         '#81c784',
  Walk:         '#aed581',
  VirtualRide:  '#4fc3f7',
  VirtualRun:   '#fc4c02',
};

function colorFor(sportType) {
  return SPORT_COLORS[sportType] ?? '#ce93d8';
}

// ── State ──────────────────────────────────────────────────────────────────

let map = null;
let allRoutes = [];
let renderedPolylines = [];
let activeSports = new Set();
let mapFitted = false;

// ── Init ───────────────────────────────────────────────────────────────────

async function init() {
  const res = await fetch('/api/status');
  const { authenticated } = await res.json();

  if (!authenticated) {
    document.getElementById('connect-screen').classList.remove('hidden');
    document.getElementById('btn-sync').classList.add('hidden');
    return;
  }

  document.getElementById('app').classList.remove('hidden');
  initMap();
  await Promise.all([loadRoutes(), loadStats()]);
  bindFilters();
}

function initMap() {
  map = L.map('map', { zoomControl: true, preferCanvas: true }).setView([39.5, -98.35], 4);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);
}

// ── Routes ─────────────────────────────────────────────────────────────────

async function loadRoutes() {
  const params = buildFilterParams();
  const res = await fetch(`/api/routes?${params}`);
  allRoutes = await res.json();

  // Collect all sport types present
  activeSports = new Set(allRoutes.map(r => r.sport_type));

  renderRoutes(allRoutes);
}

function buildFilterParams() {
  const p = new URLSearchParams();
  const after  = document.getElementById('date-after')?.value;
  const before = document.getElementById('date-before')?.value;
  if (after)  p.append('after', after + 'T00:00:00Z');
  if (before) p.append('before', before + 'T23:59:59Z');
  // Sport types checked in sidebar
  document.querySelectorAll('.sport-checkbox:checked').forEach(cb => {
    p.append('sport_types', cb.value);
  });
  return p.toString();
}

function renderRoutes(routes) {
  // Clear existing polylines
  renderedPolylines.forEach(p => p.remove());
  renderedPolylines = [];

  const tooltip  = document.getElementById('tooltip');

  routes.forEach(route => {
    if (route.coords.length < 2) return;

    const poly = L.polyline(route.coords, {
      color:   colorFor(route.sport_type),
      weight:  2,
      opacity: 0.35,
      smoothFactor: 1,
    }).addTo(map);

    poly.on('mouseover', (e) => {
      poly.setStyle({ opacity: 0.9, weight: 3 });
      showTooltip(e.originalEvent, route);
    });

    poly.on('mousemove', (e) => {
      positionTooltip(e.originalEvent);
    });

    poly.on('mouseout', () => {
      poly.setStyle({ opacity: 0.35, weight: 2 });
      tooltip.classList.add('hidden');
    });

    renderedPolylines.push(poly);
  });

  // Fit map to routes only on first load
  if (!mapFitted && renderedPolylines.length > 0) {
    const group = L.featureGroup(renderedPolylines);
    map.fitBounds(group.getBounds().pad(0.05));
    mapFitted = true;
  }
}

// ── Tooltip ────────────────────────────────────────────────────────────────

function showTooltip(event, route) {
  const tooltip = document.getElementById('tooltip');
  const date = new Date(route.start_date).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  });
  const km = (route.distance_m / 1000).toFixed(1);
  const mins = Math.floor(route.moving_time_s / 60);
  const secs = String(route.moving_time_s % 60).padStart(2, '0');

  tooltip.innerHTML = `
    <div class="tt-title">${escHtml(route.name)}</div>
    <div class="tt-meta">
      ${escHtml(route.sport_type)} &middot; ${date}<br>
      ${km} km &middot; ${mins}:${secs}
    </div>
  `;
  tooltip.classList.remove('hidden');
  positionTooltip(event);
}

function positionTooltip(event) {
  const t  = document.getElementById('tooltip');
  const tw = t.offsetWidth;
  const th = t.offsetHeight;
  let x = event.clientX + 16;
  let y = event.clientY + 16;
  if (x + tw > window.innerWidth  - 8) x = event.clientX - tw - 8;
  if (y + th > window.innerHeight - 8) y = event.clientY - th - 8;
  t.style.left = x + 'px';
  t.style.top  = y + 'px';
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
  const res = await fetch('/api/stats');
  const stats = await res.json();
  renderStats(stats);
  renderSportFilters(stats.by_sport);
}

function renderStats(stats) {
  const km = (stats.total_distance_m / 1000).toLocaleString('en-US', { maximumFractionDigits: 0 });
  let html = `<div>Activities: <strong>${stats.total_count.toLocaleString()}</strong></div>`;
  html    += `<div>Total dist: <strong>${km} km</strong></div>`;
  html    += `<div style="margin-top:8px">`;
  Object.entries(stats.by_sport).sort((a,b) => b[1]-a[1]).forEach(([sport, count]) => {
    html += `<div><span style="color:${colorFor(sport)}">${sport}</span>: <strong>${count}</strong></div>`;
  });
  html += `</div>`;
  document.getElementById('stats').innerHTML = html;
}

function renderSportFilters(bySport) {
  const container = document.getElementById('sport-filters');
  container.innerHTML = '';

  Object.entries(bySport).sort((a,b) => b[1]-a[1]).forEach(([sport, count]) => {
    const row = document.createElement('label');
    row.className = 'sport-row';
    row.innerHTML = `
      <input type="checkbox" class="sport-checkbox" value="${escHtml(sport)}" checked />
      <span class="sport-dot" style="background:${colorFor(sport)}"></span>
      <span class="sport-label">${escHtml(sport)}</span>
      <span class="sport-count">${count}</span>
    `;
    container.appendChild(row);
  });
}

// ── Filters ────────────────────────────────────────────────────────────────

function bindFilters() {
  // Sport checkboxes — re-render without re-fetching
  document.getElementById('sport-filters').addEventListener('change', applyLocalFilters);

  // Date inputs — re-fetch from server (date filter happens server-side)
  document.getElementById('date-after').addEventListener('change', loadRoutes);
  document.getElementById('date-before').addEventListener('change', loadRoutes);
}

function applyLocalFilters() {
  const checked = new Set(
    [...document.querySelectorAll('.sport-checkbox:checked')].map(cb => cb.value)
  );
  const visible = allRoutes.filter(r => checked.has(r.sport_type));
  renderRoutes(visible);
}

// ── Sync ───────────────────────────────────────────────────────────────────

async function triggerSync() {
  const btn    = document.getElementById('btn-sync');
  const status = document.getElementById('sync-status');

  btn.disabled = true;
  status.textContent = 'Syncing…';

  try {
    const res  = await fetch('/api/sync', { method: 'POST' });
    const data = await res.json();
    status.textContent = `Synced ${data.synced} activities`;
    await Promise.all([loadRoutes(), loadStats()]);
    setTimeout(() => { status.textContent = ''; }, 4000);
  } catch (err) {
    status.textContent = 'Sync failed';
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

// ── Start ──────────────────────────────────────────────────────────────────

init();
