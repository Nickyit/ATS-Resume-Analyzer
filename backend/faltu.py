# name = input("Enter your name: ")
# print(f"Hello {name}, welcome to the resume analyzer\n")

# required_skills = ['python', 'cpp', 'sql', 'git', 'github']

# skills = input("Enter your Skills: ").split(",")

# skills = [skill.strip().lower() for skill in skills]
# matched = 0
# for skill in required_skills:
#     if skill in skills:
#         print(f"You have skill {skill}")
#         matched += 1
#     else:
#         print(f"You don't have skill {skill}")

# score = (matched / len(required_skills)) * 100

# print(f"\nMatched Skills: {matched}")
# print(f"ATS Score: {score:.0f}%")

# diff = list(set(required_skills) - set(skills))
# print("\nMissing Skills:")

# for skill in diff:
#     print("-", skill)


# if score >= 80:
#     print("Excellent Resume")
# elif score >= 60:
#     print("Good Resume")
# elif score >= 40:
#     print("Needs Improvement")
# else:
#     print("Poor ATS Score")

# projects = input("Are you work at any project ? (yes/no): ").lower().strip()

# if projects == "yes" or "y" or "yup":
#     print("Great !")
#     project = int(input("Enter the number of project you have done: "))
#     projects_dict = {}
#     for i in range(project):
#         project_name = input("Enter the project name: ")
#         projects_dict[f"Project {i+1}"] = project_name
#     print(f"\nYour projects are : {projects_dict}")
# else:
#     print("No problem , you will do it next time!")

# with open(os.path.join(os.path.dirname(__file__), "resume.txt") , 'r') as f:
#     text = f.read().lower()

# def extract_section(text, start_tag, end_tag):
#     start = text.find(start_tag)
#     end = text.find(end_tag)

#     if start == -1 or end == -1:
#         return ""

#     return text[start:end]

# #Technical skills Extraction
# skills_section = extract_section(text, "technical skills:", "education:")

# skills_lines = skills_section.split("\n")

# resume_skills = []

# for line in skills_lines:
#     line = line.strip("- ").strip()

#     if line and line != "technical skills:":
#         resume_skills.append(line)

# print(f"Your skills are {resume_skills}\n")

# #skills Matching
# required_skills = ['python', 'cpp', 'sql', 'git', 'github']

# matched = []
# missing = []

# matched_count = 0
# for skill in required_skills:
#     if skill in resume_skills:
#         matched.append(skill)
#         matched_count+=1
#     else:
#         missing.append(skill)

# print("Matched:", matched)
# print("Missing:", missing)

# #Recomendation for the skills
# print("\nRecomendation for the skills:")
# for skill in missing:
#     print(f"You should learn {skill}.")


# score = (matched_count / len(required_skills)) * 100

# #ATS Score and feedback
# print(f"\nATS Score: {score:.0f}%")

# if score >= 80:
#     print("\nExcellent Resume! Keep it up")
# elif score >= 60:
#     print("\nGood Resume Great work keep it up!")
# elif score >= 40:
#     print("\nNeeds Improvement! You should focus on the following skills: ", missing)
# else:
#     print("\nPoor ATS Score 😟")


# #Phone and email Extraction 
# email = ""
# phone = ""

# for line in text.split("\n"):
#     if "email:" in line:
#         email = line.replace("email:", "").strip()

#     if "phone:" in line:
#         phone = line.replace("phone:", "").strip()

# print("Email:", email)
# print("Phone:", phone)


# #Projects Extraction 
# projects_section = extract_section(text, "projects:", "certifications:")

# projects_lines = projects_section.split("\n")

# resume_projects = []

# for line in projects_lines:
#     line = line.strip("- ").strip()

#     if line and line != "projects:":
#         resume_projects.append(line)


# project_count = len(resume_projects)

# for line in resume_projects:
#     print(line)

# print(f"\nYou have done {project_count} projects.")

# #overall Resume Score
# if score >= 80 and project_count >= 2:
#     print("Strong Resume")
# elif score >= 60:
#     print("Average Resume")
# else:
#     print("Needs Improvement")

# #Education Extraction 
# education_section = extract_section(text, "education:", "projects:")

# print("\n",education_section)