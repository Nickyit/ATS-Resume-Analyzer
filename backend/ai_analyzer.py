"""
AI-powered project relevance analyzer using Google Gemini API.
Analyzes how relevant each resume project is to the target job role.
Falls back gracefully if the API key is missing or the call fails.
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# The prompt template for project relevance analysis
RELEVANCE_PROMPT = """You are an ATS Resume Analyzer.

Target Role:
{job_role}

Experience Level:
{experience_level}

Project Description:
{project_text}

Your task:

1. Decide if this project is relevant to the target role at the specified experience level.
2. Give a relevance score from 0 to 100.
3. Clearly state:
   * Relevant
   * Partially Relevant
   * Not Relevant
4. Give a short explanation considering the experience level.
5. Mention which skills or technologies support your decision.

Return ONLY in this format:

Relevance: Relevant / Partially Relevant / Not Relevant

Score: XX/100

Reason:
<2-3 sentences>

Relevant Skills:
* skill1
* skill2
* skill3"""

# The prompt template for evaluating skills sufficiency
SKILLS_EVALUATION_PROMPT = """You are an ATS Resume Analyzer.

Target Role:
{job_role}

Experience Level:
{experience_level}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Your task:
1. Evaluate if the matched skills are sufficient for this role at this experience level.
2. Consider the missing skills: are they critical dealbreakers, or nice-to-haves that can be learned?
3. Provide a brief 2-3 sentence analysis of the candidate's skill readiness for this specific level.
4. Conclude with a clear verdict label.

Return ONLY in this format:

Verdict: Sufficient / Needs Improvement / Insufficient

Analysis:
<2-3 sentences evaluating readiness considering the experience level>"""

# The prompt template for evaluating experience matching
EXPERIENCE_EVALUATION_PROMPT = """You are an ATS Resume Analyzer.

Target Experience Level:
{experience_level}

Extracted Experience Section from Resume:
{experience_text}

Your task:
1. Carefully read the candidate's work history.
2. Calculate the total years of relevant experience they have based on the dates provided.
3. Compare their total years of experience against the Target Experience Level.
4. Conclude if they meet the requirement.
5. Provide a brief 2-3 sentence analysis of their work history duration.

If the Target Experience Level is 'Junior (1-3 years)' and the candidate does not have at least 2 years of experience or is missing their last experience information, you MUST explicitly output this exact phrase in the Analysis:
"experience of two years is not present in your resume"

Return ONLY in this format:

Total Years: <number>
Verdict: Match / Underqualified / Overqualified
Analysis:
<2-3 sentences explaining the calculation and comparison>"""


# Map internal role keys to human-readable role names for the prompt
ROLE_DISPLAY_NAMES = {
    "ai/ml": "AI / ML Engineer",
    "data analyst": "Data Analyst",
    "frontend": "Frontend Developer",
    "sde": "Software Development Engineer (SDE)"
}

# Map experience level keys to display names for the prompt
EXPERIENCE_LEVEL_DISPLAY = {
    "internship": "Internship / Trainee",
    "entry": "Entry Level (0-1 years)",
    "junior": "Junior (1-3 years)",
    "mid": "Mid Level (3-5 years)",
    "senior": "Senior (5-8 years)",
    "lead": "Lead / Staff (8+ years)",
    "expert": "Industry Expert / Principal"
}


def _get_gemini_client():
    """Creates and returns a Gemini API client. Returns None if API key is missing."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. AI project analysis disabled.")
        return None
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except ImportError:
        print("Warning: google-genai package not installed. AI project analysis disabled.")
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini client: {e}")
        return None


def parse_ai_response(response_text):
    """
    Parses the structured AI response to extract relevance category, score, reason, and skills.
    
    Expected format:
        Relevance: Relevant / Partially Relevant / Not Relevant
        Score: XX/100
        Reason:
        <text>
        Relevant Skills:
        * skill1
        * skill2
    
    Returns a dict with keys: category, score, reason, relevant_skills
    Returns None if parsing fails.
    """
    try:
        # Extract the relevance category (e.g., "Relevance: Relevant")
        category = "Unknown"
        category_match = re.search(
            r'Relevance:\s*(Relevant|Partially\s+Relevant|Not\s+Relevant)',
            response_text,
            re.IGNORECASE
        )
        if category_match:
            category = category_match.group(1).strip().title()
        
        # Extract the score (e.g., "Score: 85/100" or "Score: 85%")
        score = 0
        score_match = re.search(r'Score:\s*(\d+)\s*[/%]', response_text, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
        
        # Clamp score to 0-100
        score = max(0, min(100, score))
        
        # Extract the reason section
        reason = ""
        reason_match = re.search(
            r'Reason:\s*\n(.*?)(?=\nRelevant\s+Skills:|$)',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        if reason_match:
            reason = reason_match.group(1).strip()
        
        # Extract relevant skills (lines starting with "*", "-", or "•")
        skills = []
        skills_match = re.search(
            r'Relevant\s+Skills:\s*\n(.*)',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        if skills_match:
            skills_text = skills_match.group(1)
            skills = [
                line.strip().lstrip("-•*").strip()
                for line in skills_text.split("\n")
                if line.strip() and line.strip().startswith(("-", "•", "*"))
            ]
        
        return {
            "category": category,
            "score": score,
            "reason": reason,
            "relevant_skills": skills
        }
    except Exception as e:
        print(f"Warning: Failed to parse AI response: {e}")
        return None


def analyze_project_relevance(project_title, project_text, job_role, experience_level="entry"):
    """
    Analyzes how relevant a single project is to the target job role using Gemini AI.
    
    Args:
        project_title: The title/name of the project
        project_text: The full description text of the project
        job_role: The target job role key (e.g., "ai/ml", "sde")
        experience_level: The experience level key (e.g., "internship", "senior")
    
    Returns:
        A dict with keys: category, score, reason, relevant_skills
        Returns None if the analysis fails or API is unavailable.
    """
    client = _get_gemini_client()
    if client is None:
        return None
    
    # Build the full project context (title + description)
    full_project_text = f"{project_title}\n{project_text}" if project_text else project_title
    
    # Get display names for role and level
    role_name = ROLE_DISPLAY_NAMES.get(job_role, job_role)
    level_name = EXPERIENCE_LEVEL_DISPLAY.get(experience_level, experience_level)
    
    # Fill in the prompt template
    prompt = RELEVANCE_PROMPT.format(
        job_role=role_name,
        experience_level=level_name,
        project_text=full_project_text
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Parse the response
        result = parse_ai_response(response.text)
        if result:
            print(f"  AI Relevance for '{project_title[:40]}...': {result['score']}%")
        return result
        
    except Exception as e:
        print(f"Warning: AI analysis failed for project '{project_title[:40]}': {e}")
        return None


def analyze_all_projects(valid_projects, project_blocks, job_role, experience_level="entry"):
    """
    Analyzes relevance for all projects. Returns a dict mapping project titles to their relevance data.
    
    Args:
        valid_projects: List of project title strings
        project_blocks: Dict mapping project titles to their description lines
        job_role: Target job role key
        experience_level: Experience level key
    
    Returns:
        Tuple of (project_relevance dict, ai_available bool)
        project_relevance: {project_title: {score, reason, relevant_skills}} or empty dict
        ai_available: True if AI analysis was successfully used
    """
    if not valid_projects:
        return {}, False
    
    project_relevance = {}
    ai_available = False
    
    for project in valid_projects:
        proj_text = "\n".join(project_blocks.get(project, []))
        result = analyze_project_relevance(project, proj_text, job_role, experience_level)
        
        if result is not None:
            project_relevance[project] = result
            ai_available = True
        # If one project fails, we continue trying the rest
    
    return project_relevance, ai_available


def calculate_relevance_bonus(project_relevance, project_count):
    """
    Calculates the ATS bonus score based on AI relevance analysis.
    
    If AI analysis is available:
        Bonus = (average_relevance / 100) * 15 (max 15 points)
    
    If AI analysis is not available (fallback):
        +5 for 1-2 projects, +10 for 3+ projects
    
    Args:
        project_relevance: Dict of project relevance results (may be empty)
        project_count: Total number of projects found
    
    Returns:
        Tuple of (bonus_score, used_ai)
    """
    if project_relevance:
        # AI-powered scoring
        scores = [data["score"] for data in project_relevance.values()]
        avg_relevance = sum(scores) / len(scores) if scores else 0
        bonus = (avg_relevance / 100) * 15
        return round(bonus, 1), True
    else:
        # Fallback to flat bonus
        if project_count >= 3:
            return 10, False
        elif project_count >= 1:
            return 5, False
        return 0, False

def evaluate_skills_sufficiency(matched_skills, missing_skills, job_role, experience_level="entry"):
    """
    Evaluates if the candidate's skills are sufficient for the role and experience level.
    """
    client = _get_gemini_client()
    if client is None:
        return None
        
    role_name = ROLE_DISPLAY_NAMES.get(job_role, job_role)
    level_name = EXPERIENCE_LEVEL_DISPLAY.get(experience_level, experience_level)
    
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"
    
    prompt = SKILLS_EVALUATION_PROMPT.format(
        job_role=role_name,
        experience_level=level_name,
        matched_skills=matched_str,
        missing_skills=missing_str
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Parse the response
        text = response.text
        verdict = "Unknown"
        analysis = ""
        
        verdict_match = re.search(r'Verdict:\s*(Sufficient|Needs Improvement|Insufficient)', text, re.IGNORECASE)
        if verdict_match:
            verdict = verdict_match.group(1).strip().title()
            
        analysis_match = re.search(r'Analysis:\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
        if analysis_match:
            analysis = analysis_match.group(1).strip()
            
        return {
            "verdict": verdict,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Warning: AI skills evaluation failed: {e}")
        return None

def evaluate_experience(experience_text, experience_level="entry"):
    """
    Evaluates if the candidate's actual years of experience matches the selected level.
    """
    level_name = EXPERIENCE_LEVEL_DISPLAY.get(experience_level, experience_level)
    
    # 1. If experience text is empty or missing
    if not experience_text or not experience_text.strip():
        if experience_level == "junior":
            return {
                "total_years": "0",
                "verdict": "Underqualified",
                "analysis": "experience of two years is not present in your resume"
            }
        return {
            "total_years": "0",
            "verdict": "Underqualified",
            "analysis": "No experience section was found in the resume to evaluate."
        }
        
    client = _get_gemini_client()
    if client is None:
        # Fallback when AI is offline
        if experience_level == "junior":
            # Simple heuristic check for "2 years" or "two years"
            has_two_years = False
            if re.search(r'(2|3|4|5|two|three|four|five)\s+years?', experience_text, re.IGNORECASE):
                has_two_years = True
            
            if not has_two_years:
                return {
                    "total_years": "0-1",
                    "verdict": "Underqualified",
                    "analysis": "experience of two years is not present in your resume"
                }
        return {
            "total_years": "Unknown",
            "verdict": "Match",
            "analysis": f"Evaluated against target level {level_name} (AI analysis offline)."
        }
    
    prompt = EXPERIENCE_EVALUATION_PROMPT.format(
        experience_level=level_name,
        experience_text=experience_text
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        text = response.text
        total_years = "Unknown"
        verdict = "Unknown"
        analysis = ""
        
        years_match = re.search(r'Total Years:\s*(.*)', text, re.IGNORECASE)
        if years_match:
            total_years = years_match.group(1).strip()
            
        verdict_match = re.search(r'Verdict:\s*(Match|Underqualified|Overqualified)', text, re.IGNORECASE)
        if verdict_match:
            verdict = verdict_match.group(1).strip().title()
            
        analysis_match = re.search(r'Analysis:\s*\n(.*)', text, re.DOTALL | re.IGNORECASE)
        if analysis_match:
            analysis = analysis_match.group(1).strip()
            
        # Post-processing: If junior level and underqualified, force the exact string in analysis
        if experience_level == "junior" and verdict == "Underqualified":
            analysis = "experience of two years is not present in your resume"
            
        return {
            "total_years": total_years,
            "verdict": verdict,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Warning: AI experience evaluation failed: {e}")
        if experience_level == "junior":
            return {
                "total_years": "0-1",
                "verdict": "Underqualified",
                "analysis": "experience of two years is not present in your resume"
            }
        return {
            "total_years": "Unknown",
            "verdict": "Underqualified",
            "analysis": f"AI evaluation failed: {str(e)}"
        }

