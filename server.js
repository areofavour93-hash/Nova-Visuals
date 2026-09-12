const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=__dirname;
const DATA_DIR=process.env.DATA_DIR || ROOT;
const DATA=process.env.DATA_FILE || path.join(DATA_DIR,'data.json');
const PORT=Number(process.env.PORT || 3000);
const HOST=process.env.HOST || '0.0.0.0';
function defaultData(){
  return {
    admin:{
      id:'admin',
      role:'admin',
      name:'Administrator',
      username:'admin',
      email:'admin@mywebsite.com',
      password:process.env.DEFAULT_ADMIN_PASSWORD || 'Admin12345',
      disabled:false
    },
    users:[]
  };
}
function load(){
  fs.mkdirSync(path.dirname(DATA),{recursive:true});
  if(!fs.existsSync(DATA)) save(defaultData());
  try {
    const parsed=JSON.parse(fs.readFileSync(DATA,'utf8'));
    if(!parsed.admin) parsed.admin=defaultData().admin;
    if(!Array.isArray(parsed.users)) parsed.users=[];
    return parsed;
  } catch {
    const fresh=defaultData();
    save(fresh);
    return fresh;
  }
}
function save(d){fs.writeFileSync(DATA,JSON.stringify(d,null,2))} function n(x){return String(x||'').trim().toLowerCase()} function match(a,i){return n(a.username)===n(i)||n(a.email)===n(i)}
function send(res,status,obj){const b=Buffer.from(JSON.stringify(obj));res.writeHead(status,{'Content-Type':'application/json','Content-Length':b.length,'Access-Control-Allow-Origin':'*'});res.end(b)}
const server=http.createServer((req,res)=>{let body='';req.on('data',c=>body+=c);req.on('end',()=>{const u=new URL(req.url,'http://localhost').pathname,d=load();let b={};try{b=body?JSON.parse(body):{}}catch{};
if(req.method==='GET'&&u==='/health')return send(res,200,{ok:true}); if(req.method==='GET'&&u==='/api/users')return send(res,200,{users:d.users}); if(req.method==='GET'&&u==='/api/admin')return send(res,200,{admin:d.admin});
if(req.method==='POST'&&u==='/api/login'){const a=b.role==='admin'?d.admin:d.users.find(x=>match(x,b.identifier));if(!a||!match(a,b.identifier)||a.password!==b.password||a.disabled||a.role!==b.role)return send(res,401,{error:'Invalid username/email or password.'});return send(res,200,{success:true,account:a})}
if(req.method==='POST'&&u==='/api/register'){if(!b.username||!b.email||String(b.password||'').length<6)return send(res,400,{error:'Required fields are missing.'});if(match(d.admin,b.username)||match(d.admin,b.email)||d.users.some(x=>n(x.username)===n(b.username)||n(x.email)===n(b.email)))return send(res,409,{error:'Username or email is already in use.'});const x={id:'user_'+crypto.randomUUID(),role:'user',createdAt:new Date().toISOString(),...b,disabled:false};d.users.push(x);save(d);return send(res,200,{success:true,account:x})}
if(req.method==='POST'&&u==='/api/admin/users'){if(b.adminId!=='admin')return send(res,403,{error:'Administrator access required.'});const x={id:'user_'+crypto.randomUUID(),role:'user',...(b.user||{})};d.users.push(x);save(d);return send(res,200,{success:true,users:d.users})}
if(req.method==='POST'&&u==='/api/reset-password'){const a=match(d.admin,b.identifier)?d.admin:d.users.find(x=>match(x,b.identifier));if(!a)return send(res,404,{error:'Account not found.'});a.password=b.password;save(d);return send(res,200,{success:true})}
if(req.method==='PUT'&&u==='/api/admin'){d.admin={...d.admin,...(b.admin||{}),id:'admin',role:'admin'};save(d);return send(res,200,{success:true,admin:d.admin})}
if(req.method==='PUT'&&u==='/api/users'){const map=new Map(d.users.map(x=>[String(x.id),x]));for(const x of (b.users||[]))if(x.id)map.set(String(x.id),{...(map.get(String(x.id))||{}),...x,role:'user'});d.users=[...map.values()];save(d);return send(res,200,{success:true,users:d.users})}
if(u.startsWith('/api/'))return send(res,404,{error:'Not found'});
let file=path.join(ROOT,u==='/'?'index.html':u); if(!fs.existsSync(file)||!fs.statSync(file).isFile())return send(res,404,{error:'File not found'});const ext=path.extname(file);const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
})}); server.listen(PORT,HOST,()=>console.log(`Dashboard running on ${HOST}:${PORT}`)); server.on('error',e=>{console.error('Server failed to start:',e.message);process.exit(1)});
