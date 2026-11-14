import os, sys
R = '/home/claude/twin-citys'
def rd(p): return open(os.path.join(R, p), encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
    open(os.path.join(R, p), 'w', encoding='utf-8').write(s)

def sub(s, pairs, name):
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            # allow explicit multi with tuple of 3
            raise SystemExit(f'{name}: expected 1 match, got {n}: {a[:80]!r}')
        s = s.replace(a, b)
    return s
def suball(s, a, b, n_exp, name):
    n = s.count(a)
    if n != n_exp: raise SystemExit(f'{name}: expected {n_exp} of {a[:60]!r}, got {n}')
    return s.replace(a, b)

SNIP = """<script>try{var p=localStorage.getItem('tc-lang');if(p&&p!==document.documentElement.lang.slice(0,2)){var a=document.querySelector('link[rel="alternate"][hreflang="'+p+'"]');if(a&&a.href!==location.origin+location.pathname)location.replace(a.href+location.search+location.hash);}}catch(e){}</script>"""
CSS = """.lang { position: relative; display: inline-grid; grid-template-columns: 1fr 1fr; align-items: center; height: 30px; padding: 2px; border: 1px solid currentColor; border-radius: 999px; font-size: 10px; font-weight: 600; letter-spacing: .14em; line-height: 1; text-decoration: none; text-transform: uppercase; -webkit-tap-highlight-color: transparent; }
.lang::before { content: ""; position: absolute; top: 2px; bottom: 2px; left: 2px; width: calc(50% - 2px); border-radius: 999px; background: currentColor; transition: transform .32s cubic-bezier(.2,.8,.2,1); }
.lang[data-on="es"]::before { transform: translateX(100%); }
.lang span { position: relative; z-index: 1; padding: 0 9px; line-height: 24px; text-align: center; opacity: .75; transition: color .32s, opacity .32s; }
.lang span.on { color: var(--black); opacity: 1; }
.lang:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
"""
JS = """<script>
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
"""
def pill(en, es, is_es):
    if is_es:
        return f'<a class="lang" href="{en}" data-on="es" hreflang="en" lang="en" aria-label="View in English"><span data-l="en">EN</span><span data-l="es" class="on">ES</span></a>'
    return f'<a class="lang" href="{es}" data-on="en" hreflang="es" lang="es" aria-label="Ver en español"><span data-l="en" class="on">EN</span><span data-l="es">ES</span></a>'
def alts(en, es):
    return (f'<link rel="alternate" hreflang="en" href="https://twincitys.net{en}">\n'
            f'<link rel="alternate" hreflang="es" href="https://twincitys.net{es}">\n'
            f'<link rel="alternate" hreflang="x-default" href="https://twincitys.net{en}">\n' + SNIP + '\n')

def common(s, en, es, is_es, head_anchor, extra_css, top_pairs, name):
    """head_anchor: insert alternates+snippet right before this string."""
    s = sub(s, [(head_anchor, alts(en, es) + head_anchor)], name)
    s = sub(s, [('</style>\n</head>', CSS + extra_css + '</style>\n</head>')], name)
    s = sub(s, [(a, b.replace('PILL', pill(en, es, is_es))) for a, b in top_pairs], name)
    s = sub(s, [('</body>\n</html>', JS + '</body>\n</html>')], name)
    return s

# ---------------------------------------------------------------- START
EN, ES = '/start/', '/es/empezar/'
src = rd('start/index.html')
start_css = """.top__r { display: inline-flex; align-items: center; gap: 18px; }
.top a.lang { display: inline-grid; min-height: 0; gap: 0; }
@media (max-width: 480px) { .top { letter-spacing: .2em; } .top__r { gap: 12px; } }
"""
def start_top(back_href, back_txt):
    return [(f'    <a class="place" href="{back_href}"><span aria-hidden="true">←</span> {back_txt}</a>',
             f'    <span class="top__r">\n      PILL\n      <a class="place" href="{back_href}"><span aria-hidden="true">←</span> {back_txt}</a>\n    </span>')]

es = src
es = sub(es, [
    ('<html lang="en">', '<html lang="es">'),
    ('content="Start a project with Twin Citys, a Miami creative studio. One short form, plain words, no tech talk."',
     'content="Empieza un proyecto con Twin Citys, un estudio creativo en Miami. Un formulario corto, en palabras sencillas, sin lenguaje técnico."'),
    ('<meta name="robots" content="noindex">', '<meta name="robots" content="noindex">\n<link rel="canonical" href="https://twincitys.net/es/empezar/">'),
    ('<title>Twin Citys Project Form</title>', '<title>Formulario de proyecto Twin Citys</title>'),
    ('<div class="intro__bottom"><span>Start a project</span>', '<div class="intro__bottom"><span>Empezar un proyecto</span>'),
    ('<a href="https://twincitys.net/" aria-label="Twin Citys home">', '<a href="https://twincitys.net/es/" aria-label="Twin Citys, inicio">'),
    ('<span class="eyebrow">Start a project</span>', '<span class="eyebrow">Empezar un proyecto</span>'),
    ("<h1>Let's build something people <em>remember.</em></h1>", '<h1>Hagamos algo que la gente <em>recuerde.</em></h1>'),
    ('<p>Four quick things and a Send button. It goes straight to our team and we reply within a day.</p>',
     '<p>Cuatro datos rápidos y un botón para enviar. Le llega directo a nuestro equipo y te respondemos en menos de un día.</p>'),
    ('<input type="hidden" name="subject" value="New project request from twincitys.net">',
     '<input type="hidden" name="subject" value="New project request from twincitys.net (Spanish)">'),
    ('<input type="hidden" name="redirect" value="https://twincitys.net/start/#sent">',
     '<input type="hidden" name="redirect" value="https://twincitys.net/es/empezar/#sent">\n        <input type="hidden" name="language" value="Spanish">'),
    ('<label for="f-name">Your name</label>', '<label for="f-name">Tu nombre</label>'),
    ('<label for="f-company">Business name</label>', '<label for="f-company">Nombre del negocio</label>'),
    ('<label for="f-contact">Email or phone</label>', '<label for="f-contact">Correo o teléfono</label>'),
    ('<legend class="h2">What do you need <em>help</em> with?</legend>', '<legend class="h2">¿Con qué necesitas <em>ayuda</em>?</legend>'),
    ('<p class="hint">Tap as many as you want.</p>', '<p class="hint">Escoge todas las que quieras.</p>'),
    ('<span>A brand new website</span>', '<span>Una página web nueva</span>'),
    ('<span>Fix or refresh my current website</span>', '<span>Arreglar o renovar mi página web</span>'),
    ('<span>Logo and brand look</span>', '<span>Logo e imagen de marca</span>'),
    ('<span>Photos or video</span>', '<span>Fotos o video</span>'),
    ('<span>Ads on Facebook and Instagram</span>', '<span>Anuncios en Facebook e Instagram</span>'),
    ('<span>Google review cards</span>', '<span>Tarjetas de reseñas de Google</span>'),
    ('<span>Not sure yet, help me decide</span>', '<span>No sé todavía, ayúdenme a decidir</span>'),
    ('<label for="f-about">Anything else we should know?</label>', '<label for="f-about">¿Algo más que debamos saber?</label>'),
    ('placeholder="e.g. your current website, when you want to start, etc."', 'placeholder="ej. tu página web actual, cuándo quieres empezar, etc."'),
    ('<b>Send me the Twin Citys monthly email</b><small>One email a month with new work and ideas for local businesses. Unsubscribe anytime.</small>',
     '<b>Mándame el correo mensual de Twin Citys</b><small>Un correo al mes con trabajos nuevos e ideas para negocios locales. Te puedes dar de baja cuando quieras.</small>'),
    ('hidden>Put an email address above to get the monthly email.</p>', 'hidden>Escribe tu correo arriba para recibir el correo mensual.</p>'),
    ('<a class="nav__privacy" href="/privacy/">Privacy</a>', '<a class="nav__privacy" href="/privacy/">Privacidad</a>'),
    ('id="send-btn">Send it over</button>', 'id="send-btn">Enviar</button>'),
    ('<h2>Got it. <em>Thank you.</em></h2>', '<h2>Listo. <em>Gracias.</em></h2>'),
    ("<p>Your message is on its way to our team. One of us will reply within a day. If it's urgent, call or text any of us.</p>",
     '<p>Tu mensaje va en camino a nuestro equipo. Uno de nosotros te responde en menos de un día. Si es urgente, llama o escríbele a cualquiera de nosotros.</p>'),
    ('<a class="btn btn--go" href="https://twincitys.net/">See our work</a>', '<a class="btn btn--go" href="https://twincitys.net/es/#work">Ver nuestro trabajo</a>'),
    ('<a class="btn btn--ghost" href="https://twincitys.net/start/#intro">Send another</a>', '<a class="btn btn--ghost" href="https://twincitys.net/es/empezar/#intro">Enviar otro</a>'),
    ('<span>Design | Develop | Create</span>', '<span>Diseño | Desarrollo | Creación</span>'),
    ("st.textContent = 'We need your name, business and a way to reach you.';", "st.textContent = 'Necesitamos tu nombre, tu negocio y una forma de contactarte.';"),
    ("st.textContent = 'Sending…';", "st.textContent = 'Enviando…';"),
    ("st.textContent = 'That didn’t go through. Email us instead at eric@twincitys.net.';", "st.textContent = 'No se pudo enviar. Escríbenos a eric@twincitys.net.';"),
], 'es/empezar')
es = common(es, EN, ES, True, '<link rel="icon" href="../favicon.svg"', start_css,
            start_top('https://twincitys.net/', 'Back to home'), 'es/empezar')
es = sub(es, [('<a class="place" href="https://twincitys.net/"><span aria-hidden="true">←</span> Back to home</a>',
               '<a class="place" href="/es/"><span aria-hidden="true">←</span> Volver al inicio</a>')], 'es/empezar')
es = es.replace('href="../favicon.svg"', 'href="/favicon.svg"')
wr('es/empezar/index.html', es)
en = common(src, EN, ES, False, '<link rel="icon" href="../favicon.svg"', start_css,
            start_top('https://twincitys.net/', 'Back to home'), 'start')
wr('start/index.html', en)

# ---------------------------------------------------------------- CHECK
EN, ES = '/check/', '/es/chequeo/'
src = rd('check/index.html')
check_css = """.top__links a.lang { display: inline-grid; justify-content: stretch; min-height: 30px; }
@media (max-width: 400px) { .top__links { gap: 14px; } }
"""
check_top = [('        <a class="top__ig" href="https://instagram.com/twincitys.co"', '        PILL\n        <a class="top__ig" href="https://instagram.com/twincitys.co"')]
es = src
STUDIO_ES = 'Estudio de diseño web en Miami. Hacemos y lanzamos páginas web para restaurantes, panaderías y tiendas locales.'
es = sub(es, [
    ('<html lang="en">', '<html lang="es">'),
    ('<title>Free Google check for your business · Twin Citys</title>', '<title>Chequeo gratis de tu negocio en Google · Twin Citys</title>'),
    ('<meta name="description" content="Look your business up the way customers do and check seven things on Google: your profile, hours, phone, reviews, photos and website. A free two-minute check from Twin Citys, Miami.">',
     '<meta name="description" content="Busca tu negocio como lo hacen tus clientes y revisa siete cosas en Google: tu perfil, horario, teléfono, reseñas, fotos y página web. Un chequeo gratis de dos minutos de Twin Citys, Miami.">'),
    ('<link rel="canonical" href="https://twincitys.net/check/">', '<link rel="canonical" href="https://twincitys.net/es/chequeo/">'),
    ('content="Does your business look right on Google? · Twin Citys"', 'content="¿Tu negocio se ve bien en Google? · Twin Citys"'),
    ('content="A free two-minute check for Miami businesses: seven things customers should see when they look you up."',
     'content="Un chequeo gratis de dos minutos para negocios de Miami: siete cosas que tus clientes deberían ver cuando te buscan."'),
    ('<meta property="og:url" content="https://twincitys.net/check/">', '<meta property="og:url" content="https://twincitys.net/es/chequeo/">\n<meta property="og:locale" content="es_US">'),
    ('"description": "Web design studio in Miami. We build and launch websites for restaurants, bakeries and local shops."', f'"description": "{STUDIO_ES}"'),
    ('"@id": "https://twincitys.net/check/",\n      "url": "https://twincitys.net/check/",', '"@id": "https://twincitys.net/es/chequeo/",\n      "url": "https://twincitys.net/es/chequeo/",'),
    ('"name": "Free Google check for your business",', '"name": "Chequeo gratis de tu negocio en Google",'),
    ('"description": "Look your business up the way customers do and check seven things on Google: your profile, hours, phone, reviews, photos and website.",',
     '"description": "Busca tu negocio como lo hacen tus clientes y revisa siete cosas en Google: tu perfil, horario, teléfono, reseñas, fotos y página web.",'),
    ('"inLanguage": "en-US"', '"inLanguage": "es-US"'),
    ('<a class="brand" href="/">', '<a class="brand" href="/es/">'),
    ('<nav class="top__links" aria-label="Contact">\n        <a href="/#contact">Contact</a>', '<nav class="top__links" aria-label="Contacto">\n        <a href="/es/#contact">Contacto</a>'),
    ('aria-label="Twin Citys on Instagram"', 'aria-label="Twin Citys en Instagram"'),
    ('<p class="label node" id="h-label">Free Google check</p>', '<p class="label node" id="h-label">Chequeo gratis de Google</p>'),
    ('<h1 id="h-title">Does your business look right on Google?</h1>', '<h1 id="h-title">¿Tu negocio se ve bien en Google?</h1>'),
    ('<p class="lede" id="h-lede">Most customers find you on Google before they ever walk in. Look your business up the way they do, then check seven things in about two minutes.</p>',
     '<p class="lede" id="h-lede">Casi todos tus clientes te encuentran en Google antes de llegar a tu puerta. Busca tu negocio como lo hacen ellos y revisa siete cosas en unos dos minutos.</p>'),
    ('<p class="label node">01 · Search</p>', '<p class="label node">01 · Buscar</p>'),
    ('<h2 id="s1">Find yourself like a customer does.</h2>', '<h2 id="s1">Búscate como lo haría un cliente.</h2>'),
    ('<p class="sentence">Look up <input id="biz" type="text" autocomplete="organization" placeholder="your business" aria-label="Business name"> in <input id="city" type="text" value="Miami" aria-label="City"></p>',
     '<p class="sentence">Busca <input id="biz" type="text" autocomplete="organization" placeholder="tu negocio" aria-label="Nombre del negocio"> en <input id="city" type="text" value="Miami" aria-label="Ciudad"></p>'),
    ('aria-disabled="true">Search Google <span aria-hidden="true">→</span></a>', 'aria-disabled="true">Buscar en Google <span aria-hidden="true">→</span></a>'),
    ('<p class="hint">Opens in a new tab. Come back and go down the list.</p>', '<p class="hint">Se abre en otra pestaña. Vuelve aquí y sigue la lista.</p>'),
    ('<p class="label node">02 · Check</p>', '<p class="label node">02 · Revisar</p>'),
    ("<h2 id=\"s2\">Tick what's right. Leave what's missing.</h2>", '<h2 id="s2">Marca lo que está bien. Deja lo que falta.</h2>'),
    ('<b>Your Google profile shows up</b><span class="d">A box with your name, map and photos, on the right on a computer or at the top on a phone.</span>',
     '<b>Aparece tu perfil de Google</b><span class="d">Un cuadro con tu nombre, mapa y fotos: a la derecha en la computadora o arriba en el celular.</span>'),
    ('<b>Your hours are right</b><span class="d">Including holidays and any days you close early.</span>',
     '<b>Tu horario está bien</b><span class="d">Incluyendo los días feriados y los días que cierras temprano.</span>'),
    ('<b>Your phone number works</b><span class="d">Tap it. It should ring your business, not an old line.</span>',
     '<b>Tu número de teléfono funciona</b><span class="d">Tócalo. Debe sonar en tu negocio, no en una línea vieja.</span>'),
    ("<b>You have recent reviews</b><span class=\"d\">Some from the last few months, and you've replied to them.</span>",
     '<b>Tienes reseñas recientes</b><span class="d">Algunas de los últimos meses, y les has respondido.</span>'),
    ('<b>The photos make you look good</b><span class="d">Real photos of your place, your food or your work, not blurry ones a stranger took.</span>',
     '<b>Las fotos te hacen ver bien</b><span class="d">Fotos reales de tu local, tu comida o tu trabajo, no fotos borrosas que tomó un desconocido.</span>'),
    ('<b>Your own website is on the first page</b><span class="d">Not only Yelp, Facebook or a directory.</span>',
     '<b>Tu propia página web sale en los primeros resultados</b><span class="d">No solo Yelp, Facebook o un directorio.</span>'),
    ('<b>The website link goes to your site</b><span class="d">On your Google profile, the Website button opens your real website.</span>',
     '<b>El enlace a tu página web funciona</b><span class="d">En tu perfil de Google, el botón Sitio web abre tu página web de verdad.</span>'),
    ('<p class="big" id="verdict">Your score fills in as you go.</p>', '<p class="big" id="verdict">Tu puntaje se llena a medida que avanzas.</p>'),
    ('<p class="muted" id="sub">Seven out of seven means customers can find you and trust what they see.</p>',
     '<p class="muted" id="sub">Siete de siete significa que tus clientes te encuentran y confían en lo que ven.</p>'),
    ('<a class="btn" href="/start/">Start a project <span aria-hidden="true">→</span></a>', '<a class="btn" href="/es/empezar/">Empezar un proyecto <span aria-hidden="true">→</span></a>'),
    ('<a class="btn btn--line" href="/#work">See our work</a>', '<a class="btn btn--line" href="/es/#work">Ver nuestro trabajo</a>'),
    ('<a href="/start/">Start a project</a><a href="https://www.instagram.com/twincitys.co/"', '<a href="/es/empezar/">Empezar un proyecto</a><a href="https://www.instagram.com/twincitys.co/"'),
    ('<a href="/areas/">Areas we serve</a><a href="/privacy/">Privacy</a>', '<a href="/areas/">Zonas donde trabajamos</a><a href="/privacy/">Privacidad</a>'),
    ("textContent = 'Subscription confirmed';", "textContent = 'Suscripción confirmada';"),
    ("""textContent = "You're on the list.";""", "textContent = 'Ya estás en la lista.';"),
    ("textContent = 'One email a month, nothing more. Now do the thing from our email: look your business up the way a customer would.';",
     "textContent = 'Un correo al mes, nada más. Ahora haz lo que te dijimos en el correo: busca tu negocio como lo haría un cliente.';"),
    ("""verdict.textContent = "You're in good shape.";""", "verdict.textContent = 'Vas muy bien.';"),
    ("""sub.textContent = "Customers can find you and trust what they see. We'll send ideas each month to keep it that way.";""",
     "sub.textContent = 'Tus clientes te encuentran y confían en lo que ven. Te mandamos ideas cada mes para que siga así.';"),
    ("verdict.textContent = missing === 1 ? 'One thing is missing or wrong.' : missing + ' things are missing or wrong.';",
     "verdict.textContent = missing === 1 ? 'Falta una cosa o está mal.' : 'Faltan ' + missing + ' cosas o están mal.';"),
    ("""sub.textContent = "That's usually the first thing we fix, and most of it takes a day. Reply to our email or start a project and tell us what you saw.";""",
     "sub.textContent = 'Eso suele ser lo primero que arreglamos, y casi todo toma un día. Responde a nuestro correo o empieza un proyecto y cuéntanos lo que viste.';"),
], 'es/chequeo')
es = suball(es, "verdict.textContent = 'Your score fills in as you go.';", "verdict.textContent = 'Tu puntaje se llena a medida que avanzas.';", 1, 'es/chequeo')
es = suball(es, "sub.textContent = 'Seven out of seven means customers can find you and trust what they see.';", "sub.textContent = 'Siete de siete significa que tus clientes te encuentran y confían en lo que ven.';", 1, 'es/chequeo')
es = common(es, EN, ES, True, '<meta property="og:type"', check_css, check_top, 'es/chequeo')
wr('es/chequeo/index.html', es)
en = common(src, EN, ES, False, '<meta property="og:type"', check_css, check_top, 'check')
wr('check/index.html', en)

# ---------------------------------------------------------------- BREAK-EVEN
EN, ES = '/break-even/', '/es/calculadora/'
src = rd('break-even/index.html')
be_css = """.top nav a.lang { opacity: 1; }
@media (max-width: 480px) { .top { letter-spacing: .2em; } .top nav { gap: 14px; } }
"""
be_top = [('<a href="/#contact">Contact</a></nav>', '<a href="/#contact">Contact</a>PILL</nav>')]
# English: replace the dead /missed-calls/ links first
src2 = sub(src, [
    ('<a class="more-link" href="/missed-calls/">What missed calls cost you →</a>', '<a class="more-link" href="/services/crm/">See how we follow up →</a>'),
    ('<a class="more-link" href="/missed-calls/">This assumes every lead gets answered. What missed calls cost you →</a>',
     '<a class="more-link" href="/services/crm/">This assumes every lead gets answered. See how we follow up →</a>'),
], 'break-even')
es = src2
L = 'cliente potencial'
es = sub(es, [
    ('<html lang="en">', '<html lang="es">'),
    ('<title>Ad break-even calculator: what you can afford to pay for a lead · Twin Citys</title>',
     '<title>Calculadora de anuncios: cuánto puedes pagar por un cliente potencial · Twin Citys</title>'),
    ('<meta name="description" content="Free ad break-even calculator for small businesses. Drag three sliders and see the most you can pay per lead before your ads lose money, then check the ads you\'re running now.">',
     '<meta name="description" content="Calculadora gratis para anuncios de pequeños negocios. Mueve tres barras y mira lo máximo que puedes pagar por cliente potencial antes de que tus anuncios pierdan dinero. Después revisa los anuncios que tienes ahora.">'),
    ('<link rel="canonical" href="https://twincitys.net/break-even/">', '<link rel="canonical" href="https://twincitys.net/es/calculadora/">'),
    ('content="What can you afford to pay for a lead? · Twin Citys"', 'content="¿Cuánto puedes pagar por un cliente potencial? · Twin Citys"'),
    ('content="A free ten-second tool for Miami businesses: the most you can pay per lead before your ads lose money."',
     'content="Una herramienta gratis de diez segundos para negocios de Miami: lo máximo que puedes pagar por cliente potencial antes de que tus anuncios pierdan dinero."'),
    ('<meta property="og:url" content="https://twincitys.net/break-even/">', '<meta property="og:url" content="https://twincitys.net/es/calculadora/">\n<meta property="og:locale" content="es_US">'),
    ('"description": "Web design studio in Miami. We build and launch websites for restaurants, bakeries and local shops."', f'"description": "{STUDIO_ES}"'),
    ('"@id": "https://twincitys.net/break-even/",\n      "url": "https://twincitys.net/break-even/",', '"@id": "https://twincitys.net/es/calculadora/",\n      "url": "https://twincitys.net/es/calculadora/",'),
    ('"name": "Ad break-even calculator",', '"name": "Calculadora de punto de equilibrio para anuncios",'),
    ('"description": "The most a small business can pay per lead and per customer before its ads lose money.",',
     '"description": "Lo máximo que un pequeño negocio puede pagar por cliente potencial y por cliente antes de que sus anuncios pierdan dinero.",'),
    ('"inLanguage": "en-US"', '"inLanguage": "es-US"'),
    ('.meter__you::after { content: "you";', '.meter__you::after { content: "tú";'),
    ('<a class="brand" href="/">', '<a class="brand" href="/es/">'),
    ('<small>Free tool · Ad break-even</small>', '<small>Herramienta gratis · Calculadora de anuncios</small>'),
    ('<nav aria-label="Site"><a href="/services/ads/">Ads</a><a href="/#contact">Contact</a></nav>',
     '<nav aria-label="Sitio"><a href="/es/servicios/anuncios/">Anuncios</a><a href="/es/#contact">Contacto</a></nav>'),
    ('<h1 id="h">What can you afford to pay for a lead?</h1>', '<h1 id="h">¿Cuánto puedes pagar por un cliente potencial?</h1>'),
    ('<p class="lede">Three dials about your business. The number on the right is your limit, and it moves as you drag.</p>',
     '<p class="lede">Tres datos de tu negocio. El número grande es tu límite, y se mueve mientras arrastras.</p>'),
    ('<label for="ticket">A customer spends</label>', '<label for="ticket">Un cliente gasta</label>'),
    ('aria-label="Average sale in dollars"', 'aria-label="Venta promedio en dólares"'),
    ("<p class=\"dial__why\">A typical sale, not your biggest one. For a restaurant that's one table's check; for a plumber, one average job.</p>",
     '<p class="dial__why">Una venta normal, no la más grande. Para un restaurante es la cuenta de una mesa; para un plomero, un trabajo promedio.</p>'),
    ('aria-label="Average sale slider"', 'aria-label="Barra de venta promedio"'),
    ('<label for="margin">Profit on each sale</label>', '<label for="margin">Ganancia en cada venta</label>'),
    ('aria-label="Percent of each sale that is profit"', 'aria-label="Porcentaje de cada venta que es ganancia"'),
    ("<p class=\"dial__why\">What's left after food, materials and labor for that sale. Food runs 55–70%. Services run higher.</p>",
     '<p class="dial__why">Lo que te queda después de la comida, los materiales y la mano de obra de esa venta. En comida suele ser 55–70%. En servicios, más.</p>'),
    ('aria-label="Profit margin slider"', 'aria-label="Barra de margen de ganancia"'),
    ('<label for="close">Leads who end up buying</label>', '<label for="close">Clientes potenciales que compran</label>'),
    ('aria-label="Percent of leads who become customers"', 'aria-label="Porcentaje de clientes potenciales que se vuelven clientes"'),
    ('<p class="dial__why">Of ten people who call, message or fill out a form, how many become customers? Three is normal when leads are answered fast.</p>',
     '<p class="dial__why">De diez personas que llaman, escriben o llenan un formulario, ¿cuántas se vuelven clientes? Tres es normal cuando se les responde rápido.</p>'),
    ('aria-label="Close rate slider"', 'aria-label="Barra de tasa de cierre"'),
    ('aria-controls="moreBody">Already running ads? Check them</button>', 'aria-controls="moreBody">¿Ya tienes anuncios? Revísalos</button>'),
    ('<label for="spend">Ad spend a month</label>', '<label for="spend">Gasto en anuncios al mes</label>'),
    ('aria-label="Monthly ad spend in dollars"', 'aria-label="Gasto mensual en anuncios en dólares"'),
    ('aria-label="Ad spend slider"', 'aria-label="Barra de gasto en anuncios"'),
    ('<label for="leads">Leads from ads a month</label>', '<label for="leads">Clientes potenciales al mes</label>'),
    ('aria-label="Leads a month from ads"', 'aria-label="Clientes potenciales al mes que vienen de anuncios"'),
    ('<p class="dial__why">Calls, messages and forms that came from the ads, not from Google or walk-ins.</p>',
     '<p class="dial__why">Llamadas, mensajes y formularios que vinieron de los anuncios, no de Google ni de gente que pasó por el local.</p>'),
    ('aria-label="Leads slider"', 'aria-label="Barra de clientes potenciales"'),
    ('<a class="more-link" href="/services/crm/">See how we follow up →</a>', '<a class="more-link" href="/es/servicios/seguimiento-de-clientes/">Mira cómo damos seguimiento →</a>'),
    ('<a class="more-link" href="/services/crm/">This assumes every lead gets answered. See how we follow up →</a>',
     '<a class="more-link" href="/es/servicios/seguimiento-de-clientes/">Esto asume que cada cliente potencial recibe respuesta. Mira cómo damos seguimiento →</a>'),
    ('<p class="eyebrow" id="eyebrow">Your limit per lead</p>', '<p class="eyebrow" id="eyebrow">Tu límite por cliente potencial</p>'),
    ('<span class="per" id="per">the most one call or message can cost you</span>', '<span class="per" id="per">lo máximo que te puede costar una llamada o un mensaje</span>'),
    ('<span>Comfortable zone</span><span>Limit <b id="limitTick">', '<span>Zona cómoda</span><span>Límite <b id="limitTick">'),
    ("<p class=\"say\" id=\"say\">Pay less than this for each lead and every ad you run makes money. Pay more and you're buying customers at a loss.</p>",
     '<p class="say" id="say">Paga menos que esto por cada cliente potencial y cada anuncio te deja ganancia. Paga más y estás comprando clientes a pérdida.</p>'),
    ('<p class="say" id="say2">Each paying customer is worth <b id="percust">$60</b> in profit to you, so aim to pay about half your limit per lead. That leaves room for the slow weeks.</p>',
     '<p class="say" id="say2">Cada cliente que paga te deja <b id="percust">$60</b> de ganancia, así que trata de pagar más o menos la mitad de tu límite por cliente potencial. Eso te deja espacio para las semanas lentas.</p>'),
    ('<li>Per lead now <b id="cpl">', '<li>Por cliente potencial ahora <b id="cpl">'),
    ('<li>Per customer now <b id="cpc">', '<li>Por cliente ahora <b id="cpc">'),
    ('<li>Customers from ads <b id="custs">0</b>/mo</li>', '<li>Clientes de anuncios <b id="custs">0</b>/mes</li>'),
    ('<li id="netRow">Ads net you <b id="net">$0</b>/mo</li>', '<li id="netRow">Los anuncios te dejan <b id="net">$0</b>/mes</li>'),
    ("$('eyebrow').textContent = 'Your limit per lead';", "$('eyebrow').textContent = 'Tu límite por cliente potencial';"),
    ("$('per').textContent = 'the most one call or message can cost you';", "$('per').textContent = 'lo máximo que te puede costar una llamada o un mensaje';"),
    ("$('say').innerHTML = 'Pay less than this for each lead and every ad you run makes money. Pay more and you’re buying customers at a loss.';",
     "$('say').innerHTML = 'Paga menos que esto por cada cliente potencial y cada anuncio te deja ganancia. Paga más y estás comprando clientes a pérdida.';"),
    ("$('say2').innerHTML = 'Each paying customer is worth <b>' + money(perCust) + '</b> in profit to you, so aim to pay about half your limit per lead. That leaves room for the slow weeks.';",
     "$('say2').innerHTML = 'Cada cliente que paga te deja <b>' + money(perCust) + '</b> de ganancia, así que trata de pagar más o menos la mitad de tu límite por cliente potencial. Eso te deja espacio para las semanas lentas.';"),
    ("$('eyebrow').textContent = net >= 0 ? 'Your ads make you' : 'Your ads cost you';", "$('eyebrow').textContent = net >= 0 ? 'Tus anuncios te dejan' : 'Tus anuncios te cuestan';"),
    ("$('per').textContent = net >= 0 ? 'in profit every month, after the ad spend' : 'every month, more than they bring in';",
     "$('per').textContent = net >= 0 ? 'de ganancia cada mes, después de pagar los anuncios' : 'cada mes, más de lo que te traen';"),
    ("$('say').innerHTML = 'You’re paying <b>' + money(cpl) + '</b> a lead against a <b>' + money(perLead) + '</b> limit. Usually that means the wrong people are seeing the ad, or the offer isn’t clear enough to act on. Both are fixable.';",
     "$('say').innerHTML = 'Estás pagando <b>' + money(cpl) + '</b> por cliente potencial con un límite de <b>' + money(perLead) + '</b>. Casi siempre eso quiere decir que el anuncio le llega a la gente equivocada, o que la oferta no está tan clara como para actuar. Las dos cosas tienen arreglo.';"),
    ("$('say').innerHTML = 'Profitable, but thin: <b>' + money(cpl) + '</b> a lead against a <b>' + money(perLead) + '</b> limit. One slow month or a price bump and this turns negative. Tighter targeting usually brings the lead cost down.';",
     "$('say').innerHTML = 'Deja ganancia, pero poca: <b>' + money(cpl) + '</b> por cliente potencial con un límite de <b>' + money(perLead) + '</b>. Un mes lento o una subida de precio y esto pasa a pérdida. Afinar a quién le llega el anuncio casi siempre baja ese costo.';"),
    ("$('say').innerHTML = 'Your ads pay for themselves: <b>' + money(cpl) + '</b> a lead against a <b>' + money(perLead) + '</b> limit. The question now is how much more you can spend and keep that number.';",
     "$('say').innerHTML = 'Tus anuncios se pagan solos: <b>' + money(cpl) + '</b> por cliente potencial con un límite de <b>' + money(perLead) + '</b>. Ahora la pregunta es cuánto más puedes gastar sin que suba ese número.';"),
], 'es/calculadora')
es = suball(es, '<a class="btn" href="/start/?service=ads&amp;offer=free">Get a free ad check <span aria-hidden="true">→</span></a>',
            '<a class="btn" href="/es/empezar/?service=ads&amp;offer=free">Revisa tus anuncios gratis <span aria-hidden="true">→</span></a>', 2, 'es/calculadora')
es = suball(es, '<p class="fine" style="display:block">An estimate from your numbers, not a promise. Ad costs move with the season and what you sell.</p>',
            '<p class="fine" style="display:block">Un estimado con tus números, no una promesa. El costo de los anuncios cambia con la temporada y con lo que vendes.</p>', 1, 'es/calculadora')
es = suball(es, '<p class="fine">An estimate from your numbers, not a promise. Ad costs move with the season and what you sell.</p>',
            '<p class="fine">Un estimado con tus números, no una promesa. El costo de los anuncios cambia con la temporada y con lo que vendes.</p>', 1, 'es/calculadora')
be_top_es = [('<a href="/es/#contact">Contacto</a></nav>', '<a href="/es/#contact">Contacto</a>PILL</nav>')]
es = common(es, EN, ES, True, '<meta property="og:type"', be_css, be_top_es, 'es/calculadora')
wr('es/calculadora/index.html', es)
en = common(src2, EN, ES, False, '<meta property="og:type"', be_css, be_top, 'break-even')
wr('break-even/index.html', en)

# ---------------------------------------------------------------- SITEMAP
sm = rd('sitemap.xml')
line = '  <url><loc>https://twincitys.net/check/</loc><priority>0.8</priority></url>\n'
add = ''.join(line.replace('/check/', p) for p in ['/es/empezar/', '/es/chequeo/', '/es/calculadora/'])
sm = sub(sm, [('</urlset>', add + '</urlset>')], 'sitemap')
wr('sitemap.xml', sm)
print('ok')
