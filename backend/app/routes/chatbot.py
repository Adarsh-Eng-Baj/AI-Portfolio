"""
routes/chatbot.py — AI chatbot endpoint.
Uses OpenAI if API key is set, falls back to rule-based responses.
"""

from flask import Blueprint, request, jsonify
from app.services.ai_service import get_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)


# ─────────────────────────────────────────────
# POST /api/chat
# ─────────────────────────────────────────────
@chatbot_bp.route('', methods=['POST'])
def chat():
    """
    Accept a user message and return an AI/rule-based response.
    Request body: { "message": "...", "history": [...] }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    if len(user_message) > 1000:
        return jsonify({'error': 'Message too long (max 1000 chars)'}), 400
    
    # Conversation history (list of {role, content} dicts)
    history = data.get('history', [])
    
    try:
        response = get_chatbot_response(user_message, history)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({
            'response': "Sorry, I'm having trouble right now. Please try again! 🤖",
            'error': str(e)
        }), 200  # Return 200 so frontend doesn't break
