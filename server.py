from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import json, os, uuid

ROOT=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(ROOT,'data.json')

def load():
    if not os.path.exists(DATA):
        d={'admin':{'id':'admin','role':'admin','name':'Administrator','username':'admin','email':'admin@mywebsite.com','password':'Admin12345','disabled':False},'users':[]}
        save(d); return d
    try:
        with open(DATA,'r',encoding='utf-8') as f: d=json.load(f)
    except: d={'admin':{},'users':[]}
    d.setdefault('users',[]); d.setdefault('admin',{})
    return d

def save(d):
    tmp=DATA+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f: json.dump(d,f,indent=2,ensure_ascii=False)
    os.replace(tmp,DATA)

def norm(x): return str(x or '').strip().lower()
def match(a,i): return norm(a.get('username'))==norm(i) or norm(a.get('email'))==norm(i)

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        # serve files from project root
        path=path.split('?',1)[0]
        rel=path.lstrip('/') or 'index.html'
        return os.path.join(ROOT,rel)
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(raw)
    def body(self):
        n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.send_header('Access-Control-Allow-Methods','GET,POST,PUT,OPTIONS'); self.end_headers()
    def do_GET(self):
        u=urlparse(self.path).path; d=load()
        if u=='/api/users': return self.send_json({'users':d['users']})
        if u=='/api/admin': return self.send_json({'admin':d['admin']})
        if u.startswith('/api/'): return self.send_json({'error':'Not found'},404)
        return super().do_GET()
    def do_POST(self):
        u=urlparse(self.path).path; d=load(); b=self.body()
        if u=='/api/login':
            role=b.get('role'); a=d['admin'] if role=='admin' else next((x for x in d['users'] if match(x,b.get('identifier'))),None)
            if not a or not match(a,b.get('identifier')) or a.get('password')!=b.get('password') or a.get('disabled') or a.get('role')!=role: return self.send_json({'error':'Invalid username/email or password.'},401)
            return self.send_json({'success':True,'account':a})
        if u=='/api/register':
            b=b
            if not b.get('username') or not b.get('email') or len(str(b.get('password','')))<6: return self.send_json({'error':'Required fields are missing.'},400)
            if match(d['admin'],b.get('username')) or match(d['admin'],b.get('email')) or any(norm(x.get('username'))==norm(b.get('username')) or norm(x.get('email'))==norm(b.get('email')) for x in d['users']): return self.send_json({'error':'Username or email is already in use.'},409)
            u={'id':'user_'+uuid.uuid4().hex,'role':'user','createdAt':__import__('datetime').datetime.now().isoformat(),**b,'disabled':False}; d['users'].append(u); save(d); return self.send_json({'success':True,'account':u})
        if u=='/api/admin/users':
            if b.get('adminId')!='admin': return self.send_json({'error':'Administrator access required.'},403)
            u=b.get('user',{}); u={'id':u.get('id') or 'user_'+uuid.uuid4().hex,'role':'user',**u}
            d['users'].append(u); save(d); return self.send_json({'success':True,'users':d['users']})
        if u=='/api/reset-password':
            a=d['admin'] if match(d['admin'],b.get('identifier')) else next((x for x in d['users'] if match(x,b.get('identifier'))),None)
            if not a:return self.send_json({'error':'Account not found.'},404)
            a['password']=b.get('password',''); save(d); return self.send_json({'success':True})
        return self.send_json({'error':'Not found'},404)
    def do_PUT(self):
        u=urlparse(self.path).path; d=load(); b=self.body()
        if u=='/api/admin': d['admin']={**d['admin'],**b.get('admin',{}),'id':'admin','role':'admin'}; save(d); return self.send_json({'success':True,'admin':d['admin']})
        if u=='/api/users':
            incoming=b.get('users',[]); by={str(x.get('id')):x for x in d['users'] if x.get('id')}
            for x in incoming:
                if x.get('id'): by[str(x['id'])]={**by.get(str(x['id']),{}),**x,'role':'user'}
            d['users']=list(by.values()); save(d); return self.send_json({'success':True,'users':d['users']})
        return self.send_json({'error':'Not found'},404)

if __name__=='__main__':
    port=int(os.environ.get('PORT','3000')); server=ThreadingHTTPServer(('0.0.0.0',port),Handler); print(f'Dashboard running at http://localhost:{port}'); server.serve_forever()
