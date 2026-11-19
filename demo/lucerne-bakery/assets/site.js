(function () {
  var body = document.body;

  function setLang(l) {
    body.classList.toggle('es', l === 'es');
    document.documentElement.lang = l === 'es' ? 'es' : 'en';
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.lang === l));
    });
    try { localStorage.setItem('lucerne-lang', l); } catch (e) {}
    renderTime();
  }
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.lang); });
  });

  var HOURS = [[6, 13], [5, 13], [5, 13], [5, 13], [5, 13], [5, 13], [5, 13]];
  var DAYS = {
    en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    es: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
  };
  function fmt(h) { return h === 13 ? '1:00 PM' : (h < 12 ? h + ':00 AM' : (h - 12) + ':00 PM'); }
  function short(h) { return h === 13 ? '1 PM' : h + ' AM'; }
  function miami() {
    var parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'short', hour: 'numeric', minute: '2-digit', hour12: false }).formatToParts(new Date());
    var g = function (t) { return parts.find(function (p) { return p.type === t; }).value; };
    return { wd: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(g('weekday')), h: +g('hour') % 24, m: +g('minute') };
  }

  function renderTime() {
    var L = body.classList.contains('es') ? 'es' : 'en', t = miami(), o = HOURS[t.wd][0], c = HOURS[t.wd][1], now = t.h + t.m / 60;
    var open = now >= o && now < c;
    document.querySelectorAll('[data-status]').forEach(function (el) {
      var msg;
      if (open) msg = L === 'en' ? 'Open until 1 PM' : 'Abierto hasta la 1 PM';
      else {
        var next = now < o ? t.wd : (t.wd + 1) % 7;
        msg = L === 'en' ? 'Opens at ' + short(HOURS[next][0]) : 'Abre a las ' + short(HOURS[next][0]);
      }
      el.textContent = msg;
      var box = el.closest('[data-status-box]'); if (box) box.classList.toggle('closed', !open);
    });
    document.querySelectorAll('[data-hours]').forEach(function (tb) {
      tb.innerHTML = '';
      [[1, 2, 3, 4, 5, 6], [0]].forEach(function (g) {
        var tr = document.createElement('tr');
        if (g.indexOf(t.wd) >= 0) tr.className = 'today';
        var label = g.length > 1 ? (L === 'en' ? 'Mon – Sat' : 'Lun – Sáb') : DAYS[L][0];
        tr.innerHTML = '<td>' + label + '</td><td>' + fmt(HOURS[g[0]][0]) + ' – ' + fmt(HOURS[g[0]][1]) + '</td>';
        tb.appendChild(tr);
      });
    });
  }

  var copy = document.querySelector('[data-copy]');
  if (copy) copy.addEventListener('click', function () {
    var L = body.classList.contains('es');
    var done = function () { copy.textContent = L ? 'Copiado' : 'Copied'; setTimeout(function () { copy.textContent = L ? 'Copiar' : 'Copy'; }, 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText('(305) 986-1507').then(done, function () {}); else done();
  });

  var saved = null;
  try { saved = localStorage.getItem('lucerne-lang'); } catch (e) {}
  setLang(saved || ((navigator.language || '').toLowerCase().indexOf('es') === 0 ? 'es' : 'en'));
  setInterval(renderTime, 60000);
})();
