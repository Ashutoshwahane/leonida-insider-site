"""Create a separate static release directory. Never publish or change DNS."""
from pathlib import Path
from urllib.parse import urlparse
import argparse, shutil, re, json, html, xml.etree.ElementTree as ET
parser=argparse.ArgumentParser()
parser.add_argument('--origin',required=True,help='Approved production URL, including repository path if needed')
a=parser.parse_args()
u=urlparse(a.origin)
if u.scheme!='https' or not u.netloc or u.query or u.fragment or u.username or any(c in a.origin for c in '\"<>\\') or any(c.isspace() for c in a.origin):
    parser.error('Use an HTTPS production origin without credentials, queries or fragments')
origin=a.origin.rstrip('/')
root=Path(__file__).resolve().parent.parent
out=root/'dist'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for f in [*root.glob('*.html'),root/'styles.css',root/'script.js',root/'.nojekyll']:
    shutil.copy(f,out/f.name)
shutil.copytree(root/'assets',out/'assets')
if (root/'CNAME').is_file(): shutil.copy(root/'CNAME',out/'CNAME')
for file in out.glob('*.html'):
    txt=file.read_text()
    canonical=origin+'/' + ('' if file.name=='index.html' else file.name)
    if file.name!='404.html':
        txt=txt.replace('content="noindex, nofollow"','content="index, follow"')
        txt=txt.replace('</head>',f'<link rel="canonical" href="{canonical}"><meta property="og:url" content="{canonical}"></head>')
    txt=txt.replace('content="assets/social-card.png"',f'content="{origin}/assets/social-card.png"')
    if file.name != '404.html':
        publisher = origin + '/#publisher'
        website = origin + '/#website'
        page = {"@type":"WebPage", "@id":canonical + '#page', "url":canonical, "inLanguage":"en", "isPartOf":{"@id":website}}
        title = html.unescape(re.search(r'<title>(.*?)</title>', txt).group(1))
        page['name'] = title
        graph = [page]
        if file.name == 'index.html':
            graph += [
                {"@type":"Organization", "@id":publisher, "name":"Leonida Insider", "url":origin+'/', "logo":origin+'/assets/app-icon.png', "email":"cybernerd404notfound@gmail.com"},
                {"@type":"WebSite", "@id":website, "name":"Leonida Insider", "url":origin+'/', "inLanguage":"en", "publisher":{"@id":publisher}},
            ]
        elif file.name == 'reading-announcements.html':
            graph.append({"@type":"Article", "@id":canonical+'#article', "headline":"Before you share that GTA VI headline, check these things.", "mainEntityOfPage":{"@id":canonical+'#page'}, "author":{"@type":"Organization","@id":publisher,"name":"Leonida Insider editorial","url":origin+'/about.html'}, "publisher":{"@id":publisher}, "dateCreated":"2026-11-06", "datePublished":"2026-11-06", "inLanguage":"en", "isAccessibleForFree":True, "description":"Check the source, date, platform, and wording before sharing a GTA VI headline."})
        elif file.name == 'articles.html':
            page['@type'] = 'CollectionPage'
            graph.append({"@type":"ItemList", "itemListElement":[{"@type":"ListItem","position":1,"url":origin+'/reading-announcements.html',"name":"Before you share that GTA VI headline, check these things."}]})
        elif file.name == 'about.html':
            page['@type'] = 'AboutPage'
            page['about'] = {"@id":publisher}
        if file.name != 'index.html':
            crumbs=[{"@type":"ListItem","position":1,"name":"Home","item":origin+'/'}]
            if file.name == 'reading-announcements.html': crumbs.append({"@type":"ListItem","position":2,"name":"News & guides","item":origin+'/articles.html'})
            crumbs.append({"@type":"ListItem","position":len(crumbs)+1,"name":title.split(' | ')[0],"item":canonical})
            graph.append({"@type":"BreadcrumbList","itemListElement":crumbs})
        structured=json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False).replace('<','\\u003c')
        txt=txt.replace('</head>','<script type="application/ld+json">'+structured+'</script></head>')
    if file.name == '404.html': txt=txt.replace('</head>', '<base href="'+origin+'/"></head>')
    file.write_text(txt)
ns='http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('',ns)
urls=ET.Element('{'+ns+'}urlset')
for path in ['', 'articles.html', 'about.html', 'reading-announcements.html', 'privacy.html','terms.html']:
    url=ET.SubElement(urls,'{'+ns+'}url');ET.SubElement(url,'{'+ns+'}loc').text=origin+'/'+path
ET.ElementTree(urls).write(out/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(out/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n')
print(f'Prepared {out}; no deployment performed.')
