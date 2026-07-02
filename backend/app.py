import os
import re
import sys
import pdfplumber
from ai_analyzer import analyze_all_projects, calculate_relevance_bonus, evaluate_skills_sufficiency, evaluate_experience

# Force UTF-8 output on Windows to prevent UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# pyrefly: ignore [missing-import]
from sumy.parsers.plaintext import PlaintextParser
# pyrefly: ignore [missing-import]
from sumy.nlp.tokenizers import Tokenizer
# pyrefly: ignore [missing-import]
from sumy.summarizers.text_rank import TextRankSummarizer

# Dictionary defining the required skills for different job roles
roles = {
    "data analyst": ["python", "sql", "excel", "power bi", "tableau", "pandas", "numpy"],
    "ai/ml": ["python", "machine learning", "nlp", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"],
    "frontend": ["html", "css", "javascript", "react", "git"],
    "sde": ["java", "python", "c++", "sql", "git", "dsa"],
    "backend": ["python", "java", "node.js", "django", "flask", "sql", "nosql", "api", "aws"],
    "fullstack": ["html", "css", "javascript", "react", "node.js", "python", "sql", "git"],
    "devops": ["aws", "azure", "docker", "kubernetes", "ci/cd", "linux", "jenkins", "terraform", "bash"],
    "product manager": ["agile", "scrum", "jira", "product strategy", "user research", "roadmap", "leadership"],
    "marketing": ["seo", "content marketing", "social media", "google analytics", "email marketing", "copywriting"],
    "sales": ["b2b", "crm", "lead generation", "cold calling", "negotiation", "salesforce", "communication"],
    "hr": ["recruitment", "onboarding", "employee relations", "performance management", "hr policies", "communication"],
    "business analyst": ["requirements gathering", "sql", "excel", "data analysis", "agile", "stakeholder management"]
}

def extract_text(pdf_file):
    """Extracts all text from a given PDF file and returns it in lowercase."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except FileNotFoundError:
        print(f"Error: The file {pdf_file} was not found.")
        return ""
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

    return text.lower()


def extract_email(text):
    """Finds and extracts an email address from the text using a regular expression."""
    # Search for an email pattern (e.g., example@domain.com)
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)

    # If an email is found, return the matched string
    if email:
        return email.group()

    # If no email is found, return an empty string
    return ""


def extract_phone(text):
    """Finds and extracts an Indian phone number from the text using a regular expression."""
    # Search for a 10-digit number, optionally starting with +91 (Indian country code)
    phone = re.search(r'(\+91\s?)?[6-9]\d{9}', text)

    # If a phone number is found, return the matched string
    if phone:
        return phone.group()

    # If no phone number is found, return an empty string
    return ""


def get_required_skills(job_role):
    """Returns the list of required skills based on the user's selected job role."""
    # Check if the role is related to AI/ML and return the matching skills list
    if job_role in ["ai/ml", "ai", "ml"]:
        return roles["ai/ml"]

    # Check for Data Analyst roles
    elif job_role in ["data analyst", "data", "analyst"]:
        return roles["data analyst"]

    # Check for Frontend roles
    elif job_role in ["frontend", "web", "frontend developer"]:
        return roles["frontend"]

    # Check for Software Development Engineer (SDE) roles
    elif job_role in ["sde", "software", "engineer"]:
        return roles["sde"]

    # Check for Backend roles
    elif job_role in ["backend", "backend developer"]:
        return roles["backend"]
        
    # Check for Full Stack roles
    elif job_role in ["fullstack", "full stack developer", "full stack"]:
        return roles["fullstack"]
        
    # Check for DevOps roles
    elif job_role in ["devops", "devops engineer"]:
        return roles["devops"]
        
    # Check for Product Manager roles
    elif job_role in ["product manager", "pm", "product"]:
        return roles["product manager"]
        
    # Check for Marketing roles
    elif job_role in ["marketing", "digital marketing"]:
        return roles["marketing"]
        
    # Check for Sales roles
    elif job_role in ["sales", "sales executive", "business development"]:
        return roles["sales"]
        
    # Check for HR roles
    elif job_role in ["hr", "human resources", "recruiter", "talent acquisition"]:
        return roles["hr"]
        
    # Check for Business Analyst roles
    elif job_role in ["business analyst", "ba"]:
        return roles["business analyst"]

    # If the role doesn't match anything, return None
    return None


def extract_skills_section(text):
    """Extracts only the 'Skills' section from the resume text to avoid false positives."""
    lines = text.split('\n') # Split the entire text into individual lines
    skills_text = [] # List to hold the lines that belong to the skills section
    in_skills = False # Flag to track if we are currently reading the skills section
    
    # Common headers that might appear after the skills section, signaling its end
    headers = [
        "education", "experience", "projects", "certifications", "languages", 
        "work experience", "professional experience", "work history", 
        "employment", "achievements", "summary", "profile", "objective", "publications", "interests", "hobbies"
    ]
    
    # Iterate through every line in the resume
    for line in lines:
        cleaned_line = line.strip() # Remove leading/trailing whitespaces
        # Remove trailing colons from headers (e.g., "Education:" -> "Education")
        if cleaned_line.endswith(':'):
            cleaned_line = cleaned_line[:-1].strip()
            
        # Check if the line is the start of the skills section
        if cleaned_line in ["skills", "technical skills", "core competencies", "technical expertise",
                            "technologies", "tech stack", "programming languages"]:
            in_skills = True # We found the skills section, start tracking
            continue # Skip the header line itself
            
        # If we are currently inside the skills section
        if in_skills:
            # If we encounter another section header, we know the skills section is over
            if cleaned_line in headers:
                break
            # Add the current line to our skills text
            skills_text.append(line)
            
    # If we successfully captured lines, combine them into a single string and return
    if skills_text:
        return "\n".join(skills_text)
        
    # Fallback: If line-by-line parsing failed, try simple substring extraction based on keywords
    start_idx = text.find("technical skills")
    if start_idx == -1:
        start_idx = text.find("skills")
        
    # If a keyword was found
    if start_idx != -1:
        end_idx = len(text) # Assume the section goes to the end of the file by default
        # Search for any of the common headers to find where the skills section ends
        for h in headers:
            # Look for header at the start of a line to avoid false positives (e.g., matching the word "education" inside a sentence)
            idx = text.find("\n" + h)
            # If the header is found after the start index and before the current end index
            if idx != -1 and idx > start_idx and idx < end_idx:
                end_idx = idx # Update the end index
        return text[start_idx:end_idx] # Return the text strictly within these bounds
        
    # If all extraction attempts fail, return the entire text as a last resort
    return text

def extract_experience_section(text):
    """Extracts the 'Experience' section from the resume text."""
    lines = text.split('\n')
    exp_text = []
    in_exp = False
    
    headers = [
        "education", "skills", "projects", "certifications", "languages", 
        "achievements", "summary", "profile", "objective", "publications", "interests", "hobbies",
        "technical skills"
    ]
    
    exp_headers = [
        "experience", "work experience", "professional experience", "work history", "employment", "employment history"
    ]
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if cleaned_line.endswith(':'):
            cleaned_line = cleaned_line[:-1].strip()
            
        if cleaned_line in exp_headers:
            in_exp = True
            continue
            
        if in_exp:
            if cleaned_line in headers:
                break
            exp_text.append(line)
            
    if exp_text:
        return "\n".join(exp_text)
        
    return ""


def extract_projects_section(text):

    project_headers = [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ]

    end_headers = [
        "education", "experience", "skills", "certifications",
        "achievements", "languages", "work experience",
        "professional experience", "work history", "employment"
    ]

    lines = text.split("\n")

    projects = []
    in_projects = False

    for line in lines:

        clean = line.strip().lower()

        if clean.endswith(":"):
            clean = clean[:-1]

        if clean in project_headers:
            in_projects = True
            continue

        if in_projects:
            # Check if this line starts a new section (partial match)
            if any(h in clean for h in end_headers):
                break

            projects.append(line)

    return "\n".join(projects)

def summarize_project(project_text):

    parser = PlaintextParser.from_string(
        project_text,
        Tokenizer("english")
    )

    summarizer = TextRankSummarizer()

    summary = ""

    for sentence in summarizer(parser.document, 1):
        summary += str(sentence)

    return summary


# Map experience level keys to display names
EXPERIENCE_LEVEL_NAMES = {
    "internship": "Internship",
    "entry": "Entry Level",
    "junior": "Junior",
    "mid": "Mid Level",
    "senior": "Senior",
    "lead": "Lead / Staff",
    "expert": "Industry Expert"
}

def analyze_resume(pdf_file, job_role, experience_level="entry"):
    """Main function that orchestrates the resume analysis process."""
    # 1. Extract all text from the PDF
    text = extract_text(pdf_file)

    # 2. Extract contact information
    email = extract_email(text)
    phone = extract_phone(text)

    # 3. Retrieve the required skills for the given role
    required_skills = get_required_skills(job_role)

    # If the user entered an invalid role, exit the function
    if required_skills is None:
        print("Invalid role selected.")
        return

    # 4. Isolate the 'Skills' section from the resume to analyze it accurately
    skills_text = extract_skills_section(text)
    projects_text = extract_projects_section(text)

    found_skills = []

    # 5. Check which required skills are present in the skills section
    for skill in required_skills:
        # Create a regex pattern to match whole words only (e.g., matching "C++" but not part of a larger word)
        # re.escape ensures special characters like '+' are treated as literals
        pattern = rf"\b{re.escape(skill)}\b"

        # If the skill pattern is found in the skills section
        if re.search(pattern, skills_text):
            found_skills.append(skill) # Add it to our found list

    missing_skills = []

    # 6. Determine which required skills were not found
    for skill in required_skills:
        if skill not in found_skills:
            missing_skills.append(skill) # Add it to our missing list

    # 7. Calculate the ATS (Applicant Tracking System) score as a percentage
    score = (len(found_skills) / len(required_skills)) * 100

    # if no skills section found print there is no skills in resume:
    if not skills_text:
        print("No skills section found in the resume.")
        return {
            "error": "No skills section found"
        }


     
    # 8. Print the generated report to the console
    print("\n" + "=" * 40)
    print("ATS RESUME ANALYSIS REPORT")
    print("=" * 40)

    print(f"\nRole: {job_role}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")

    print("\nMatched Skills:")
    for skill in found_skills:
        print(f"  [+] {skill}")

    print("\nMissing Skills:")
    for skill in missing_skills:
        print(f"  [-] {skill}")

    print("Projects:")
    project_lines = projects_text.split("\n") if projects_text else []
    
    valid_projects = []
    project_blocks = {}
    current_proj = None
    
    for line in project_lines:
        line = line.strip()
        if not line:
            continue
            
        is_bullet = line.startswith(("-", "•", "*", "▪", "✓"))
        
        # A project title is identified by the pipe '|' separator
        # e.g., "Sentiment Analysis using NLP | Personal Project | 2025"
        # Exclude education/degree lines that also use '|'
        education_keywords = [
            "bachelor", "master", "b.tech", "btech", "m.tech", "mtech",
            "b.e.", "m.e.", "b.sc", "m.sc", "phd", "diploma", "degree",
            "engineering", "university", "institute", "college"
        ]
        line_lower = line.lower()
        is_education = any(kw in line_lower for kw in education_keywords)
        is_title = not is_bullet and "|" in line and not is_education
                
        if is_title:
            current_proj = line
            valid_projects.append(current_proj)
            project_blocks[current_proj] = []
        elif current_proj:
            project_blocks[current_proj].append(line)

    project_summaries = {}
    project_count = len(valid_projects)
    
    for p in valid_projects:
        print(f"  [+] {p}")
        # Summarize just the text belonging to this specific project
        proj_text = "\n".join(project_blocks.get(p, []))
        if proj_text.strip():
            summary = summarize_project(proj_text)
            if summary:
                print(f"  Summary: {summary}")
            project_summaries[p] = summary

    # 9. AI-powered project relevance analysis
    print("\nAnalyzing project relevance with AI...")
    project_relevance, ai_available = analyze_all_projects(valid_projects, project_blocks, job_role, experience_level)
    
    # 9b. AI-powered skills evaluation
    print("\nEvaluating skills sufficiency with AI...")
    skills_evaluation = evaluate_skills_sufficiency(found_skills, missing_skills, job_role, experience_level)
    
    # 9c. AI-powered experience evaluation
    print("Evaluating actual experience against target level with AI...")
    experience_text = extract_experience_section(text)
    experience_evaluation = evaluate_experience(experience_text, experience_level)
    
    # 10. Calculate project bonus (AI-weighted or flat fallback)
    project_bonus, used_ai = calculate_relevance_bonus(project_relevance, project_count)
    score += project_bonus
    
    if used_ai:
        print(f"  AI Relevance Bonus: +{project_bonus} points")
    else:
        print(f"  Flat Project Bonus: +{project_bonus} points (AI unavailable)")

    # Cap score at 100%
    score = min(score, 100.0)

    # Display the score formatted to 0 decimal places
    print(f"\nATS Score: {score:.0f}%")
    
    # Return the analysis results as a dictionary so it can be used by the Flask API
    level_display = EXPERIENCE_LEVEL_NAMES.get(experience_level, experience_level)
    return {
        "role": job_role,
        "experience_level": level_display,
        "email": email,
        "phone": phone,
        "matched_skills": found_skills,
        "missing_skills": missing_skills,
        "skills_evaluation": skills_evaluation,
        "experience_evaluation": experience_evaluation,
        "projects": valid_projects,
        "project_summaries": project_summaries,
        "project_relevance": project_relevance,
        "ai_available": ai_available,
        "ats_score": round(score, 0)
    }


# --- Main Execution Block ---

# Only run this interactive block if the script is executed directly (not imported)
if __name__ == "__main__":
    # Prompt the user for the PDF file name
    pdf_file = input(
        "Enter PDF file name: "
    ).strip()
    # Automatically append .pdf extension if the user forgot it
    if not pdf_file.endswith(".pdf"):
        pdf_file += ".pdf"
    
    # Prompt the user for the target role they are applying for
    job_role = input(
        "Enter target role (AI/ML, Data Analyst, Frontend, SDE): "
    ).lower() # Convert to lowercase for consistent matching
    
    # Construct the absolute path to the PDF file (assumes it's in the same directory as this script)
    pdf_path = os.path.join(
        os.path.dirname(__file__),
        pdf_file
    )
    
    # Run the resume analyzer with the provided inputs
    analyze_resume(
        pdf_path,
        job_role
    )
