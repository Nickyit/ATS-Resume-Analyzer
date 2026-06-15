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

Your task is to analyze whether a project is relevant to a target job role.

Target Role:
{job_role}

Project Description:
{project_text}

Instructions:
1. Read the project description carefully.
2. Decide how relevant the project is to the target role.
3. Give a relevance score between 0 and 100.
4. Explain the reason in 2-3 simple sentences.
5. Mention which technologies or concepts make the project relevant.
6. Keep the response concise.

Output Format:

Relevance Score: <score>%

Reason:
<short explanation>

Relevant Skills:
- skill 1
- skill 2
- skill 3"""

# Map internal role keys to human-readable role names for the prompt
ROLE_DISPLAY_NAMES = {
    "ai/ml": "AI / ML Engineer",
    "data analyst": "Data Analyst",
    "frontend": "Frontend Developer",
    "sde": "Software Development Engineer (SDE)"
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
    Parses the structured AI response to extract relevance score, reason, and skills.
    
    Expected format:
        Relevance Score: <number>%
        Reason:
        <text>
        Relevant Skills:
        - skill1
        - skill2
    
    Returns a dict with keys: score, reason, relevant_skills
    Returns None if parsing fails.
    """
    try:
        # Extract the relevance score (e.g., "Relevance Score: 85%")
        score_match = re.search(r'Relevance\s+Score:\s*(\d+)\s*%', response_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0
        
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
        
        # Extract relevant skills (lines starting with "- ")
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
            "score": score,
            "reason": reason,
            "relevant_skills": skills
        }
    except Exception as e:
        print(f"Warning: Failed to parse AI response: {e}")
        return None


def analyze_project_relevance(project_title, project_text, job_role):
    """
    Analyzes how relevant a single project is to the target job role using Gemini AI.
    
    Args:
        project_title: The title/name of the project
        project_text: The full description text of the project
        job_role: The target job role key (e.g., "ai/ml", "sde")
    
    Returns:
        A dict with keys: score, reason, relevant_skills
        Returns None if the analysis fails or API is unavailable.
    """
    client = _get_gemini_client()
    if client is None:
        return None
    
    # Build the full project context (title + description)
    full_project_text = f"{project_title}\n{project_text}" if project_text else project_title
    
    # Get the display name for the role
    role_name = ROLE_DISPLAY_NAMES.get(job_role, job_role)
    
    # Fill in the prompt template
    prompt = RELEVANCE_PROMPT.format(
        job_role=role_name,
        project_text=full_project_text
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
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


def analyze_all_projects(valid_projects, project_blocks, job_role):
    """
    Analyzes relevance for all projects. Returns a dict mapping project titles to their relevance data.
    
    Args:
        valid_projects: List of project title strings
        project_blocks: Dict mapping project titles to their description lines
        job_role: Target job role key
    
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
        result = analyze_project_relevance(project, proj_text, job_role)
        
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
