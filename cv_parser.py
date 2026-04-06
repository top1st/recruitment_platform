import PyPDF2
import docx
import re
from typing import List, Dict
import spacy

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Common tech skills dictionary
COMMON_SKILLS = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "swift",
    "kotlin", "php", "html", "css", "sql", "nosql", "mongodb", "postgresql", "mysql",
    
    # Frameworks & libraries
    "react", "angular", "vue", "django", "flask", "spring", "express", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "selenium", "jquery", "bootstrap",
    
    # Tools & platforms
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
    "jira", "confluence", "slack", "trello", "agile", "scrum", "kanban",
    
    # Data & ML
    "machine learning", "deep learning", "nlp", "computer vision", "data analysis", "data science",
    "excel", "tableau", "power bi", "looker", "statistics",
    
    # Soft skills (commonly listed)
    "communication", "leadership", "project management", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity", "collaboration",
    
    # HR/Recruiting specific
    "recruiting", "hr policies", "onboarding", "performance management", "employee relations",
    "benefits administration", "payroll", "hris", "workday", "bamboo hr",
    
    # Finance
    "accounting", "financial modeling", "forecasting", "budgeting", "auditing", "tax",
    "quickbooks", "xero", "sap", "oracle",
    
    # Operations
    "logistics", "supply chain", "inventory management", "procurement", "vendor management",
    "process improvement", "six sigma", "lean",
    
    # Marketing
    "seo", "sem", "social media", "content marketing", "email marketing", "google analytics",
    "hubspot", "marketo", "salesforce"
}

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file) -> str:
    """Extract text from uploaded DOCX file"""
    try:
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using keyword matching + NLP"""
    text_lower = text.lower()
    found_skills = set()
    
    # Exact keyword matching
    for skill in COMMON_SKILLS:
        # Check for whole word match (with word boundaries)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    # Use NLP to find technical terms (nouns and proper nouns)
    doc = nlp(text[:10000])  # Limit to first 10k chars for performance
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
            potential_skill = token.text.lower()
            if potential_skill in COMMON_SKILLS:
                found_skills.add(potential_skill)
    
    return sorted(list(found_skills))

def extract_experience_from_text(text: str) -> int:
    """Extract years of experience from text"""
    text_lower = text.lower()
    
    # Common patterns: "X years of experience", "X+ years", etc.
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+exp',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            years = int(match.group(1))
            return min(years, 30)  # Cap at 30 years
    
    # Try to find the highest year number near "experience"
    sentences = re.split(r'[.!?]', text_lower)
    for sentence in sentences:
        if 'experience' in sentence:
            numbers = re.findall(r'\b(\d+)\b', sentence)
            if numbers:
                # Take the most reasonable number (between 0-40)
                for num in numbers:
                    years = int(num)
                    if 1 <= years <= 40:
                        return years
    
    return 0  # Default if not found

def parse_cv(file, candidate_name: str = None) -> Dict:
    """
    Parse uploaded CV file and extract:
    - Name (if not provided)
    - Skills
    - Years of experience
    - Text content
    """
    file_extension = file.name.split('.')[-1].lower()
    
    # Extract text based on file type
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file)
    elif file_extension == 'docx':
        text = extract_text_from_docx(file)
    else:
        raise Exception("Unsupported file format. Please upload PDF or DOCX.")
    
    # Extract information
    skills = extract_skills_from_text(text)
    experience = extract_experience_from_text(text)
    
    # Try to extract name if not provided
    if not candidate_name:
        # Look for common name patterns at beginning of CV
        lines = text.split('\n')[:10]  # First 10 lines
        for line in lines:
            # Name is often in first few lines, capitalized words
            words = line.strip().split()
            if len(words) >= 2 and len(words) <= 4:
                # Check if it looks like a name (all words capitalized)
                if all(word[0].isupper() and word.isalpha() for word in words):
                    candidate_name = ' '.join(words)
                    break
        
        if not candidate_name:
            candidate_name = "Unknown Candidate"
    
    return {
        "name": candidate_name,
        "skills": skills,
        "experience_years": experience,
        "full_text": text[:500] + "..." if len(text) > 500 else text  # Preview
    }