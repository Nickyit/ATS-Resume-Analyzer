import os
import tempfile
from flask import Flask, render_template, request
from app import analyze_resume
import nltk

# Download NLTK data required by Sumy for Vercel
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


# Point Flask to the 'frontend' directory for HTML templates and static files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, template_folder=frontend_dir, static_folder=frontend_dir, static_url_path='/static')

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Ensure a file is provided
        if 'resume' not in request.files:
            return "No file uploaded", 400
            
        file = request.files['resume']
        if file.filename == '':
            return "No selected file", 400
            
        # Get the selected role from the form dropdown
        role = request.form.get('role')
        if not role:
            return "No role selected", 400
        
        # Get the selected experience level
        experience_level = request.form.get('experience_level', 'entry')
            
        # Save the uploaded file to a temporary location
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            # Call the analyzer with the uploaded file, selected role, and experience level
            result = analyze_resume(temp_path, role, experience_level)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Render the HTML template and pass the result data to it
        return render_template("resume.html", data=result)

    # If it's a GET request, just render the upload form
    return render_template("resume.html", data=None)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)