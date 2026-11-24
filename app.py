import os, sqlite3, secrets, hashlib, hmac, html, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from pathlib import Path
BASE=Path(__file__).parent
DB=BASE/'site.db'
PASSWORD=os.environ.get('AADI_ADMIN_PASSWORD')
if not PASSWORD or len(PASSWORD)<12: raise SystemExit('Set AADI_ADMIN_PASSWORD to at least 12 characters.')
SESS={}
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
with db() as c:
 c.executescript('CREATE TABLE IF NOT EXISTS apps(slug TEXT PRIMARY KEY,name TEXT,category TEXT,description TEXT,store TEXT,privacy TEXT,terms TEXT,support TEXT,icon TEXT,screenshots TEXT,published INTEGER); CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,app TEXT,email TEXT,kind TEXT,body TEXT,status TEXT DEFAULT "New"); CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);')
 for s,n,k,d in [('storynest','StoryNest AI','Education','Imaginative storytelling experiences.'),('closetiq','ClosetIQ AI','Lifestyle','Smart wardrobe organization.'),('vibiq','VIBIQ','Social technology','Let the vibe find you.'),('vibeme','VibeMe AI','Creativity','Creative visual transformation.'),('memorymovie','MemoryMovie AI','Entertainment','Turn memories into cinematic experiences.'),('bhakti','Aadi Anant Bhakti Dhara','Culture','Devotional music and Indian heritage.')]:
  c.execute('INSERT OR IGNORE INTO apps VALUES(?,?,?,?,?,?,?,?,?,?,?)',(s,n,k,d,'','','','','','',0))
 for k,v in [('headline','From the beginning. Beyond infinity.'),('about','Inspired by Indian heritage, we create intelligent digital experiences for a connected world.'),('news','Our application portfolio is in development.')]: c.execute('INSERT OR IGNORE INTO settings VALUES(?,?)',(k,v))
def e(x): return html.escape(str(x or ''),quote=True)
def safeurl(x): return x if urlparse(x).scheme=='https' and urlparse(x).netloc else ''
def page(title,body): return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | AADi Infinity Labs</title><link rel="stylesheet" href="/style.css"><header><a class="brand" href="/"><b>∞</b> AADi INFINITY <small>LABS</small></a><nav><a href="/apps">Applications</a><a href="/about">About</a><a href="/news">News</a><a href="/support">Support</a><a href="/admin">Admin</a></nav></header><main>{body}</main><footer>Indian Roots. Infinite Vision. · © 2026 AADi Infinity Labs (proposed brand)<br><a href="/privacy">Privacy center</a> · <a href="/terms">Legal center</a> · <a href="/delete-account">Account deletion</a></footer></html>'''
def field(n,v='',multi=False): return f'<label>{e(n.title())}'+(f'<textarea name="{n}">{e(v)}</textarea>' if multi else f'<input name="{n}" value="{e(v)}">')+'</label>'
class H(BaseHTTPRequestHandler):
 def send(self,body,status=200,typ='text/html; charset=utf-8',cookie=None):
  self.send_response(status); self.send_header('Content-Type',typ); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' https:; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"); self.send_header('Cache-Control','no-store');
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers(); self.wfile.write(body.encode())
 def session(self):
  token=next((x.strip()[5:] for x in self.headers.get('Cookie','').split(';') if x.strip().startswith('aadi=')),''); return token if SESS.get(token,0)>time.time() else ''
 def redirect(self,path,cookie=None):
  self.send_response(303); self.send_header('Location',path)
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers()
 def do_GET(self):
  p=urlparse(self.path).path; c=db(); apps=c.execute('SELECT * FROM apps WHERE published=1').fetchall(); settings=dict(c.execute('SELECT key,value FROM settings').fetchall()); token=self.session()
  if p=='/style.css': return self.send((BASE/'style.css').read_text(),typ='text/css')
  cards=''.join(f'<a class="card" href="/app/{e(a["slug"])}"><span class="eyebrow">{e(a["category"])}</span><h2>{e(a["name"])}</h2><p>{e(a["description"])}</p>Explore →</a>' for a in apps) or '<p>Our portfolio is being prepared. Check back for product announcements.</p>'
  if p=='/': b=f'<section class="hero"><div class="symbol">∞</div><span class="eyebrow">INDIAN ROOTS. INFINITE VISION.</span><h1>{e(settings["headline"])}</h1><p>{e(settings["about"])}</p><a class="button" href="/apps">Explore our innovations</a></section><h2>Our applications</h2><div class="grid">{cards}</div>'
  elif p=='/apps': b=f'<h1>Our applications</h1><div class="grid">{cards}</div>'
  elif p in ['/about','/news']: b=f'<h1>{p[1:].title()}</h1><p>{e(settings[p[1:]])}</p>'
  elif p.startswith('/app/') or p.startswith('/privacy/') or p.startswith('/terms/'):
   a=c.execute('SELECT * FROM apps WHERE slug=? AND published=1',(p.split('/')[-1],)).fetchone()
   if not a:return self.send(page('Not found','<h1>Not found</h1>'),404)
   kind=p.split('/')[1]; b=f'<h1>{e(a["name"])}</h1>'
   if kind=='app':
    b+=f'<div class="prose">{e(a["support"]) }</div>'
    b+=f'<p>{e(a["description"])}</p>' + ''.join(f'<img class="shot" alt="Application preview" src="{e(safeurl(u))}">' for u in (a['icon']+'\n'+a['screenshots']).splitlines() if safeurl(u)); b+=f'<p><a href="/privacy/{e(a["slug"])}">Privacy</a> · <a href="/terms/{e(a["slug"])}">Terms</a> · <a href="/support?app={e(a["slug"])}">Support</a></p>'; b+=f'<a class="button" href="{e(safeurl(a["store"]))}">App Store</a>' if safeurl(a['store']) else '<p>Store link not yet available.</p>'
   else:b+=f'<h2>{kind.title()}</h2><div class="prose">{e(a[kind] or "Not yet published.")}</div>'
  elif p in ['/privacy','/terms']: b=f'<h1>{p[1:].title()} center</h1>'+''.join(f'<p><a href="{p}/{e(a["slug"])}">{e(a["name"])}</a></p>' for a in apps)
  elif p in ['/support','/delete-account']:
   kind='Deletion' if p=='/delete-account' else 'Support'; selected=parse_qs(urlparse(self.path).query).get('app',[''])[0]; b=f'<h1>{kind} request</h1><p>Do not include passwords or sensitive information. Requests are reviewed manually; submission does not delete an account.</p><form method="post" action="/request"><input type="hidden" name="kind" value="{kind}"><label>Application<select name="app">'+''.join(f'<option {"selected" if a["slug"]==selected else ""} value="{e(a["slug"])}">{e(a["name"])}</option>' for a in apps)+'</select></label><label>Email<input type="email" name="email" required></label><label>Message<textarea name="body" required maxlength="3000"></textarea></label><button>Submit request</button></form>'
  elif p=='/admin':
   if not token:b='<h1>Administrator sign in</h1><form method="post" action="/login"><label>Password<input type="password" name="password" required></label><button>Sign in</button></form>'
   else:
    hidden=f'<input type="hidden" name="csrf" value="{token}">'; b='<h1>Administration</h1><p>Manage applications, legal content and requests.</p><form method="post" action="/logout">'+hidden+'<button>Sign out</button></form><h2>Website content</h2><form method="post" action="/settings">'+hidden+''.join(field(k,v,True) for k,v in settings.items())+'<button>Save content</button></form><h2>Applications</h2>'
    for a in [dict(x) for x in c.execute('SELECT * FROM apps')]+[{}]:
     b+=f'<details><summary>{e(a.get("name","Add application"))} — {"Published" if a.get("published") else "Draft"}</summary><form method="post" action="/save">{hidden}'+''.join(field(k,a.get(k,''),k in ['description','privacy','terms','support','screenshots']) for k in ['slug','name','category','description','store','privacy','terms','support','icon','screenshots'])+f'<label><input type="checkbox" name="published" {"checked" if a.get("published") else ""}> Publish</label><button>Save application</button></form></details>'
    b+='<h2>Requests</h2>'+''.join(f'<div class="card"><b>{e(m["kind"])} · {e(m["status"])}</b><p>{e(m["app"])} · {e(m["email"])}</p><p>{e(m["body"])}</p><form method="post" action="/resolve">{hidden}<input type="hidden" name="id" value="{m["id"]}"><button>Mark reviewed</button></form></div>' for m in c.execute('SELECT * FROM messages ORDER BY id DESC'))
  else:return self.send(page('Not found','<h1>Not found</h1>'),404)
  self.send(page('AADi Infinity Labs',b))
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length','0')); assert 0<size<1000000
   f={k:v[0] for k,v in parse_qs(self.rfile.read(size).decode(),keep_blank_values=True).items()}; p=self.path; token=self.session()
   if p=='/login':
    if not hmac.compare_digest(f.get('password','').encode(),PASSWORD.encode()): time.sleep(1); return self.send(page('Sign in','<p>Invalid password. <a href="/admin">Try again</a></p>'),403)
    token=secrets.token_hex(32); SESS[token]=time.time()+3600; return self.redirect('/admin',f'aadi={token}; HttpOnly; SameSite=Strict; Path=/'+('; Secure' if os.environ.get('AADI_HTTPS')=='1' else ''))
   with db() as c:
    if p=='/request':
     assert f.get('kind') in ['Support','Deletion'] and '@' in f.get('email','') and 0<len(f.get('body',''))<=3000 and c.execute('SELECT 1 FROM apps WHERE slug=? AND published=1',(f.get('app'),)).fetchone(); c.execute('INSERT INTO messages(app,email,kind,body) VALUES(?,?,?,?)',(f['app'],f['email'],f['kind'],f['body'])); return self.send(page('Received','<h1>Request received</h1><p>Your request is awaiting review.</p>'))
    if not token or not hmac.compare_digest(token,f.get('csrf','')):return self.send('Forbidden',403)
    if p=='/logout': SESS.pop(token,None); return self.redirect('/admin','aadi=; Max-Age=0; Path=/')
    if p=='/settings':
     for k in ['headline','about','news']:c.execute('UPDATE settings SET value=? WHERE key=?',(f.get(k,''),k))
    elif p=='/save':
     import re
     assert re.fullmatch('[a-z0-9-]{1,60}',f['slug']) and f['name']; published=int('published' in f); assert not published or (f.get('privacy') and f.get('terms') and f.get('support')); c.execute('INSERT OR REPLACE INTO apps VALUES(?,?,?,?,?,?,?,?,?,?,?)',tuple(f.get(k,'') for k in ['slug','name','category','description','store','privacy','terms','support','icon','screenshots'])+(published,))
    elif p=='/resolve':c.execute('UPDATE messages SET status="Reviewed" WHERE id=?',(f['id'],))
    else:return self.send('Not found',404)
   self.redirect('/admin')
  except (ValueError,AssertionError,KeyError):self.send(page('Invalid request','<h1>Invalid request</h1><p>Check required fields. Published apps need privacy, terms and support content.</p><a href="/admin">Return</a>'),400)
if __name__=='__main__': HTTPServer(('127.0.0.1',int(os.environ.get('PORT','8080'))),H).serve_forever()
