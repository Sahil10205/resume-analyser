import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z+ ]', '', text)
    return text

def keyword_score(resume, job_desc):
    skills = [
        "python", "c++", "java", "javascript", "html", "css",
        "sql", "dbms", "git", "github",
        "data structures", "algorithms", "oop"
    ]

    resume = resume.lower()
    job_desc = job_desc.lower()

    match = 0
    total = 0

    for skill in skills:
        if skill in job_desc:
            total += 1
            if skill in resume:
                match += 1

    if total == 0:
        return 0

    return (match / total) * 100

def calculate_ats_score(resume, job_desc):
    resume_clean = clean_text(resume)
    job_clean = clean_text(job_desc)

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_clean, job_clean])

    tfidf_score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100
    kw_score = keyword_score(resume_clean, job_clean)

    final_score = (0.3 * tfidf_score) + (0.7 * kw_score)

    return round(final_score, 2)

def get_missing_keywords(resume, job_desc):
    resume = clean_text(resume)
    job_desc = clean_text(job_desc)

    resume_words = set(resume.split())
    job_words = set(job_desc.split())

    stopwords = {
        "the","and","or","for","with","a","an","to","in","on","of","is","are"
    }

    job_words = job_words - stopwords
    missing = job_words - resume_words

    return list(missing)[:10]

def skill_match(resume, job_desc):
    skills = [
        "python", "c++", "java", "javascript", "html", "css",
        "sql", "dbms", "git", "github",
        "data structures", "algorithms", "oop"
    ]

    resume = resume.lower()
    job_desc = job_desc.lower()

    matched = []

    for skill in skills:
        if skill in job_desc and skill in resume:
            matched.append(skill)

    return matched

def generate_suggestions(missing_keywords):
    return [f"Add '{word}' to improve ATS score" for word in missing_keywords[:5]]