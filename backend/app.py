from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import spacy
import re

app = Flask(__name__)
CORS(app)

nlp = spacy.load('en_core_web_sm')

SKILLS_LIST = [
    'python', 'java', 'javascript', 'reactjs', 'react', 'flask', 'spring boot',
    'mysql', 'sql', 'mongodb', 'html', 'css', 'node.js', 'git', 'github',
    'machine learning', 'deep learning', 'nlp', 'rest api', 'tailwind',
    'postman', 'maven', 'numpy', 'pandas', 'scikit-learn', 'tensorflow',
    'docker', 'kubernetes', 'aws', 'azure', 'typescript', 'graphql'
]

REQUIRED_SECTIONS = ['education', 'skills', 'projects', 'experience']
GOOD_SECTIONS = ['summary', 'certifications', 'objective', 'achievements']

def extract_text(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

def check_skills(text):
    text_lower = text.lower()
    found = [s for s in SKILLS_LIST if s in text_lower]
    missing = [s for s in SKILLS_LIST if s not in text_lower]
    return found, missing

def check_sections(text):
    text_lower = text.lower()
    found_required = [s for s in REQUIRED_SECTIONS if s in text_lower]
    found_good = [s for s in GOOD_SECTIONS if s in text_lower]
    missing_required = [s for s in REQUIRED_SECTIONS if s not in text_lower]
    return found_required, found_good, missing_required

def check_contact(text):
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'[\+\d][\d\s\-]{9,}', text))
    has_linkedin = 'linkedin' in text.lower()
    has_github = 'github' in text.lower()
    return has_email, has_phone, has_linkedin, has_github

def calculate_score(found_skills, found_required, found_good, text, has_email, has_phone, has_linkedin, has_github):
    score = 0

    # Skills — max 30 points
    skill_score = (len(found_skills) / len(SKILLS_LIST)) * 30
    score += round(min(skill_score, 30))

    # Required sections — max 25 points (each worth ~6)
    score += len(found_required) * 6

    # Good sections — max 10 points
    score += min(len(found_good) * 5, 10)

    # Contact info — max 15 points
    if has_email: score += 5
    if has_phone: score += 4
    if has_linkedin: score += 3
    if has_github: score += 3

    # Word count — max 10 points
    word_count = len(text.split())
    if word_count > 400: score += 10
    elif word_count > 250: score += 6
    elif word_count > 150: score += 3

    # Action verbs — max 10 points
    action_verbs = ['built', 'developed', 'designed', 'implemented',
                    'created', 'managed', 'led', 'improved', 'achieved', 'deployed']
    text_lower = text.lower()
    found_verbs = [v for v in action_verbs if v in text_lower]
    score += min(len(found_verbs), 10)

    return min(round(score), 100)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['resume']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400

    text = extract_text(file)
    found_skills, missing_skills = check_skills(text)
    found_required, found_good, missing_required = check_sections(text)
    has_email, has_phone, has_linkedin, has_github = check_contact(text)

    score = calculate_score(
        found_skills, found_required, found_good, text,
        has_email, has_phone, has_linkedin, has_github
    )

    suggestions = []
    if not has_email:
        suggestions.append('Add your email address to the resume')
    if not has_phone:
        suggestions.append('Add your phone number to the resume')
    if not has_linkedin:
        suggestions.append('Add your LinkedIn profile link')
    if not has_github:
        suggestions.append('Add your GitHub profile link')
    if 'summary' not in text.lower() and 'objective' not in text.lower():
        suggestions.append('Add a Professional Summary or Objective section')
    if 'experience' not in text.lower():
        suggestions.append('Add a Work Experience section or expand your Projects section')
    if len(found_skills) < 6:
        suggestions.append('Add more technical skills — only ' + str(len(found_skills)) + ' recognized skills found')
    if len(text.split()) < 250:
        suggestions.append('Resume is too short — add more details to projects and experience')
    if score >= 80:
        suggestions.append('Strong resume! Make sure all links are working and content is up to date.')

    return jsonify({
        'score': score,
        'found_skills': found_skills,
        'missing_skills': missing_skills[:8],
        'found_sections': found_required + found_good,
        'missing_sections': missing_required,
        'suggestions': suggestions,
        'word_count': len(text.split()),
        'contact': {
            'email': has_email,
            'phone': has_phone,
            'linkedin': has_linkedin,
            'github': has_github
        }
    })

@app.route('/')
def home():
    return jsonify({'message': 'AI Resume Analyzer API is running!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
