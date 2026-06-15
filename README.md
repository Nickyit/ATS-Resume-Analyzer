# ATS Resume Analyzer

A web-based ATS (Applicant Tracking System) Resume Analyzer built using Python, Flask, HTML, CSS, and PDF processing techniques. Upload your resume, select a target role, and get an instant ATS compatibility score with actionable feedback.

---

## ✨ Features

### Core Analysis
- 📄 Upload PDF resumes
- 📧 Automatic email and phone number extraction
- 🎯 Role-based skill analysis for:
  - AI / ML Engineer
  - Data Analyst
  - Frontend Developer
  - Software Development Engineer (SDE)
- ✅ Skill matching against role-specific requirements
- ❌ Missing skill detection
- 📊 ATS score calculation (percentage-based)

### Project Analysis
- 🗂️ Automatic extraction of the **Projects** section from resumes
- 🧠 **NLP-powered project summarization** using TextRank (via Sumy)
- 🏷️ Smart project title detection (filters out education/degree lines)
- 📋 Per-project summary displayed in the results

### AI-Powered Relevance Analysis *(New)*
- 🤖 **Gemini AI** analyzes each project's relevance to the target role
- 🎯 **Relevance score (0–100%)** per project with color-coded badges
- 💡 AI-generated **reasoning** explaining why the project is relevant
- 🏷️ **Relevant skills** extracted from each project by AI
- 📈 **Weighted ATS bonus** based on average project relevance (up to +15 points)
- ⚡ **Graceful fallback** to flat scoring if API key is not configured

### User Interface
- 🌑 Modern dark-themed UI with glassmorphism effects
- 📱 Fully responsive design (mobile-friendly)
- 🎨 Gradient accents and smooth hover animations
- 🔵 Circular ATS score visualization with conic gradient
- 💜 Dedicated project cards with hover effects and summaries
- 🟢🟡🔴 Color-coded relevance badges with micro-animations

---

## 📸 Project Demo

### Homepage — Upload Resume
![Homepage Screenshot](screenshots/homepage.png)

> Upload your resume in PDF format, select a target job role, and get an instant ATS compatibility score with skill analysis and project summaries.

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python | Core language |
| Flask | Web framework & routing |
| PDFPlumber | PDF text extraction |
| Sumy (TextRank) | NLP-based project summarization |
| Google Gemini AI | AI-powered project relevance analysis |
| python-dotenv | Environment variable management |
| Regex | Contact info & pattern extraction |

### Frontend
| Technology | Purpose |
|---|---|
| HTML (Jinja2 templates) | Page structure & templating |
| CSS | Styling with CSS variables & glassmorphism |
| SVG Icons | Inline icons for UI elements |

---

## 🚀 How It Works

1. Upload a resume in **PDF format**.
2. Select the **target job role** from the dropdown.
3. The application extracts all text from the PDF.
4. **Skills** are matched against role-specific requirements.
5. **Projects** are extracted and summarized using NLP.
6. **Gemini AI** analyzes each project's relevance to the target role.
7. **ATS score** is calculated (skill match % + AI-weighted project bonus).
8. Results are displayed with matched skills, missing skills, project summaries, relevance scores, and recommendations.

---

## 📁 Project Structure

```
ATS-Resume-Analyzer/
├── backend/
│   ├── app.py              # Core analysis engine (skill matching, project extraction, NLP summarization)
│   ├── ai_analyzer.py       # AI-powered project relevance analysis (Gemini)
│   ├── flask_app.py         # Flask web server & routes
│   └── __pycache__/
├── frontend/
│   ├── resume.html          # Jinja2 template (upload form + results page)
│   ├── resume.css           # Dark theme styles with glassmorphism
│   └── resume.js            # Frontend JavaScript
├── screenshots/             # Project demo screenshots
│   └── homepage.png
├── .env.example             # API key template
├── .env                     # Your API keys (git-ignored)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Nickyit/ATS-Resume-Analyzer.git
   ```

2. **Navigate to the project directory**

   ```bash
   cd ATS-Resume-Analyzer
   ```

3. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

4. **Activate the virtual environment**

   ```bash
   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Set up your API key** *(for AI project analysis)*

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your [Google Gemini API key](https://aistudio.google.com/apikey) (free tier available):

   ```
   GEMINI_API_KEY=your_actual_api_key
   ```

   > **Note:** The app works without an API key — it will fall back to flat project scoring.

7. **Run the application**

   ```bash
   cd backend
   python flask_app.py
   ```

7. **Open in browser**

   Navigate to `http://localhost:5001`

---

## 📦 Dependencies

- Flask 3.1.3
- PDFPlumber 0.11.9
- pdfminer.six 20251230
- Werkzeug 3.1.8
- Jinja2 3.1.6
- Sumy (NLP summarization)
- google-genai (Gemini AI integration)
- python-dotenv (Environment variable management)

---

## 🗺️ Development Progress

- [x] PDF text extraction
- [x] Email & phone number extraction
- [x] Role-based skill matching (AI/ML, Data Analyst, Frontend, SDE)
- [x] ATS score calculation
- [x] Flask web interface with upload form
- [x] Modern dark-themed responsive UI
- [x] Project section extraction from resumes
- [x] NLP-powered project summarization (TextRank)
- [x] Bonus scoring for projects
- [x] Project cards with summaries in results UI
- [x] AI-powered project relevance analysis (Gemini)
- [x] Relevance-weighted ATS scoring with fallback
- [x] Color-coded relevance badges and skill tags
- [ ] Resume section extraction (Education, Experience, etc.)
- [ ] Experience analysis and scoring
- [ ] Resume-job description matching
- [ ] AI-powered resume feedback
- [ ] Resume improvement suggestions
- [ ] Support for DOCX resumes

---

## 🔮 Future Improvements

- Resume section extraction (Education, Experience, Summary)
- Work experience analysis and scoring
- Custom job description matching (paste a JD and compare)
- AI-powered feedback and improvement suggestions
- Support for DOCX and TXT resume formats
- Export analysis report as PDF
- Multi-language resume support

---

## 👩‍💻 Author

**Nikita Digodiya**

Built as a learning project to understand Python, Flask, PDF processing, NLP, and web application development.
