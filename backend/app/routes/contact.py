"""
routes/contact.py — Contact form submission endpoint.
Stores messages in the database and returns confirmation.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models import ContactMessage

contact_bp = Blueprint('contact', __name__)


# ─────────────────────────────────────────────
# POST /api/contact
# ─────────────────────────────────────────────
@contact_bp.route('', methods=['POST'])
def submit_contact():
    """Submit a contact form message. Stores in DB."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    # Validate required fields
    required = ['name', 'email', 'message']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400
    
    # Basic email format check
    email = data['email'].strip()
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Get client IP (handles Render/Vercel proxy headers)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    
    msg = ContactMessage(
        name=data['name'].strip(),
        email=email,
        subject=data.get('subject', 'General Inquiry').strip(),
        message=data['message'].strip(),
        ip_address=ip,
    )
    
    db.session.add(msg)
    db.session.commit()

    # Send automated emails in a background thread
    from threading import Thread
    from flask import current_app
    
    app = current_app._get_current_object()
    
    def send_emails_async(app_obj, name, email_addr, sub, msg_text):
        with app_obj.app_context():
            try:
                from app.services.email_service import send_contact_confirmation, send_new_contact_notification
                send_contact_confirmation(
                    recipient_name=name,
                    recipient_email=email_addr,
                    subject=sub,
                    message_preview=msg_text
                )
                send_new_contact_notification(
                    sender_name=name,
                    sender_email=email_addr,
                    subject=sub,
                    message=msg_text
                )
            except Exception as e:
                import traceback
                print(f"[CONTACT] Async email notification failed: {e}")
                traceback.print_exc()

    Thread(target=send_emails_async, args=(
        app, msg.name, msg.email, msg.subject, msg.message
    )).start()
    
    return jsonify({
        'message': "Message sent successfully! I'll get back to you soon.",
        'id': msg.id
    }), 201


# ─────────────────────────────────────────────
# GET /api/contact  (Admin only)
# ─────────────────────────────────────────────
@contact_bp.route('', methods=['GET'])
@jwt_required()
def get_messages():
    """Get all contact messages (admin only). Supports ?unread=true."""
    unread_only = request.args.get('unread', '').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ContactMessage.query
    if unread_only:
        query = query.filter_by(is_read=False)
    
    paginated = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'messages': [m.to_dict() for m in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'unread_count': ContactMessage.query.filter_by(is_read=False).count()
    }), 200


# ─────────────────────────────────────────────
# PUT /api/contact/<id>/read  (Admin only)
# ─────────────────────────────────────────────
@contact_bp.route('/<int:msg_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(msg_id):
    """Mark a contact message as read (admin only)."""
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200


# ─────────────────────────────────────────────
# DELETE /api/contact/<id>  (Admin only)
# ─────────────────────────────────────────────
@contact_bp.route('/<int:msg_id>', methods=['DELETE'])
@jwt_required()
def delete_message(msg_id):
    """Delete a contact message (admin only)."""
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'message': 'Message deleted'}), 200
