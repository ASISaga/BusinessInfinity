from flask import Flask, send_from_directory
from flask_cors import CORS
from conversation_api import get_conversation
import os

# Set static folder to businessinfinity.asisaga.com
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'businessinfinity.asisaga.com')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app)

@app.route('/api/conversation')
def conversation_route():
    return get_conversation()

@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)
