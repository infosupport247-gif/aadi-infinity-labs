import os,json,sqlite3,secrets,hmac,html,re
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from pathlib import Path
ROOT=Path(__file__).parent; DB=ROOT/'site.db'; PASSWORD=os.environ.get('AADI_ADMIN_PASSWORD'); sessions=set()
apps=[('StoryNest AI','Education & Entertainment','Imaginative storytelling for children.'),('ClosetIQ AI','Fashion & Lifestyle','Intelligent wardrobe management and outfit planning.'),('VIBIQ','Social Technology','Let the vibe find you.'),('VibeMe AI','AI & Creativity','Creative visual transformation.'),('MemoryMovie AI','Photography & Entertainment','Turn memories into cinematic experiences.'),('Aadi Anant Bhakti Dhara','Spirituality & Culture','Devotional music and Indian heritage.')]
def db(): return sqlite3.connect(DB)
with db() as c:
 c.execute('create table if not exists apps (slug text primary key, data text)'); c.execute('create table if not exists settings (id integer primary key, data text)')
 if not c.execute('select 1 from settings').fetchone():
  c.execute('insert into settings values(1,?)',(json.dumps(dict(brand='AADi INFINITY LABS',tagline='Indian Roots. Infinite Vision.',headline='Building Beyond Boundaries.',intro='Technology inspired by heritage. Innovation designed for humanity.',email='',about='A technology studio inspired by Indian heritage and driven by global innovation.')),))
  for n,cat,d in apps:
   slug=re.sub('[^a-z0-9]+','-',n.lower()).strip('-'); c.execute('insert into apps values(?,?)',(slug,json.dumps(dict(slug=slug,name=n,category=cat,description=d,status='In development',store='',icon='',screenshots='',privacy='',terms='',support='',deletion=''))))
class Handler(BaseHTTPRequestHandler):
 def send(self,obj,status=200):
  b=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
 def auth(self): return any(hmac.compare_digest(x, self.headers.get('Cookie','').replace('aadi_session=','')) for x in sessions)
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/api/site':
   with db() as c: self.send(dict(settings=json.loads(c.execute('select data from settings').fetchone()[0]),apps=[json.loads(x[0]) for x in c.execute('select data from apps')]))
  elif p=='/api/session': self.send({'authenticated':self.auth(),'configured':bool(PASSWORD)})
  elif p in ['/','/admin'] or p.startswith('/app/') or p.startswith('/legal/') or p in ['/support','/about','/contact','/privacy','/terms','/delete-account']:
   self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write((ROOT/'index.html').read_bytes())
  else: self.send({'error':'Not found'},404)
 def do_POST(self):
  p=urlparse(self.path).path
  if self.headers.get('Origin') and self.headers['Origin'] not in ['http://'+self.headers.get('Host',''),'https://'+self.headers.get('Host','')]: return self.send({'error':'Invalid origin'},403)
  try:
   n=int(self.headers.get('Content-Length',0)); assert n<=1000000; d=json.loads(self.rfile.read(n))
  except Exception: return self.send({'error':'Invalid request'},400)
  if p=='/api/login':
   if not PASSWORD or not hmac.compare_digest(str(d.get('password','')),PASSWORD): return self.send({'error':'Invalid password or admin not configured'},403)
   t=secrets.token_urlsafe(32); sessions.add(t); self.send_response(200); self.send_header('Set-Cookie',f'aadi_session={t}; HttpOnly; SameSite=Strict; Path=/'); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b'{"ok":true}'); return
  if not self.auth(): return self.send({'error':'Sign in required'},401)
  with db() as c:
   if p=='/api/settings':
    old=json.loads(c.execute('select data from settings').fetchone()[0]); old.update({k:str(v) for k,v in d.items() if k in old}); c.execute('update settings set data=? where id=1',(json.dumps(old),))
   elif p=='/api/app':
    slug=d.get('slug','');
    if not re.fullmatch('[a-z0-9-]{1,80}',slug) or not d.get('name'): return self.send({'error':'Valid slug and name required'},400)
    c.execute('insert or replace into apps values(?,?)',(slug,json.dumps({k:str(d.get(k,'')) for k in ['slug','name','category','description','status','store','icon','screenshots','privacy','terms','support','deletion']})))
   elif p=='/api/delete': c.execute('delete from apps where slug=?',(d.get('slug'),))
   elif p=='/api/logout': sessions.discard(self.headers.get('Cookie','').replace('aadi_session=',''))
   else: return self.send({'error':'Not found'},404)
  self.send({'ok':True})
if __name__=='__main__':
 print('AADi Infinity Labs: http://localhost:8769',flush=True); ThreadingHTTPServer(('127.0.0.1',8769),Handler).serve_forever()
