import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Foxy_Company_Cloud is Running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 25565))
    app.run(host='0.0.0.0', port=port)
