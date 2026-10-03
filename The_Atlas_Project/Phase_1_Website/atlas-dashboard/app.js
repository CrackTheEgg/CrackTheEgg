const $ = (id) => document.getElementById(id);
const fmtNumber = (value, digits = 0) => value == null ? '—' : Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
const fmtBytes = (value) => value == null ? '—' : `${fmtNumber(value / 1024 ** 3, 1)} GB`;
const fmtMemoryBytes = (value) => value == null ? '—' : value < 1024 ** 3 ? `${fmtNumber(value / 1024 ** 2, 0)} MB` : fmtBytes(value);
const fmtMoney = (value, currency = 'USD') => value == null ? '—' : new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 2 }).format(value);
const setText = (id, value) => { $(id).textContent = value; };
const setBar = (id, value) => { $(id).style.width = `${Math.max(0, Math.min(100, value || 0))}%`; };
let selectedProject = 'demo';
const staticPreview = !['http:', 'https:'].includes(window.location.protocol);
const publicDemo = window.ATLAS_PUBLIC_DEMO === true || new URLSearchParams(window.location.search).get('demo') === '1';


function renderProcesses(processes) {
  const parent = $('process-list'); parent.replaceChildren();
  if (!processes.length) {
    const p = document.createElement('p'); p.className = 'insight-description'; p.textContent = 'Process activity is unavailable.'; parent.append(p); return;
  }
  const max = Math.max(1, ...processes.map(item => item.cpuPercent));
  processes.forEach((item, index) => {
    const row = document.createElement('div'); row.className = 'process-row';
    const top = document.createElement('div'); top.className = 'process-row-top';
    const name = document.createElement('span'); name.textContent = item.name;
    const cpu = document.createElement('strong'); cpu.textContent = `${fmtNumber(item.cpuPercent, 1)}%`;
    const track = document.createElement('div'); track.className = 'process-track';
    const fill = document.createElement('div'); fill.className = `process-fill ${index === 0 ? 'first' : ''}`; fill.style.width = `${Math.min(100, item.cpuPercent / max * 100)}%`;
    top.append(name, cpu); track.append(fill); row.append(top, track); parent.append(row);
  });
}


function drawChart(raw) {
  const values = raw.map(item => typeof item === 'number' ? item : item.cost);
  if (!values.length) { $('chart-line').setAttribute('d', ''); $('chart-area').setAttribute('d', ''); return; }
  const max = Math.max(1, ...values);
  const points = values.map((value, i) => [values.length === 1 ? 260 : 8 + i * 504 / (values.length - 1), 114 - value / max * 96]);
  const line = points.map(([x, y], i) => `${i ? 'L' : 'M'} ${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  $('chart-line').setAttribute('d', line);
  $('chart-area').setAttribute('d', `${line} L ${points.at(-1)[0].toFixed(1)} 126 L ${points[0][0].toFixed(1)} 126 Z`);
}

function renderServices(data) {
  const parent = $('service-list');
  parent.replaceChildren();
  if (!data.services?.length) { const p = document.createElement('p'); p.className = 'empty-state'; p.textContent = 'No service cost data is available yet.'; parent.append(p); return; }
  const max = Math.max(...data.services.map(item => item.cost), 1);
  data.services.slice(0, 5).forEach(item => {
    const row = document.createElement('div'); row.className = 'service-row';
    const top = document.createElement('div'); top.className = 'service-row-top';
    const name = document.createElement('strong'); name.textContent = item.name;
    const cost = document.createElement('span'); cost.textContent = fmtMoney(item.cost, data.currency);
    const track = document.createElement('div'); track.className = 'service-track';
    const fill = document.createElement('div'); fill.className = 'service-fill'; fill.style.width = `${Math.max(0, Math.min(100, item.cost / max * 100))}%`;
    top.append(name, cost); track.append(fill); row.append(top, track); parent.append(row);
  });
}

function renderResources(data) {
  const parent = $('resource-body'); parent.replaceChildren();
  const resources = data.resources || [];
  setText('resource-count', fmtNumber(resources.length));
  if (!resources.length) {
    const tr = document.createElement('tr'); const td = document.createElement('td');
    td.colSpan = 5; td.className = 'empty-state'; td.textContent = 'No tagged resources found in the configured regions.';
    tr.append(td); parent.append(tr); return;
  }
  resources.forEach(item => {
    const tr = document.createElement('tr');
    const name = document.createElement('td');
    const title = document.createElement('span'); title.className = 'resource-name'; title.textContent = item.name;
    const detail = document.createElement('span'); detail.className = 'resource-detail'; detail.textContent = item.detail || '';
    name.append(title, detail);
    const type = document.createElement('td'); type.textContent = item.type;
    const region = document.createElement('td'); region.textContent = item.region;
    const stateCell = document.createElement('td'); const state = document.createElement('span');
    state.className = `state ${['running', 'available', 'active'].includes(item.status) ? '' : 'neutral'}`; state.textContent = item.status || 'tagged'; stateCell.append(state);
    const cpu = document.createElement('td'); cpu.className = 'cpu-cell'; cpu.textContent = item.cpu == null ? '—' : `${fmtNumber(item.cpu, 1)}%`;
    tr.append(name, type, region, stateCell, cpu); parent.append(tr);
  });
}

function renderProject(data) {
  setText('cost-amount', fmtMoney(data.monthCost, data.currency));
  setText('cost-badge', data.source === 'demo' ? 'SAMPLE DATA' : 'AWS DATA');
  drawChart(data.dailyCost || []);
  renderServices(data); renderResources(data);
  const notice = $('project-notice');
  if (data.source === 'demo') { notice.hidden = false; notice.querySelector('span:last-child').textContent = data.note; }
  else if (data.warnings?.length) { notice.hidden = false; notice.querySelector('span:last-child').textContent = data.warnings.join(' '); }
  else { notice.hidden = true; }
  const checked = data.checkedAt ? new Date(data.checkedAt).toLocaleString() : 'unknown';
  setText('sync-text', `${data.source === 'demo' ? 'Sample' : 'AWS'} · Updated ${checked}`);
}


function setClock() { setText('clock', new Date().toLocaleString(undefined, { weekday: 'short', hour: '2-digit', minute: '2-digit' })); }
setClock();
{
  $('file-preview').hidden = false;
  if (publicDemo) $('file-preview').querySelector('span:last-child').textContent = 'Portfolio demo · All computer, network, and AWS readings below are illustrative sample data.';
  setText('machine-meta', 'Sample Mac Studio · Apple Silicon · 20 logical cores');
  setText('machine-status', 'Sample data');
  setText('load-value', '2.15'); setText('load-5', '2.31'); setText('core-count', '20'); setText('load-percent', '11%'); setBar('load-bar', 11);
  setText('memory-value', '32.4 GB'); setText('memory-total', '128.0 GB'); setText('memory-percent', '25.3%'); setBar('memory-bar', 25.3);
  setText('disk-value', '1,300.0 GB'); setText('disk-total', '2,000.0 GB'); setText('disk-free', '700.0 GB free'); setBar('disk-bar', 65);
  setText('uptime-value', '2d 6h'); setText('chip', 'Apple Silicon');
  setText('cpu-value', '9.8%'); setText('cpu-user', 'User 6.4%'); setText('cpu-system', 'System 3.4%'); setBar('cpu-bar', 9.8);
  setText('thermal-value', 'Nominal'); setText('pressure-state', 'Normal'); $('pressure-state').dataset.state = 'normal';
  setText('swap-used', '0 MB'); setText('compressed-memory', '1.2 GB');
  setText('disk-throughput', '3.40'); setText('disk-ops', '88 / sec'); setText('disk-device', 'internal SSD');
  renderProcesses([{ name: 'Design Studio', cpuPercent: 18.2 }, { name: 'Browser Renderer', cpuPercent: 11.4 }, { name: 'Window Manager', cpuPercent: 7.1 }, { name: 'Sync Service', cpuPercent: 3.5 }, { name: 'Music Player', cpuPercent: 1.2 }]);
  setText('network-status', 'Sample data'); setText('internet-status', 'Connected'); setText('latency-value', '19 ms');
  setText('download-rate', '4.80 Mbps'); setText('upload-rate', '0.70 Mbps'); setText('network-interface', 'sample interface'); setText('probe-target', 'illustrative check');
  setText('wifi-name', 'Studio Wi-Fi (sample)'); setText('wifi-signal', '-58 dBm'); setText('wifi-channel', '44 (5 GHz)'); setText('wifi-link', '866 Mbps'); setText('wifi-noise', '-91 dBm / 33 dB'); setText('wifi-mode', '802.11ax');
  $('project-select').disabled = true;
  $('refresh').disabled = true;
  renderProject({
    source: 'demo', name: 'Sample project', monthCost: 13.9, currency: 'USD',
    dailyCost: [7.8, 6.1],
    services: [{ name: 'Amazon EC2', cost: 7.78 }, { name: 'Amazon RDS', cost: 4.03 }, { name: 'Amazon S3', cost: 2.09 }],
    resources: [
      { name: 'api-server', type: 'EC2 instance', region: 'eu-west-2', status: 'running', cpu: 28.4, detail: 't3.medium' },
      { name: 'app-database', type: 'RDS database', region: 'eu-west-2', status: 'available', cpu: null, detail: 'db.t4g.medium' },
      { name: 'media-bucket', type: 'S3 bucket', region: 'eu-west-2', status: 'active', cpu: null, detail: 'storage' },
    ],
    checkedAt: new Date().toISOString(), note: 'Illustrative AWS project data for the portfolio demo.'
  });

}


// The portfolio host periodically replaces this file with an allowlisted AWS
// snapshot. The browser never receives AWS credentials or Mac telemetry.
let publicProjects = [];
let selectedPublicProject = null;
let lastSnapshotAt = null;
const projectLink = $('project-link');

function displayPublicProject() {
  const project = publicProjects.find(item => item.id === selectedPublicProject);
  if (!project) return;
  renderProject(project);
  projectLink.hidden = !project.url;
  if (project.url) projectLink.href = project.url;
  else projectLink.removeAttribute('href');
}

async function loadPublicSnapshot() {
  try {
    const response = await fetch('./data/latest.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Snapshot unavailable');
    const snapshot = await response.json();
    if (snapshot.schemaVersion !== 1 || !Array.isArray(snapshot.projects) || !snapshot.projects.length)
      throw new Error('No public projects configured');
    publicProjects = snapshot.projects.filter(item => item && item.source === 'aws' && typeof item.id === 'string');
    if (!publicProjects.length) throw new Error('No public projects configured');
    lastSnapshotAt = snapshot.generatedAt;
    const select = $('project-select');
    select.replaceChildren(...publicProjects.map(project => new Option(project.name, project.id)));
    if (!publicProjects.some(project => project.id === selectedPublicProject)) selectedPublicProject = publicProjects[0].id;
    select.value = selectedPublicProject;
    select.disabled = false;
    displayPublicProject();
    const age = Date.now() - Date.parse(snapshot.generatedAt);
    if (!Number.isFinite(age) || age > 15 * 60 * 1000) {
      setText('cost-badge', 'OLDER SNAPSHOT');
      const notice = $('project-notice');
      notice.hidden = false;
      notice.querySelector('span:last-child').textContent = `Last AWS snapshot: ${new Date(snapshot.generatedAt).toLocaleString()}.`;
    }
  } catch (error) {
    const notice = $('project-notice');
    notice.hidden = false;
    notice.querySelector('span:last-child').textContent = lastSnapshotAt
      ? `AWS snapshot temporarily unavailable. Showing the last update from ${new Date(lastSnapshotAt).toLocaleString()}.`
      : 'AWS feed is being connected. Project figures shown here are illustrative sample data.';
    if (lastSnapshotAt) setText('cost-badge', 'LAST SNAPSHOT');
  }
}

$('refresh').disabled = false;
$('refresh').addEventListener('click', loadPublicSnapshot);
$('project-select').addEventListener('change', event => {
  selectedPublicProject = event.target.value;
  displayPublicProject();
});
loadPublicSnapshot();
setInterval(loadPublicSnapshot, 60000);
