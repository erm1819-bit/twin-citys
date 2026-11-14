# Twin Citys EN/ES conventions (shared by every page)

## Spanish style
Plain Latin American / Miami Spanish. Use tú (never usted, never vosotros). "celular" not "móvil", "página web" for website, "anuncios" for ads, "cliente(s)" for customers/leads where natural. Keep it as short and plain as the English. Keep brand/proper names as-is (Twin Citys, Google, Instagram, Meta, Facebook, Miami, La Vasca, Lucerne, Marino Plumbing). Match the existing /es/ homepage voice (see es/index.html in the repo).

## URL map (English -> Spanish twin)
/                      -> /es/
/services/websites/    -> /es/servicios/paginas-web/
/services/ads/         -> /es/servicios/anuncios/
/services/content/     -> /es/servicios/fotos-y-video/
/services/crm/         -> /es/servicios/seguimiento-de-clientes/
/services/google/      -> /es/servicios/seo-local/
/services/social/      -> /es/servicios/redes-sociales/
/start/                -> /es/empezar/
/check/                -> /es/chequeo/
/break-even/           -> /es/calculadora/
Pages with no Spanish twin (privacy, terms, areas, work, demo) stay English; Spanish pages may link to them as-is.
On a Spanish page every internal link that has a twin must point to the Spanish twin (e.g. "/#contact" -> "/es/#contact", "/start/?service=ads" -> "/es/empezar/?service=ads").

## Head tags on BOTH twins
<link rel="alternate" hreflang="en" href="https://twincitys.net/EN-PATH">
<link rel="alternate" hreflang="es" href="https://twincitys.net/ES-PATH">
<link rel="alternate" hreflang="x-default" href="https://twincitys.net/EN-PATH">
Spanish page: <html lang="es">, canonical = its own Spanish URL, og:url Spanish, og:locale es_US, translated title/description/og text and JSON-LD text.
Then, immediately after the alternate links, this exact snippet (remembers the visitor's language choice):
<script>try{var p=localStorage.getItem('tc-lang');if(p&&p!==document.documentElement.lang.slice(0,2)){var a=document.querySelector('link[rel="alternate"][hreflang="'+p+'"]');if(a&&a.href!==location.origin+location.pathname)location.replace(a.href+location.search+location.hash);}}catch(e){}</script>

## The EN/ES switch (same pill as the homepage)
Markup on an English page:
<a class="lang" href="SPANISH-PATH" data-on="en" hreflang="es" lang="es" aria-label="Ver en español"><span data-l="en" class="on">EN</span><span data-l="es">ES</span></a>
On a Spanish page:
<a class="lang" href="ENGLISH-PATH" data-on="es" hreflang="en" lang="en" aria-label="View in English"><span data-l="en">EN</span><span data-l="es" class="on">ES</span></a>
CSS (adapt the --black var name to the page's own dark color var if different):
.lang { position: relative; display: inline-grid; grid-template-columns: 1fr 1fr; align-items: center; height: 30px; padding: 2px; border: 1px solid currentColor; border-radius: 999px; font-size: 10px; font-weight: 600; letter-spacing: .14em; line-height: 1; text-decoration: none; text-transform: uppercase; -webkit-tap-highlight-color: transparent; }
.lang::before { content: ""; position: absolute; top: 2px; bottom: 2px; left: 2px; width: calc(50% - 2px); border-radius: 999px; background: currentColor; transition: transform .32s cubic-bezier(.2,.8,.2,1); }
.lang[data-on="es"]::before { transform: translateX(100%); }
.lang span { position: relative; z-index: 1; padding: 0 9px; line-height: 24px; text-align: center; opacity: .75; transition: color .32s, opacity .32s; }
.lang span.on { color: var(--black); opacity: 1; }
.lang:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
Script, once per page before </body>:
<script>
document.querySelectorAll('.lang').forEach(function (t) {
  t.addEventListener('click', function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    var to = t.dataset.on === 'en' ? 'es' : 'en';
    try { localStorage.setItem('tc-lang', to); } catch (x) {}
    t.dataset.on = to;
    t.querySelectorAll('span').forEach(function (s) { s.classList.toggle('on', s.dataset.l === to); });
    setTimeout(function () { location.href = t.getAttribute('href') + location.search + location.hash; }, 300);
  });
});
</script>
