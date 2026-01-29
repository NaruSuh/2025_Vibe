"""
필터링 및 정렬 유틸리티 모듈
동영상 필터링, 정렬 기능
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone

from config import (
    logger,
    SortOptions,
    DateFilterOptions,
)


def parse_iso_date(date_str: str) -> datetime:
    """ISO 8601 날짜 문자열을 datetime으로 파싱"""
    try:
        # YouTube API의 날짜 형식: 2024-01-15T10:30:00Z
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def filter_videos_by_date(videos: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """지정된 일 수 이내의 동영상만 필터링

    Args:
        videos: 동영상 목록
        days: 필터링할 일 수 (0이면 필터 없음)

    Returns:
        필터링된 동영상 목록
    """
    if days <= 0:
        return videos

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []

    for video in videos:
        published_at = video.get('snippet', {}).get('publishedAt', '')
        video_date = parse_iso_date(published_at)

        if video_date >= cutoff_date:
            filtered.append(video)

    logger.info(f"날짜 필터 적용: {len(videos)} -> {len(filtered)} (최근 {days}일)")
    return filtered


def sort_videos(videos: List[Dict[str, Any]], sort_option: str) -> List[Dict[str, Any]]:
    """동영상 목록 정렬

    Args:
        videos: 동영상 목록
        sort_option: 정렬 옵션 (SortOptions 클래스의 값)

    Returns:
        정렬된 동영상 목록
    """
    if not videos:
        return videos

    if sort_option == SortOptions.RELEVANCE:
        # 기본 순서 유지 (YouTube API가 관련성순으로 반환)
        return videos

    elif sort_option == SortOptions.VIEW_COUNT_DESC:
        return sorted(
            videos,
            key=lambda v: int(v.get('statistics', {}).get('viewCount', '0') or '0'),
            reverse=True
        )

    elif sort_option == SortOptions.VIEW_COUNT_ASC:
        return sorted(
            videos,
            key=lambda v: int(v.get('statistics', {}).get('viewCount', '0') or '0'),
            reverse=False
        )

    elif sort_option == SortOptions.DATE_DESC:
        return sorted(
            videos,
            key=lambda v: parse_iso_date(v.get('snippet', {}).get('publishedAt', '')),
            reverse=True
        )

    elif sort_option == SortOptions.DATE_ASC:
        return sorted(
            videos,
            key=lambda v: parse_iso_date(v.get('snippet', {}).get('publishedAt', '')),
            reverse=False
        )

    logger.warning(f"알 수 없는 정렬 옵션: {sort_option}")
    return videos


def filter_videos_by_channel(videos: List[Dict[str, Any]], channel_name: str) -> List[Dict[str, Any]]:
    """특정 채널의 동영상만 필터링

    Args:
        videos: 동영상 목록
        channel_name: 채널 이름 (빈 문자열이면 필터 없음)

    Returns:
        필터링된 동영상 목록
    """
    if not channel_name:
        return videos

    channel_lower = channel_name.lower()
    filtered = [
        v for v in videos
        if channel_lower in v.get('snippet', {}).get('channelTitle', '').lower()
    ]

    logger.info(f"채널 필터 적용: {len(videos)} -> {len(filtered)} (채널: {channel_name})")
    return filtered


def get_unique_channels(videos: List[Dict[str, Any]]) -> List[str]:
    """동영상 목록에서 고유 채널 이름 추출

    Args:
        videos: 동영상 목록

    Returns:
        고유 채널 이름 목록 (정렬됨)
    """
    channels = set()
    for video in videos:
        channel = video.get('snippet', {}).get('channelTitle', '')
        if channel:
            channels.add(channel)
    return sorted(channels)


def apply_video_filters(
    videos: List[Dict[str, Any]],
    sort_option: str = SortOptions.RELEVANCE,
    date_filter: str = DateFilterOptions.ALL,
    channel_filter: str = ""
) -> List[Dict[str, Any]]:
    """모든 필터를 적용한 동영상 목록 반환

    Args:
        videos: 원본 동영상 목록
        sort_option: 정렬 옵션
        date_filter: 날짜 필터 옵션
        channel_filter: 채널 필터 (빈 문자열이면 없음)

    Returns:
        필터링 및 정렬된 동영상 목록
    """
    if not videos:
        return videos

    result = videos.copy()

    # 1. 날짜 필터
    days = DateFilterOptions.to_days(date_filter)
    if days > 0:
        result = filter_videos_by_date(result, days)

    # 2. 채널 필터
    if channel_filter:
        result = filter_videos_by_channel(result, channel_filter)

    # 3. 정렬
    result = sort_videos(result, sort_option)

    return result


def get_video_stats_summary(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """동영상 목록의 통계 요약

    Returns:
        통계 정보 딕셔너리
    """
    if not videos:
        return {
            "total": 0,
            "total_views": 0,
            "avg_views": 0,
            "channels": 0,
            "oldest": None,
            "newest": None
        }

    total_views = sum(
        int(v.get('statistics', {}).get('viewCount', '0') or '0')
        for v in videos
    )

    dates = [
        parse_iso_date(v.get('snippet', {}).get('publishedAt', ''))
        for v in videos
    ]
    valid_dates = [d for d in dates if d != datetime.min.replace(tzinfo=timezone.utc)]

    return {
        "total": len(videos),
        "total_views": total_views,
        "avg_views": total_views // len(videos) if videos else 0,
        "channels": len(get_unique_channels(videos)),
        "oldest": min(valid_dates).strftime('%Y-%m-%d') if valid_dates else None,
        "newest": max(valid_dates).strftime('%Y-%m-%d') if valid_dates else None
    }
