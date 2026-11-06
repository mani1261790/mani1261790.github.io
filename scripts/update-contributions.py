"""Refresh the calendar from GitHub's public profile, without credentials."""
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.tips = {}
        self.tip = None
        self.heading = False
        self.total = ''
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date') and 'data-level' in attrs:
            self.days[attrs['id']] = (date.fromisoformat(attrs['data-date']), int(attrs['data-level']))
        if tag == 'tool-tip':
            self.tip = attrs.get('for')
        if tag == 'h2' and attrs.get('id') == 'js-contribution-activity-description':
            self.heading = True
    def handle_data(self, text):
        if self.tip:
            self.tips[self.tip] = self.tips.get(self.tip, '') + text
        if self.heading:
            self.total += text
    def handle_endtag(self, tag):
        if tag == 'tool-tip': self.tip = None
        if tag == 'h2': self.heading = False

request = urllib.request.Request('https://github.com/users/mani1261790/contributions', headers={'User-Agent': 'mani-portfolio-calendar', 'Accept-Language': 'en'})
with urllib.request.urlopen(request, timeout=30) as response:
    html = response.read().decode()
calendar = Calendar()
calendar.feed(html)
match = re.search(r'([\d,]+)\s+contributions', calendar.total)
if not match or not 350 <= len(calendar.days) <= 371:
    raise ValueError('Unexpected GitHub calendar response; existing calendar left unchanged')
rows = []
for key, (day, level) in calendar.days.items():
    tip = calendar.tips.get(key, '')
    count = re.match(r'(No|[\d,]+) contributions? on ', tip)
    if not count or level not in range(5):
        raise ValueError('Unexpected day data; existing calendar left unchanged')
    rows.append((day, level, 0 if count[1] == 'No' else int(count[1].replace(',', ''))))
rows.sort()
if len({row[0] for row in rows}) != len(rows) or (rows[-1][0]-rows[0][0]).days != len(rows)-1:
    raise ValueError('Incomplete calendar')
start, end = rows[0][0], rows[-1][0]
colors = ['rgba(215,235,245,0.07)', 'rgba(153,205,226,0.22)', 'rgba(153,205,226,0.42)', 'rgba(165,220,240,0.66)', 'rgba(195,235,250,0.92)']
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 970 204" role="img" aria-labelledby="calendar-title calendar-desc">',
       '<title id="calendar-title">GitHubの活動カレンダー</title>',
       f'<desc id="calendar-desc">{start}から{end}まで。水色がはっきり見える日ほど活動量が多いカレンダーです。</desc>']
for label, y in [('月', 75), ('水', 107), ('金', 139)]:
    svg.append(f'<text x="0" y="{y}" fill="#d0d5df" font-size="12">{label}</text>')
last_month = None
for day, level, count in rows:
    offset = (day-start).days
    week, weekday = (offset + (start.weekday()+1)%7)//7, (day.weekday()+1)%7
    x, y = 30+week*17, 46+weekday*16
    if day.day == 1 or (offset == 0 and day.day <= 7):
        svg.append(f'<text x="{x}" y="14" fill="#d0d5df" font-size="11">{day.year}年</text>')
        svg.append(f'<text x="{x}" y="31" fill="#d0d5df" font-size="12">{day.month}月</text>')
    svg.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{colors[level]}" stroke="rgba(220,240,250,0.12)" stroke-width="0.6"><title>{day}：{count} contributions</title></rect>')
svg.append('<text x="742" y="190" fill="#d0d5df" font-size="12">少</text>')
for level, color in enumerate(colors):
    svg.append(f'<rect x="{766+level*19}" y="179" width="12" height="12" rx="3" fill="{color}" stroke="rgba(220,240,250,0.12)" stroke-width="0.6"/>')
svg.append('<text x="868" y="190" fill="#d0d5df" font-size="12">多</text></svg>')
updated = datetime.now(timezone.utc).strftime('%Y-%m-%d')
block = f'''    <section class="panel contributions" aria-labelledby="contributions-heading">
      <div class="section-heading">
        <div><h2 id="contributions-heading">GitHubでの活動</h2><p>過去1年間で <strong id="contribution-count">{match[1]}</strong> contributions</p></div>
        <a class="work-link" href="https://github.com/mani1261790" target="_blank" rel="noopener noreferrer">GitHubを見る <span aria-hidden="true">↗︎</span></a>
      </div>
      <div class="calendar-scroll" tabindex="0" role="region" aria-label="日ごとの活動量。狭い画面では横にスクロールできます。">{''.join(svg)}</div>
      <p class="calendar-note" id="calendar-period">{start.year}年{start.month}月{start.day}日 〜 {end.year}年{end.month}月{end.day}日 · 左から右へ、1列が1週間</p>
      <p class="calendar-note" id="calendar-status" aria-live="polite" data-snapshot="{updated}">保存データ：{updated}取得（UTC）</p>
    </section>'''
path = Path(__file__).resolve().parent.parent / 'index.html'
source = path.read_text()
before, rest = source.split('    <!-- contributions:start -->', 1)
_, after = rest.split('    <!-- contributions:end -->', 1)
path.write_text(before + '    <!-- contributions:start -->\n' + block + '\n    <!-- contributions:end -->' + after)
print(f'Updated {len(rows)} days, {match[1]} contributions; {start} – {end}')
