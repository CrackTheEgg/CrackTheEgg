const $ = (id) => document.getElementById(id);
const fmtNumber = (value, digits = 0) => value == null ? '—' : Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
const fmtMoney = (value, currency = 'USD') => value == null ? '—' : new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 2 }).format(value);
const fmtPercent = (value) => value == null ? '—' : `${fmtNumber(value, 2)}%`;
const fmtTransfer = (bytes) => bytes == null ? '—' : bytes >= 1024 ** 3 ? `${fmtNumber(bytes / 1024 ** 3, 2)} GB` : `${fmtNumber(bytes / 1024 ** 2, 1)} MB`;
const setText = (id, value) => { $(id).textContent = value; };
const staticPreview = window.location.protocol === 'file:';

async function getJSON(path) {
  const response = await fetch(path, { cache: 'no-store' });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function renderTraffic(data) {
  const traffic = data.traffic || {};
  setText('visits-value', fmtNumber(traffic.visits));
  setText('pageviews-value', fmtNumber(traffic.pageViews));
  setText('requests-value', fmtNumber(traffic.requests));
  setText('transfer-value', fmtTransfer(traffic.bytesDownloaded));
  const analyticsReady = traffic.visits != null || traffic.pageViews != null;
  setText('traffic-status', analyticsReady ? 'Analytics connected' : 'Awaiting analytics');
  const updated = traffic.checkedAt ? new Date(traffic.checkedAt).toLocaleString() : null;
  setText('traffic-updated', updated ? `Traffic checked ${updated}. Visits are sessions; CloudFront requests include assets and prefetches.` : 'Visits and page views appear after project analytics is connected. CloudFront delivery metrics appear when configured.');
}

function renderHealth(data) {
  const health = data.health || {};
  setText('availability-value', fmtPercent(health.availabilityPercent));
  setText('error5xx-value', fmtPercent(health.error5xxPercent));
  setText('error4xx-value', fmtPercent(health.error4xxPercent));
  const available = ['availabilityPercent', 'error5xxPercent', 'error4xxPercent'].some(key => health[key] != null);
  setText('health-status', available ? 'AWS readings' : 'Awaiting checks');
  const updated = health.checkedAt ? new Date(health.checkedAt).toLocaleString() : null;
  setText('health-updated', updated
    ? `Last 24 hours · Checked ${updated}. Availability is the share of successful scheduled checks.`
    : 'Availability needs a scheduled check; error rates need a connected CloudFront distribution.');
}

function renderForecast(data) {
  setText('forecast-amount', fmtMoney(data.monthForecast, data.forecastCurrency || data.currency));
  setText('forecast-note', data.monthForecast == null
    ? 'AWS forecast unavailable for this project.'
    : 'Estimated full-month cost from AWS Cost Explorer. Actual charges may differ.');
  const updated = data.forecastCheckedAt ? new Date(data.forecastCheckedAt).toLocaleString() : null;
  setText('forecast-updated', updated ? `Forecast checked ${updated}` : 'No forecast yet');
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
    td.colSpan = 5; td.className = 'empty-state'; td.textContent = 'No resource inventory is available yet.';
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
  const allocation = data.costAllocation || {};
  setText('project-deploy-status', data.deploymentStatus === 'not deployed' ? 'App not deployed' : 'Live project');
  setText('direct-cost', fmtMoney(allocation.directAwsCost, data.currency));
  setText('dns-cost', fmtMoney(allocation.allocatedDnsCost, data.currency));
  setText('combined-cost', fmtMoney(allocation.combinedOperatingCost, data.currency));
  const costDate = data.costCheckedAt ? new Date(data.costCheckedAt).toLocaleString() : 'unavailable';
  setText('allocation-updated', `Direct AWS cost checked ${costDate}. ${allocation.allocationMethod || 'No DNS allocation configured'}.${allocation.combinedOperatingCost == null ? ' Combined cost remains unavailable until direct cost is confirmed.' : ' Combined cost includes the DNS allocation once.'}`);
  setText('cost-amount', fmtMoney(data.monthCost, data.currency));
  setText('cost-badge', data.monthCost == null ? 'COST UNAVAILABLE' : 'AWS COST DATA');
  renderTraffic(data);
  renderHealth(data);
  renderForecast(data);
  drawChart(data.dailyCost || []);
  renderServices(data); renderResources(data);
  const notice = $('project-notice');
  if (data.warnings?.length) { notice.hidden = false; notice.querySelector('span:last-child').textContent = data.warnings.join(' '); }
  else { notice.hidden = true; }
  const checked = data.checkedAt ? new Date(data.checkedAt).toLocaleString() : 'unknown';
  const costChecked = data.costCheckedAt ? new Date(data.costCheckedAt).toLocaleString() : 'unavailable';
  setText('sync-text', `AWS snapshot ${checked} · Cost checked ${costChecked}`);
}

function renderAccount(account = {}) {
  const currency = account.currency || 'USD';
  setText('account-status', account.checkedAt ? 'Cost Explorer reading' : 'Awaiting Cost Explorer');
  const operating = [account.total, account.domainRegistrationCost, account.tax].every(value => value != null)
    ? Math.round((account.total - account.domainRegistrationCost - account.tax) * 100) / 100 : null;
  const projectOperating = account.directProjectCost != null && account.allocatedDnsCost != null
    ? Math.round((account.directProjectCost + account.allocatedDnsCost) * 100) / 100 : null;
  setText('hero-operating', fmtMoney(operating, currency));
  setText('operating-total', fmtMoney(operating, currency));
  setText('project-operating', fmtMoney(projectOperating, currency));
  setText('project-operating-note', account.directProjectPartial
    ? 'Confirmed direct charges plus DNS; other project costs may still be missing'
    : 'Direct AWS charges plus allocated hosted-zone DNS');
  setText('account-total', fmtMoney(account.total, currency));
  setText('account-direct', fmtMoney(account.directProjectCost, currency));
  setText('account-direct-note', account.directProjectPartial ? 'Partial: some projects have no tagged cost data yet' : 'All configured projects included');
  setText('account-dns', fmtMoney(account.allocatedDnsCost, currency));
  setText('account-shared', fmtMoney(account.sharedUnallocatedCost, currency));
  setText('account-shared-note', account.sharedIncludesUnattributedProjects ? 'Includes charges awaiting project attribution' : 'Remaining shared or unallocated charges');
  setText('account-domain', fmtMoney(account.domainRegistrationCost, currency));
  setText('account-tax', fmtMoney(account.tax, currency));
  const checked = account.checkedAt ? `AWS costs checked ${new Date(account.checkedAt).toLocaleString()}. ` : 'AWS account costs unavailable. ';
  const difference = account.dnsDiscrepancy;
  const dnsNote = difference == null ? 'Hosted-zone reconciliation awaits Cost Explorer.'
    : Math.abs(difference) < 0.005 ? 'Hosted-zone charges reconcile with the manual allocations.'
    : `Hosted-zone difference (actual minus allocated): ${fmtMoney(difference, currency)}. Review the charge; DNS queries are excluded from this comparison.`;
  setText('account-reconciliation', `${checked}${dnsNote} Allocations redistribute the AWS total and are not added to it. ${account.warning || ''}`);
}

function renderOverviewProjects(projects) {
  const parent = $('project-cards');
  parent.replaceChildren();
  for (const project of projects) {
    const allocation = project.costAllocation || {};
    const card = document.createElement('a');
    card.className = 'project-card';
    card.href = `#project/${encodeURIComponent(project.id)}`;
    card.setAttribute('aria-label', `Open ${project.name} details`);
    const top = document.createElement('div'); top.className = 'project-card-top';
    const label = document.createElement('span'); label.className = 'overline'; label.textContent = 'AWS PROJECT';
    const status = document.createElement('span'); status.className = 'status-pill';
    status.textContent = project.deploymentStatus === 'not deployed' ? 'DNS only' : 'Live app';
    top.append(label, status);
    const title = document.createElement('h3'); title.textContent = project.name;
    const cost = document.createElement('div'); cost.className = 'project-cost';
    cost.textContent = fmtMoney(allocation.combinedOperatingCost ?? allocation.allocatedDnsCost, project.currency);
    const meta = document.createElement('p'); meta.className = 'project-meta';
    meta.textContent = allocation.combinedOperatingCost != null ? 'Confirmed operating cost this month'
      : allocation.allocatedDnsCost != null ? 'Allocated DNS only · direct AWS cost unavailable' : 'Operating cost unavailable';
    const traffic = document.createElement('p'); traffic.className = 'project-meta';
    traffic.textContent = project.traffic?.requests == null ? 'Traffic unavailable' : `${fmtNumber(project.traffic.requests)} CloudFront requests this month`;
    const open = document.createElement('span'); open.className = 'project-open'; open.textContent = 'Open project details ↗';
    card.append(top, title, cost, meta, traffic, open);
    parent.append(card);
  }
}

function renderOverviewTraffic(projects) {
  const live = projects.filter(project => project.deploymentStatus !== 'not deployed');
  const sumIfComplete = key => live.length && live.every(project => project.traffic?.[key] != null)
    ? live.reduce((sum, project) => sum + Number(project.traffic[key]), 0) : null;
  setText('overview-visits', fmtNumber(sumIfComplete('visits')));
  setText('overview-pageviews', fmtNumber(sumIfComplete('pageViews')));
  setText('overview-requests', fmtNumber(sumIfComplete('requests')));
  setText('overview-transfer', fmtTransfer(sumIfComplete('bytesDownloaded')));
  setText('overview-traffic-note', live.length
    ? `Across ${live.length} live project${live.length === 1 ? '' : 's'}. Missing project readings stay unavailable; CloudFront requests are not visits. Projects sharing one distribution may overlap.`
    : 'No live project traffic is available yet.');
}

function showDashboardRoute(projects, scroll = false) {
  let route = '';
  try { route = decodeURIComponent(location.hash.slice(1)); } catch { route = ''; }
  const match = /^project\/([a-z0-9-]+)$/.exec(route);
  const legacyDetail = route === 'traffic' || route === 'reliability';
  const selected = projects.find(project => project.id === (match?.[1] || (legacyDetail ? projects[0]?.id : null)));
  const detail = Boolean(selected);
  $('overview-view').hidden = detail;
  $('detail-view').hidden = !detail;
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => item.classList.toggle('active', detail ? item.hash === '#projects' : item.hash === (route === 'projects' ? '#projects' : '#overview')));
  if (selected) {
    setText('breadcrumb-current', selected.name);
    setText('detail-title', selected.name);
    const select = $('project-select');
    select.value = selected.id;
    select.disabled = false;
    renderProject(selected);
    const projectLink = $('project-link');
    projectLink.hidden = !selected.url;
    if (selected.url) { projectLink.href = selected.url; projectLink.textContent = `Visit ${selected.name} ↗`; }
    else projectLink.removeAttribute('href');
  } else {
    setText('breadcrumb-current', 'Overview');
  }
  if (scroll) {
    if (legacyDetail) $(route).scrollIntoView();
    else if (!detail && route === 'projects') $('projects').scrollIntoView();
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}


// The public site reads only an allowlisted AWS snapshot.
let publicProjects = [];
let lastSnapshotAt = null;

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
    renderAccount(snapshot.accountCost || {});
    renderOverviewProjects(publicProjects);
    renderOverviewTraffic(publicProjects);
    const select = $('project-select');
    select.replaceChildren(...publicProjects.map(project => new Option(project.name, project.id)));
    select.disabled = false;
    showDashboardRoute(publicProjects);
    const age = Date.now() - Date.parse(snapshot.generatedAt);
    const notice = $('feed-notice');
    if (!Number.isFinite(age) || age > 15 * 60 * 1000) {
      notice.hidden = false;
      notice.querySelector('span:last-child').textContent = `Last AWS snapshot: ${new Date(snapshot.generatedAt).toLocaleString()}.`;
    } else notice.hidden = true;
  } catch (error) {
    const notice = $('feed-notice');
    notice.hidden = false;
    notice.querySelector('span:last-child').textContent = lastSnapshotAt
      ? `AWS snapshot temporarily unavailable. Showing the last update from ${new Date(lastSnapshotAt).toLocaleString()}.`
      : 'AWS feed is being connected. Account and project metrics are unavailable.';
  }
}

function setClock() { setText('clock', new Date().toLocaleString(undefined, { weekday: 'short', hour: '2-digit', minute: '2-digit' })); }
setClock();
$('refresh').addEventListener('click', loadPublicSnapshot);
$('project-select').addEventListener('change', event => {
  location.hash = `project/${event.target.value}`;
});
window.addEventListener('hashchange', () => showDashboardRoute(publicProjects, true));
loadPublicSnapshot();
setInterval(loadPublicSnapshot, 60000);
setInterval(setClock, 30000);
