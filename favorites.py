"""
즐겨찾기 관리 모듈
교수 및 동영상 즐겨찾기 기능
"""
import streamlit as st
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import (
    logger,
    FavoritesConfig,
    FavoritesKeys,
)


def init_favorites() -> None:
    """즐겨찾기 세션 상태 초기화"""
    if FavoritesKeys.PROFESSORS not in st.session_state:
        st.session_state[FavoritesKeys.PROFESSORS] = {}
    if FavoritesKeys.VIDEOS not in st.session_state:
        st.session_state[FavoritesKeys.VIDEOS] = {}
    if FavoritesKeys.COMPARE_LIST not in st.session_state:
        st.session_state[FavoritesKeys.COMPARE_LIST] = []


# =============================================================================
# 교수 즐겨찾기
# =============================================================================
def add_professor_favorite(professor_data: Dict[str, Any]) -> bool:
    """교수를 즐겨찾기에 추가

    Returns:
        True if added, False if already exists or limit reached
    """
    init_favorites()
    favorites = st.session_state[FavoritesKeys.PROFESSORS]

    # 고유 키 생성
    prof = professor_data.get("professor", {})
    key = f"{professor_data.get('university', '')}_{prof.get('name', '')}"

    if key in favorites:
        logger.info(f"교수 즐겨찾기 중복: {key}")
        return False

    if len(favorites) >= FavoritesConfig.MAX_PROFESSORS:
        logger.warning(f"교수 즐겨찾기 한도 초과: {FavoritesConfig.MAX_PROFESSORS}")
        return False

    favorites[key] = {
        **professor_data,
        "added_at": datetime.now().isoformat()
    }
    logger.info(f"교수 즐겨찾기 추가: {key}")
    return True


def remove_professor_favorite(key: str) -> bool:
    """교수를 즐겨찾기에서 제거"""
    init_favorites()
    favorites = st.session_state[FavoritesKeys.PROFESSORS]

    if key in favorites:
        del favorites[key]
        logger.info(f"교수 즐겨찾기 제거: {key}")
        return True
    return False


def get_professor_favorites() -> Dict[str, Dict[str, Any]]:
    """모든 교수 즐겨찾기 반환"""
    init_favorites()
    return st.session_state[FavoritesKeys.PROFESSORS]


def is_professor_favorite(professor_data: Dict[str, Any]) -> bool:
    """교수가 즐겨찾기에 있는지 확인"""
    init_favorites()
    prof = professor_data.get("professor", {})
    key = f"{professor_data.get('university', '')}_{prof.get('name', '')}"
    return key in st.session_state[FavoritesKeys.PROFESSORS]


def get_professor_favorite_key(professor_data: Dict[str, Any]) -> str:
    """교수 데이터에서 즐겨찾기 키 생성"""
    prof = professor_data.get("professor", {})
    return f"{professor_data.get('university', '')}_{prof.get('name', '')}"


# =============================================================================
# 동영상 즐겨찾기
# =============================================================================
def add_video_favorite(video: Dict[str, Any]) -> bool:
    """동영상을 즐겨찾기에 추가"""
    init_favorites()
    favorites = st.session_state[FavoritesKeys.VIDEOS]

    video_id = video.get("id", "")
    if not video_id:
        return False

    if video_id in favorites:
        logger.info(f"동영상 즐겨찾기 중복: {video_id}")
        return False

    if len(favorites) >= FavoritesConfig.MAX_VIDEOS:
        logger.warning(f"동영상 즐겨찾기 한도 초과: {FavoritesConfig.MAX_VIDEOS}")
        return False

    snippet = video.get("snippet", {})
    favorites[video_id] = {
        "id": video_id,
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
        "published_at": snippet.get("publishedAt", ""),
        "view_count": video.get("statistics", {}).get("viewCount", "0"),
        "added_at": datetime.now().isoformat()
    }
    logger.info(f"동영상 즐겨찾기 추가: {video_id}")
    return True


def remove_video_favorite(video_id: str) -> bool:
    """동영상을 즐겨찾기에서 제거"""
    init_favorites()
    favorites = st.session_state[FavoritesKeys.VIDEOS]

    if video_id in favorites:
        del favorites[video_id]
        logger.info(f"동영상 즐겨찾기 제거: {video_id}")
        return True
    return False


def get_video_favorites() -> Dict[str, Dict[str, Any]]:
    """모든 동영상 즐겨찾기 반환"""
    init_favorites()
    return st.session_state[FavoritesKeys.VIDEOS]


def is_video_favorite(video_id: str) -> bool:
    """동영상이 즐겨찾기에 있는지 확인"""
    init_favorites()
    return video_id in st.session_state[FavoritesKeys.VIDEOS]


# =============================================================================
# 비교 목록 관리
# =============================================================================
def add_to_compare(professor_data: Dict[str, Any]) -> bool:
    """교수를 비교 목록에 추가"""
    init_favorites()
    compare_list = st.session_state[FavoritesKeys.COMPARE_LIST]

    key = get_professor_favorite_key(professor_data)

    # 이미 있으면 추가하지 않음
    for item in compare_list:
        if get_professor_favorite_key(item) == key:
            return False

    from config import CompareConfig
    if len(compare_list) >= CompareConfig.MAX_PROFESSORS:
        return False

    compare_list.append(professor_data)
    logger.info(f"비교 목록 추가: {key}")
    return True


def remove_from_compare(professor_data: Dict[str, Any]) -> bool:
    """교수를 비교 목록에서 제거"""
    init_favorites()
    compare_list = st.session_state[FavoritesKeys.COMPARE_LIST]

    key = get_professor_favorite_key(professor_data)

    for i, item in enumerate(compare_list):
        if get_professor_favorite_key(item) == key:
            compare_list.pop(i)
            logger.info(f"비교 목록 제거: {key}")
            return True
    return False


def get_compare_list() -> List[Dict[str, Any]]:
    """비교 목록 반환"""
    init_favorites()
    return st.session_state[FavoritesKeys.COMPARE_LIST]


def clear_compare_list() -> None:
    """비교 목록 초기화"""
    init_favorites()
    st.session_state[FavoritesKeys.COMPARE_LIST] = []
    logger.info("비교 목록 초기화")


def is_in_compare(professor_data: Dict[str, Any]) -> bool:
    """교수가 비교 목록에 있는지 확인"""
    init_favorites()
    key = get_professor_favorite_key(professor_data)
    for item in st.session_state[FavoritesKeys.COMPARE_LIST]:
        if get_professor_favorite_key(item) == key:
            return True
    return False


# =============================================================================
# 내보내기/가져오기
# =============================================================================
def export_favorites() -> str:
    """즐겨찾기를 JSON 문자열로 내보내기"""
    init_favorites()
    data = {
        "professors": st.session_state[FavoritesKeys.PROFESSORS],
        "videos": st.session_state[FavoritesKeys.VIDEOS],
        "exported_at": datetime.now().isoformat()
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_favorites(json_str: str) -> bool:
    """JSON 문자열에서 즐겨찾기 가져오기"""
    try:
        data = json.loads(json_str)
        init_favorites()

        if "professors" in data:
            st.session_state[FavoritesKeys.PROFESSORS] = data["professors"]
        if "videos" in data:
            st.session_state[FavoritesKeys.VIDEOS] = data["videos"]

        logger.info("즐겨찾기 가져오기 성공")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"즐겨찾기 가져오기 실패: {e}")
        return False
