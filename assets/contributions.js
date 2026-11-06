// The browser requests public profile data on each page visit. The upstream API
// caches responses for up to one hour; the static daily snapshot remains fallback.
(async () => {
  const container = document.querySelector('.calendar-scroll');
  const status = document.getElementById('calendar-status');
  if (!container || !status) return;
  const snapshot = status.dataset.snapshot;
  status.textContent = `更新を確認中 · 保存データ：${snapshot}取得（UTC）`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch('https://github-contributions-api.jogruber.de/v4/mani1261790?y=last', {
      signal: controller.signal,
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      cache: 'no-store'
    });
    if (!response.ok) throw new Error('Calendar request failed');
    const data = await response.json();
    const rows = data.contributions;
    const total = data.total?.lastYear;
    if (!Array.isArray(rows) || rows.length < 350 || rows.length > 371 ||
        !Number.isSafeInteger(total) || total < 0) throw new Error('Invalid calendar');
    rows.sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const dayMS = 86400000;
    let previous;
    for (const row of rows) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(row.date) ||
          !Number.isSafeInteger(row.count) || row.count < 0 ||
          !Number.isInteger(row.level) || row.level < 0 || row.level > 4) throw new Error('Invalid day');
      const time = Date.parse(`${row.date}T00:00:00Z`);
      if (!Number.isFinite(time) || new Date(time).toISOString().slice(0, 10) !== row.date ||
          (previous !== undefined && time - previous !== dayMS)) throw new Error('Incomplete calendar');
      previous = time;
    }
    if (rows.reduce((sum, row) => sum + row.count, 0) !== total) throw new Error('Total mismatch');
    const first = new Date(`${rows[0].date}T00:00:00Z`);
    const last = new Date(`${rows.at(-1).date}T00:00:00Z`);
    // Never replace a snapshot with a stale or future calendar response.
    const today = Math.floor(Date.now() / dayMS) * dayMS;
    if (last.getTime() < today - 2 * dayMS || last.getTime() > today + dayMS) throw new Error('Stale calendar');
    const colors = ['rgba(215,235,245,0.07)', 'rgba(153,205,226,0.22)', 'rgba(153,205,226,0.42)', 'rgba(165,220,240,0.66)', 'rgba(195,235,250,0.92)'];
    const ns = 'http://www.w3.org/2000/svg';
    const node = (tag, attrs, text) => {
      const el = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, String(value)));
      if (text !== undefined) el.textContent = text;
      return el;
    };
    const svg = node('svg', {viewBox: '0 0 970 204', role: 'img', 'aria-labelledby': 'calendar-title calendar-desc'});
    svg.append(node('title', {id: 'calendar-title'}, 'GitHubの活動カレンダー'));
    svg.append(node('desc', {id: 'calendar-desc'}, `${rows[0].date}から${rows.at(-1).date}まで。左から右へ時間が進み、1列が1週間です。水色がはっきり見える日ほど活動量が多くなります。`));
    const text = (x, y, value, size = 12) => node('text', {x, y, fill: '#d0d5df', 'font-size': size}, value);
    const square = (x, y, level) => node('rect', {x, y, width: 12, height: 12, rx: 3, fill: colors[level], stroke: 'rgba(220,240,250,0.12)', 'stroke-width': 0.6});
    for (const [label, y] of [['月', 75], ['水', 107], ['金', 139]]) svg.append(text(0, y, label));
    rows.forEach((row, offset) => {
      const day = new Date(`${row.date}T00:00:00Z`);
      const week = Math.floor((offset + first.getUTCDay()) / 7);
      const x = 30 + week * 17;
      if (day.getUTCDate() === 1 || (offset === 0 && day.getUTCDate() <= 7)) {
        svg.append(text(x, 14, `${day.getUTCFullYear()}年`, 11));
        svg.append(text(x, 31, `${day.getUTCMonth() + 1}月`));
      }
      const rect = square(x, 46 + day.getUTCDay() * 16, row.level);
      rect.append(node('title', {}, `${row.date}：${row.count} contributions`));
      svg.append(rect);
    });
    svg.append(text(742, 190, '少'));
    colors.forEach((_, i) => svg.append(square(766 + i * 19, 179, i)));
    svg.append(text(868, 190, '多'));
    container.replaceChildren(svg);
    document.getElementById('contribution-count').textContent = total.toLocaleString('ja-JP');
    const dateLabel = day => `${day.getUTCFullYear()}年${day.getUTCMonth() + 1}月${day.getUTCDate()}日`;
    document.getElementById('calendar-period').textContent = `${dateLabel(first)} 〜 ${dateLabel(last)} · 左から右へ、1列が1週間`;
    status.textContent = 'ページを開いたときに取得 · データの更新は最大1時間遅れる場合があります';
    status.dataset.state = 'live';
  } catch {
    status.textContent = `更新を取得できなかったため、${snapshot}取得の保存データを表示しています（UTC）`;
    status.dataset.state = 'fallback';
  } finally {
    clearTimeout(timeout);
  }
})();
