import time
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify

app = Flask("Foxy_Company_Cloud")
app.secret_key = "foxy_enterprise_secret_key"

# Rendszer Memória
shared_chat = [{'sender': 'Rendszer_Bot', 'text': 'A Foxy_Company felhőalapú hálózati magja elindult. Minden rendszer online és VÉDETT.', 'time': time.strftime("%H:%M:%S")}]
shared_stats = {'total_messages': 1}
shared_users = {
    "Foxy": {"pass": "Foxybest.hu", "2fa": "ADMINS_OF_BOTS_88"},
    "Balu": {"pass": "Ferima677", "2fa": None},
    "Amon202394": {"pass": "AmonGaming.hu", "2fa": None}
}
shared_logs = [f"[{time.strftime('%H:%M:%S')}] SYSTEM: Felhő klaszter inicializálva. Tűzfal aktív."]

# CSS és Stílusok (A kért stílus)
FOXY_STYLE = """
<style>
    :root { --bg-color: #0b0b0e; --card-color: #13131a; --primary: #ff6b35; --text: #f4f4f6; --text-muted: #6c6c84; --border: #1f1f2a; --success: #2ec4b6; --danger: #ef233c; }
    body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text); margin: 0; min-height: 100vh; }
    .navbar { width: 100%; background-color: var(--card-color); border-bottom: 1px solid var(--border); padding: 15px 0; text-align: center; }
    .container { background-color: var(--card-color); border: 1px solid var(--border); border-radius: 12px; padding: 30px; margin: 40px auto; max-width: 500px; }
    .full-width { max-width: 400px; margin: 15vh auto; text-align: center; }
    .btn { padding: 12px 24px; background-color: var(--primary); border: none; color: white; border-radius: 6px; cursor: pointer; width: 100%; }
    input { width: 100%; padding: 12px; margin: 10px 0; background: #070709; border: 1px solid var(--border); color: white; border-radius: 6px; box-sizing: border-box; }
    .chat-box { height: 380px; overflow-y: auto; background: #070709; padding: 15px; border-radius: 8px; }
    .log-box { font-family: monospace; font-size: 12px; height: 120px; overflow-y: auto; background: #070709; padding: 10px; }
</style>
"""

# LOGIN ÉS 2FA LOGIKA
@app.route('/login', methods=['GET'])
def login_route():
    nxt = request.args.get('next', 'home')
    error = request.args.get('error')
    return render_template_string(f"""{FOXY_STYLE}
    <div class="container full-width">
        <h1>Foxy_<span>Company</span></h1>
        <p>Bejelentkezés</p>
        <p style="color:red;">{error or ''}</p>
        <form method="post" action="/login?next={nxt}">
            <input type="text" name="username" placeholder="Felhasználónév" required>
            <input type="password" name="password" placeholder="Jelszó" required>
            <button type="submit" class="btn">Belépés</button>
        </form>
    </div>""")

@app.route('/login', methods=['POST'])
def do_login():
    nxt = request.args.get('next', 'home')
    user = request.form['username']
    password = request.form['password']
    
    if user in shared_users and (user == "Foxy" and shared_users[user]['pass'] == password or (user != "Foxy" and shared_users[user] == password)):
        if user == "Foxy":
            session['pre_auth_user'] = user
            return render_template_string(f"""{FOXY_STYLE}
            <div class="container full-width">
                <h1>🦊 2. SZINTŰ VÉDELEM</h1>
                <form method="post" action="/verify-2fa?next={nxt}">
                    <input type="password" name="code" placeholder="ADMINS_OF_BOTS_88" required>
                    <button type="submit" class="btn">HITELÉS</button>
                </form>
            </div>""")
        session['user'] = user
        session['optimized'] = False
        return redirect(url_for('loading'))
    return redirect(url_for('login_route', next=nxt, error="Hibás adatok!"))

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    code = request.form['code']
    user = session.get('pre_auth_user')
    nxt = request.args.get('next', 'home')
    if user and shared_users[user]['2fa'] == code:
        session['user'] = user
        session.pop('pre_auth_user')
        session['optimized'] = False
        shared_logs.append(f"[{time.strftime('%H:%M:%S')}] SECURITY: Foxy sikeres 2FA belépés.")
        return redirect(url_for('loading'))
    return redirect(url_for('login_route', next=nxt, error="HIBÁS ADMIN_BOT_KÓD!"))

# EGYÉB FUNKCIÓK (Chat, Admin, stb - az eredeti logikád alapján)
@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login_route', next='home'))
    if not session.get('optimized', False): return redirect(url_for('loading'))
    return "Foxy_Company Cloud Online. (Ide illeszd vissza a korábbi home tartalmadat a layouttal)"

@app.route('/api/chat')
def get_chat(): return jsonify(shared_chat)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_route'))

@app.route('/loading')
def loading():
    session['optimized'] = True
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
