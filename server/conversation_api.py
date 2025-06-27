import os
import json
from flask import jsonify

CONVERSATION_FILE = 'assets/data/conversation.json'

def load_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def get_conversation():
    return jsonify(load_conversation())
