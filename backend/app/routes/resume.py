"""
routes/resume.py — PDF resume generation endpoint.
Dynamically builds a PDF from DB data using ReportLab.
"""

import io
from flask import Blueprint, send_file
from app.services.pdf_service import generate_resume_pdf

resume_bp = Blueprint('resume', __name__)


# ─────────────────────────────────────────────
# GET /api/resume/download
# ─────────────────────────────────────────────
@resume_bp.route('/download', methods=['GET'])
def download_resume():
    """
    Generate and stream a PDF resume for Adarsh Sutar.
    Pulls data from the database dynamically.
    """
    try:
        pdf_buffer = generate_resume_pdf()
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Adarsh_Sutar_Resume.pdf'
        )
    except Exception as e:
        from flask import jsonify
        return jsonify({'error': f'Failed to generate resume: {str(e)}'}), 500
