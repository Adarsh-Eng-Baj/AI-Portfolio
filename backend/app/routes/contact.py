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

    # Send automated emails (best-effort — don't fail the request if email fails)
    try:
        from app.services.email_service import send_contact_confirmation, send_new_contact_notification
        send_contact_confirmation(
            recipient_name=msg.name,
            recipient_email=msg.email,
            subject=msg.subject,
            message_preview=msg.message
        )
        send_new_contact_notification(
            sender_name=msg.name,
            sender_email=msg.email,
            subject=msg.subject,
            message=msg.message
        )
    except Exception as e:
        print(f"[CONTACT] Email notification failed: {e}")
    
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
