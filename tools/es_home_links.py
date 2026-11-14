"""After regenerating es/index.html (the Spanish homepage), point its links at the Spanish pages,
and make sure both homepages remember the visitor's language. Run from the repo root:
    python3 tools/es_home_links.py
"""
import re, sys
sys.path.insert(0, 'tools')
from es_services import SLUG, REMEMBER
def remember(s):
    s = re.sub(r'<script>try\{var p=localStorage\.getItem\(\'tc-lang\'\).*?</script>\n', '', s, flags=re.S)
    s = s.replace('<link rel="alternate" hreflang="x-default" href="https://twincitys.net/">\n', '<link rel="alternate" hreflang="x-default" href="https://twincitys.net/">\n' + REMEMBER + '\n', 1)
    if "localStorage.setItem('tc-lang'" not in s:
        s = s.replace("    var to = t.dataset.on === 'en' ? 'es' : 'en';\n", "    var to = t.dataset.on === 'en' ? 'es' : 'en';\n    try { localStorage.setItem('tc-lang', to); } catch (x) {}\n", 1)
    # footer text links (English / Español) remember too
    return s
en = remember(open('index.html').read())
open('index.html', 'w').write(en)
es = remember(open('es/index.html').read())
for k, v in SLUG.items():
    es = es.replace(f'href="/services/{k}/"', f'href="/es/servicios/{v}/"')
es = es.replace('href="/check/"', 'href="/es/chequeo/"').replace('href="/break-even/"', 'href="/es/calculadora/"')
es = es.replace('href="https://twincitys.net/start"', 'href="/es/empezar/"')
open('es/index.html', 'w').write(es)
print('ok', es.count('/es/servicios/'), es.count('/es/empezar/'))
