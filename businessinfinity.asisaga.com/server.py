from flask import Flask, send_from_directory
from flask_cors import CORS
from conversation_api import get_conversation

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/api/conversation')
def conversation_route():
    return get_conversation()

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True)
