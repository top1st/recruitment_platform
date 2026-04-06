import re
from typing import Dict, List

def calculate_match_score(candidate: dict, job: dict) -> dict:
    """
    Calculate match score between candidate and job.
    Returns: {score: 0-100, missing_skills: list, match_reason: str}
    """
    required_skills = set([s.lower() for s in job.get("required_skills", [])])
    candidate_skills = set([s.lower() for s in candidate.get("skills", [])])
    
    # Skill match
    matched_skills = required_skills.intersection(candidate_skills)
    missing_skills = required_skills - candidate_skills
    
    skill_score = (len(matched_skills) / len(required_skills)) * 70 if required_skills else 70
    
    # Experience score (assuming 0-10+ years)
    exp = candidate.get("exp", 0)
    if exp >= 5:
        exp_score = 30
    elif exp >= 3:
        exp_score = 20
    elif exp >= 1:
        exp_score = 10
    else:
        exp_score = 0
    
    total_score = skill_score + exp_score
    
    # Determine match reason
    if total_score >= 80:
        reason = "Strong match - recommend interview"
    elif total_score >= 60:
        reason = "Potential match - consider screening"
    elif total_score >= 40:
        reason = "Weak match - keep as backup"
    else:
        reason = "Not recommended"
    
    return {
        "score": round(total_score, 2),
        "missing_skills": list(missing_skills),
        "matched_skills": list(matched_skills),
        "reason": reason
    }


def auto_screen_candidates(candidates: List[dict], job: dict, threshold: float = 60) -> List[dict]:
    """
    Automatically screen candidates and return only those above threshold.
    """
    screened = []
    for candidate in candidates:
        if candidate.get("job_id") != job.get("id"):
            continue
        match_result = calculate_match_score(candidate, job)
        candidate["match_score"] = match_result["score"]
        candidate["match_reason"] = match_result["reason"]
        candidate["missing_skills"] = match_result["missing_skills"]
        
        if match_result["score"] >= threshold:
            screened.append(candidate)
    
    # Sort by match score (highest first)
    screened.sort(key=lambda x: x["match_score"], reverse=True)
    return screened


def rank_candidates_for_job(candidates: List[dict], job: dict) -> List[dict]:
    """
    Rank all candidates for a job by match score (no threshold).
    """
    ranked = []
    for candidate in candidates:
        if candidate.get("job_id") != job.get("id"):
            continue
        match_result = calculate_match_score(candidate, job)
        candidate_with_score = candidate.copy()
        candidate_with_score["match_score"] = match_result["score"]
        candidate_with_score["match_reason"] = match_result["reason"]
        candidate_with_score["missing_skills"] = match_result["missing_skills"]
        candidate_with_score["matched_skills"] = match_result["matched_skills"]
        ranked.append(candidate_with_score)
    
    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked

if __name__ == "__main__":
    from data import jobs, candidates
    
    job = jobs[1]
    print(f"Testing job: {job['title']}")
    print("-" * 40)
    
    screened = auto_screen_candidates(candidates, job, threshold=60)
    for c in screened:
        print(f"{c['name']} - Score: {c['match_score']} - {c['match_reason']}")