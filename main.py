import os
import io
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import google.generativeai as genai

app = FastAPI(title="LOC-NANDO Backend Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    text = ""
    if filename.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() or ""
    elif filename.endswith(".txt"):
        text = file_bytes.decode("utf-8")
    return text.strip()

@app.post("/api/qcm")
async def generate_qcm(file: UploadFile = File(...), level: str = Form("Université")):
    contents = await file.read()
    text = extract_text_from_file(contents, file.filename)
    if not text:
        raise HTTPException(status_code=400, detail="Fichier vide ou illisible.")

    prompt = f"""
    Niveau d'étude : {level}
    Analyse ce cours et génère 4 QCM adaptés au niveau.
    Format JSON strict (tableau d'objets) :
    [
      {{
        "question": "Texte de la question",
        "options": ["Choix A", "Choix B", "Choix C", "Choix D"],
        "answer": 0,
        "explanation": "Explication pédagogique de la bonne réponse"
      }}
    ]
    Texte source :
    {text[:4000]}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    return {"status": "ok", "qcm": json.loads(clean_json)}

@app.post("/api/flashcards")
async def generate_flashcards(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_file(contents, file.filename)
    
    prompt = f"""
    Extrais 4 concepts clés de ce cours pour créer des Flashcards.
    Format JSON strict :
    [
      {{
        "recto": "Question ou Concept à définir",
        "verso": "Définition concise ou explication"
      }}
    ]
    Texte source :
    {text[:4000]}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    return {"status": "ok", "flashcards": json.loads(clean_json)}

@app.post("/api/mindmap")
async def generate_mindmap(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_file(contents, file.filename)

    prompt = f"""
    Extrais la structure hiérarchique de ce cours pour afficher une carte mentale.
    Format JSON strict :
    {{
      "title": "Titre central du cours",
      "branches": [
        {{
          "topic": "Sous-titre 1",
          "subtopics": ["Concept A", "Concept B", "Concept C"]
        }}
      ]
    }}
    Texte source :
    {text[:4000]}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    return {"status": "ok", "mindmap": json.loads(clean_json)}

@app.post("/api/podcast")
async def generate_podcast(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_file(contents, file.filename)

    prompt = f"""
    Transforme ce cours en un script de podcast pédagogique.
    Format JSON strict :
    {{
      "titre": "Titre du podcast",
      "duree_estimee": "3 minutes",
      "script": [
        {{"intervenant": "Tuteur IA", "texte": "Bienvenue..."}}
      ]
    }}
    Texte source :
    {text[:4000]}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    return {"status": "ok", "podcast": json.loads(clean_json)}

@app.post("/api/feynman/evaluate")
async def evaluate_feynman(concept: str = Form(...), student_explanation: str = Form(...)):
    prompt = f"""
    Tu es un évaluateur pédagogique selon la Méthode Feynman.
    L'apprenant explique : "{concept}". Explication : "{student_explanation}"
    Evalue et réponds en JSON strict :
    {{
      "score": 85,
      "points_forts": ["Clarté"],
      "lacunes": ["Précision"],
      "conseil": "Conseil d'amélioration..."
    }}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    return {"status": "ok", "evaluation": json.loads(clean_json)}
  from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
async def read_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Bienvenue sur LOC-NANDO ! Fichier index.html introuvable.</h1>"
    
