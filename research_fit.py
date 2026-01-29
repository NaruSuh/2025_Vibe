"""
Research Fit Analyzer 모듈
연구 관심사 매칭, 유사 교수 추천, 키워드 분석
"""
from typing import Dict, List, Any, Tuple, Set
import re
from collections import Counter

from config import logger


# =============================================================================
# 키워드 처리 유틸리티
# =============================================================================
def extract_keywords(text: str) -> Set[str]:
    """텍스트에서 키워드 추출 (소문자, 정규화)"""
    if not text:
        return set()

    # 소문자 변환 및 특수문자 제거
    text = text.lower()
    text = re.sub(r'[^\w\s가-힣]', ' ', text)

    # 단어 분리 및 짧은 단어 제거
    words = text.split()
    keywords = {w.strip() for w in words if len(w) > 2}

    return keywords


def normalize_research_area(area: str) -> str:
    """연구 분야명 정규화"""
    return area.lower().strip()


# =============================================================================
# 유사도 계산
# =============================================================================
def calculate_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Jaccard 유사도 계산

    Args:
        set1: 첫 번째 키워드 집합
        set2: 두 번째 키워드 집합

    Returns:
        0.0 ~ 1.0 사이의 유사도 점수
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def calculate_overlap_coefficient(set1: Set[str], set2: Set[str]) -> float:
    """Overlap Coefficient 계산 (작은 집합 기준)

    Jaccard보다 작은 집합에 유리한 유사도
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    min_size = min(len(set1), len(set2))

    return intersection / min_size if min_size > 0 else 0.0


def calculate_keyword_match_score(
    user_keywords: Set[str],
    professor_keywords: Set[str],
    professor_areas: List[str]
) -> Tuple[float, List[str], List[str]]:
    """키워드 매칭 점수 계산

    Args:
        user_keywords: 사용자 입력 키워드
        professor_keywords: 교수 연구 키워드
        professor_areas: 교수 연구 분야

    Returns:
        (점수, 매칭된 키워드 리스트, 매칭된 연구분야 리스트)
    """
    # 교수의 연구 분야도 키워드로 변환
    area_keywords = set()
    for area in professor_areas:
        area_keywords.update(extract_keywords(area))

    all_prof_keywords = professor_keywords | area_keywords

    # 매칭된 키워드 찾기
    matched_keywords = user_keywords & all_prof_keywords

    # 매칭된 연구 분야 찾기
    matched_areas = []
    for area in professor_areas:
        area_kw = extract_keywords(area)
        if area_kw & user_keywords:
            matched_areas.append(area)

    # 복합 점수 계산 (Jaccard 50% + Overlap 50%)
    jaccard = calculate_jaccard_similarity(user_keywords, all_prof_keywords)
    overlap = calculate_overlap_coefficient(user_keywords, all_prof_keywords)

    score = (jaccard * 0.5) + (overlap * 0.5)

    return score, list(matched_keywords), matched_areas


# =============================================================================
# 교수 매칭 분석
# =============================================================================
def analyze_professor_fit(
    user_interests: str,
    professor_data: Dict[str, Any]
) -> Dict[str, Any]:
    """단일 교수와의 연구 적합도 분석

    Args:
        user_interests: 사용자 연구 관심사 텍스트
        professor_data: 교수 정보 딕셔너리

    Returns:
        분석 결과 딕셔너리
    """
    prof = professor_data.get("professor", {})

    # 사용자 키워드 추출
    user_keywords = extract_keywords(user_interests)

    # 교수 키워드 추출
    prof_keywords = extract_keywords(prof.get("research_keywords", ""))
    prof_areas = prof.get("research_areas", [])

    # 점수 계산
    score, matched_keywords, matched_areas = calculate_keyword_match_score(
        user_keywords, prof_keywords, prof_areas
    )

    # 매칭되지 않은 키워드 (차이점)
    all_prof_keywords = prof_keywords | set(kw for area in prof_areas for kw in extract_keywords(area))
    unmatched_user = user_keywords - all_prof_keywords
    unmatched_prof = all_prof_keywords - user_keywords

    return {
        "professor": prof.get("name", "Unknown"),
        "university": professor_data.get("university", "Unknown"),
        "location": professor_data.get("location", ""),
        "program_type": professor_data.get("program_type", ""),
        "score": round(score * 100, 1),  # 백분율로 변환
        "matched_keywords": matched_keywords[:10],  # 상위 10개만
        "matched_areas": matched_areas,
        "user_unique_interests": list(unmatched_user)[:5],  # 사용자만의 관심사
        "professor_unique_areas": list(unmatched_prof)[:5],  # 교수만의 분야
        "research_areas": prof_areas,
        "lab": prof.get("lab", ""),
        "email": prof.get("email", ""),
        "full_data": professor_data  # 원본 데이터 보존
    }


def find_matching_professors(
    user_interests: str,
    professors_db: Dict[str, Any],
    top_n: int = 10,
    min_score: float = 5.0
) -> List[Dict[str, Any]]:
    """사용자 관심사에 맞는 교수 찾기

    Args:
        user_interests: 사용자 연구 관심사 텍스트
        professors_db: 교수 데이터베이스
        top_n: 반환할 최대 교수 수
        min_score: 최소 점수 (백분율)

    Returns:
        점수순으로 정렬된 교수 매칭 결과 리스트
    """
    if not user_interests or not user_interests.strip():
        return []

    results = []

    for university, info in professors_db.items():
        for prof in info.get("professors", []):
            professor_data = {
                "professor": prof,
                "university": university,
                "location": info.get("location", ""),
                "program_type": info.get("program_type", "")
            }

            analysis = analyze_professor_fit(user_interests, professor_data)

            if analysis["score"] >= min_score:
                results.append(analysis)

    # 점수순 정렬
    results.sort(key=lambda x: x["score"], reverse=True)

    logger.info(f"연구 적합도 분석 완료 - 총 {len(results)}명 매칭 (상위 {top_n}명 반환)")

    return results[:top_n]


def find_similar_professors(
    target_professor: Dict[str, Any],
    professors_db: Dict[str, Any],
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """특정 교수와 비슷한 연구를 하는 교수 찾기

    Args:
        target_professor: 대상 교수 데이터
        professors_db: 교수 데이터베이스
        top_n: 반환할 최대 교수 수

    Returns:
        유사 교수 리스트
    """
    target_prof = target_professor.get("professor", {})
    target_name = target_prof.get("name", "")

    # 대상 교수의 연구 키워드 결합
    target_interests = " ".join([
        target_prof.get("research_keywords", ""),
        " ".join(target_prof.get("research_areas", []))
    ])

    # 매칭 실행
    matches = find_matching_professors(
        target_interests,
        professors_db,
        top_n=top_n + 1  # 자기 자신 제외를 위해 +1
    )

    # 자기 자신 제외
    matches = [m for m in matches if m["professor"] != target_name]

    return matches[:top_n]


# =============================================================================
# 연구 분야 통계
# =============================================================================
def get_research_area_statistics(professors_db: Dict[str, Any]) -> Dict[str, int]:
    """전체 교수진의 연구 분야 통계

    Returns:
        연구 분야별 교수 수
    """
    area_counts = Counter()

    for university, info in professors_db.items():
        for prof in info.get("professors", []):
            for area in prof.get("research_areas", []):
                normalized = normalize_research_area(area)
                area_counts[normalized] += 1

    return dict(area_counts.most_common())


def get_keyword_statistics(professors_db: Dict[str, Any]) -> Dict[str, int]:
    """전체 교수진의 키워드 통계

    Returns:
        키워드별 출현 빈도
    """
    keyword_counts = Counter()

    for university, info in professors_db.items():
        for prof in info.get("professors", []):
            keywords = extract_keywords(prof.get("research_keywords", ""))
            keyword_counts.update(keywords)

    return dict(keyword_counts.most_common(50))  # 상위 50개만


# =============================================================================
# SOP/질문 생성 헬퍼
# =============================================================================
def generate_match_summary(match_result: Dict[str, Any]) -> str:
    """매칭 결과를 텍스트 요약으로 변환"""
    summary_parts = []

    score = match_result.get("score", 0)
    prof_name = match_result.get("professor", "Unknown")
    university = match_result.get("university", "Unknown")

    summary_parts.append(f"**{prof_name}** ({university})")
    summary_parts.append(f"매칭 점수: {score}%")

    matched_areas = match_result.get("matched_areas", [])
    if matched_areas:
        summary_parts.append(f"공통 연구 분야: {', '.join(matched_areas)}")

    matched_keywords = match_result.get("matched_keywords", [])
    if matched_keywords:
        summary_parts.append(f"매칭 키워드: {', '.join(matched_keywords[:5])}")

    return "\n".join(summary_parts)


def get_sop_talking_points(match_result: Dict[str, Any], user_interests: str) -> List[str]:
    """SOP 작성을 위한 포인트 생성"""
    points = []

    matched_areas = match_result.get("matched_areas", [])
    if matched_areas:
        points.append(f"연구 관심사 중 '{matched_areas[0]}'가 교수님의 주요 연구 분야와 일치합니다.")

    lab = match_result.get("lab", "")
    if lab:
        points.append(f"'{lab}' 연구실의 프로젝트와 연계 가능성을 언급하세요.")

    unique_interests = match_result.get("user_unique_interests", [])
    if unique_interests:
        points.append(f"당신만의 독특한 관심사({', '.join(unique_interests[:3])})가 연구실에 기여할 수 있는 점을 강조하세요.")

    return points
