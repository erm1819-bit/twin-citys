/* Twin Citys concept page templates. Used by the demo builder and by Node (module.exports). */
(function (root) {
  var NICHES = {
    restaurant: {
      label: 'Restaurant / café / bakery',
      kind: 'Cuban restaurant',
      action: 'order',
      locked: ['Full menu', 'Order online', 'Reservations', 'Catering', 'Reviews', 'Gift cards'],
      slots: ['Hero', 'Dish 1', 'Dish 2', 'Dish 3', 'Inside'],
      dishesTitle: 'What people order',
      tagline: 'The plate the whole neighborhood talks about.',
      about: 'Family-run, made fresh every morning, and the same recipes since day one. Come in hungry.'
    }
  };

  var FONTS = {
    classic: { label: 'Classic', head: "'Playfair Display',Georgia,serif", body: "'Inter',system-ui,sans-serif", url: 'Playfair+Display:wght@500;700&family=Inter:wght@300;400;500;600', headWeight: 500 },
    warm: { label: 'Warm', head: "'Fraunces',Georgia,serif", body: "'Inter',system-ui,sans-serif", url: 'Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@300;400;500;600', headWeight: 400 },
    modern: { label: 'Modern', head: "'DM Sans',system-ui,sans-serif", body: "'DM Sans',system-ui,sans-serif", url: 'DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,700', headWeight: 500 },
    bold: { label: 'Bold', head: "'Oswald',Impact,sans-serif", body: "'Inter',system-ui,sans-serif", url: 'Oswald:wght@500;600&family=Inter:wght@300;400;500;600', headWeight: 600, upper: true }
  };

  var ACTIONS = {
    order: { label: 'Order online', btn: 'Order now' },
    call: { label: 'Call', btn: 'Call us' },
    book: { label: 'Reserve a table', btn: 'Reserve a table' },
    visit: { label: 'Come in / directions', btn: 'Get directions' }
  };

  var CONTACTS = {
    eric: ['Eric Martinez', '(305) 767-6128', 'eric@twincitys.net'],
    kevin: ['Kevin Butchers', '(305) 986-6414', 'k.butchers@twincitys.net'],
    daniel: ['Daniel Navarro', '(786) 478-2150', 'daniel@twincitys.net']
  };

  /* color helpers */
  function hexToRgb(h) { h = (h || '#8a5a3c').replace('#', ''); if (h.length === 3) h = h.replace(/./g, '$&$&'); var n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function rgbToHex(c) { return '#' + c.map(function (v) { v = Math.max(0, Math.min(255, Math.round(v))); return (v < 16 ? '0' : '') + v.toString(16); }).join(''); }
  function mix(a, b, t) { a = hexToRgb(a); b = hexToRgb(b); return rgbToHex(a.map(function (v, i) { return v + (b[i] - v) * t; })); }
  function lum(h) { return hexToRgb(h).map(function (v) { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }).reduce(function (s, v, i) { return s + v * [.2126, .7152, .0722][i]; }, 0); }
  function contrast(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function readable(accent, bg, toward) { var c = accent, i = 0; while (contrast(c, bg) < 4.5 && i < 20) { c = mix(c, toward, .12); i++; } return c; }

  function theme(t) {
    t = t || {};
    var accent = /^#[0-9a-f]{6}$/i.test(t.accent || '') ? t.accent : '#b5562f';
    var dark = t.mode !== 'light';
    var text = dark ? '#f4efe7' : '#1c1915';
    var bg = dark ? mix(accent, '#0d0c0b', .9) : mix(accent, '#fbf8f3', .94);
    return {
      accent: accent, dark: dark, text: text, bg: bg,
      surface: dark ? mix(accent, '#0d0c0b', .8) : mix(accent, '#fbf8f3', .86),
      muted: dark ? 'rgba(244,239,231,.68)' : 'rgba(28,25,21,.66)',
      line: dark ? 'rgba(244,239,231,.14)' : 'rgba(28,25,21,.14)',
      accentText: readable(accent, bg, text),
      onAccent: contrast(accent, '#ffffff') >= contrast(accent, '#111111') ? '#ffffff' : '#111111',
      font: FONTS[t.font] || FONTS.classic
    };
  }

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function slug(s) { return (s || 'business-name').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'business-name'; }
  function lines(s) { return String(s || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean); }
  function telHref(p) { return 'tel:' + String(p || '').replace(/[^\d+]/g, ''); }
  function mapHref(a) { return 'https://maps.google.com/?q=' + encodeURIComponent(a); }
  function igHref(h) { return 'https://instagram.com/' + String(h || '').replace(/^@/, '').replace(/^https?:\/\/(www\.)?instagram\.com\//, '').replace(/\/$/, ''); }

  /* "Name — note — $12" per line */
  function parseDishes(s) {
    return lines(s).slice(0, 3).map(function (l) {
      var p = l.split(/\s+[—–|-]\s+/);
      var price = p.length > 1 && /\$|\d/.test(p[p.length - 1]) && p[p.length - 1].length < 10 ? p.pop() : '';
      return { name: p[0] || '', note: p.slice(1).join(' — '), price: price };
    });
  }

  /* Pull phone, address and hours out of text copied from a Google listing */
  function parseListing(text) {
    var out = {}, t = String(text || '');
    var ph = t.match(/\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/); if (ph) out.phone = ph[0].replace(/^\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})$/, '($1) $2-$3');
    var ad = t.match(/\d{2,6}\s+[^\n,]+,\s*[^\n,]+,\s*FL\s*\d{5}/i) || t.match(/\d{2,6}\s+[^\n]+FL\s*\d{5}/i); if (ad) out.address = ad[0].replace(/\s+/g, ' ').trim();
    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], hrs = [];
    days.forEach(function (d) {
      var m = t.match(new RegExp(d + '\\s*[:\\t]?\\s*([^\\n]*?(?:Closed|Open 24 hours|\\d{1,2}(?::\\d{2})?\\s*[AP]M\\s*[–-]\\s*\\d{1,2}(?::\\d{2})?\\s*[AP]M(?:,\\s*\\d{1,2}(?::\\d{2})?\\s*[AP]M\\s*[–-]\\s*\\d{1,2}(?::\\d{2})?\\s*[AP]M)?))', 'i'));
      if (m) hrs.push([d.slice(0, 3), m[1].replace(/\s+/g, ' ').replace(/ /g, ' ').trim()]);
    });
    if (hrs.length) {
      var grouped = [];
      hrs.forEach(function (h) { var g = grouped[grouped.length - 1]; if (g && g.v === h[1]) g.to = h[0]; else grouped.push({ from: h[0], to: h[0], v: h[1] }); });
      out.hours = grouped.map(function (g) { return (g.from === g.to ? g.from : g.from + '–' + g.to) + '  ' + g.v; }).join('\n');
    }
    var ig = t.match(/instagram\.com\/([A-Za-z0-9._]+)/i) || t.match(/(^|\s)@([A-Za-z0-9._]{3,})/); if (ig) out.ig = '@' + (ig[2] || ig[1]);
    return out;
  }

  function primaryAction(d) {
    var a = d.action || 'order', A = ACTIONS[a] || ACTIONS.order;
    if (a === 'order' && d.orderUrl) return { href: d.orderUrl, label: A.btn, ext: true };
    if (a === 'book' && d.orderUrl) return { href: d.orderUrl, label: A.btn, ext: true };
    if (a === 'visit' && d.address) return { href: mapHref(d.address), label: A.btn, ext: true };
    if (d.phone) return { href: telHref(d.phone), label: a === 'call' ? 'Call us' : A.btn };
    return { href: '#visit', label: A.btn };
  }

  function restaurant(d) {
    var N = NICHES.restaurant, T = theme(d.theme), F = T.font, P = d.photos || {};
    var name = d.name || 'Your Restaurant', kind = d.kind || N.kind, area = d.area || 'Miami, FL';
    var tagline = d.tagline || N.tagline, about = d.about || N.about;
    var dishes = parseDishes(d.dishes); while (dishes.length < 3) dishes.push({ name: ['House special', 'The one everyone orders', 'Something sweet'][dishes.length], note: '', price: '' });
    var dishPh = P.dishes || [];
    var hours = lines(d.hours), locked = (d.locked || []).filter(Boolean).slice(0, 8);
    var act = primaryAction(d), O = d.offer || {};
    var who = (O.who === 'all' ? ['eric', 'kevin', 'daniel'] : [O.who || 'eric']).map(function (k) { return CONTACTS[k] || CONTACTS.eric; });
    var second = d.address && d.action !== 'visit' ? { href: mapHref(d.address), label: 'Directions', ext: true } : d.phone && d.action !== 'call' ? { href: telHref(d.phone), label: 'Call us' } : null;
    function link(a, cls) { return '<a class="' + cls + '" href="' + esc(a.href) + '"' + (a.ext ? ' target="_blank" rel="noopener"' : '') + '>' + esc(a.label) + '</a>'; }
    var up = F.upper ? 'text-transform:uppercase;letter-spacing:.01em;' : '';

    var css = [
      ':root{color-scheme:' + (T.dark ? 'dark' : 'light') + ';--bg:' + T.bg + ';--surface:' + T.surface + ';--text:' + T.text + ';--muted:' + T.muted + ';--line:' + T.line + ';--accent:' + T.accent + ';--accent-text:' + T.accentText + ';--on-accent:' + T.onAccent + ';--head:' + F.head + ';--body:' + F.body + ';--tc:"Montserrat","Helvetica Neue",Arial,sans-serif;--ease:cubic-bezier(.3,.7,.2,1)}',
      '*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:400 16px/1.6 var(--body);-webkit-font-smoothing:antialiased}h1,h2,h3,p{margin:0}a{color:inherit;text-decoration:none}img{display:block;max-width:100%}',
      '.wrap{width:min(100%,1160px);margin:0 auto;padding:0 clamp(16px,4vw,40px)}',
      '.ribbon{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:9px clamp(16px,4vw,40px);background:rgba(11,11,11,.9);backdrop-filter:blur(12px);color:#a19b90;font:500 10px var(--tc);letter-spacing:.28em;text-transform:uppercase}.ribbon b{display:inline-flex;align-items:center;gap:10px;color:#e8e3d9;font-weight:500}.ribbon svg{width:20px;height:17px;fill:currentColor}.ribbon a{color:#e8e3d9;border-bottom:1px solid #4a4743}',
      '.hero{position:relative;min-height:min(92vh,900px);display:grid;align-items:end;overflow:hidden;isolation:isolate;padding:clamp(96px,14vw,160px) 0 clamp(40px,6vw,72px)}.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2;animation:drift 20s var(--ease) both}.hero::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(to top,var(--bg) 2%,color-mix(in srgb,var(--bg) 62%,transparent) 42%,color-mix(in srgb,var(--bg) 12%,transparent) 100%)}.hero.plain{background:radial-gradient(ellipse at 70% 10%,var(--surface),var(--bg) 70%)}@keyframes drift{from{transform:scale(1.1)}to{transform:scale(1.02)}}',
      '.logo{height:clamp(48px,7vw,76px);width:auto;margin-bottom:22px;object-fit:contain}.kick{font:500 12px var(--body);letter-spacing:.24em;text-transform:uppercase;color:var(--accent-text);margin-bottom:16px}',
      '.hero h1{font:' + F.headWeight + ' clamp(46px,9.5vw,128px)/.95 var(--head);' + up + 'max-width:12ch;text-wrap:balance}.hero p.tag{margin-top:20px;max-width:40ch;font-size:clamp(17px,1.8vw,22px);font-weight:300}.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}',
      '.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:0 28px;border-radius:999px;background:var(--accent);color:var(--on-accent);font:600 15px var(--body);border:1px solid var(--accent);transition:transform .25s var(--ease),filter .25s}.btn:hover{transform:translateY(-1px);filter:brightness(1.06)}.btn.ghost{background:transparent;color:var(--text);border-color:var(--line)}',
      '.strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.strip div{padding:22px 24px 22px 0}.strip div+div{padding-left:24px;border-left:1px solid var(--line)}.strip span{display:block;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}.strip p{font-size:16px}',
      'section.wrap{padding-top:clamp(64px,10vw,128px);padding-bottom:clamp(64px,10vw,128px)}#visit{padding-top:0}.h2{font:' + F.headWeight + ' clamp(32px,4.6vw,60px)/1.04 var(--head);' + up + 'text-wrap:balance}.sub{color:var(--muted);margin-top:12px;max-width:52ch}',
      '.dishes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(14px,2vw,24px);margin-top:clamp(28px,4vw,48px)}.dish .ph{aspect-ratio:4/5;border-radius:18px;overflow:hidden;background:var(--surface)}.dish .ph img{width:100%;height:100%;object-fit:cover;transition:transform .8s var(--ease)}.dish:hover .ph img{transform:scale(1.04)}.dish .row{display:flex;justify-content:space-between;gap:12px;align-items:baseline;margin-top:16px}.dish h3{font:' + F.headWeight + ' clamp(20px,2vw,26px)/1.15 var(--head);' + up + '}.dish b{color:var(--accent-text);font-weight:600;white-space:nowrap}.dish p{color:var(--muted);margin-top:6px;font-size:15px}',
      '.empty{width:100%;height:100%;display:grid;place-items:center;color:var(--muted);font-size:12px;letter-spacing:.2em;text-transform:uppercase}',
      '.about{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(28px,6vw,88px);align-items:center}.about .ph{aspect-ratio:5/6;border-radius:22px;overflow:hidden;background:var(--surface)}.about .ph img{width:100%;height:100%;object-fit:cover}.about p.body{font-size:clamp(17px,1.6vw,20px);font-weight:300;margin-top:22px;max-width:44ch}.about .ig{display:inline-block;margin-top:24px;color:var(--accent-text);font-weight:500;border-bottom:1px solid currentColor}',
      '.visit{background:var(--surface);border-radius:28px;padding:clamp(28px,5vw,64px);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:clamp(28px,5vw,64px)}.hrs{margin-top:26px;display:grid;gap:10px}.hrs div{display:flex;justify-content:space-between;gap:16px;padding-bottom:10px;border-bottom:1px solid var(--line);font-size:15px}.hrs div span:first-child{color:var(--muted)}.addr{margin-top:26px;font-size:17px}.visit .cta{margin-top:24px}.map{border-radius:18px;overflow:hidden;min-height:320px;background:var(--bg)}.map iframe{width:100%;height:100%;min-height:320px;border:0;display:block' + (T.dark ? ';filter:grayscale(.4) invert(.9) hue-rotate(180deg) contrast(.9)' : '') + '}',
      '.tc{font-family:var(--tc);background:#0b0b0b;color:#e8e3d9}.tc .wrap{padding-top:clamp(56px,8vw,96px);padding-bottom:clamp(40px,6vw,64px)}.tc .k{font-size:10px;letter-spacing:.4em;text-transform:uppercase;color:#a19b90;margin-bottom:14px}',
      '.locked{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:clamp(40px,6vw,64px)}.locked div{position:relative;border:1px dashed #4a4743;padding:22px 16px 18px;color:#77726b;font-weight:300;font-size:17px;line-height:1.2}.locked div::before{content:"";position:absolute;top:12px;right:12px;width:10px;height:13px;border:1.5px solid #4a4743;border-radius:3px 3px 1px 1px;box-shadow:inset 0 -6px 0 #4a4743}.locked span{display:block;margin-top:8px;font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:#4a4743}',
      '.offer{border:1px solid #e8e3d9;padding:clamp(28px,5vw,56px);display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:32px;align-items:center}.offer h2{font-weight:300;font-size:clamp(26px,3.4vw,44px);line-height:1.1}.offer h2 em{font-style:normal;font-weight:500;color:#fff}.offer p{color:#a19b90;margin-top:14px;max-width:46ch}.offer .code{display:grid;gap:12px}.offer .code div{border:1px solid rgba(232,227,217,.18);padding:14px 18px}.offer .code span{display:block;color:#a19b90;font-size:10px;letter-spacing:.34em;text-transform:uppercase;margin-bottom:4px}.offer .code b{font-weight:500;font-size:clamp(20px,2.4vw,28px);letter-spacing:.06em}.who{display:flex;flex-wrap:wrap;gap:18px 36px;margin-top:22px;font-size:14px;color:#a19b90}.who b{display:block;color:#e8e3d9;font-weight:500}.tcbtn{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:0 28px;background:#e8e3d9;color:#0b0b0b;font:500 11px var(--tc);letter-spacing:.3em;text-transform:uppercase;text-indent:.3em}',
      '.tc footer{display:flex;justify-content:space-between;gap:16px;margin-top:clamp(40px,6vw,64px);padding-top:24px;border-top:1px solid rgba(232,227,217,.18);color:#4a4743;font-size:10px;letter-spacing:.3em;text-transform:uppercase}',
      '.bar{display:none}.bar .ghost{background:var(--bg)}',
      '@media(max-width:820px){.strip{grid-template-columns:1fr}.strip div{padding:16px 0}.strip div+div{padding-left:0;border-left:0;border-top:1px solid var(--line)}.dishes{grid-template-columns:1fr}.dish .ph{aspect-ratio:4/3}.about,.visit,.offer{grid-template-columns:1fr}.about .ph{aspect-ratio:4/3}.tc footer{flex-direction:column}.ribbon span{display:none}',
      '.bar{display:flex;gap:10px;position:fixed;left:12px;right:12px;bottom:12px;z-index:30}.bar a{flex:1;min-height:52px}body{padding-bottom:76px}}',
      '@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}'
    ].join('\n');

    function photo(src, alt, label) { return src ? '<img src="' + src + '" alt="' + esc(alt) + '" loading="lazy">' : '<div class="empty">' + esc(label) + '</div>'; }

    return '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex, nofollow">\n<title>' + esc(name) + ' · concept by Twin Citys</title>\n<meta name="theme-color" content="' + T.bg + '">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=' + F.url + '&family=Montserrat:wght@300;400;500&display=swap">\n<style>\n' + css + '\n</style>\n</head>\n<body>\n' +
      '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="tc" viewBox="0 0 892 756"><polygon points="0,0 70,96 280,97 280,632 407,742 407,1"/><polygon points="892,0 463,1 463,756 802,581 582,580 582,97 813,96"/></symbol></svg>\n' +
      '<div class="ribbon"><b><svg><use href="#tc"/></svg>A concept for ' + esc(name) + '</b><span>Made by <a href="https://twincitys.net/">Twin Citys</a> · <a href="#offer">see your offer</a></span></div>\n' +
      '<header class="hero' + (P.hero ? '' : ' plain') + '">' + (P.hero ? '<img src="' + P.hero + '" alt="">' : '') + '<div class="wrap">' + (P.logo ? '<img class="logo" src="' + P.logo + '" alt="' + esc(name) + ' logo">' : '') + '<p class="kick">' + esc(kind) + ' · ' + esc(area) + '</p><h1>' + esc(name) + '</h1><p class="tag">' + esc(tagline) + '</p><div class="cta">' + link(act, 'btn') + (second ? link(second, 'btn ghost') : '') + '</div></div></header>\n' +
      '<div class="wrap"><div class="strip"><div><span>Hours</span><p>' + esc(hours[0] || 'Open daily') + '</p></div><div><span>Find us</span><p>' + esc(d.address || area) + '</p></div><div><span>Call</span><p>' + (d.phone ? '<a href="' + telHref(d.phone) + '">' + esc(d.phone) + '</a>' : 'Your number') + '</p></div></div></div>\n' +
      '<main>\n<section class="wrap" id="menu"><h2 class="h2">' + esc(N.dishesTitle) + '</h2><p class="sub">A few favorites. The full menu comes with the finished site.</p><div class="dishes">' +
      dishes.map(function (x, i) { return '<article class="dish"><div class="ph">' + photo(dishPh[i], x.name, 'Dish photo') + '</div><div class="row"><h3>' + esc(x.name) + '</h3>' + (x.price ? '<b>' + esc(x.price) + '</b>' : '') + '</div>' + (x.note ? '<p>' + esc(x.note) + '</p>' : '') + '</article>'; }).join('') + '</div></section>\n' +
      '<section class="wrap about" id="about"><div class="ph">' + photo(P.about, 'Inside ' + name, 'Inside photo') + '</div><div><p class="kick">Our story</p><h2 class="h2">' + esc(name) + '</h2><p class="body">' + esc(about) + '</p>' + (d.ig ? '<a class="ig" href="' + esc(igHref(d.ig)) + '" target="_blank" rel="noopener">' + esc(d.ig.charAt(0) === '@' ? d.ig : '@' + d.ig) + ' on Instagram</a>' : '') + '</div></section>\n' +
      '<section class="wrap" id="visit"><div class="visit"><div><p class="kick">Come by</p><h2 class="h2">Visit us</h2>' +
      (hours.length ? '<div class="hrs">' + hours.map(function (h) { var m = h.match(/^(\S+(?:\s*[–-]\s*\S+)?)\s{1,}(.+)$/); return m ? '<div><span>' + esc(m[1]) + '</span><span>' + esc(m[2]) + '</span></div>' : '<div><span>' + esc(h) + '</span></div>'; }).join('') + '</div>' : '') +
      '<p class="addr">' + esc(d.address || 'Your address') + '</p><div class="cta">' + link(act, 'btn') + (d.address ? '<a class="btn ghost" href="' + mapHref(d.address) + '" target="_blank" rel="noopener">Directions</a>' : '') + '</div></div>' +
      '<div class="map">' + (d.address ? '<iframe title="Map" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q=' + encodeURIComponent(d.address) + '&z=15&output=embed"></iframe>' : '') + '</div></div></section>\n</main>\n' +
      '<div class="tc" id="offer"><div class="wrap">' +
      (locked.length ? '<p class="k">Part of the full site</p><div class="locked">' + locked.map(function (l) { return '<div>' + esc(l) + '<span>Unlocks with the full site</span></div>'; }).join('') + '</div>' : '') +
      '<div class="offer"><div><p class="k">Like what you see?</p><h2>This is a concept. <em>The full site is yours' + (O.disc ? ' with ' + esc(O.disc) + '.' : '.') + '</em></h2><p>We built this from what you already have. The finished site adds the rest: the full menu, ordering or reservations, and every page built to look this good on a phone.' + (O.exp ? ' Your rate is good through ' + esc(O.exp) + '.' : '') + '</p><div class="who">' + who.map(function (w) { return '<div><b>' + esc(w[0]) + '</b>' + esc(w[1]) + '<br>' + esc(w[2]) + '</div>'; }).join('') + '</div></div><div class="code">' +
      (O.disc ? '<div><span>Your rate</span><b>' + esc(O.disc) + '</b></div>' : '') + (O.code ? '<div><span>Code</span><b>' + esc(O.code) + '</b></div>' : '') + (O.exp ? '<div><span>Good through</span><b>' + esc(O.exp) + '</b></div>' : '') +
      '<a class="tcbtn" href="https://twincitys.net/start">Let’s build it</a></div></div>' +
      '<footer><span>Concept by Twin Citys · Miami, FL</span><span>Design | Develop | Create</span></footer></div></div>\n' +
      '<nav class="bar">' + link(act, 'btn') + (second ? link(second, 'btn ghost') : '') + '</nav>\n' +
      '</body>\n</html>\n';
  }

  var api = { NICHES: NICHES, FONTS: FONTS, ACTIONS: ACTIONS, CONTACTS: CONTACTS, build: function (d) { return restaurant(d || {}); }, theme: theme, slug: slug, parseListing: parseListing, mix: mix, contrast: contrast };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.TCDemo = api;
})(this);
