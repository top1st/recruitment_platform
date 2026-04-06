jobs = {
    1: {"id": 1, "title": "Software Engineer", "dept": "Engineering", "paygrade": "GR-7", "required_skills": ["python", "sql", "aws"]},
    2: {"id": 2, "title": "HR Manager", "dept": "HR", "paygrade": "GR-6", "required_skills": ["recruiting", "hr policies", "communication"]},
    3: {"id": 3, "title": "Finance Analyst", "dept": "Finance", "paygrade": "GR-6", "required_skills": ["excel", "accounting", "financial modeling"]},
    4: {"id": 4, "title": "Program Manager", "dept": "Programs", "paygrade": "GR-9", "required_skills": ["project management", "leadership", "agile"]},
    5: {"id": 5, "title": "Operations Coordinator", "dept": "Operations", "paygrade": "GR-7", "required_skills": ["logistics", "communication", "problem solving"]},
}

candidates = [
    # Internal candidates
    {"id": 1, "name": "Alice Chen", "source": "internal", "skills": ["python", "sql", "aws"], "exp": 5, "job_id": 1, "status": "hired", "agency_name": None},
    {"id": 2, "name": "Bob Smith", "source": "internal", "skills": ["recruiting", "communication"], "exp": 4, "job_id": 2, "status": "hired", "agency_name": None},
    {"id": 3, "name": "Carol Davis", "source": "internal", "skills": ["excel", "accounting"], "exp": 3, "job_id": 3, "status": "screened", "agency_name": None},
    {"id": 4, "name": "David Kim", "source": "internal", "skills": ["python", "java"], "exp": 2, "job_id": 1, "status": "rejected", "agency_name": None},
    
    # External candidates
    {"id": 5, "name": "Emma Wilson", "source": "external", "skills": ["python", "sql", "aws", "docker"], "exp": 7, "job_id": 1, "status": "hired", "agency_name": None},
    {"id": 6, "name": "Frank Miller", "source": "external", "skills": ["recruiting", "hr policies"], "exp": 6, "job_id": 2, "status": "hired", "agency_name": None},
    {"id": 7, "name": "Grace Lee", "source": "external", "skills": ["excel", "financial modeling"], "exp": 4, "job_id": 3, "status": "hired", "agency_name": None},
    {"id": 8, "name": "Henry Zhao", "source": "external", "skills": ["python", "sql"], "exp": 1, "job_id": 1, "status": "rejected", "agency_name": None},
    {"id": 9, "name": "Ivy Patel", "source": "external", "skills": ["project management", "leadership"], "exp": 8, "job_id": 4, "status": "hired", "agency_name": None},
    {"id": 10, "name": "Jack Ryan", "source": "external", "skills": ["logistics", "problem solving"], "exp": 3, "job_id": 5, "status": "screened", "agency_name": None},
    
    # Referrals
    {"id": 11, "name": "Karen White", "source": "referral", "skills": ["python", "sql", "aws"], "exp": 4, "job_id": 1, "status": "hired", "agency_name": None},
    {"id": 12, "name": "Leo Martinez", "source": "referral", "skills": ["recruiting", "communication"], "exp": 3, "job_id": 2, "status": "rejected", "agency_name": None},
    {"id": 13, "name": "Mona Gupta", "source": "referral", "skills": ["project management", "agile"], "exp": 5, "job_id": 4, "status": "hired", "agency_name": None},
    {"id": 14, "name": "Nick Adams", "source": "referral", "skills": ["excel", "accounting"], "exp": 2, "job_id": 3, "status": "screened", "agency_name": None},
    
    # Agency placements
    {"id": 15, "name": "Olivia Brown", "source": "agency", "skills": ["python", "sql", "aws", "ml"], "exp": 9, "job_id": 1, "status": "hired", "agency_name": "TechRecruiters"},
    {"id": 16, "name": "Paul Garcia", "source": "agency", "skills": ["recruiting", "hr policies", "communication"], "exp": 7, "job_id": 2, "status": "hired", "agency_name": "HRExperts"},
    {"id": 17, "name": "Quinn Taylor", "source": "agency", "skills": ["excel", "accounting", "financial modeling"], "exp": 6, "job_id": 3, "status": "hired", "agency_name": "FinancePros"},
    {"id": 18, "name": "Rachel Green", "source": "agency", "skills": ["python", "sql"], "exp": 3, "job_id": 1, "status": "screened", "agency_name": "TechRecruiters"},
    {"id": 19, "name": "Steve Jobs", "source": "agency", "skills": ["project management", "leadership", "agile"], "exp": 10, "job_id": 4, "status": "hired", "agency_name": "ExecutiveSearch"},
]