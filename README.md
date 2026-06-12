# ATS Resume Analyzer

A web-based ATS (Applicant Tracking System) Resume Analyzer built using Python, Flask, HTML, CSS, and PDF processing techniques.

## Features

* Upload PDF resumes
* Extract email and phone number automatically
* Role-based analysis for:

  * AI/ML Engineer
  * Data Analyst
  * Frontend Developer
  * Software Development Engineer (SDE)

* Skill matching based on target role
* Missing skill detection
* ATS score calculation
* Personalized recommendations
* Modern and responsive user interface

## Tech Stack

### Backend

* Python
* Flask
* PDFPlumber
* Regular Expressions (Regex)

### Frontend

* HTML
* CSS

## How It Works

1. Upload a resume in PDF format.
2. Select the target job role.
3. The application extracts resume content.
4. Skills are matched against role-specific requirements.
5. ATS score is calculated.
6. Missing skills and recommendations are displayed.

## Project Structure

backend/
│
├── app.py
├── flask_app.py
├── templates/
│ ├── index.html
│ └── result.html
├── static/
│ ├── style.css
│ └── assets/
└── uploads/

## Installation

1. Clone the repository

git clone https://github.com/Nickyit/ATS-Resume-Analyzer.git

2. Navigate to the project directory

cd ATS-Resume-Analyzer

3. Create a virtual environment

python -m venv .venv

4. Activate the virtual environment

Windows:
.venv\Scripts\activate

5. Install dependencies

pip install -r requirements.txt

6. Run the application

python flask_app.py


## Future Improvements

* Resume section extraction
* Project and experience analysis
* Resume-job description matching
* AI-powered resume feedback
* Resume improvement suggestions
* Support for DOCX resumes

## Author

Nikita Digodiya

Built as a learning project to understand Python, Flask, PDF processing, and web application development.
