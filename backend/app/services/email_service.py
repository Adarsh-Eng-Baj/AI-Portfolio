"""
services/email_service.py — Gmail auto-reply service.
Sends automated confirmation emails to users who contact Adarsh.
"""

import os
import requests
from flask_mail import Mail, Message

mail = Mail()


def send_contact_confirmation(recipient_name: str, recipient_email: str, subject: str, message_preview: str) -> bool:
    """
    Send an automated confirmation email using Resend API.
    """
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        print("[EMAIL] Error: RESEND_API_KEY not found in environment.")
        return False

    # Note: If domain is not verified, "from" must be "onboarding@resend.dev"
    # and "to" can only be the account owner.
    # To send to any recipient, you must verify your domain in Resend dashboard.
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": "Adarsh Portfolio <onboarding@resend.dev>",
            "to": [recipient_email],
            "subject": f"Thanks for reaching out, {recipient_name.split()[0]}! — Adarsh Sutar",
            "html": _build_confirmation_html(recipient_name, subject, message_preview)
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"[EMAIL] Success: Confirmation sent to {recipient_email}")
            return True
        else:
            print(f"[EMAIL] Resend Error: {response.text}")
            return False
            
    except Exception as e:
        import traceback
        print(f"[EMAIL] Exception in send_contact_confirmation: {e}")
        traceback.print_exc()
        return False


def send_new_contact_notification(sender_name: str, sender_email: str, subject: str, message: str) -> bool:
    """
    Notify Adarsh about a new contact form submission using Resend API.
    """
    api_key = os.environ.get('RESEND_API_KEY')
    my_email = os.environ.get('MAIL_USERNAME', 'adarshasutar24@gmail.com')
    
    if not api_key:
        print("[EMAIL] Error: RESEND_API_KEY not found in environment.")
        return False

    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": "Portfolio Bot <onboarding@resend.dev>",
            "to": [my_email],
            "subject": f"[Portfolio Contact] New message from {sender_name}",
            "html": _build_notification_html(sender_name, sender_email, subject, message)
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"[EMAIL] Success: Adarsh notified of new message from {sender_email}")
            return True
        else:
            print(f"[EMAIL] Resend Error (Notification): {response.text}")
            return False
            
    except Exception as e:
        import traceback
        print(f"[EMAIL] Exception in send_new_contact_notification: {e}")
        traceback.print_exc()
        return False


def _build_confirmation_html(name: str, subject: str, preview: str) -> str:
    first_name = name.split()[0] if name else "there"
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Message Received — Adarsh Sutar</title>
</head>
<body style="margin:0;padding:0;background:#0f0a1e;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0a1e;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1033;border-radius:16px;overflow:hidden;border:1px solid rgba(124,58,237,0.3);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:40px 40px 30px;text-align:center;">
              <div style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-bottom:16px;">
                <span style="font-size:32px;">✉️</span>
              </div>
              <h1 style="color:#fff;margin:0;font-size:28px;font-weight:700;">Message Received!</h1>
              <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:16px;">I'll get back to you soon</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="color:#e2e8f0;font-size:16px;margin:0 0 20px;">Hi <strong style="color:#a78bfa;">{first_name}</strong>,</p>
              <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 20px;">
                Thank you for reaching out! I've received your message and will respond within <strong style="color:#e2e8f0;">24–48 hours</strong>.
              </p>

              <!-- Message Preview Card -->
              <div style="background:#0f0a1e;border:1px solid rgba(124,58,237,0.2);border-left:4px solid #7c3aed;border-radius:8px;padding:20px;margin:24px 0;">
                <p style="color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin:0 0 8px;">YOUR MESSAGE</p>
                <p style="color:#94a3b8;font-size:14px;font-weight:600;margin:0 0 6px;">{subject or '(No subject)'}</p>
                <p style="color:#64748b;font-size:13px;margin:0;font-style:italic;">{preview[:200]}{'...' if len(preview) > 200 else ''}</p>
              </div>

              <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:24px 0;">
                While you wait, feel free to explore my projects or connect with me on social media:
              </p>

              <!-- Social Links -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;">
                <tr>
                  <td align="center">
                    <a href="https://github.com/Adarsh-Eng-Baj" style="display:inline-block;margin:4px;padding:10px 18px;background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);border-radius:8px;color:#a78bfa;text-decoration:none;font-size:13px;font-weight:600;">GitHub</a>
                    <a href="https://www.linkedin.com/in/adarsha-sutar-80807532b/" style="display:inline-block;margin:4px;padding:10px 18px;background:rgba(37,99,235,0.15);border:1px solid rgba(37,99,235,0.3);border-radius:8px;color:#60a5fa;text-decoration:none;font-size:13px;font-weight:600;">LinkedIn</a>
                    <a href="https://www.instagram.com/_adarsh88/" style="display:inline-block;margin:4px;padding:10px 18px;background:rgba(219,39,119,0.15);border:1px solid rgba(219,39,119,0.3);border-radius:8px;color:#f472b6;text-decoration:none;font-size:13px;font-weight:600;">Instagram</a>
                  </td>
                </tr>
              </table>

              <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0;">
                Best regards,<br />
                <strong style="color:#e2e8f0;">Adarsh Sutar</strong><br />
                <span style="color:#64748b;font-size:13px;">B.Tech CSE-AI · GIET Bhubaneswar · AI/ML & Cloud Developer</span>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0f0a1e;padding:24px 40px;border-top:1px solid rgba(124,58,237,0.15);">
              <p style="color:#475569;font-size:12px;margin:0;text-align:center;">
                This is an automated message from Adarsh's portfolio. Please do not reply to this email.<br />
                &copy; 2024 Adarsh Sutar · <a href="http://localhost:8000" style="color:#7c3aed;text-decoration:none;">adarshsutar.dev</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _build_notification_html(sender_name: str, sender_email: str, subject: str, message: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;padding:20px;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:24px;">
      <h2 style="color:#fff;margin:0;">📬 New Portfolio Contact</h2>
    </div>
    <div style="padding:32px;">
      <table width="100%" cellpadding="8">
        <tr><td style="color:#64748b;font-size:13px;width:80px;vertical-align:top;">FROM</td>
            <td><strong>{sender_name}</strong> &lt;{sender_email}&gt;</td></tr>
        <tr><td style="color:#64748b;font-size:13px;vertical-align:top;">SUBJECT</td>
            <td><strong>{subject or '(No subject)'}</strong></td></tr>
        <tr><td style="color:#64748b;font-size:13px;vertical-align:top;">MESSAGE</td>
            <td style="white-space:pre-wrap;color:#374151;">{message}</td></tr>
      </table>
      <div style="margin-top:24px;padding-top:24px;border-top:1px solid #e2e8f0;">
        <a href="mailto:{sender_email}?subject=Re: {subject}" 
           style="display:inline-block;padding:12px 24px;background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff;border-radius:8px;text-decoration:none;font-weight:600;">
          Reply to {sender_name.split()[0]}
        </a>
      </div>
    </div>
  </div>
</body>
</html>
"""
