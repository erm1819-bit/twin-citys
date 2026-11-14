"""Build the Spanish service pages (es/servicios/<slug>/) from the English ones (services/<id>/),
and add the EN/ES switch + hreflang + remembered-language redirect to both.

Run from the repo root:  python3 tools/es_services.py
Re-run it whenever an English service page changes. It prints any English text it could not find,
so new copy on the English pages shows up as a 'missing' line: add its Spanish to T below.
"""
import re, sys

SLUG = {'websites': 'paginas-web', 'ads': 'anuncios', 'content': 'fotos-y-video',
        'crm': 'seguimiento-de-clientes', 'google': 'seo-local', 'social': 'redes-sociales'}
TWIN = {'/': '/es/', '/start/': '/es/empezar/', '/check/': '/es/chequeo/', '/break-even/': '/es/calculadora/'}
TWIN.update({f'/services/{k}/': f'/es/servicios/{v}/' for k, v in SLUG.items()})

# ---------- per-page head text ----------
HEAD = {
 'websites': [
  ('Web design in Miami for small businesses · Twin Citys', 'Diseño de páginas web en Miami para pequeños negocios · Twin Citys'),
  ('Websites designed, built and launched for Miami restaurants, bakeries and small businesses. Built around your business, never a template.', 'Páginas web diseñadas, hechas y lanzadas para restaurantes, panaderías y pequeños negocios de Miami. Hechas para tu negocio, nunca una plantilla.'),
  ('"name": "Website design and development"', '"name": "Diseño y desarrollo de páginas web"'),
  ('"serviceType": "Web design"', '"serviceType": "Diseño web"'),
  ('Custom websites designed, built, launched and hosted for Miami restaurants, bakeries and local businesses. Designed around each business, never a template.', 'Páginas web a la medida, diseñadas, hechas, lanzadas y alojadas para restaurantes, panaderías y negocios locales de Miami. Diseñadas para cada negocio, nunca una plantilla.')],
 'ads': [
  ('Google Ads &amp; Facebook ads agency in Miami · Twin Citys', 'Agencia de anuncios en Google y Facebook en Miami · Twin Citys'),
  ('Google Ads & Facebook ads agency in Miami · Twin Citys', 'Agencia de anuncios en Google y Facebook en Miami · Twin Citys'),
  ('Google Ads and Facebook ad campaigns built and managed for Miami businesses, with plain reporting on what every dollar brings back.', 'Campañas de anuncios en Google y Facebook hechas y manejadas para negocios de Miami, con reportes claros de lo que te trae cada dólar.'),
  ('"name": "Meta and Google advertising management"', '"name": "Manejo de anuncios en Meta y Google"'),
  ('"serviceType": "Advertising agency service"', '"serviceType": "Servicio de agencia de publicidad"'),
  ('Facebook, Instagram and Google ad campaigns built and managed for Miami businesses, with reporting on what every dollar brings back.', 'Campañas de anuncios en Facebook, Instagram y Google hechas y manejadas para negocios de Miami, con reportes de lo que te trae cada dólar.')],
 'content': [
  ('Photo &amp; video content in Miami for small businesses · Twin Citys', 'Fotos y videos en Miami para pequeños negocios · Twin Citys'),
  ('Photo & video content in Miami for small businesses · Twin Citys', 'Fotos y videos en Miami para pequeños negocios · Twin Citys'),
  ('Photos and short video for Miami businesses that don’t have the time, or don’t know how, to make their own. Shot locally, ready for your site, socials and ads.', 'Fotos y videos cortos para negocios de Miami que no tienen tiempo, o no saben cómo hacerlos. Hechos aquí, listos para tu página, tus redes y tus anuncios.'),
  ('"name": "Photography and video production"', '"name": "Producción de fotos y video"'),
  ('"serviceType": "Commercial photography and videography"', '"serviceType": "Fotografía y video comercial"'),
  ('Photography and short-form video of your food, your work and your space, shot in Miami and delivered ready for a website, ads and social media.', 'Fotos y videos cortos de tu comida, tu trabajo y tu local, hechos en Miami y entregados listos para tu página web, tus anuncios y tus redes.')],
 'crm': [
  ('Lead follow-up &amp; CRM setup for Miami businesses · Twin Citys', 'Seguimiento de clientes y CRM para negocios de Miami · Twin Citys'),
  ('Lead follow-up & CRM setup for Miami businesses · Twin Citys', 'Seguimiento de clientes y CRM para negocios de Miami · Twin Citys'),
  ('Every call, form and message in one place, with follow-ups that send themselves. Lead tracking set up for small businesses in Miami.', 'Cada llamada, formulario y mensaje en un solo lugar, con seguimientos que se mandan solos. Hecho para pequeños negocios de Miami.'),
  ('"name": "CRM dashboard setup"', '"name": "Instalación de un panel CRM"'),
  ('"serviceType": "Customer relationship management setup"', '"serviceType": "Instalación de CRM para manejo de clientes"'),
  ('A single dashboard where calls, web forms, ad leads and social messages land, with automated follow-up, set up for small businesses in Miami.', 'Un solo panel donde llegan las llamadas, los formularios, los clientes de los anuncios y los mensajes de redes, con seguimiento automático, para pequeños negocios de Miami.')],
 'google': [
  ('Local SEO &amp; Google Business Profile in Miami · Twin Citys', 'SEO local y perfil de Google en Miami · Twin Citys'),
  ('Local SEO & Google Business Profile in Miami · Twin Citys', 'SEO local y perfil de Google en Miami · Twin Citys'),
  ('Your Google Business Profile, reviews and map listing set up so Miami customers find you first. Free profile check, no obligation.', 'Tu perfil de Google, tus reseñas y tu lugar en el mapa bien configurados para que los clientes de Miami te encuentren primero. Chequeo gratis, sin compromiso.'),
  ('"name": "Google Business Profile optimization"', '"name": "Optimización del perfil de Google"'),
  ('"serviceType": "Local search optimization"', '"serviceType": "Optimización para búsquedas locales"'),
  ('Google Business Profile setup and optimization, review generation and local search visibility for Miami businesses.', 'Configuración y optimización del perfil de Google, más reseñas y más visibilidad en búsquedas locales para negocios de Miami.')],
 'social': [
  ('Social media management in Miami · Twin Citys', 'Manejo de redes sociales en Miami · Twin Citys'),
  ('We plan, shoot, write and post your Instagram and Facebook every week, for Miami restaurants, bakeries and local shops.', 'Planeamos, grabamos, escribimos y publicamos tu Instagram y Facebook cada semana, para restaurantes, panaderías y tiendas de Miami.'),
  ('"name": "Social media management"', '"name": "Manejo de redes sociales"'),
  ('"serviceType": "Social media marketing"', '"serviceType": "Marketing en redes sociales"'),
  ('Weekly Instagram and Facebook planning, shooting, writing and posting for Miami businesses.', 'Planeación, fotos, textos y publicaciones semanales en Instagram y Facebook para negocios de Miami.')],
}

# ---------- shared text (menu, page chrome, every service's copy) ----------
T = [
('<html lang="en">', '<html lang="es">'),
# top bar
('<span>Twin Citys <em>· Web design, Miami</em></span>', '<span>Twin Citys <em>· Diseño web, Miami</em></span>'),
('aria-label="Site"><button type="button" class="bar__svc" id="svc-btn" aria-expanded="false" aria-controls="svc-menu">Services</button><a href="/#work">Work</a><a href="/#contact">Contact</a><a class="cta-sm" href="https://twincitys.net/start">Start a project</a>',
 'aria-label="Sitio"><button type="button" class="bar__svc" id="svc-btn" aria-expanded="false" aria-controls="svc-menu">Servicios</button><a href="/es/#work">Trabajos</a><a href="/es/#contact">Contacto</a><a class="cta-sm" href="/es/empezar/">Empezar<span class="cta-more">&nbsp;un proyecto</span></a>'),
('<nav class="tabs" id="tabs" aria-label="Services">', '<nav class="tabs" id="tabs" aria-label="Servicios">'),
# services menu
('<nav class="svcmenu" id="svc-menu" aria-label="Services"', '<nav class="svcmenu" id="svc-menu" aria-label="Servicios"'),
('<b>Web Design</b><span>Websites for Miami small businesses.</span>', '<b>Diseño web</b><span>Páginas web para pequeños negocios de Miami.</span>'),
('<b>Ads</b><span>Ads that bring in calls, not just clicks.</span>', '<b>Anuncios</b><span>Anuncios que traen llamadas, no solo clics.</span>'),
('<b>Photo &amp; Video</b><span>Photos and video, done for you.</span>', '<b>Fotos y video</b><span>Fotos y videos, hechos para ti.</span>'),
('<b>Lead Follow-up</b><span>Never miss a lead again.</span>', '<b>Seguimiento de clientes</b><span>Que no se te escape ningún cliente.</span>'),
('<b>Local SEO</b><span>Show up first on Google Maps.</span>', '<b>SEO local</b><span>Sal primero en Google Maps.</span>'),
('<b>Social Media</b><span>Instagram and Facebook, handled weekly.</span>', '<b>Redes sociales</b><span>Instagram y Facebook, manejados cada semana.</span>'),
('<p>Free tools</p><a href="/check/">Google check <span>Does your business look right?</span></a><a href="/break-even/">Ad break-even <span>What can you pay for a lead?</span></a>',
 '<p>Herramientas gratis</p><a href="/es/chequeo/">Chequeo de Google <span>¿Tu negocio se ve bien en Google?</span></a><a href="/es/calculadora/">Calculadora de anuncios <span>¿Cuánto puedes pagar por cliente?</span></a>'),
('>Areas we serve</a>', '>Zonas donde trabajamos</a>'),
('alt="The Twin Citys homepage: Look this good online, without lifting a finger, with the Start a project button"', 'alt="La página principal de Twin Citys con el botón para empezar un proyecto"'),
('<p>Websites for Miami small businesses.</p>', '<p>Páginas web para pequeños negocios de Miami.</p>'),
('alt="The Lucerne guava pastry, as an ad"', 'alt="El pastelito de guayaba de Lucerne, como anuncio"'),
('<span>Free</span><b>Check your ad math, free</b><i>See the most you can pay per lead before your ads lose money.</i>', '<span>Gratis</span><b>Revisa los números de tus anuncios, gratis</b><i>Mira cuánto puedes pagar por cada cliente antes de perder dinero con tus anuncios.</i>'),
('<p>Ads that bring in calls, not just clicks.</p>', '<p>Anuncios que traen llamadas, no solo clics.</p>'),
('aria-label="The drive into Miami at dusk"', 'aria-label="Llegando a Miami al atardecer"'),
('<p>Photos and video, done for you.</p>', '<p>Fotos y videos, hechos para ti.</p>'),
('aria-label="A lead list: names, where each came from, and follow-ups sent"', 'aria-label="Una lista de clientes: nombres, de dónde llegó cada uno y los seguimientos enviados"'),
('>LEADS · THIS WEEK<', '>CLIENTES · ESTA SEMANA<'), ('>14 new<', '>14 nuevos<'),
('<text x="230" y="110">Instagram DM</text><text x="230" y="160">Website form</text><text x="230" y="210">Google ad · call</text><text x="230" y="260">Meta ad</text><text x="230" y="310">Website form</text>',
 '<text x="230" y="110">Mensaje de Instagram</text><text x="230" y="160">Formulario web</text><text x="230" y="210">Anuncio de Google · llamada</text><text x="230" y="260">Anuncio de Meta</text><text x="230" y="310">Formulario web</text>'),
('>BOOKED<', '>AGENDADO<'), ('>FOLLOW-UP SENT<', '>SEGUIMIENTO<'), ('>REPLIED · 9s<', '>RESPONDIÓ · 9s<'),
('<p>Never miss a lead again.</p>', '<p>Que no se te escape ningún cliente.</p>'),
('alt="Marino Plumbing’s Google Business Profile, verified, 90% complete"', 'alt="Perfil de Google de Marino Plumbing, verificado, 90% completo"'),
('<p>Show up first on Google Maps.</p>', '<p>Sal primero en Google Maps.</p>'),
('alt="Marino Plumbing’s Instagram profile"', 'alt="Perfil de Instagram de Marino Plumbing"'),
('<p>Instagram and Facebook, handled weekly.</p>', '<p>Instagram y Facebook, manejados cada semana.</p>'),
# footer
('<a href="../../privacy/">Privacy</a>', '<a href="/privacy/">Privacidad</a>'),
('target="_blank" rel="noopener">Twin Citys on Google</a>', 'target="_blank" rel="noopener">Twin Citys en Google</a>'),
('>Serving Miami, Brickell, Coral Gables, Doral, Hialeah, Kendall, Miami Beach and Homestead</a>', '>Trabajamos en Miami, Brickell, Coral Gables, Doral, Hialeah, Kendall, Miami Beach y Homestead</a>'),

# ---------- S: the six services ----------
("tab: 'Web Design'", "tab: 'Diseño web'"),
("eyebrow: 'Website design'", "eyebrow: 'Diseño de páginas web'"),
("h1: 'Websites for Miami small businesses.'", "h1: 'Páginas web para pequeños negocios de Miami.'"),
("sub: 'Designed, built and launched for your business. We handle all of it, start to finish.'", "sub: 'Diseñadas, hechas y lanzadas para tu negocio. Nosotros nos encargamos de todo, de principio a fin.'"),
("what: 'We design and build your site from scratch around your business: your photos, your menu or services, your prices if you want them, and a way to call, book or order on every screen. Then we host it and keep it running.'",
 "what: 'Diseñamos y hacemos tu página desde cero para tu negocio: tus fotos, tu menú o tus servicios, tus precios si los quieres poner, y una forma de llamar, reservar o pedir en cada pantalla. Después la alojamos y la mantenemos funcionando.'"),
("['Customers check you on their phone first.', 'Before they call or walk in, they look you up. A site that looks as good as your place is the difference.']", "['Los clientes te buscan primero en el celular.', 'Antes de llamar o de entrar, te buscan. Una página que se vea tan bien como tu local hace la diferencia.']"),
("['It answers the questions you get all day.', 'Hours, menu, prices, where you are, how to book. Fewer calls asking, more calls buying.']", "['Contesta las preguntas que te hacen todo el día.', 'Horario, menú, precios, dónde estás, cómo reservar. Menos llamadas preguntando, más llamadas comprando.']"),
("['Google can find it.', 'Built so search engines read it: the right titles, a page for what you do, your Google profile linked.']", "['Google la puede encontrar.', 'Hecha para que los buscadores la lean: los títulos correctos, una página para lo que haces y tu perfil de Google conectado.']"),
("gets: ['Design and build, from scratch', 'Made for phones first', 'Call, book or order buttons', 'Contact or booking form to your phone', 'Hosting and updates handled', 'Google-ready from day one']",
 "gets: ['Diseño y desarrollo, desde cero', 'Hecha primero para el celular', 'Botones para llamar, reservar o pedir', 'Formulario de contacto o reservas a tu celular', 'Alojamiento y actualizaciones incluidos', 'Lista para Google desde el primer día']"),
("script: ['What a bad website costs a business', 'How we build one around yours', \"What's on every site we make\", 'How to start: one short form']", "script: []"),
("close: 'See your new homepage before you pay anything.'", "close: 'Mira tu nueva página principal antes de pagar nada.'"),

("tab: 'Ads'", "tab: 'Anuncios'"),
("eyebrow: 'Google & Facebook ads'", "eyebrow: 'Anuncios en Google y Facebook'"),
("h1: 'Ads that bring in calls, not just clicks.'", "h1: 'Anuncios que traen llamadas, no solo clics.'"),
("sub: 'We run your ads on Facebook, Instagram and Google, and show you what every dollar brings back.'", "sub: 'Manejamos tus anuncios en Facebook, Instagram y Google, y te mostramos lo que te trae cada dólar.'"),
("what: 'We make your ads and run them on Facebook, Instagram and Google. You see which ones bring you customers.'", "what: 'Hacemos tus anuncios y los manejamos en Facebook, Instagram y Google. Tú ves cuáles te traen clientes.'"),
("['Reach the people near you who are ready.', 'Ads shown to the right neighborhoods and to people already searching for what you sell.']", "['Llega a la gente cerca de ti que está lista.', 'Anuncios que se muestran en los barrios correctos y a la gente que ya está buscando lo que vendes.']"),
("['Know what you get for what you spend.', 'Calls, forms and bookings tracked back to the ad that brought them.']", "['Sabe lo que te trae lo que gastas.', 'Cada llamada, formulario y reserva conectada con el anuncio que la trajo.']"),
("['It gets better every month.', 'We test the ads, keep what works and cut what doesn’t. You don’t have to touch it.']", "['Mejora cada mes.', 'Probamos los anuncios, nos quedamos con lo que funciona y quitamos lo que no. Tú no tienes que tocar nada.']"),
("gets: ['Campaign setup on Meta and Google', 'The ad photos, videos and words', 'Tracking: pixel, calls and forms', 'Weekly checks and changes', 'A monthly report in plain words', 'One person to text with questions']",
 "gets: ['Campañas listas en Meta y Google', 'Las fotos, videos y textos de los anuncios', 'Seguimiento: píxel, llamadas y formularios', 'Revisiones y cambios cada semana', 'Un reporte mensual en palabras claras', 'Una persona a quien escribirle con tus preguntas']"),
("script: ['Why boosting a post isn’t advertising', 'How we pick who sees your ads', 'How you’ll know it’s working', 'What the first month looks like']", "script: []"),
("close: 'Tell us about your business and we’ll show you where the customers are.'", "close: 'Cuéntanos de tu negocio y te mostramos dónde están los clientes.'"),

("tab: 'Photo & Video'", "tab: 'Fotos y video'"),
("eyebrow: 'Photo & video'", "eyebrow: 'Fotos y video'"),
("h1: 'Photos and video, done for you.'", "h1: 'Fotos y videos, hechos para ti.'"),
("sub: 'For businesses that don’t have the time, or don’t know how, to make their own. Your food, your products, your work and your space, ready for your site, ads and socials.'", "sub: 'Para negocios que no tienen tiempo, o no saben cómo hacerlos. Tu comida, tus productos, tu trabajo y tu local, listos para tu página, tus anuncios y tus redes.'"),
("what: 'We shoot your business the way customers see it at its best: dishes, products, the room, the team, the work being done. Then we cut it into photos and short films sized for every place you post them.'",
 "what: 'Fotografiamos tu negocio como lo ven los clientes en su mejor momento: los platos, los productos, el local, el equipo, el trabajo hecho. Después lo editamos en fotos y videos cortos del tamaño justo para cada lugar donde los publicas.'"),
("['Phone photos don’t sell.', 'Good pictures are the first reason someone picks you over the place next door.']", "['Las fotos del celular no venden.', 'Las buenas fotos son la primera razón por la que alguien te escoge a ti y no al de al lado.']"),
("['One shoot fills months of posts.', 'A single session gives you stills, reels and ad footage to use everywhere.']", "['Una sesión llena meses de posts.', 'Con una sola sesión tienes fotos, reels y videos para anuncios para usar en todas partes.']"),
("['It makes your ads cheaper.', 'Ads with strong photos and video get more clicks for the same money.']", "['Tus anuncios salen más baratos.', 'Los anuncios con buenas fotos y videos consiguen más clics por el mismo dinero.']"),
("gets: ['A planned shoot at your business', 'Edited photos, ready to post', 'Short films for reels and ads', 'Every size: site, feed, story, ad', 'Yours to use anywhere', 'Shot around your hours']",
 "gets: ['Una sesión planeada en tu negocio', 'Fotos editadas, listas para publicar', 'Videos cortos para reels y anuncios', 'Todos los tamaños: página, feed, historia, anuncio', 'Tuyas para usar donde quieras', 'Hechas en tu horario']"),
("proof: [['Lucerne Bakery · the guava pastry film', '/#work'], ['La Vasca · dish films', '/#work']]", "proof: [['Lucerne Bakery · el video del pastelito de guayaba', '/es/#work'], ['La Vasca · videos de platos', '/es/#work']]"),
("script: ['Show the Lucerne film', 'What we shoot and how long it takes', 'What you get back and when', 'Where it gets used']", "script: []"),
("close: 'Let’s make your place look the way it feels.'", "close: 'Hagamos que tu local se vea como se siente.'"),

("tab: 'Lead Follow-up'", "tab: 'Seguimiento de clientes'"),
("eyebrow: 'Lead follow-up & CRM'", "eyebrow: 'Seguimiento de clientes y CRM'"),
("h1: 'Never miss a lead again.'", "h1: 'Que no se te escape ningún cliente.'"),
("sub: 'Calls, forms and messages land on one dashboard, with follow-ups that send themselves.'", "sub: 'Las llamadas, los formularios y los mensajes llegan a un solo panel, con seguimientos que se mandan solos.'"),
("what: 'A simple dashboard, on your phone and computer, where every lead lands: website forms, ad leads, Instagram and Facebook messages. Each one shows where it came from and what happened next, and follow-up texts or emails go out on their own.'",
 "what: 'Un panel sencillo, en tu celular y en tu computadora, donde llega cada cliente: formularios de la página, clientes de los anuncios y mensajes de Instagram y Facebook. Cada uno muestra de dónde vino y qué pasó después, y los mensajes o emails de seguimiento salen solos.'"),
("['No more leads lost in a text thread.', 'Everyone who reaches out is in one list, with a reminder if nobody answered.']", "['Ningún cliente perdido en un chat.', 'Todos los que te escriben quedan en una lista, con un recordatorio si nadie contestó.']"),
("['Follow-up happens even when you’re busy.', 'An automatic reply in seconds, and a nudge later if they haven’t booked.']", "['El seguimiento pasa aunque estés ocupado.', 'Una respuesta automática en segundos, y un recordatorio después si no han reservado.']"),
("['See what actually brings customers.', 'Which ad, page or post each customer came from, in one view.']", "['Mira qué te trae clientes de verdad.', 'De qué anuncio, página o post vino cada cliente, todo en una vista.']"),
("gets: ['Dashboard set up for your business', 'Your forms, ads and DMs connected', 'Automatic replies and follow-ups', 'Lead source on every customer', 'Works on your phone', 'We train you and your team']",
 "gets: ['Un panel hecho para tu negocio', 'Tus formularios, anuncios y mensajes conectados', 'Respuestas y seguimientos automáticos', 'De dónde vino cada cliente', 'Funciona en tu celular', 'Te enseñamos a ti y a tu equipo']"),
("script: ['How many leads a business loses without one', 'Walk through the dashboard on screen', 'What follows up on its own', 'How long setup takes']", "script: []"),
("close: 'Stop losing customers you already paid to get.'", "close: 'Deja de perder clientes que ya pagaste por conseguir.'"),

("tab: 'Local SEO'", "tab: 'SEO local'"),
("eyebrow: 'Google Business Profile'", "eyebrow: 'Perfil de Google'"),
("h1: 'Show up first on Google Maps.'", "h1: 'Sal primero en Google Maps.'"),
("sub: 'Your Google profile, your reviews and your site set up so you’re the one they find.'", "sub: 'Tu perfil de Google, tus reseñas y tu página bien configurados para que te encuentren a ti.'"),
("what: 'We set up and look after your Google Business Profile, help you collect reviews with our Google review cards, and build your site so Google understands it: a page for each thing you do and each area you serve.'",
 "what: 'Configuramos y cuidamos tu perfil de Google, te ayudamos a conseguir reseñas con nuestras tarjetas de reseñas de Google, y hacemos tu página para que Google la entienda: una página para cada cosa que haces y cada zona donde trabajas.'"),
("['Get into the map results.', 'The three businesses on the map get most of the calls. A complete, active profile is how you get there.']", "['Entra en los resultados del mapa.', 'Los tres negocios que salen en el mapa se llevan la mayoría de las llamadas. Un perfil completo y activo es cómo llegas ahí.']"),
("['Reviews do the selling.', 'Review cards at your counter turn happy customers into stars on Google, in seconds.']", "['Las reseñas venden por ti.', 'Las tarjetas de reseñas en tu mostrador convierten a los clientes contentos en estrellas en Google, en segundos.']"),
("['Found for what you actually do.', 'A page per service and per neighborhood means a page waiting for each search.']", "['Que te encuentren por lo que haces.', 'Una página por servicio y por barrio quiere decir una página esperando cada búsqueda.']"),
("gets: ['Google Business Profile set up and managed', 'Google review cards for your counter', 'Photos, hours and posts kept current', 'Pages for each service and area', 'Titles and descriptions that match the search', 'A monthly check on where you show up']",
 "gets: ['Perfil de Google configurado y manejado', 'Tarjetas de reseñas de Google para tu mostrador', 'Fotos, horario y posts al día', 'Páginas para cada servicio y zona', 'Títulos y descripciones que coinciden con la búsqueda', 'Una revisión mensual de dónde sales']"),
("script: ['Search a business like theirs, live', 'What gets you into the map pack', 'Show a review card in hand', 'What we fix in the first month']", "script: []"),
("close: 'Be the first name they see.'", "close: 'Sé el primer nombre que ven.'"),

("tab: 'Social Media'", "tab: 'Redes sociales'"),
("eyebrow: 'Social media management'", "eyebrow: 'Manejo de redes sociales'"),
("h1: 'Instagram and Facebook, handled weekly.'", "h1: 'Instagram y Facebook, manejados cada semana.'"),
("sub: 'We plan it, shoot it, write it and post it. You get back to running the business.'", "sub: 'Lo planeamos, lo grabamos, lo escribimos y lo publicamos. Tú sigue manejando tu negocio.'"),
("what: 'We run your Instagram and Facebook: a monthly plan, the photos and videos, the captions, the posting, and replies to comments and messages. You approve the plan; we do the rest.'",
 "what: 'Manejamos tu Instagram y Facebook: un plan mensual, las fotos y los videos, los textos, las publicaciones y las respuestas a comentarios y mensajes. Tú apruebas el plan y nosotros hacemos el resto.'"),
("['Stay in front of your regulars.', 'People forget places that go quiet. Steady posting keeps you in their week.']", "['Mantente presente con tus clientes de siempre.', 'La gente se olvida de los lugares que se quedan callados. Publicar seguido te mantiene en su semana.']"),
("['It looks like one brand.', 'Same look, same voice, every post, instead of whatever had time that day.']", "['Se ve como una sola marca.', 'El mismo estilo y la misma voz en cada post, en vez de lo que dio tiempo ese día.']"),
("['It works with your ads.', 'Good posts become good ads, and new followers see a page worth following.']", "['Funciona con tus anuncios.', 'Los buenos posts se vuelven buenos anuncios, y los nuevos seguidores ven una página que vale la pena seguir.']"),
("gets: ['A monthly content plan you approve', 'Photos, reels and captions', 'Posting on a set schedule', 'Replies to comments and messages', 'A short recap each month', 'Ties in with your ads and site']",
 "gets: ['Un plan mensual que tú apruebas', 'Fotos, reels y textos', 'Publicaciones en un horario fijo', 'Respuestas a comentarios y mensajes', 'Un resumen corto cada mes', 'Conectado con tus anuncios y tu página']"),
("script: ['What happens when a page goes quiet', 'How a month of posts gets made', 'What you approve, what we handle', 'How to start']", "script: []"),
("close: 'Hand us the posting. Keep the customers.'", "close: 'Déjanos las publicaciones. Tú quédate con los clientes.'"),
("proof: [['La Vasca Deli Miami', '/#work'], ['Lucerne Bakery', '/#work']]", "proof: [['La Vasca Deli Miami', '/es/#work'], ['Lucerne Bakery', '/es/#work']]"),
("proof: [['La Vasca Deli Miami', '/#work']]", "proof: [['La Vasca Deli Miami', '/es/#work']]"),

# ---------- X: offers, demo steps ----------
("websites: { offer: ['Start a project', 'A site designed around your business.', 'Tell us about your business. We look into it, show you a few directions, and build the one you pick.'], badge: 'How it works', note: 'Takes about two minutes.',",
 "websites: { offer: ['Empezar un proyecto', 'Una página hecha para tu negocio.', 'Cuéntanos de tu negocio. Lo estudiamos, te mostramos algunas opciones y hacemos la que escojas.'], badge: 'Cómo funciona', note: 'Toma unos dos minutos.',"),
("steps: ['It opens with what you do', 'Your best work comes next', 'Then the details that win them over']", "steps: ['Empieza con lo que haces', 'Después tu mejor trabajo', 'Y los detalles que los convencen']"),
("nums: [['+40%', 'calls from the website'], ['2m 10s', 'average time on the menu'], ['120', 'online orders a month']]", "nums: [['+40%', 'llamadas desde la página'], ['2m 10s', 'tiempo promedio en el menú'], ['120', 'pedidos en línea al mes']]"),
("ads: { link: '/break-even/', heroBtn: 'Get a free ad check', note: 'No cost, no sign-up. Takes about ten seconds.', offer: ['Check your ad math, free', 'A free ad break-even calculator.', 'Drag three sliders and see the most you can pay per lead before your ads lose money. Already running ads? See in seconds whether they pay for themselves.'],",
 "ads: { link: '/es/calculadora/', heroBtn: 'Revisión de anuncios gratis', note: 'Gratis, sin registrarte. Toma unos diez segundos.', offer: ['Revisa los números de tus anuncios', 'Una calculadora gratis para tus anuncios.', 'Mueve tres barras y mira cuánto es lo máximo que puedes pagar por cliente antes de perder dinero con tus anuncios. ¿Ya tienes anuncios? Mira en segundos si se pagan solos.'],"),
("steps: ['Your ad reaches people nearby', 'They tap Call or Book', 'The lead lands, with the ad that brought it']", "steps: ['Tu anuncio llega a la gente cerca', 'Tocan Llamar o Reservar', 'Te llega el cliente, con el anuncio que lo trajo']"),
("nums: [['$9', 'cost per lead'], ['64', 'leads in 30 days'], ['22', 'booked from those leads']]", "nums: [['$9', 'costo por cliente'], ['64', 'clientes en 30 días'], ['22', 'citas de esos clientes']]"),
("content: { offer: ['Get free sample shots', 'A few free shots of your best seller.', 'We come by and shoot your best-selling dish or product at no cost, so you can see the difference before you book a full shoot.'],",
 "content: { offer: ['Fotos de muestra gratis', 'Unas fotos gratis de lo que más vendes.', 'Pasamos por tu negocio y fotografiamos gratis el plato o producto que más vendes, para que veas la diferencia antes de reservar una sesión completa.'],"),
("steps: ['We shoot it at your place', 'We cut it into films and stills', 'It runs on your feed, stories, site and ads']", "steps: ['Lo grabamos en tu local', 'Lo editamos en videos y fotos', 'Sale en tu feed, historias, página y anuncios']"),
("nums: [['48', 'photos from one shoot'], ['6', 'reels cut from the same day'], ['2.3×', 'more ad clicks than phone photos']]", "nums: [['48', 'fotos de una sesión'], ['6', 'reels del mismo día'], ['2.3×', 'más clics que con fotos del celular']]"),
("crm: { offer: ['Get a free lead check', 'A free check of how you answer leads.', 'We message your business the way a customer would, then show you how long it took to hear back, and what got missed.'],",
 "crm: { offer: ['Revisión de clientes gratis', 'Una revisión gratis de cómo contestas a tus clientes.', 'Le escribimos a tu negocio como lo haría un cliente, y después te mostramos cuánto tardaron en contestar y qué se quedó sin respuesta.'],"),
("steps: ['A lead comes in from anywhere', 'A reply goes out in seconds', 'Followed up until they book']", "steps: ['Llega un cliente de cualquier lado', 'Sale una respuesta en segundos', 'Seguimiento hasta que reserve']"),
("nums: [['9 sec', 'average first reply'], ['100%', 'of leads followed up'], ['−30%', 'no-shows after reminders']]", "nums: [['9 seg', 'primera respuesta promedio'], ['100%', 'de los clientes con seguimiento'], ['−30%', 'menos citas perdidas con recordatorios']]"),
("google: { link: '/check/', offer: ['Get a free Google check', 'A free check of your Google profile.', 'Look your business up the way a customer does and tick off the seven things they should see on Google. It’s yours to keep.'],",
 "google: { link: '/es/chequeo/', offer: ['Chequeo de Google gratis', 'Un chequeo gratis de tu perfil de Google.', 'Busca tu negocio como lo haría un cliente y marca las siete cosas que debería ver en Google. Es tuyo.'],"),
("steps: ['Someone nearby searches', 'Your listing shows complete, with reviews', 'You move up to where the calls are']", "steps: ['Alguien cerca te busca', 'Tu perfil sale completo, con reseñas', 'Subes a donde están las llamadas']"),
("nums: [['#1', 'on the map for the main search'], ['3,400', 'profile views a month'], ['+27', 'new Google reviews']]", "nums: [['#1', 'en el mapa para la búsqueda principal'], ['3,400', 'vistas del perfil al mes'], ['+27', 'reseñas nuevas en Google']]"),
("social: { offer: ['Get a free page review', 'A free review of your page.', 'We go through your Instagram and Facebook and send you a short list of what to fix first. Yours to keep, whether you hire us or not.'],",
 "social: { offer: ['Revisión de tu página gratis', 'Una revisión gratis de tu página.', 'Revisamos tu Instagram y Facebook y te mandamos una lista corta de lo primero que hay que arreglar. Es tuya, nos contrates o no.'],"),
("steps: ['A month of posts, planned and shot', 'Posted on schedule, without you', 'Comments and messages answered']", "steps: ['Un mes de posts, planeado y grabado', 'Publicado a tiempo, sin ti', 'Comentarios y mensajes contestados']"),
("nums: [['16', 'posts a month'], ['+60%', 'profile visits'], ['100%', 'of messages answered']]", "nums: [['16', 'posts al mes'], ['+60%', 'visitas al perfil'], ['100%', 'de los mensajes contestados']]"),

# ---------- demos ----------
("title=\"The Twin Citys homepage, playing on a phone. Touch it to scroll it yourself.\"", "title=\"La página principal de Twin Citys en un celular. Tócala para moverla tú.\""),
("<p class=\"site__hint\">Touch the phone to scroll it yourself</p>", "<p class=\"site__hint\">Toca el celular para moverlo tú</p>"),
("<iframe src=\"/?tour=1\"", "<iframe src=\"/es/?tour=1\""),
("<span><b>Your business</b><em>Sponsored</em></span><u>Call now</u>", "<span><b>Tu negocio</b><em>Patrocinado</em></span><u>Llamar</u>"),
("<div class=\"toast\"><b>New lead · phone call</b><span>From your Meta ad · just now</span></div>", "<div class=\"toast\"><b>Cliente nuevo · llamada</b><span>De tu anuncio de Meta · ahora</span></div>"),
("<span class=\"tag\" data-at=\"0\">Feed 4:5</span><span class=\"tag\" data-at=\"1\">Story 9:16</span><span class=\"tag\" data-at=\"2\">Site 16:9</span>", "<span class=\"tag\" data-at=\"0\">Feed 4:5</span><span class=\"tag\" data-at=\"1\">Historia 9:16</span><span class=\"tag\" data-at=\"2\">Página 16:9</span>"),
("<div class=\"hd\"><span>Leads · today</span><span>3 new</span></div>", "<div class=\"hd\"><span>Clientes · hoy</span><span>3 nuevos</span></div>"),
("<span>Instagram DM</span><span class=\"tag\" data-lit=\"2\">Follow-up sent</span>", "<span>Mensaje de Instagram</span><span class=\"tag\" data-lit=\"2\">Seguimiento enviado</span>"),
("<span>Website form</span><span class=\"tag lit\">Booked</span>", "<span>Formulario web</span><span class=\"tag lit\">Agendado</span>"),
("<span>Google ad · call</span><span class=\"tag\">Replied · 9s</span>", "<span>Anuncio de Google · llamada</span><span class=\"tag\">Respondió · 9s</span>"),
("<div class=\"bubble\">Thanks Maria! Here’s our booking link, any time this week works.<i>Sent automatically · 9 seconds</i></div>", "<div class=\"bubble\">¡Gracias, Maria! Aquí tienes el link para reservar, cualquier día de esta semana está bien.<i>Enviado automáticamente · 9 segundos</i></div>"),
("f.textContent = n === 2 ? 'Booked' : 'Follow-up sent';", "f.textContent = n === 2 ? 'Agendado' : 'Seguimiento enviado';"),
("text = 'plumber near me'", "text = 'plomero cerca de mí'"),
("alt=\"Marino Plumbing’s Google Business Profile: verified, 90% profile strength, 934 views, 29 interactions and 123 searches since June\"", "alt=\"El perfil de Google de Marino Plumbing: verificado, 90% completo, 934 vistas, 29 interacciones y 123 búsquedas desde junio\""),
("<div class=\"toast\"><b>934 views since June</b><span>Marino Plumbing · Google profile</span></div>", "<div class=\"toast\"><b>934 vistas desde junio</b><span>Marino Plumbing · perfil de Google</span></div>"),
("<span><b>7</b>posts</span><span><b>201</b>followers</span><span><b>177</b>following</span>", "<span><b>7</b>posts</span><span><b>201</b>seguidores</span><span><b>177</b>seguidos</span>"),
("<div class=\"badge\">Scheduled · Tue 11:00 AM</div><div class=\"toast\"><b>12 comments answered</b><span>And 4 messages · this morning</span></div>", "<div class=\"badge\">Programado · mar 11:00 AM</div><div class=\"toast\"><b>12 comentarios contestados</b><span>Y 4 mensajes · esta mañana</span></div>"),

# ---------- FAQ (JSON-LD and on-page) ----------
("How long does it take to build a website?", "¿Cuánto tiempo toma hacer una página web?"),
("Most small business sites are designed, built and live in two to four weeks. Bigger sites with booking, menus or online ordering can take a little longer, and we tell you the timeline up front.", "La mayoría de las páginas de pequeños negocios quedan diseñadas, hechas y publicadas en dos a cuatro semanas. Las más grandes, con reservas, menús o pedidos en línea, pueden tomar un poco más, y te decimos el tiempo desde el principio."),
("How much does a website cost in Miami?", "¿Cuánto cuesta una página web en Miami?"),
("It depends on how many pages you need and what the site has to do, like booking, menus or online ordering. We give you a clear number after a short call, before any work starts.", "Depende de cuántas páginas necesites y de lo que tenga que hacer la página, como reservas, menús o pedidos en línea. Te damos un precio claro después de una llamada corta, antes de empezar."),
("Do you use templates?", "¿Usan plantillas?"),
("No. Every site is designed around your business from scratch. We show you a few directions first, and build the one you pick.", "No. Cada página se diseña desde cero para tu negocio. Primero te mostramos algunas opciones y hacemos la que escojas."),
("Do you host and update the site after launch?", "¿Alojan y actualizan la página después de lanzarla?"),
("Yes. Hosting, updates and small changes are handled for you each month, so you never have to touch the site yourself.", "Sí. El alojamiento, las actualizaciones y los cambios pequeños los hacemos nosotros cada mes, así que nunca tienes que tocar la página tú."),
("Do I pay for the ads myself?", "¿Yo pago los anuncios?"),
("Yes. Ad spend goes straight from your card to Google or Meta, in your own ad account. We only bill for our work making and running the ads.", "Sí. Lo que gastas en anuncios va directo de tu tarjeta a Google o Meta, en tu propia cuenta. Nosotros solo cobramos por nuestro trabajo de hacer y manejar los anuncios."),
("Google Ads or Facebook ads, which is better for a local business?", "¿Anuncios en Google o en Facebook? ¿Qué es mejor para un negocio local?"),
("Google catches people already searching for what you do. Facebook and Instagram reach people nearby before they search. Most local businesses do best with one of each, and we'll tell you which to start with.", "Google atrapa a la gente que ya está buscando lo que haces. Facebook e Instagram llegan a la gente cerca antes de que busque. A la mayoría de los negocios locales les va mejor con uno de cada uno, y te decimos con cuál empezar."),
("How fast will I see results?", "¿Qué tan rápido voy a ver resultados?"),
("Calls and messages usually start in the first couple of weeks. The first month is for testing what works, and results get better from there.", "Las llamadas y los mensajes casi siempre empiezan en las primeras dos semanas. El primer mes es para probar qué funciona, y desde ahí los resultados mejoran."),
("How do I know the ads are working?", "¿Cómo sé si los anuncios están funcionando?"),
("Every call, form and message is tracked back to the ad that brought it in, and you get a plain-language report each month.", "Cada llamada, formulario y mensaje queda conectado con el anuncio que lo trajo, y cada mes recibes un reporte en palabras claras."),
("Do you come to my business to shoot?", "¿Van a mi negocio a hacer las fotos?"),
("Yes. We shoot on site anywhere in Miami-Dade, at your restaurant, shop, office or job site.", "Sí. Vamos a cualquier lugar de Miami-Dade: tu restaurante, tienda, oficina o donde estés trabajando."),
("What do I get from a shoot?", "¿Qué me llevo de una sesión?"),
("Edited photos and short videos sized for your website, your Google profile, Instagram and your ads, ready to post.", "Fotos editadas y videos cortos del tamaño justo para tu página, tu perfil de Google, Instagram y tus anuncios, listos para publicar."),
("I don't know what to post. Can you plan it?", "No sé qué publicar. ¿Ustedes lo pueden planear?"),
("Yes. We plan what to shoot before we come, so you get content that fits your business and actually gets used.", "Sí. Planeamos qué grabar antes de ir, para que tengas contenido que va con tu negocio y que de verdad se usa."),
("What is a CRM, in plain words?", "¿Qué es un CRM, en palabras sencillas?"),
("One place that collects every call, form and message from customers, so you can see who reached out and who still needs a reply.", "Un solo lugar que junta cada llamada, formulario y mensaje de tus clientes, para que veas quién te escribió y a quién todavía le falta una respuesta."),
("Will it follow up with leads for me?", "¿Le da seguimiento a los clientes por mí?"),
("Yes. New leads get an automatic reply in seconds, and a follow-up text or email later if they haven't booked.", "Sí. Los clientes nuevos reciben una respuesta automática en segundos, y después un mensaje o email de seguimiento si no han reservado."),
("Do I need to be good with tech?", "¿Tengo que saber de tecnología?"),
("No. We set it all up and show you how to use it in a few minutes. It works from your phone.", "No. Nosotros lo dejamos todo listo y te enseñamos a usarlo en unos minutos. Funciona desde tu celular."),
("Does it work with my website and ads?", "¿Funciona con mi página y mis anuncios?"),
("Yes. Website forms, ad leads and Instagram and Facebook messages all land in the same place.", "Sí. Los formularios de la página, los clientes de los anuncios y los mensajes de Instagram y Facebook llegan todos al mismo lugar."),
("How do I show up higher on Google Maps?", "¿Cómo salgo más arriba en Google Maps?"),
("A complete, active Google Business Profile, steady reviews, and a website with pages for what you do and where you work. We handle all three.", "Con un perfil de Google completo y activo, reseñas constantes y una página web con páginas para lo que haces y donde trabajas. Nosotros nos encargamos de las tres cosas."),
("How long does local SEO take?", "¿Cuánto tiempo toma el SEO local?"),
("Profile fixes can help within weeks. Ranking for competitive searches usually builds over a few months.", "Los arreglos al perfil pueden ayudar en semanas. Subir en las búsquedas con mucha competencia casi siempre toma unos meses."),
("Can you help me get more Google reviews?", "¿Me pueden ayudar a conseguir más reseñas en Google?"),
("Yes. We set up review cards for your counter and a simple way to ask happy customers, and we reply to every review for you.", "Sí. Te hacemos tarjetas de reseñas para tu mostrador y una forma sencilla de pedírselas a los clientes contentos, y contestamos cada reseña por ti."),
("Do I need a website for local SEO?", "¿Necesito una página web para el SEO local?"),
("It helps a lot. Google trusts businesses with a real website that matches their profile, and it gives you pages that can rank in more neighborhoods.", "Ayuda mucho. Google confía en los negocios que tienen una página web real que coincide con su perfil, y te da páginas que pueden salir en más barrios."),
("Which platforms do you manage?", "¿Qué redes manejan?"),
("Instagram and Facebook for most businesses, and TikTok when it fits. We focus on where your customers actually are.", "Instagram y Facebook para la mayoría de los negocios, y TikTok cuando tiene sentido. Nos enfocamos en donde de verdad están tus clientes."),
("How often do you post?", "¿Cada cuánto publican?"),
("Usually 8 to 20 posts a month depending on your plan, on a steady schedule.", "Normalmente de 8 a 20 posts al mes, según tu plan, en un horario fijo."),
("Do I have to approve posts?", "¿Tengo que aprobar los posts?"),
("You approve the monthly plan. After that we shoot, write and post, so you don't have to think about it.", "Tú apruebas el plan del mes. Después nosotros grabamos, escribimos y publicamos, así que no tienes que pensar en eso."),
("Do you reply to comments and messages?", "¿Contestan los comentarios y mensajes?"),
("Yes. We answer comments and messages so customers hear back quickly.", "Sí. Contestamos los comentarios y mensajes para que tus clientes reciban respuesta rápido."),

# ---------- render() chrome ----------
("'<div class=\"ctas\"><a class=\"link\" href=\"#watch\">Watch ' + v[0] + ' explain it</a></div></div>'", "'<div class=\"ctas\"><a class=\"link\" href=\"#watch\">Mira a ' + v[0] + ' explicarlo</a></div></div>'"),
("aria-label=\"Play: ' + v[0] + ' on ' + esc(s.tab) + ', ' + v[1] + '\"", "aria-label=\"Ver: ' + v[0] + ' sobre ' + esc(s.tab) + ', ' + v[1] + '\""),
("'<span class=\"vsl__meta\" aria-hidden=\"true\"><span>' + v[0] + ' on ' + esc(s.tab) + '</span>", "'<span class=\"vsl__meta\" aria-hidden=\"true\"><span>' + v[0] + ' · ' + esc(s.tab) + '</span>"),
("<p class=\"label\">How it works</p><h2>See it work.</h2>", "<p class=\"label\">Cómo funciona</p><h2>Míralo funcionar.</h2>"),
("esc(x.badge || 'Free')", "esc(x.badge || 'Gratis')"),
("(x.note ? esc(x.note) : x.link ? 'No cost. Takes about two minutes.' : 'No cost, no obligation. Takes two minutes to ask.')", "(x.note ? esc(x.note) : x.link ? 'Gratis. Toma unos dos minutos.' : 'Gratis, sin compromiso. Toma dos minutos pedirlo.')"),
("<p class=\"label\">What it is</p>", "<p class=\"label\">Qué es</p>"),
("<p class=\"label\">How it helps you</p><h2>Why it’s worth it.</h2>", "<p class=\"label\">Cómo te ayuda</p><h2>Por qué vale la pena.</h2>"),
("<p class=\"label\">What you get</p><h2>Included.</h2>", "<p class=\"label\">Lo que recibes</p><h2>Incluido.</h2>"),
("<p class=\"label\">Questions</p><h2>Good to know.</h2>", "<p class=\"label\">Preguntas</p><h2>Bueno saber.</h2>"),
("<p>Ready for the whole thing? No prices before we talk. Tell us about your business in one short form.</p>", "<p>¿Listo para todo? No damos precios antes de hablar. Cuéntanos de tu negocio en un formulario corto.</p>"),
("'\">Start a project</a><a class=\"link\" href=\"https://maps.google.com/?cid=1861668075067573854\" target=\"_blank\" rel=\"noopener\">See our reviews on Google</a>", "'\">Empezar un proyecto</a><a class=\"link\" href=\"https://maps.google.com/?cid=1861668075067573854\" target=\"_blank\" rel=\"noopener\">Mira nuestras reseñas en Google</a>"),
("<p class=\"label\">Also from Twin Citys</p>", "<p class=\"label\">También en Twin Citys</p>"),
# links/paths inside the script
("var start = 'https://twincitys.net/start?service=' + s.id;", "var start = '/es/empezar/?service=' + s.id;"),
("tabs.innerHTML = S.map(function (s) { return '<a class=\"tab\" href=\"../' + s.id + '/\">' + s.tab + '</a>'; }).join('');", "tabs.innerHTML = S.map(function (s) { return '<a class=\"tab\" href=\"../' + SLUG[s.id] + '/\">' + s.tab + '</a>'; }).join('');"),
("if (a.getAttribute('href') === '../' + s.id + '/')", "if (a.getAttribute('href') === '../' + SLUG[s.id] + '/')"),
("others.map(function (o) { return '<a href=\"../' + o.id + '/\">", "others.map(function (o) { return '<a href=\"../' + SLUG[o.id] + '/\">"),
("vid.src = m + '.mp4';", "vid.src = m + '-es.mp4';"),
("location.pathname.indexOf('/services/' + l.getAttribute('href').replace('../', ''))", "location.pathname.indexOf('/es/servicios/' + l.getAttribute('href').replace('../', ''))"),
]

LANG_CSS = """
.lang { position: relative; display: inline-grid; grid-template-columns: 1fr 1fr; align-items: center; height: 30px; padding: 2px; border: 1px solid currentColor; border-radius: 999px; font-size: 10px; font-weight: 600; letter-spacing: .14em; line-height: 1; text-decoration: none; text-transform: uppercase; color: var(--ivory); -webkit-tap-highlight-color: transparent; }
.lang::before { content: ""; position: absolute; top: 2px; bottom: 2px; left: 2px; width: calc(50% - 2px); border-radius: 999px; background: currentColor; transition: transform .32s cubic-bezier(.2,.8,.2,1); }
.lang[data-on="es"]::before { transform: translateX(100%); }
.lang span { position: relative; z-index: 1; padding: 0 9px; line-height: 24px; text-align: center; opacity: .75; transition: color .32s, opacity .32s; }
.lang span.on { color: var(--black); opacity: 1; }
.lang:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
.sitenav a.lang { display: inline-grid; min-height: 0; padding: 2px; color: var(--ivory); letter-spacing: .14em; }
@media (max-width: 860px) { .sitenav a.lang { display: inline-grid; } .cta-sm .cta-more { display: none; } .sitenav { gap: 0 12px; } .sitenav .bar__svc { letter-spacing: .18em; } }
"""
LANG_JS = """<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[hreflang]');if(a)try{localStorage.setItem('tc-lang',a.getAttribute('hreflang').slice(0,2))}catch(x){}},true);</script>
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
"""
REMEMBER = """<script>try{var p=localStorage.getItem('tc-lang');if(p&&p!==document.documentElement.lang.slice(0,2)){var a=document.querySelector('link[rel="alternate"][hreflang="'+p+'"]');if(a){var u=new URL(a.href);if(u.pathname!==location.pathname)location.replace(u.pathname+location.search+location.hash);}}}catch(e){}</script>"""

def alternates(en, es):
    return (f'<link rel="alternate" hreflang="en" href="https://twincitys.net{en}">\n'
            f'<link rel="alternate" hreflang="es" href="https://twincitys.net{es}">\n'
            f'<link rel="alternate" hreflang="x-default" href="https://twincitys.net{en}">\n' + REMEMBER + '\n')

def pill(lang, href):
    if lang == 'en':
        return f'<a class="lang" href="{href}" data-on="en" hreflang="es" lang="es" aria-label="Ver en español"><span data-l="en" class="on">EN</span><span data-l="es">ES</span></a>'
    return f'<a class="lang" href="{href}" data-on="es" hreflang="en" lang="en" aria-label="View in English"><span data-l="en">EN</span><span data-l="es" class="on">ES</span></a>'

def add_switch(s, lang, en, es):
    """hreflang + remember snippet in head, pill before the Start button, CSS, click script."""
    s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', '', s)
    s = re.sub(r'<script>try\{var p=localStorage\.getItem\(\'tc-lang\'\).*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<a class="lang" [^>]*>.*?</a>', '', s)
    s = s.replace('<link rel="icon"', alternates(en, es) + '<link rel="icon"', 1)
    s = re.sub(r'(<a class="cta-sm" )', pill(lang, es if lang == 'en' else en) + r'\1', s, count=1)
    if '.lang::before' not in s:
        s = s.replace('</style>', LANG_CSS + '</style>', 1)
    if "closest('a[hreflang]')" not in s:
        i = s.rindex('</body>'); s = s[:i] + LANG_JS + s[i:]
    return s

def build(k):
    en_path, es_path = f'/services/{k}/', f'/es/servicios/{SLUG[k]}/'
    src = open(f'services/{k}/index.html').read()
    # English page: switch only
    open(f'services/{k}/index.html', 'w').write(add_switch(src, 'en', en_path, es_path))
    s = src
    miss = []
    for en, es in HEAD[k] + T:
        if en in s: s = s.replace(en, es)
        else: miss.append(en)
    # urls
    s = s.replace(f'https://twincitys.net/services/{k}/', f'https://twincitys.net{es_path}')
    s = s.replace(f'"serviceUrl": "https://twincitys.net/start/?service={k}"', f'"serviceUrl": "https://twincitys.net/es/empezar/?service={k}"')
    s = s.replace('<meta property="og:url"', '<meta property="og:locale" content="es_US">\n<meta property="og:url"', 1)
    s = s.replace('../../', '/')
    s = s.replace('<a class="brand" href="/">', '<a class="brand" href="/es/">')
    s = s.replace("location.pathname.indexOf('/es/servicios/' + l.getAttribute('href').replace('/', ''))", "location.pathname.indexOf('/es/servicios/' + l.getAttribute('href').replace('../', ''))")
    # services menu links -> Spanish slugs (they are relative ../<id>/ in the English file)
    for kk, slug in SLUG.items():
        s = s.replace(f'<a href="../{kk}/" data-i=', f'<a href="../{slug}/" data-i=').replace(f'<a class="" href="../{kk}/" data-i=', f'<a class="" href="../{slug}/" data-i=')
    s = s.replace("  var S = [", "  var SLUG = " + repr(SLUG).replace("'", '"') + ";\n  var S = [", 1)
    s = s.replace("render('" + k + "');", "render('" + k + "');", 1)
    s = add_switch(s, 'es', en_path, es_path)
    import os; os.makedirs(f'es/servicios/{SLUG[k]}', exist_ok=True)
    open(f'es/servicios/{SLUG[k]}/index.html', 'w').write(s)
    return miss

if __name__ == '__main__':
    allmiss = {}
    for k in SLUG:
        for m in build(k): allmiss.setdefault(m, []).append(k)
    # strings that belong to a single service page are expected to be missing on the other five
    real = {m: ks for m, ks in allmiss.items() if len(ks) == 6}
    print('missing on every page:', len(real))
    for m in real: print('  ', m[:110])
