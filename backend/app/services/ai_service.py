"""
services/ai_service.py — AI chatbot service.
Uses OpenAI GPT-3.5 if API key is configured, else rule-based fallback.
"""

import os
import re

# Portfolio context for the AI (about Adarsh Sutar)
PORTFOLIO_CONTEXT = """
You are Adarsh's AI assistant on his portfolio website.
Here is the context about Adarsh Sutar:

NAME: Adarsh Sutar
EDUCATION: B.Tech in Computer Science & Engineering (AI), 2nd Year student
COLLEGE: Gandhi Institute of Excellent Technocrats (GIET), Ghangapatna, Bhubaneswar, Odisha
SGPA: 8.44 (last semester)

SKILLS:
- Languages: Python (90%), JavaScript (80%), C++ (75%), Java (70%), HTML/CSS (88%)
- AI/ML: TensorFlow, Scikit-learn, NumPy, Pandas, OpenCV, NLTK, MediaPipe
- Cloud: AWS (EC2, S3, Lambda, IAM), Cloud Computing
- Frameworks: Flask (88%), FastAPI (75%), Spring Boot (60%), React (65%)
- Databases: MySQL, PostgreSQL, SQLite, MongoDB
- Tools: Git/GitHub, VS Code, Jupyter Notebook, Docker, Postman

PROJECTS:
1. AI-Powered Study Planner - Smart study schedule generator with AI adaptation
2. Smart ATS Resume Analyzer - NLP-based resume scoring using cosine similarity
3. Kheti Mitra - AI farming assistant with crop disease detection for Indian farmers
4. Student Performance Analyzer - ML-based grade prediction system (Java + Python)
5. Hand Gesture Recognition - OpenCV + MediaPipe real-time gesture control system
6. AI Portfolio Website - This very site with Flask, AI chatbot, analytics

INTERESTS: Artificial Intelligence, Machine Learning, Computer Vision, Full-Stack Development, Cloud Computing (AWS)
CONTACT: Available via the contact form on this site
GITHUB: github.com/adarshsutar
LOCATION: Bhubaneswar, Odisha, India

Be helpful, friendly, and conversational. Keep responses concise (2-4 sentences max).
If asked about something unrelated to the portfolio, politely redirect to Adarsh's work.
"""

# ─────────────────────────────────────────────
# Rule-Based Fallback Patterns
# ─────────────────────────────────────────────
RULES = [
    # Greetings
    (r'\b(hi|hello|hey|howdy|namaste|namaskar)\b',
     "Hi there! 👋 I'm Adarsh's AI assistant. Ask me anything about his skills, projects, or how to get in touch!"),

    # Name / identity
    (r'\b(who are you|what are you|introduce)\b',
     "I'm the AI assistant on Adarsh Sutar's portfolio. He's a B.Tech CSE-AI student who builds cool AI and web projects! 🤖"),

    (r'\b(adarsh|sutar)\b',
     "Adarsh Sutar is a 2nd-year B.Tech CSE-AI student at Gandhi Institute of Excellent Technocrats (GIET), Bhubaneswar. He specializes in AI/ML, Python, Flask, AWS Cloud, and full-stack development."),

    # Skills
    (r'\b(skill|skills|know|language|languages|tech|technology|stack)\b',
     "Adarsh is skilled in Python, JavaScript, C++, Java, Flask, TensorFlow, Scikit-learn, OpenCV, React, AWS (EC2, S3, Lambda), and databases like MySQL & PostgreSQL. AI/ML + Cloud Computing is his core strength."),

    # Projects
    (r'\b(project|projects|built|build|work|created)\b',
     "Adarsh has built 6 impressive projects: AI Study Planner, Smart ATS Resume Analyzer, Kheti Mitra (AI for farmers), Student Performance Analyzer, Hand Gesture Recognition, and this Portfolio! Check the Projects page."),

    # Study Planner
    (r'\b(study planner|study plan|schedule)\b',
     "The AI Study Planner is a smart schedule generator that adapts to learning pace and exam dates. Built with Python, Flask, and Chart.js!"),

    # ATS
    (r'\b(ats|resume analyzer|resume|cv)\b',
     "The Smart ATS Resume Analyzer uses NLP and cosine similarity to score resumes against job descriptions, find missing keywords, and suggest improvements."),

    # Kheti Mitra
    (r'\b(kheti|farming|farmer|agriculture|crop)\b',
     "Kheti Mitra is an AI farming assistant for Indian farmers. It detects crop diseases using CNN, recommends crops based on soil/weather data, and supports Hindi & Odia. Built with FastAPI + TensorFlow."),

    # Hand gesture
    (r'\b(hand|gesture|opencv|computer vision)\b',
     "The Hand Gesture Recognition project uses OpenCV + MediaPipe to detect and classify hand gestures in real-time. Control your PC without touching it!"),

    # Education
    (r'\b(education|college|university|study|studying|degree|btech|b\.tech|cse|giet)\b',
     "Adarsh is pursuing B.Tech in CSE (AI specialization) at Gandhi Institute of Excellent Technocrats (GIET), Ghangapatna, Bhubaneswar. He's in his 2nd year with an SGPA of 8.44 in his last semester."),

    # School / HSC
    (r'\b(school|hsc|12th|higher secondary|pcm)\b',
     "Adarsh completed his HSC (12th) from Khaira Higher Secondary School, Khaira, Balasore, Odisha with PCM-IT subjects."),

    # AWS / Cloud
    (r'\b(aws|cloud|ec2|s3|lambda|serverless)\b',
     "Adarsh is learning AWS Cloud Computing including EC2, S3, Lambda, and IAM. He's passionate about building scalable cloud-native applications!"),

    # Contact
    (r'\b(contact|reach|email|hire|collaborate|connect)\b',
     "You can reach Adarsh via the Contact page or directly at adarshasutar24@gmail.com. He's open to collaboration, internships, and exciting projects!"),

    # GitHub
    (r'\b(github|code|repository|source)\b',
     "Check out Adarsh's GitHub at github.com/Adarsh-Eng-Baj for all his project source code!"),

    # Social / LinkedIn
    (r'\b(linkedin|instagram|twitter|social)\b',
     "Connect with Adarsh: LinkedIn - linkedin.com/in/adarsha-sutar-80807532b | Instagram - @_adarsh88 | Twitter - @adarsha_sutar"),

    # Location
    (r'\b(location|where|city|state|india|odisha|bhubaneswar)\b',
     "Adarsh is based in Bhubaneswar, Odisha, India. He studies at GIET, Ghangapatna."),

    # Internship / job
    (r'\b(internship|intern|job|opportunity|hire|hiring)\b',
     "Adarsh is actively looking for internship opportunities in AI/ML, Cloud Computing, and Full-Stack development! Reach out on the Contact page."),

    # AI/ML
    (r'\b(ai|ml|machine learning|deep learning|artificial intelligence|neural|tensorflow|scikit)\b',
     "AI/ML is Adarsh's core passion! He works with TensorFlow, Scikit-learn, NLTK, OpenCV, and MediaPipe. Projects span NLP, Computer Vision, and Predictive Analytics."),

    # Python
    (r'\b(python|flask|fastapi|django)\b',
     "Python is Adarsh's primary language at 90% proficiency! He uses Flask and FastAPI for backend APIs and TensorFlow/Scikit-learn for ML projects."),

    # SGPA / marks
    (r'\b(sgpa|cgpa|gpa|marks|grade|score)\b',
     "Adarsh secured 8.44 SGPA in his last semester at GIET Bhubaneswar. He's consistently performing well in his B.Tech CSE-AI program."),
]

FALLBACK_RESPONSE = "That's an interesting question! 🤔 I'm best at answering questions about Adarsh's skills, projects, education, and how to contact him. What would you like to know?"


def get_chatbot_response(user_message: str, history: list = None) -> str:
    """
    Get a chatbot response for the user message.
    Tries Gemini first, then OpenAI; falls back to rule-based if neither key is set or on error.
    """
    gemini_key = os.environ.get('GEMINI_API_KEY', '')
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    
    # 1. Try Gemini
    if gemini_key and gemini_key.startswith('AIza'):
        try:
            return _gemini_response(user_message, history or [])
        except Exception as e:
            print(f"Gemini error: {e} — trying OpenAI or fallback")

    # 2. Try OpenAI (Fallback)
    if openai_key and openai_key.startswith('sk-'):
        try:
            return _openai_response(user_message, history or [])
        except Exception as e:
            print(f"OpenAI error: {e} — using rule-based fallback")
    
    return _rule_based_response(user_message)


def _gemini_response(user_message: str, history: list) -> str:
    """Use Google Gemini to generate a context-aware response."""
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    
    # Use gemini-1.5-flash — 15 RPM free tier, fast and capable
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=PORTFOLIO_CONTEXT
    )
    
    # Build conversation history for Gemini
    gemini_history = []
    for msg in history[-6:]:
        role = 'user' if msg.get('role') == 'user' else 'model'
        gemini_history.append({'role': role, 'parts': [msg.get('content', '')]})
    
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_message)
    
    return response.text.strip()


def _openai_response(user_message: str, history: list) -> str:
    """Use OpenAI GPT to generate a response."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    messages = [{'role': 'system', 'content': PORTFOLIO_CONTEXT}]
    for msg in history[-6:]:
        if 'role' in msg and 'content' in msg:
            messages.append({'role': msg['role'], 'content': msg['content']})
    messages.append({'role': 'user', 'content': user_message})
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _rule_based_response(user_message: str) -> str:
    """Simple pattern-matching rule-based chatbot fallback."""
    msg_lower = user_message.lower()
    
    for pattern, response in RULES:
        if re.search(pattern, msg_lower):
            return response
    
    return FALLBACK_RESPONSE
