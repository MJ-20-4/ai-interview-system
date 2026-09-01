import re


SKILL_CATALOG = {
    "programming_languages": [
        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "c",
        "sql",
    ],
    "ml_ai": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "computer vision",
        "natural language processing",
        "nlp",
        "rag",
        "retrieval augmented generation",
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "scikit learn",
        "pandas",
        "numpy",
        "opencv",
        "transformers",
        "langchain",
    ],
    "backend": [
        "fastapi",
        "flask",
        "django",
        "node.js",
        "nodejs",
        "express",
        "rest api",
        "api",
        "microservices",
    ],
    "databases_devops": [
        "mongodb",
        "mysql",
        "postgresql",
        "postgres",
        "sqlite",
        "redis",
        "docker",
        "kubernetes",
        "git",
        "github",
        "linux",
        "aws",
    ],
    "frontend": [
        "react",
        "vite",
        "html",
        "css",
        "tailwind",
    ],
}


def normalize_skill(skill: str) -> str:
    replacements = {
        "scikit learn": "scikit-learn",
        "nodejs": "node.js",
        "nlp": "natural language processing",
        "postgres": "postgresql",
    }

    return replacements.get(skill, skill)


def has_skill(text: str, skill: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_skills(resume_text: str) -> list[str]:
    found_skills = []

    for skills in SKILL_CATALOG.values():
        for skill in skills:
            if has_skill(resume_text, skill):
                normalized = normalize_skill(skill)

                if normalized not in found_skills:
                    found_skills.append(normalized)

    return found_skills


def determine_experience_level(resume_text: str) -> str:
    text = resume_text.lower()

    advanced_signals = [
        "senior",
        "lead",
        "architect",
        "5 years",
        "6 years",
        "7 years",
        "8 years",
    ]

    intermediate_signals = [
        "internship",
        "intern",
        "deployed",
        "production",
        "freelance",
        "1 year",
        "2 years",
        "3 years",
    ]

    if any(signal in text for signal in advanced_signals):
        return "advanced"

    if any(signal in text for signal in intermediate_signals):
        return "intermediate"

    return "beginner"


def extract_projects(resume_text: str) -> list[str]:
    project_keywords = [
        "project",
        "developed",
        "built",
        "implemented",
        "created",
        "deployed",
    ]

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    matching_lines = [
        line
        for line in lines
        if any(keyword in line.lower() for keyword in project_keywords)
    ]

    return matching_lines[:5]


def analyze_resume(resume_text: str) -> dict:
    skills = extract_skills(resume_text)

    return {
        "skills": skills,
        "experience_level": determine_experience_level(resume_text),
        "projects": extract_projects(resume_text),
        "resume_length": len(resume_text),
    }
