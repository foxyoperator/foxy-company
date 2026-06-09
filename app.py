import time
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask("Foxy_Company_Cloud")
app.secret_key = "foxy_enterprise_secret_key"

# Rendszer Memória (Mivel nincs multiprocessing, ez így szuper stabil)
shared_chat = [
    {'sender': 'Rendszer_Bot', 'text': 'A Foxy_Company felhőalapú hálózati magja elindult. Minden rendszer online és VÉDETT.', 'time': time.strftime("%H:%M:%S")}
]
shared_stats = {'total_messages': 1}
shared_users = {
    "Foxy": "Foxybest.hu",
    "Balu": "Ferima677",
    "Amon202394": "AmonGaming.hu"
}
shared_logs = [f"[{time.strftime('%H:%M:%S')}] SYSTEM: Felhő klaszter inicializálva. Tűzfal aktív."]

# ==========================================
# FIX UI ÉS STÍLUS
# ==========================================
FOXY_STYLE = """
<style>
    :root {
        --bg-color: #0b0b0e;
        --card-color: #13131a;
        --primary: #ff6b35;
        --primary-hover: #e0531f;
        --text: #f4f4f6;
        --text-muted: #6c6c84;
        --border: #1f1f2a;
        --success: #2ec4b6;
        --accent: #7209b7;
        --danger: #ef233c;
    }
    body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg-color);
        color: var(--text);
        margin: 0; padding: 0; min-height: 100vh;
    }
    .navbar {
        width: 100%; background-color: var(--card-color);
        border-bottom: 1px solid var(--border); padding: 15px 0;
        text-align: center; position: sticky; top: 0; z-index: 100;
    }
    .navbar a {
        color: var(--text-muted); text-decoration: none;
        margin: 0 15px; font-weight: 600; transition: 0.3s;
    }
    .navbar a:hover, .navbar a.active { color: var(--primary); }
    
    .layout {
        display: grid; grid-template-columns: 1.1fr 1.4fr; gap: 25px;
        max-width: 1300px; margin: 40px auto; padding: 0 20px;
    }
    .container {
        background-color: var(--card-color); border: 1px solid var(--border);
        border-radius: 12px; padding: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.7);
        margin-bottom: 25px;
    }
    .full-width { max-width: 400px; margin: 15vh auto; text-align: center; }
    h1, h2, h3 { color: var(--text); margin-top: 0; font-weight: 700; }
    h1 span, h3 span { color: var(--primary); }
    p { color: var(--text-muted); line-height: 1.6; }
    
    .chat-box {
        background-color: #070709; border: 1px solid var(--border);
        border-radius: 8px; height: 380px; overflow-y: auto;
        padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px;
    }
    .msg {
        background-color: #1a1a24; padding: 10px 14px; border-radius: 8px;
        max-width: 85%; width: fit-content; border-left: 3px solid var(--text-muted);
    }
    .msg.foxy { border-left-color: var(--primary); background-color: #241914; }
    .msg.balu { border-left-color: #3a86ff; background-color: #141b2d; }
    .msg.amon202394 { border-left-color: #ff006e; background-color: #2b1420; }
    .msg.rendszer_bot { border-left-color: var(--success); background-color: #0f1816; }
    .msg-meta { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; font-weight: 600; }
    .msg-text { font-size: 14px; word-break: break-word; }
    
    .loader-wrapper {
        position: fixed; top:0; left:0; width:100vw; height:100vh;
        background-color: var(--bg-color); z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .progress-bar-container {
        width: 80%; max-width: 500px; background-color: #1a1a24;
        height: 8px; border-radius: 4px; overflow: hidden; margin-top: 25px; border: 1px solid var(--border);
    }
    .progress-bar { height: 100%; width: 0%; background-color: var(--primary); }
    #loader-status { color: var(--primary); font-family: monospace; font-size: 14px; margin-top: 15px; }
    
    .form-group { margin-bottom: 15px; text-align: left; }
    label { display: block; margin-bottom: 5px; color: var(--text-muted); font-size: 13px; }
    .chat-input-group { display: flex; gap: 10px; }
    input[type="text"], input[type="password"], select {
        width: 100%; padding: 12px; border: 1px solid var(--border);
        background-color: #070709; color: var(--text); border-radius: 6px; font-size: 14px; box-sizing: border-box;
    }
    input:focus, select:focus { border-color: var(--primary); outline: none; }
    .btn {
        padding: 12px 24px; background-color: var(--primary); border: none;
        color: white; font-weight: 600; border-radius: 6px; cursor: pointer;
    }
    .btn:hover { background-color: var(--primary-hover); }
    .btn-danger { background-color: var(--danger); }
    .badge {
        background-color: var(--primary); color: white; padding: 3px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    .badge-success { background-color: var(--success); }
    .announcement {
        background: linear-gradient(135deg, #1e1310, #13131a);
        border: 1px solid #ff6b3533; padding: 15px; border-radius: 8px; margin-bottom: 20px;
    }
    .log-box {
        background-color: #070709; border: 1px solid var(--border); border-radius: 6px;
        padding: 10px; font-family: monospace; font-size: 12px; color: #a5a5b5; height: 120px; overflow-y: auto;
    }
</style>
"""

def get_shared_login_page(app_title, redirect_to, error_msg=None):
    err_html = f'<p style="color: var(--danger); font-size: 14px; font-weight:600;">{error_msg}</p>' if error_msg else ''
    return f"""
    {FOXY_STYLE}
    <div class="container full-width">
        <h1>Foxy_<span>Company</span></h1>
        <p>{app_title} - Bejelentkezés</p>
        {err_html}
        <form method="post" action="/login?next={redirect_to}">
            <input type="text" name="username" placeholder="Felhasználónév" required style="margin-bottom:15px;"><br>
            <input type="password" name="password" placeholder="Jelszó" required style="margin-bottom:20px;"><br>
            <button type="submit" class="btn" style="width:100%;">Belépés a Rendszerbe</button>
        </form>
    </div>
    """

# ==========================================
# UTVONALAK (Közös porton, szétválasztva)
# ==========================================

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login_route', next='home'))
    if not session.get('optimized', False): return redirect(url_for('loading'))
        
    current_user = session['user']
    account_editor_html = ""
    system_logs_html = ""
    
    if current_user == "Foxy":
        user_options = "".join([f'<option value="{u}">{u}</option>' for u in shared_users.keys() if u != "Foxy"])
        account_editor_html = f"""
        <div class="container" style="border-color: var(--primary); margin-top:20px;">
            <h3>⚙️ Központi <span>Fiókszerkesztő</span> <span class="badge">Foxy Only</span></h3>
            <p style="font-size:13px; margin-bottom:15px;">Módosítsd a munkatársak jelszavait élőben a felhő memóriában:</p>
            <form action="/api/edit-user" method="post">
                <div class="form-group">
                    <label>Munkatárs kiválasztása</label>
                    <select name="target_user">{user_options}</select>
                </div>
                <div class="form-group">
                    <label>Új biztonságos jelszó</label>
                    <input type="text" name="new_password" placeholder="Írd be az új jelszót..." required autocomplete="off">
                </div>
                <button type="submit" class="btn" style="width:100%;">Jelszó Frissítése Élőben</button>
            </form>
        </div>
        """
        
        logs_content = "".join([f'<div>{log}</div>' for log in reversed(shared_logs)])
        system_logs_html = f"""
        <div class="container" style="border-color: var(--border);">
            <h3>🛡️ Biztonsági <span>Rendszernapló</span></h3>
            <div class="log-box">{logs_content}</div>
        </div>
        """

    return f"""
    {FOXY_STYLE}
    <div class="navbar">
        <a class="active" href="/">Munkatér</a>
        <a href="/admin">Admin Vezérlő</a>
        <a href="/bot">Foxy_Bot Panel</a>
        <a href="/logout" style="color: #ff4444;">Kijelentkezés</a>
    </div>
    
    <div class="layout">
        <div>
            <div class="container announcement">
                <h3 style="margin-bottom:5px;">📢 Üdvözlünk, <span>{current_user}</span>!</h3>
                <small style="color:var(--text-muted)">Foxy_Company Felhő Rendszer</small>
                <p style="margin-top:10px; font-size:14px;">Minden modulod sikeresen fut a felhőben 24/7-ben!</p>
            </div>
            
            <div class="container">
                <h3>📋 Aktuális <span>Feladatok</span></h3>
                <hr style="border-color: var(--border); margin: 15px 0;">
                <p style="font-size: 14px;">🔲 Foxy_OS kernel fájlok tesztelése parancssorban.</p>
                <p style="font-size: 14px;">🔲 Új zenék bemásolása a <code>music</code> mappába.</p>
                <p style="font-size: 14px;">✅ Szerver sikeresen kiköltöztetve a felhőbe (Single-Port Cloud mód).</p>
            </div>
            {account_editor_html}
            {system_logs_html}
        </div>
        
        <div class="container">
            <h3>💬 Élő <span>Vállalati Chat</span> <span class="badge badge-success">Auto-Refresh</span></h3>
            <p>Biztonságos belső üzenetváltás</p>
            <div class="chat-box" id="chatBox"></div>
            <div class="chat-input-group">
                <input type="text" id="msgText" placeholder="Írj egy üzenetet..." required autocomplete="off" onkeydown="if(event.key === 'Enter') sendMsg()">
                <button onclick="sendMsg()" class="btn">Küldés</button>
            </div>
        </div>
    </div>
    
    <script>
        let lastChatLength = 0;
        function fetchChat() {{
            fetch('/api/chat')
                .then(function(r) {{ return r.json(); }})
                .then(function(data) {{
                    const box = document.getElementById('chatBox');
                    if (data.length !== lastChatLength) {{
                        box.innerHTML = '';
                        data.forEach(function(m) {{
                            let cls = m.sender.toLowerCase();
                            box.innerHTML += '<div class="msg ' + cls + '"><div class="msg-meta">' + m.sender + ' • ' + m.time + '</div><div class="msg-text">' + m.text + '</div></div>';
                        }});
                        box.scrollTop = box.scrollHeight;
                        lastChatLength = data.length;
                    }}
                }});
        }}
        function sendMsg() {{
            const input = document.getElementById('msgText');
            const t = input.value.trim();
            if(!t) return;
            fetch('/api/send', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'message=' + encodeURIComponent(t)
            }}).then(function() {{ input.value = ''; fetchChat(); }});
        }}
        setInterval(fetchChat, 1000);
        fetchChat();
    </script>
    """

@app.route('/admin', methods=['GET'])
def admin_home():
    if 'user' not in session: return redirect(url_for('login_route', next='admin_home'))
    if session['user'] != "Foxy":
        return redirect(url_for('login_route', next='admin_home', error="Hozzáférés megtagadva: Nincs elegendő rangod!"))

    return f"""
    {FOXY_STYLE}
    <div class="navbar">
        <a href="/">Vissza a Munkatérre</a>
        <a class="active" href="#">Központi Vezérlő</a>
        <a href="/logout" style="color: #ff4444; margin-left:20px;">Kijelentkezés</a>
    </div>
    
    <div class="layout" style="max-width: 900px; grid-template-columns: 1fr 1fr;">
        <div class="container" style="border-color: var(--primary);">
            <h3>Rendszer <span>Monitor</span> <span class="badge">Adminisztrátor</span></h3>
            <p>🟢 Cloud Core: <span class="badge badge-success">ONLINE (24/7)</span></p>
            <p>Összes küldött üzenet: <span class="badge">{shared_stats['total_messages']}</span></p>
        </div>
        
        <div class="container">
            <h3>Admin <span>Sürgősségi Parancsok</span></h3>
            <form action="/admin/clear" method="post">
                <button type="submit" class="btn btn-danger" style="width:100%;">Összes Üzenet Törlése</button>
            </form>
        </div>
    </div>
    """

@app.route('/bot', methods=['GET'])
def bot_home():
    if 'user' not in session: return redirect(url_for('login_route', next='bot_home'))
    if session['user'] != "Foxy":
        return redirect(url_for('login_route', next='bot_home', error="Hozzáférés megtagadva: Nincs elegendő rangod!"))

    return f"""
    {FOXY_STYLE}
    <div class="navbar">
        <a href="/">Vissza a Munkatérre</a>
        <a class="active" href="#">Foxy_Bot Konzol</a>
        <a href="/logout" style="color: #ff4444; margin-left:20px;">Kijelentkezés</a>
    </div>
    
    <div class="layout" style="max-width: 800px; grid-template-columns: 1fr;">
        <div class="container" style="border-color: var(--success);">
            <h3>🤖 Foxy_Bot <span>Központi Parancssor</span></h3>
            <div style="background-color:#070709; padding:20px; border-radius:8px; font-family:monospace; color:var(--success); border: 1px solid var(--border); margin-bottom:20px;">
                [SYSTEM] Foxy_Bot felhő modul aktív.<br>
                [STATUS] Listening on central web port...
            </div>
            <h3>Üzenet küldése Botként</h3>
            <form action="/bot/inject" method="post" class="chat-input-group">
                <input type="text" name="bot_message" placeholder="Írd be a bot üzenetét..." required autocomplete="off">
                <button type="submit" class="btn" style="background-color: var(--success);">Küldés</button>
            </form>
        </div>
    </div>
    """

# ==========================================
# API ÉS KISZOLGÁLÓ RUTINOK
# ==========================================

@app.route('/loading')
def loading():
    if 'user' not in session: return redirect(url_for('login_route', next='home'))
    return f"""
    {FOXY_STYLE}
    <div class="loader-wrapper">
        <h2>Foxy_<span>Company</span> Cloud</h2>
        <p>Felhőmodulok optimalizálása...</p>
        <div class="progress-bar-container"><div class="progress-bar" id="pbar"></div></div>
        <div id="loader-status">Kapcsolódás...</div>
    </div>
    <script>
        let p = 0; const bar = document.getElementById('pbar'); const txt = document.getElementById('loader-status');
        const steps = ["Biztonsági protokollok...","Felhő kapcsolat...","Szervermag ellenőrzés...","Sikeres hitelesítés!"];
        const iv = setInterval(function() {{
            p += 2; bar.style.width = p + '%';
            if (p % 25 === 0) {{ let idx = Math.floor(p / 25); if(steps[idx]) txt.innerText = steps[idx]; }}
            if (p >= 100) {{ clearInterval(iv); fetch('/api/complete-optimization').then(function() {{ window.location.href = '/'; }}); }}
        }}, 50);
    </script>
    """

@app.route('/login', methods=['GET'])
def login_route():
    nxt = request.args.get('next', 'home')
    error = request.args.get('error')
    return render_template_string(get_shared_login_page("Központi Rendszer", nxt, error))

@app.route('/login', methods=['POST'])
def do_login():
    nxt = request.args.get('next', 'home')
    username_input = request.form['username']
    password_input = request.form['password']
    
    if username_input in shared_users and shared_users[username_input] == password_input:
        if (nxt in ['admin_home', 'bot_home']) and username_input != "Foxy":
            shared_logs.append(f"[{time.strftime('%H:%M:%S')}] SECURITY ALERT: {username_input} illetéktelenül próbált az admin felületre lépni.")
            return redirect(url_for('login_route', next=nxt, error="Nincs elegendő rangod ehhez a felülethez!"))
            
        session['user'] = username_input
        session['optimized'] = False
        shared_logs.append(f"[{time.strftime('%H:%M:%S')}] P_AUTH: {username_input} sikeresen belépett.")
        return redirect(url_for('loading'))
    else:
        shared_logs.append(f"[{time.strftime('%H:%M:%S')}] WARNING: Hibás belépési kísérlet -> {username_input}")
        return redirect(url_for('login_route', next=nxt, error="Helytelen felhasználónév vagy jelszó!"))

@app.route('/api/edit-user', methods=['POST'])
def edit_user():
    if session.get('user') == "Foxy":
        target = request.form['target_user']
        new_pass = request.form['new_password']
        if target in shared_users and target != "Foxy":
            shared_users[target] = new_pass
            shared_logs.append(f"[{time.strftime('%H:%M:%S')}] SECURITY: Foxy módosította {target} jelszavát.")
    return redirect(url_for('home'))

@app.route('/api/chat')
def get_chat(): return jsonify(shared_chat)

@app.route('/api/send', methods=['POST'])
def api_send():
    if 'user' in session:
        msg_text = request.form['message']
        shared_chat.append({'sender': session['user'], 'text': msg_text, 'time': time.strftime("%H:%M:%S")})
        shared_stats['total_messages'] += 1
        return jsonify({'status': 'success'})
    return jsonify({'status': 'unauthorized'}), 401

@app.route('/bot/inject', methods=['POST'])
def inject_msg():
    if session.get('user') == "Foxy":
        msg_text = request.form['bot_message']
        shared_chat.append({'sender': 'Rendszer_Bot', 'text': msg_text, 'time': time.strftime("%H:%M:%S")})
        shared_stats['total_messages'] += 1
    return redirect(url_for('bot_home'))

@app.route('/admin/clear', methods=['POST'])
def clear_chat():
    if session.get('user') == "Foxy":
        shared_chat.clear()
        shared_logs.append(f"[{time.strftime('%H:%M:%S')}] COMMAND: Foxy törölte a teljes chatet.")
    return redirect(url_for('admin_home'))

@app.route('/api/complete-optimization')
def complete_opt():
    session['optimized'] = True
    return jsonify({'status': 'done'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_route', next='home'))

if __name__ == '__main__':
    # Helyi teszteléshez (a felhőben ezt a sort a szolgáltató felülbírálja, ami tökéletes)
    app.run(host='127.0.0.1', port=25565, debug=True)
