"""
services/pdf_service.py — Dynamic PDF resume generator using ReportLab.
Pulls live data from the database to build a professional resume PDF.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ── Color Palette ──────────────────────────────────────
PURPLE   = colors.HexColor('#7c3aed')
DARK_BG  = colors.HexColor('#1e1b4b')
LIGHT_BG = colors.HexColor('#f5f3ff')
GRAY     = colors.HexColor('#64748b')
DARK     = colors.HexColor('#1e293b')
WHITE    = colors.white


def generate_resume_pdf() -> io.BytesIO:
    """
    Generate a professional PDF resume for Adarsh Sutar.
    Returns a BytesIO buffer containing the PDF.
    """
    # ── Import models inside function to avoid circular imports ──
    from app.models import Skill, Experience, Project
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        title='Adarsh Sutar — Resume',
        author='Adarsh Sutar',
    )
    
    # ── Styles ─────────────────────────────────────────
    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle(
        'NameStyle', fontSize=26, fontName='Helvetica-Bold',
        textColor=DARK, alignment=TA_LEFT, spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', fontSize=11, fontName='Helvetica',
        textColor=GRAY, alignment=TA_LEFT, spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'ContactStyle', fontSize=9, fontName='Helvetica',
        textColor=GRAY, alignment=TA_LEFT, spaceAfter=2
    )
    section_style = ParagraphStyle(
        'SectionStyle', fontSize=13, fontName='Helvetica-Bold',
        textColor=PURPLE, spaceBefore=14, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyStyle', fontSize=9.5, fontName='Helvetica',
        textColor=DARK, leading=14, spaceAfter=4
    )
    small_style = ParagraphStyle(
        'SmallStyle', fontSize=8.5, fontName='Helvetica',
        textColor=GRAY, leading=12
    )
    bold_style = ParagraphStyle(
        'BoldStyle', fontSize=10, fontName='Helvetica-Bold',
        textColor=DARK, spaceAfter=2
    )
    
    story = []
    
    # ── Header ─────────────────────────────────────────
    story.append(Paragraph('Adarsh Sutar', name_style))
    story.append(Paragraph('B.Tech CSE (Artificial Intelligence) • 2nd Year', subtitle_style))
    story.append(Paragraph(
        '📍 Bhubaneswar, Odisha, India  |  ✉ adarshasutar24@gmail.com  |  🐙 github.com/Adarsh-Eng-Baj',
        contact_style
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=PURPLE, spaceAfter=8))
    
    # ── Summary ────────────────────────────────────────
    story.append(Paragraph('Professional Summary', section_style))
    story.append(Paragraph(
        'Passionate B.Tech CSE-AI student with hands-on experience in Python, Machine Learning, '
        'Computer Vision, and Full-Stack web development. Built 6+ end-to-end projects combining '
        'AI/ML backends with modern frontends. Strong foundation in Data Structures, Algorithms, '
        'and Software Engineering principles. Seeking internship opportunities to apply AI skills '
        'to real-world problems.',
        body_style
    ))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=4))
    
    # ── Skills ────────────────────────────────────────
    story.append(Paragraph('Technical Skills', section_style))
    
    skills = Skill.query.order_by(Skill.category, Skill.order_index).all()
    
    # Group by category
    skill_categories = {}
    for skill in skills:
        cat = skill.category or 'Other'
        if cat not in skill_categories:
            skill_categories[cat] = []
        skill_categories[cat].append(f"{skill.name} ({skill.proficiency}%)")
    
    for cat, skill_list in skill_categories.items():
        row = [
            Paragraph(f'<b>{cat}:</b>', body_style),
            Paragraph(', '.join(skill_list), body_style)
        ]
        t = Table([row], colWidths=[3.5*cm, 14*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t)
    
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=4))
    
    # ── Projects ───────────────────────────────────────
    story.append(Paragraph('Featured Projects', section_style))
    
    projects = Project.query.filter_by(featured=True).order_by(Project.created_at.desc()).all()
    if not projects:
        projects = Project.query.order_by(Project.created_at.desc()).limit(4).all()
    
    for project in projects:
        tech = ', '.join(project.tech_stack.split(',')[:6]) if project.tech_stack else ''
        block = [
            Paragraph(f'<b>{project.title}</b>  <font color="#7c3aed" size="8">[{project.category}]</font>', bold_style),
            Paragraph(project.description or '', body_style),
            Paragraph(f'<i>Tech: {tech}</i>', small_style),
            Spacer(1, 4),
        ]
        story.append(KeepTogether(block))
    
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=4))
    
    # ── Experience / Education ─────────────────────────
    story.append(Paragraph('Education & Experience', section_style))
    
    experiences = Experience.query.order_by(Experience.order_index).all()
    
    for exp in experiences:
        end = 'Present' if exp.is_current else (exp.end_date or '')
        date_range = f"{exp.start_date} – {end}"
        
        row_title = Table([[
            Paragraph(f'<b>{exp.role}</b>', bold_style),
            Paragraph(date_range, ParagraphStyle('date', fontSize=9, fontName='Helvetica', textColor=GRAY, alignment=TA_RIGHT))
        ]], colWidths=[12*cm, 5.5*cm])
        row_title.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        
        story.append(row_title)
        story.append(Paragraph(f'{exp.company}  •  {exp.location or ""}', small_style))
        story.append(Paragraph(exp.description or '', body_style))
        story.append(Spacer(1, 4))
    
    # ── Footer ─────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=PURPLE, spaceBefore=8, spaceAfter=4))
    story.append(Paragraph(
        f'Generated on {datetime.now().strftime("%B %d, %Y")} • adarshsutar.vercel.app',
        ParagraphStyle('footer', fontSize=8, fontName='Helvetica', textColor=GRAY, alignment=TA_CENTER)
    ))
    
    doc.build(story)
    return buffer
