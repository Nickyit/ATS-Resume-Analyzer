
import pdfplumber # Used to extract text from PDF files
import re # Used for regular expressions (pattern matching for emails, phones, skills)
import os # Used for interacting with the operating system (like getting file paths)

# Print the current working directory to debug file path issues
print(os.getcwd())

# Dictionary defining the required skills for different job roles
roles = {
    "data analyst": ["python", "sql", "excel", "power bi", "tableau", "pandas", "numpy"],
    "ai/ml": ["python", "machine learning", "nlp", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy"],
    "frontend": ["html", "css", "javascript", "react", "git"],
    "sde": ["java", "python", "c++", "sql", "git", "dsa"]
}

def extract_text(pdf_file):
    """Extracts all text from a given PDF file and returns it in lowercase."""
    text = "" # Initialize an empty string to hold the extracted text

    # Open the PDF file using pdfplumber
    with pdfplumber.open(pdf_file) as pdf:
        # Loop through each page in the PDF
        for page in pdf.pages:
            page_text = page.extract_text() # Extract text from the current page

            # If text is found on the page, append it to the overall text
            if page_text:
                text += page_text

    # Return the entire extracted text converted to lowercase for easier matching
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
        if cleaned_line in ["skills", "technical skills", "core competencies", "technologies", "technical proficiencies"]:
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


def analyze_resume(pdf_file, job_role):
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

    # 8. Print the generated report to the console
    print("\n" + "=" * 40)
    print("ATS RESUME ANALYSIS REPORT")
    print("=" * 40)

    print(f"\nRole: {job_role}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")

    print("\nMatched Skills:")
    for skill in found_skills:
        print(f"✓ {skill}")

    print("\nMissing Skills:")
    for skill in missing_skills:
        print(f"✗ {skill}")

    # Display the score formatted to 0 decimal places
    print(f"\nATS Score: {score:.0f}%")
    
    # Return the analysis results as a dictionary so it can be used by the Flask API
    return {
        "role": job_role,
        "email": email,
        "phone": phone,
        "matched_skills": found_skills,
        "missing_skills": missing_skills,
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
