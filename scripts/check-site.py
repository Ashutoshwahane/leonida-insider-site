"""Check export links, indexing, metadata, structured data and sitemap consistency."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse, json, xml.etree.ElementTree as ET

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.meta={}; self.links=[]; self.ids=set(); self.title=''; self.in_title=False; self.h1=0; self.jsonld=[]; self.in_json=False; self.chunk=''; self.canonical=None; self.images=[]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if d.get('id'): self.ids.add(d['id'])
        if tag=='h1': self.h1+=1
        if tag=='title': self.in_title=True
        if tag=='meta': self.meta[d.get('name',d.get('property',''))]=d.get('content','')
        if tag=='link' and d.get('rel')=='canonical': self.canonical=d.get('href')
        if tag=='script' and d.get('type')=='application/ld+json': self.in_json=True; self.chunk=''
        if tag=='img': self.images.append(d)
        for key in ['src','href']:
            if d.get(key): self.links.append(d[key])
    def handle_data(self, data):
        if self.in_title:self.title+=data
        if self.in_json:self.chunk+=data
    def handle_endtag(self, tag):
        if tag=='title':self.in_title=False
        if tag=='script' and self.in_json:
            self.jsonld.append(json.loads(self.chunk));self.in_json=False

a=argparse.ArgumentParser();a.add_argument('directory',nargs='?',default=str(Path(__file__).resolve().parent.parent/'dist'));root=Path(a.parse_args().directory)
pages={f.name:Page(f.read_text()) for f in root.glob('*.html')};errors=[];titles=[]
for name,p in pages.items():
    if p.h1!=1:errors.append(f'{name}: expected one h1, got {p.h1}')
    if not p.title or not p.meta.get('description'):errors.append(f'{name}: missing title/description')
    titles.append(p.title)
    if name!='404.html':
        if not p.canonical or not p.canonical.startswith('https://'):errors.append(f'{name}: missing HTTPS canonical')
        if p.meta.get('robots')!='index, follow':errors.append(f'{name}: export is not indexable')
        if p.meta.get('og:url')!=p.canonical:errors.append(f'{name}: social/canonical mismatch')
        if not p.jsonld:errors.append(f'{name}: missing structured data')
    elif 'noindex' not in p.meta.get('robots',''):errors.append('404 must stay noindex')
    if not p.meta.get('og:image','').startswith('https://'):errors.append(f'{name}: social image is not absolute')
    for img in p.images:
        if 'alt' not in img:errors.append(f'{name}: missing image alt attribute')
        if not img.get('width') or not img.get('height'):errors.append(f'{name}: image has no dimensions')
    for href in p.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        dest=unquote(u.path) or name
        if dest in ['.','./']:dest='index.html'
        if not (root/dest).exists():errors.append(f'{name}: broken local target {href}')
        if u.fragment:
            target=pages.get(dest)
            if target and u.fragment not in target.ids:errors.append(f'{name}: broken fragment {href}')
if len(set(titles))!=len(titles):errors.append('Duplicate page titles')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[x.text for x in ET.parse(root/'sitemap.xml').findall('.//s:loc',ns)]
expected={p.canonical for name,p in pages.items() if name!='404.html'}
if set(urls)!=expected:errors.append('Sitemap differs from canonical pages')
robots=(root/'robots.txt').read_text()
if 'Disallow: /' in robots or 'Sitemap: https://' not in robots:errors.append('Production robots blocks crawling or lacks sitemap')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} HTML pages; local links/fragments, titles/descriptions, image metadata, canonical/OG URLs, JSON-LD parsing, indexing and sitemap consistency.')
print('Local validation only; Google Rich Results Test, Search Console and live indexing are not verified.')
