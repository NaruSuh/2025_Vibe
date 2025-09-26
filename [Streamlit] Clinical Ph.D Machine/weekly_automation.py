#!/usr/bin/env python3
"""
GitHub Actions에서 실행되는 주간 연구 업데이트 자동화 스크립트
매주 월요일 오전 9시에 구독자들에게 최신 연구 동향을 이메일로 발송합니다.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """환경 설정"""
    # GitHub Actions에서 실행 시 환경변수에서 API 키 가져오기
    os.environ.setdefault('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
    os.environ.setdefault('YOUTUBE_API_KEY', os.getenv('YOUTUBE_API_KEY', ''))
    os.environ.setdefault('BREVO_API_KEY', os.getenv('BREVO_API_KEY', ''))
    os.environ.setdefault('PUBMED_API_KEY', os.getenv('PUBMED_API_KEY', ''))

def main():
    """메인 자동화 실행 함수"""
    logger.info("🚀 Weekly Research Update Automation Started")

    try:
        setup_environment()

        # 모듈 import (환경 설정 후)
        from subscriber_manager import subscriber_manager
        from pubmed_service import pubmed_service
        from email_service import email_service
        from report_generator import report_generator
        from datetime import datetime

        # 1. 활성 구독자 조회
        weekly_subscribers = subscriber_manager.get_active_subscribers("weekly")
        logger.info(f"📊 Found {len(weekly_subscribers)} weekly subscribers")

        if not weekly_subscribers:
            logger.info("📭 No weekly subscribers found. Skipping email generation.")
            return

        # 2. 최신 연구 동향 수집
        logger.info("📚 Collecting latest research trends...")
        research_data = collect_weekly_research_data()

        if not research_data:
            logger.error("❌ Failed to collect research data")
            return

        # 3. 구독자별 맞춤 이메일 발송
        success_count = 0
        error_count = 0

        for subscriber in weekly_subscribers:
            try:
                # 개인화된 리포트 생성
                logger.info(f"🔄 Generating personalized report for {subscriber['email']}")
                report = report_generator.generate_report(research_data, subscriber)

                # HTML 리포트 렌더링
                html_content = report_generator.render_html_report(report)

                # 리포트 저장 (선택사항)
                report_path = report_generator.save_report(report, "automation_reports")

                # 이메일 발송 (HTML 콘텐츠 사용)
                success = email_service.send_html_email(
                    subscriber["email"],
                    f"🧠 주간 임상심리학 연구 동향 - {datetime.now().strftime('%Y.%m.%d')}",
                    html_content
                )

                if success:
                    success_count += 1
                    subscriber_manager.mark_sent(subscriber["email"])
                    logger.info(f"✅ Email sent to {subscriber['email']}")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to send email to {subscriber['email']}")

            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing subscriber {subscriber['email']}: {str(e)}")

        # 4. 결과 로깅
        logger.info(f"📊 Automation completed: {success_count} success, {error_count} errors")

        # 5. 통계 업데이트
        update_automation_stats(success_count, error_count, len(weekly_subscribers))

        logger.info("🎉 Weekly Research Update Automation Completed Successfully!")

    except Exception as e:
        logger.error(f"💥 Critical error in automation: {str(e)}")
        sys.exit(1)

def collect_weekly_research_data() -> Dict:
    """주간 연구 데이터 수집"""
    from pubmed_service import pubmed_service
    import requests

    research_data = {
        "papers": [],
        "videos": [],
        "trending_topics": []
    }

    # 주요 임상심리학 키워드들
    key_topics = [
        "depression", "anxiety", "cognitive behavioral therapy",
        "PTSD", "trauma therapy", "mindfulness", "DBT", "ACT"
    ]

    try:
        # PubMed에서 최신 논문 수집 (지난 7일)
        logger.info("📄 Collecting papers from PubMed...")
        all_papers = []

        for topic in key_topics[:3]:  # 상위 3개 주제만 처리 (API 제한 고려)
            try:
                papers = pubmed_service.search_recent_papers([topic], days_back=7, max_results=3)
                all_papers.extend(papers)
            except Exception as e:
                logger.warning(f"⚠️ Failed to get papers for {topic}: {str(e)}")
                continue

        # 중복 제거 및 상위 5개 선택
        unique_papers = []
        seen_titles = set()

        for paper in all_papers:
            if paper['title'] not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(paper['title'])
                if len(unique_papers) >= 5:
                    break

        research_data["papers"] = unique_papers
        logger.info(f"✅ Collected {len(unique_papers)} unique papers")

        # YouTube 동영상 수집 (YouTube API 사용)
        logger.info("🎬 Collecting videos from YouTube...")
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')

        if youtube_api_key:
            videos = search_psychology_videos_for_automation(youtube_api_key)
            research_data["videos"] = videos[:3]  # 상위 3개
            logger.info(f"✅ Collected {len(videos)} videos")

        # 트렌딩 주제 분석
        logger.info("📈 Analyzing trending topics...")
        try:
            trending = pubmed_service.get_trending_topics(days_back=14)  # 2주간 데이터
            research_data["trending_topics"] = trending[:3]
            logger.info(f"✅ Found {len(trending)} trending topics")
        except Exception as e:
            logger.warning(f"⚠️ Trending analysis failed: {str(e)}")

    except Exception as e:
        logger.error(f"❌ Error collecting research data: {str(e)}")
        return None

    return research_data

def search_psychology_videos_for_automation(api_key: str) -> List[Dict]:
    """자동화용 YouTube 동영상 검색"""
    import requests

    videos = []
    search_queries = [
        "clinical psychology research 2025",
        "CBT therapy techniques",
        "depression treatment breakthrough"
    ]

    for query in search_queries:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'order': 'relevance',
                'maxResults': 2,
                'publishedAfter': (datetime.now() - timedelta(days=14)).isoformat() + 'Z',
                'key': api_key
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    videos.append({
                        "title": item['snippet']['title'],
                        "channel": item['snippet']['channelTitle'],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        "published": item['snippet']['publishedAt']
                    })
        except Exception as e:
            logger.warning(f"⚠️ YouTube search failed for '{query}': {str(e)}")
            continue

    return videos

def filter_content_by_interests(research_data: Dict, interests: List[str]) -> Dict:
    """구독자 관심사에 따라 콘텐츠 필터링"""
    if not interests:
        return research_data

    filtered_data = {
        "papers": [],
        "videos": [],
        "trending_topics": []
    }

    # 관심사를 소문자로 변환
    lower_interests = [interest.lower() for interest in interests]

    # 논문 필터링
    for paper in research_data.get("papers", []):
        title_lower = paper.get("title", "").lower()
        abstract_lower = paper.get("abstract", "").lower()

        if any(interest in title_lower or interest in abstract_lower for interest in lower_interests):
            filtered_data["papers"].append(paper)

    # 동영상 필터링
    for video in research_data.get("videos", []):
        title_lower = video.get("title", "").lower()

        if any(interest in title_lower for interest in lower_interests):
            filtered_data["videos"].append(video)

    # 트렌딩 주제 필터링
    for topic in research_data.get("trending_topics", []):
        keyword_lower = topic.get("keyword", "").lower()

        if any(interest in keyword_lower for interest in lower_interests):
            filtered_data["trending_topics"].append(topic)

    # 필터링된 결과가 너무 적으면 원본 데이터의 일부 사용
    if len(filtered_data["papers"]) < 2:
        filtered_data["papers"] = research_data.get("papers", [])[:3]

    if len(filtered_data["videos"]) < 1:
        filtered_data["videos"] = research_data.get("videos", [])[:2]

    return filtered_data

def update_automation_stats(success: int, errors: int, total: int):
    """자동화 통계 업데이트"""
    stats = {
        "last_run": datetime.now().isoformat(),
        "emails_sent": success,
        "errors": errors,
        "total_subscribers": total,
        "success_rate": (success / total * 100) if total > 0 else 0
    }

    try:
        import json
        with open("automation_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
        logger.info("📊 Automation stats updated")
    except Exception as e:
        logger.error(f"❌ Failed to update stats: {str(e)}")

if __name__ == "__main__":
    main()