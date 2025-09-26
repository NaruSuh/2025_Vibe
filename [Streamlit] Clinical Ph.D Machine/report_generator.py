#!/usr/bin/env python3
"""
수정된 주간 연구 리포트 생성기
CSS 브레이스 이스케이프 문제 해결
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResearchReport:
    """연구 리포트 데이터 클래스"""
    subscriber_email: str
    subscriber_name: str
    papers: List[Dict]
    videos: List[Dict]
    trending_topics: List[Dict]
    generated_date: str
    personalized: bool = False

class WeeklyReportGenerator:
    """주간 연구 리포트 생성기"""

    def __init__(self):
        self.report_template = self._load_report_template()

    def _load_report_template(self) -> str:
        """이메일 리포트 HTML 템플릿 로드"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>주간 임상심리학 연구 동향</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .date {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #4facfe;
            background: #f8f9ff;
            border-radius: 5px;
        }}
        .section-title {{
            color: #4facfe;
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        .paper-item, .video-item, .topic-item {{
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .paper-title, .video-title {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .paper-authors, .video-channel {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .paper-abstract {{
            color: #555;
            font-size: 14px;
            line-height: 1.5;
            margin-top: 10px;
        }}
        .trending-badge {{
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            padding: 3px 8px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 14px;
            color: #666;
        }}
        .personalized-note {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 500;
        }}
        .no-content {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 주간 임상심리학 연구 동향</h1>
            <div class="date">{date}</div>
        </div>

        {personalized_note}

        <div class="section">
            <div class="section-title">📄 최신 연구 논문</div>
            {papers_content}
        </div>

        <div class="section">
            <div class="section-title">🎬 추천 동영상</div>
            {videos_content}
        </div>

        <div class="section">
            <div class="section-title">📈 트렌딩 주제</div>
            {trending_content}
        </div>

        <div class="footer">
            <p>📧 Clinical Psychology Research Hub<br>
            이 이메일은 주간 연구 동향 구독 서비스입니다.</p>
            <p><small>구독 해지를 원하시면 회신해 주세요.</small></p>
        </div>
    </div>
</body>
</html>"""

    def generate_report(self, research_data: Dict, subscriber: Dict) -> ResearchReport:
        """개별 구독자를 위한 리포트 생성"""
        logger.info(f"Generating report for {subscriber['email']}")

        # 구독자 관심사에 따른 데이터 필터링
        filtered_data = self._filter_by_interests(research_data, subscriber.get('interests', []))

        # 리포트 객체 생성
        report = ResearchReport(
            subscriber_email=subscriber['email'],
            subscriber_name=subscriber['name'],
            papers=filtered_data.get('papers', []),
            videos=filtered_data.get('videos', []),
            trending_topics=filtered_data.get('trending_topics', []),
            generated_date=datetime.now().isoformat(),
            personalized=bool(subscriber.get('interests'))
        )

        return report

    def _filter_by_interests(self, research_data: Dict, interests: List[str]) -> Dict:
        """관심사에 따른 데이터 필터링"""
        if not interests:
            return research_data

        lower_interests = [interest.lower() for interest in interests]
        filtered_data = {
            "papers": [],
            "videos": [],
            "trending_topics": []
        }

        # 논문 필터링
        for paper in research_data.get('papers', []):
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            if any(interest in title or interest in abstract for interest in lower_interests):
                filtered_data['papers'].append(paper)

        # 동영상 필터링
        for video in research_data.get('videos', []):
            title = video.get('title', '').lower()
            if any(interest in title for interest in lower_interests):
                filtered_data['videos'].append(video)

        # 트렌딩 주제 필터링
        for topic in research_data.get('trending_topics', []):
            keyword = topic.get('keyword', '').lower()
            if any(interest in keyword for interest in lower_interests):
                filtered_data['trending_topics'].append(topic)

        # 필터링 결과가 부족하면 일반 데이터 추가
        if len(filtered_data['papers']) < 2:
            filtered_data['papers'].extend(research_data.get('papers', [])[:3])
        if len(filtered_data['videos']) < 1:
            filtered_data['videos'].extend(research_data.get('videos', [])[:2])

        return filtered_data

    def render_html_report(self, report: ResearchReport) -> str:
        """HTML 리포트 렌더링"""

        # 개인화 노트
        personalized_note = ""
        if report.personalized:
            interests_str = ", ".join([f"#{interest}" for interest in self._get_subscriber_interests(report.subscriber_email)])
            personalized_note = f"""
            <div class="personalized-note">
                🎯 {report.subscriber_name}님의 관심 분야 ({interests_str})에 맞춘 맞춤형 리포트입니다
            </div>
            """

        # 논문 섹션 렌더링
        papers_content = self._render_papers_section(report.papers)

        # 동영상 섹션 렌더링
        videos_content = self._render_videos_section(report.videos)

        # 트렌딩 섹션 렌더링
        trending_content = self._render_trending_section(report.trending_topics)

        # 최종 HTML 생성
        html_content = self.report_template.format(
            date=datetime.now().strftime("%Y년 %m월 %d일"),
            personalized_note=personalized_note,
            papers_content=papers_content,
            videos_content=videos_content,
            trending_content=trending_content
        )

        return html_content

    def _render_papers_section(self, papers: List[Dict]) -> str:
        """논문 섹션 HTML 렌더링"""
        if not papers:
            return '<div class="no-content">이번 주에는 새로운 논문이 없습니다.</div>'

        html_parts = []
        for paper in papers:
            authors = ", ".join(paper.get('authors', [])[:3])  # 최대 3명만 표시
            if len(paper.get('authors', [])) > 3:
                authors += " 외"

            abstract = paper.get('abstract', '')[:200] + '...' if len(paper.get('abstract', '')) > 200 else paper.get('abstract', '')

            paper_html = f"""
            <div class="paper-item">
                <div class="paper-title">{paper.get('title', 'No title')}</div>
                <div class="paper-authors">👥 {authors}</div>
                <div class="paper-authors">📅 {paper.get('published_date', 'Unknown date')}</div>
                {f'<div class="paper-abstract">{abstract}</div>' if abstract else ''}
            </div>
            """
            html_parts.append(paper_html)

        return "".join(html_parts)

    def _render_videos_section(self, videos: List[Dict]) -> str:
        """동영상 섹션 HTML 렌더링"""
        if not videos:
            return '<div class="no-content">이번 주에는 추천 동영상이 없습니다.</div>'

        html_parts = []
        for video in videos:
            video_html = f"""
            <div class="video-item">
                <div class="video-title">🎬 <a href="{video.get('url', '#')}" style="color: #4facfe; text-decoration: none;">{video.get('title', 'No title')}</a></div>
                <div class="video-channel">📺 {video.get('channel', 'Unknown channel')}</div>
                <div class="video-channel">📅 {video.get('published', 'Unknown date')}</div>
            </div>
            """
            html_parts.append(video_html)

        return "".join(html_parts)

    def _render_trending_section(self, topics: List[Dict]) -> str:
        """트렌딩 섹션 HTML 렌더링"""
        if not topics:
            return '<div class="no-content">이번 주 트렌딩 주제가 없습니다.</div>'

        html_parts = []
        for topic in topics:
            topic_html = f"""
            <div class="topic-item">
                <span class="trending-badge">🔥 HOT</span>
                <div style="margin-top: 10px;">
                    <strong>#{topic.get('keyword', 'Unknown')}</strong>
                    <div style="font-size: 14px; color: #666; margin-top: 5px;">
                        📊 {topic.get('count', 0)}건의 논문 · 증가율 {topic.get('growth_rate', 0)}%
                    </div>
                </div>
            </div>
            """
            html_parts.append(topic_html)

        return "".join(html_parts)

    def _get_subscriber_interests(self, email: str) -> List[str]:
        """구독자 관심사 조회 (임시 구현)"""
        try:
            from subscriber_manager import subscriber_manager
            subscriber = subscriber_manager.get_subscriber(email)
            return subscriber.get('interests', []) if subscriber else []
        except:
            return []

    def save_report(self, report: ResearchReport, output_dir: str = "reports") -> str:
        """리포트를 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)

        # 파일명 생성
        date_str = datetime.now().strftime("%Y%m%d")
        safe_email = report.subscriber_email.replace("@", "_at_").replace(".", "_")
        filename = f"weekly_report_{date_str}_{safe_email}.html"
        filepath = os.path.join(output_dir, filename)

        # HTML 리포트 생성 및 저장
        html_content = self.render_html_report(report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Report saved: {filepath}")
        return filepath

    def generate_bulk_reports(self, research_data: Dict, subscribers: List[Dict]) -> List[ResearchReport]:
        """대량 리포트 생성"""
        reports = []

        for subscriber in subscribers:
            try:
                report = self.generate_report(research_data, subscriber)
                reports.append(report)
                logger.info(f"✅ Report generated for {subscriber['email']}")
            except Exception as e:
                logger.error(f"❌ Failed to generate report for {subscriber['email']}: {e}")

        return reports

# 전역 리포트 생성기 인스턴스
report_generator = WeeklyReportGenerator()