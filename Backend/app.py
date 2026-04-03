import os, re, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz
from google import genai

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend is running successfully"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY","")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def extract_text(file):
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "".join(p.get_text() for p in pdf)
    except:
        return file.read().decode(errors="ignore")

def clean_text(t):
    t=t.lower()
    t=re.sub(r"[^a-z0-9+ ]"," ",t)
    return re.sub(r"\s+"," ",t)

def dynamic_keyword_score(resume: str, job_desc: str):
    try:
        resume_clean = clean_text(resume)
        job_clean = clean_text(job_desc)

        # fallback keywords (IMPORTANT)
        words = list(set(job_clean.split()))
        words = [w for w in words if len(w) > 2]

        top_keywords = words[:30]  # simple keywords

        matched = [kw for kw in top_keywords if kw in resume_clean]
        missing = [kw for kw in top_keywords if kw not in resume_clean]

        score = (len(matched) / len(top_keywords) * 100) if top_keywords else 0

        return round(score, 2), matched[:15], missing[:15]

    except Exception as e:
        print("Keyword Error:", e)
        return 0.0, [], []

def tfidf_score(r,j):
    try:
        v=TfidfVectorizer(stop_words="english")
        tf=v.fit_transform([r,j])
        return cosine_similarity(tf[0:1],tf[1:2])[0][0]*100
    except:
        return 0

def section_score(r):
    sec=["education","skills","projects","experience"]
    f=[s for s in sec if s in r.lower()]
    return min(len(f)*25,100),f

def gemini_analysis(r,j):
    if not client:
        return {"semantic_score":0,"improvements":["AI not available"]}

    try:
        prompt=f"Score resume vs job (0-100). Return JSON with semantic_score and improvements.\nJD:{j[:2000]}\nRES:{r[:4000]}"
        res=client.models.generate_content(model="gemini-2.0-flash-lite",contents=prompt)
        return json.loads(res.text)
    except:
        return {"semantic_score":0,"improvements":["AI failed"]}

def calculate_ats(r,j,use_ai=True):
    rc, jc = clean_text(r), clean_text(j)

    tf=tfidf_score(rc,jc)
    kw,match,miss=dynamic_keyword_score(r,j)
    sec,found=section_score(r)

    g=gemini_analysis(r,j) if use_ai else {}
    ai=g.get("semantic_score",0)

    final=(0.4*ai+0.3*kw+0.2*tf+0.1*sec) if ai>0 else (0.45*kw+0.35*tf+0.2*sec)

    return {
        "ATS Score":round(final,1),
        "AI Score":ai if ai>0 else "Not Available",
        "Matched Skills":match,
        "Missing Keywords":miss,
        "Suggestions":g.get("improvements",[]),
        "AI Improvements":g.get("improvements",[]),
        "Breakdown":{
            "AI Semantic":ai,
            "TF-IDF":round(tf,1),
            "Keywords":round(kw,1),
            "Sections":round(sec,1)
        }
    }

@app.route("/analyze",methods=["POST"])
def analyze():
    f=request.files.get("resume")
    jd=request.form.get("job_desc","")

    if not f or not jd:
        return jsonify({"error":"missing data"}),400

    text=extract_text(f)
    res=calculate_ats(text,jd,request.form.get("mode")=="ai")

    return jsonify(res)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
