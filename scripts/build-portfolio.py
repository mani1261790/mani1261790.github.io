"""Render project cards and native detail dialogs as static HTML."""
import json
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parent.parent
catalog = json.loads((root / 'projects.json').read_text())
cards, dialogs, ids = [], [], set()
for project in catalog['projects']:
    if project['category'] not in catalog['categories']:
        raise ValueError(f"Unknown category: {project['category']}")
    key = project['id']
    if not key.replace('-', '').isalnum() or key in ids:
        raise ValueError(f'Invalid or duplicate project ID: {key}')
    ids.add(key)
    name, description, category = map(escape, (project['name'], project['description'], project['category']))
    links = []
    for link in project['links']:
        external = link['url'].startswith('https://')
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
        arrow = '↗︎' if external else '→'
        links.append(f'<a class="work-link" href="{escape(link["url"], quote=True)}"{attrs}>{escape(link["label"])} <span aria-hidden="true">{arrow}</span></a>')
    cards.append(f'''        <article class="work-card">
          <h3>{name}</h3>
          <p>{description}</p>
          <div class="tags" aria-label="用途"><span class="tag">{category}</span></div>
          <button class="work-open" type="button" data-project="{key}" aria-haspopup="dialog" aria-controls="project-{key}" aria-label="{name}の詳しい紹介を見る" hidden>詳しく見る <span aria-hidden="true">＋</span></button>
          <noscript>{' '.join(links)}</noscript>
        </article>''')
    details = '\n'.join(f'<section class="project-detail"><h3>{escape(item["heading"])}</h3><p>{escape(item["text"])}</p></section>' for item in project.get('details', []))
    figures = []
    for image in project.get('images', []):
        src = image['src']
        if not src.startswith('assets/projects/') or not (root / src).is_file():
            raise ValueError(f'Missing local project image: {src}')
        figures.append(f'''<figure class="project-image"><a href="{escape(src, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(image['alt'], quote=True)}（画像を別タブで開く）"><img src="{escape(src, quote=True)}" alt="{escape(image['alt'], quote=True)}" width="{int(image['width'])}" height="{int(image['height'])}" loading="lazy" decoding="async"></a><figcaption>{escape(image['caption'])} <span aria-hidden="true">↗︎</span></figcaption></figure>''')
    gallery = f'<div class="project-gallery">{"".join(figures)}</div>' if figures else ''
    dialogs.append(f'''      <dialog class="project-dialog" id="project-{key}" aria-labelledby="title-{key}">
        <div class="dialog-toolbar"><span class="tag">{category}</span><button class="dialog-close" type="button" autofocus aria-label="{name}の紹介を閉じる"><span aria-hidden="true">×</span></button></div>
        <div class="dialog-content">
          <h2 id="title-{key}">{name}</h2>
          {gallery}
          <p class="project-intro">{description}</p>
          {details}
          {f'<div class="project-links">{" ".join(links)}</div>' if links else ''}
        </div>
      </dialog>''')
path = root / 'index.html'
source = path.read_text()
before, rest = source.split('      <!-- works:start -->', 1)
_, after = rest.split('      <!-- works:end -->', 1)
output = before + '      <!-- works:start -->\n      <div class="works">\n' + '\n\n'.join(cards) + '\n      </div>\n' + '\n'.join(dialogs) + '\n      <!-- works:end -->' + after
path.write_text('\n'.join(line.rstrip() for line in output.splitlines()) + '\n')
