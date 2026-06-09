import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Foxy_Company_Cloud</title>
            <style>
                body { background-color: #121212; color: #ff6600; font-family: sans-serif; text-align: center; padding-top: 50px; }
                h1 { font-size: 50px; }
                p { color: #ffffff; font-size: 20px; }
            </style>
        </head>
        <body>
            <h1>🦊 FOXY_COMPANY SYSTEM 🦊</h1>
            <p>A felhő alapú rendszer sikeresen elindult és online van!</p>
            <p>RANG: OPERÁTOR</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # A Render automatikusan beállítja a PORT-ot, ha nincs, akkor 25565-ön fut
    port = int(os.environ.get('PORT', 25565))
    app.run(host='0.0.0.0', port=port)
