"""
AI Matching Engine.
Uses Sentence Transformers and cosine similarity for intelligent candidate matching.
"""
import json
import re
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Global model reference (lazy loaded)
_model = None


def get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for a text."""
    model = get_model()
    embedding = model.encode([text])[0]
    return embedding.tolist()


def calculate_match_score(query_embedding: List[float], candidate_embedding: List[float]) -> float:
    """Calculate cosine similarity between query and candidate."""
    query_vec = np.array(query_embedding).reshape(1, -1)
    candidate_vec = np.array(candidate_embedding).reshape(1, -1)
    score = cosine_similarity(query_vec, candidate_vec)[0][0]
    return float(score)


def build_candidate_text(resume_data: dict) -> str:
    """Build a comprehensive text representation of a candidate for embedding."""
    parts = []

    if resume_data.get("parsed_skills"):
        skills = json.loads(resume_data["parsed_skills"]) if isinstance(resume_data["parsed_skills"], str) else resume_data["parsed_skills"]
        parts.append(f"Habilidades: {', '.join(skills)}")

    if resume_data.get("parsed_experience"):
        exp = json.loads(resume_data["parsed_experience"]) if isinstance(resume_data["parsed_experience"], str) else resume_data["parsed_experience"]
        parts.append(f"Experiencia: {', '.join(exp)}")

    if resume_data.get("parsed_education"):
        edu = json.loads(resume_data["parsed_education"]) if isinstance(resume_data["parsed_education"], str) else resume_data["parsed_education"]
        parts.append(f"Educación: {', '.join(edu)}")

    if resume_data.get("parsed_areas"):
        areas = json.loads(resume_data["parsed_areas"]) if isinstance(resume_data["parsed_areas"], str) else resume_data["parsed_areas"]
        parts.append(f"Áreas: {', '.join(areas)}")

    if resume_data.get("parsed_languages"):
        langs = json.loads(resume_data["parsed_languages"]) if isinstance(resume_data["parsed_languages"], str) else resume_data["parsed_languages"]
        parts.append(f"Idiomas: {', '.join(langs)}")

    if resume_data.get("professional_summary"):
        parts.append(f"Resumen: {resume_data['professional_summary']}")

    return " | ".join(parts)


def search_candidates(query: str, candidates: List[dict], top_k: int = 10, threshold: float = 0.25) -> List[dict]:
    """
    Search candidates using semantic similarity.
    
    Args:
        query: Natural language search query
        candidates: List of candidate data dicts with resume info
        top_k: Maximum number of results
        threshold: Minimum similarity score
    
    Returns:
        Ranked list of matching candidates with scores
    """
    if not candidates:
        return []

    query_embedding = generate_embedding(query)
    results = []

    for candidate in candidates:
        if not candidate.get("embedding_vector"):
            candidate_text = build_candidate_text(candidate)
            if not candidate_text.strip():
                continue
            candidate_embedding = generate_embedding(candidate_text)
        else:
            emb = candidate["embedding_vector"]
            candidate_embedding = json.loads(emb) if isinstance(emb, str) else emb

        score = calculate_match_score(query_embedding, candidate_embedding)

        if score >= threshold:
            results.append({
                "user_id": candidate.get("user_id"),
                "full_name": candidate.get("full_name"),
                "email": candidate.get("email"),
                "skills": json.loads(candidate["parsed_skills"]) if candidate.get("parsed_skills") else [],
                "experience": json.loads(candidate["parsed_experience"]) if candidate.get("parsed_experience") else [],
                "education": json.loads(candidate["parsed_education"]) if candidate.get("parsed_education") else [],
                "areas": json.loads(candidate["parsed_areas"]) if candidate.get("parsed_areas") else [],
                "languages": json.loads(candidate["parsed_languages"]) if candidate.get("parsed_languages") else [],
                "summary": candidate.get("professional_summary", ""),
                "score": round(score * 100, 2),
                "years_experience": candidate.get("years_experience", 0)
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def parse_cv_text(raw_text: str) -> dict:
    """
    Parse raw CV text to extract structured information.
    Uses heuristic NLP approach.
    """
    text_lower = raw_text.lower()

    # Extract skills
    skill_keywords = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node.js", "django", "fastapi", "flask", "sql", "postgresql", "mongodb",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
        "html", "css", "bootstrap", "tailwind", "figma", "photoshop",
        "excel", "power bi", "tableau", "scrum", "agile", "jira",
        "c++", "c#", ".net", "ruby", "php", "go", "rust", "swift",
        "algebra", "cálculo", "estadística", "matemáticas", "física",
        "contabilidad", "finanzas", "marketing", "ventas", "liderazgo",
        "comunicación", "trabajo en equipo", "gestión de proyectos",
        "investigación", "docencia", "pedagogía", "educación"
    ]
    found_skills = [s for s in skill_keywords if s in text_lower]

    # Extract experience sections
    experience = []
    exp_patterns = [
        r'(?:experiencia|experience)[\s\S]{0,500}',
    ]
    for pattern in exp_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            lines = [l.strip() for l in match.split('\n') if len(l.strip()) > 10]
            experience.extend(lines[:5])

    # Extract education
    education = []
    edu_patterns = [
        r'(?:educación|education|formación|estudios)[\s\S]{0,300}',
    ]
    for pattern in edu_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            lines = [l.strip() for l in match.split('\n') if len(l.strip()) > 5]
            education.extend(lines[:5])

    # Extract languages
    language_keywords = ["español", "inglés", "francés", "alemán", "portugués",
                         "italiano", "chino", "japonés", "coreano", "árabe",
                         "spanish", "english", "french", "german", "portuguese"]
    found_languages = [l for l in language_keywords if l in text_lower]

    # Extract areas
    area_keywords = [
        "tecnología", "ingeniería", "ciencias", "educación", "salud",
        "finanzas", "marketing", "recursos humanos", "legal", "diseño",
        "investigación", "consultoría", "administración", "operaciones",
        "desarrollo de software", "inteligencia artificial", "data science",
        "academia", "docencia universitaria"
    ]
    found_areas = [a for a in area_keywords if a in text_lower]

    # Generate summary
    summary_lines = [l.strip() for l in raw_text.split('\n') if 20 < len(l.strip()) < 200]
    summary = summary_lines[0] if summary_lines else "Perfil profesional"

    return {
        "skills": found_skills if found_skills else ["general"],
        "experience": experience if experience else ["No especificada"],
        "education": education if education else ["No especificada"],
        "languages": found_languages if found_languages else ["español"],
        "areas": found_areas if found_areas else ["general"],
        "summary": summary
    }
