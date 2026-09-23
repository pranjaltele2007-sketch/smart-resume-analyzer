import re
import pdfplumber
import docx

# Predefined role skillsets for ATS comparison
ROLE_KEYWORDS = {
    "Data Analyst": ["python", "sql", "excel", "tableau", "power bi", "pandas", "statistics", "data cleaning"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "git", "api", "database"],
    "AI / ML Engineer": ["python", "machine learning", "deep learning", "nlp", "pandas", "numpy", "tensorflow", "pytorch"],
    "Cloud Engineer": ["aws", "azure", "docker", "kubernetes", "linux", "ci/cd", "terraform", "networking"]
}

def extract_text(file_path):
    """Extracts raw text from PDF or DOCX."""
    text = ""
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    return text.lower()

def analyze_resume(text, target_role):
    feedback = []
    
    # 1. Section Completeness Check (Max 40 pts)
    sections = {
        "education": r"(education|academic|qualification)",
        "skills": r"(skills|technical skills|technologies)",
        "projects": r"(projects|academic projects)",
        "experience": r"(experience|internship|work history)"
    }
    section_score = 0
    for sec, pattern in sections.items():
        if re.search(pattern, text):
            section_score += 10
        else:
            feedback.append(f"Missing a dedicated {sec.capitalize()} section.")

    # 2. Contact Information Check (Max 20 pts)
    contact_score = 0
    email_found = bool(re.search(r"[\w\.-]+@[\w\.-]+", text))
    phone_found = bool(re.search(r"\b\d{10}\b|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    
    if email_found:
        contact_score += 10
    else:
        feedback.append("Email address not clearly detected.")
    
    if phone_found:
        contact_score += 10
    else:
        feedback.append("Phone number not clearly detected.")

    # 3. Role-Based ATS Keyword Matching (Max 40 pts)
    target_skills = ROLE_KEYWORDS.get(target_role, [])
    found_skills = [skill for skill in target_skills if skill in text]
    missing_skills = [skill for skill in target_skills if skill not in text]
    
    match_ratio = len(found_skills) / len(target_skills) if target_skills else 0
    ats_score = round(match_ratio * 40)

    if missing_skills:
        feedback.append(f"Add critical {target_role} keywords: {', '.join(missing_skills[:4])}.")

    total_score = section_score + contact_score + ats_score
    ats_percentage = round((len(found_skills) / len(target_skills) * 100)) if target_skills else 0

    return {
        "total_score": total_score,
        "ats_score": ats_percentage,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "feedback": feedback
    }