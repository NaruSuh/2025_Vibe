
"""
APA Accredited Clinical Psychology Doctoral Programs Professor Database
186개 APA 인증 임상심리학 박사과정 교수진 데이터베이스
"""
import json
import os

def load_professors_database():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'professors.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

APA_PROFESSORS_DATABASE = load_professors_database()

# 연구 분야별 키워드 매핑
RESEARCH_AREA_KEYWORDS = {
    "anxiety_disorders": ["anxiety", "panic", "phobia", "GAD", "social anxiety", "OCD", "exposure therapy"],
    "depression": ["depression", "mood disorders", "major depressive disorder", "bipolar", "unipolar"],
    "trauma_ptsd": ["PTSD", "trauma", "complex trauma", "EMDR", "exposure therapy", "combat trauma"],
    "personality_disorders": ["borderline", "narcissistic", "antisocial", "personality disorders", "DBT"],
    "addiction": ["substance abuse", "addiction", "alcohol", "drug abuse", "gambling", "behavioral addiction"],
    "child_adolescent": ["child psychology", "adolescent", "developmental psychopathology", "youth"],
    "neuropsychology": ["neuroimaging", "fMRI", "brain", "cognitive assessment", "neuropsychological"],
    "psychotherapy": ["CBT", "psychodynamic", "humanistic", "evidence-based treatment", "therapy"],
    "assessment": ["psychological assessment", "testing", "psychometrics", "diagnosis", "evaluation"],
    "multicultural": ["multicultural", "diversity", "cultural competence", "minority mental health"]
}

def search_professors_by_keyword(keyword, max_results=10):
    """키워드로 교수 검색"""
    results = []
    keyword_lower = keyword.lower()
    
    for university, info in APA_PROFESSORS_DATABASE.items():
        for professor in info["professors"]:
            # 연구 분야나 키워드에서 검색
            if (keyword_lower in professor["research_keywords"].lower() or 
                any(keyword_lower in area.lower() for area in professor["research_areas"])):
                
                results.append({
                    "professor": professor,
                    "university": university,
                    "location": info["location"],
                    "program_type": info["program_type"]
                })
    
    return results[:max_results]

def get_research_areas():
    """모든 고유 연구 분야 반환"""
    areas = set()
    for university_info in APA_PROFESSORS_DATABASE.values():
        for professor in university_info["professors"]:
            areas.update(professor["research_areas"])
    return sorted(list(areas))

def get_universities():
    """모든 대학 목록 반환"""
    return sorted(list(APA_PROFESSORS_DATABASE.keys()))

def get_professors_by_university(university):
    """특정 대학의 교수진 반환"""
    if university in APA_PROFESSORS_DATABASE:
        return APA_PROFESSORS_DATABASE[university]["professors"]
    return []

def generate_video_search_keywords(professor_info):
    """교수 정보를 바탕으로 비디오 검색 키워드 생성"""
    keywords = []
    
    # 교수 이름
    keywords.append(professor_info["name"])
    
    # 연구 분야
    keywords.extend(professor_info["research_areas"])
    
    # 연구 키워드에서 주요 용어 추출
    research_terms = professor_info["research_keywords"].split()
    keywords.extend(research_terms[:5])  # 상위 5개만
    
    return " ".join(keywords)
