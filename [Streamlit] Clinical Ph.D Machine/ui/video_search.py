import streamlit as st
from datetime import datetime
from ui.shared import display_video_results, search_psychology_videos

def get_psychology_categories():
    """임상심리학 관련 카테고리 목록"""
    return {
        "임상심리학 기초": "임상심리학 기초 이론",
        "심리치료 기법": "심리치료 기법 CBT 인지행동치료",
        "정신건강": "정신건강 우울증 불안장애",
        "심리평가": "심리평가 심리검사",
        "발달심리학": "발달심리학 아동심리",
        "트라우마 치료": "트라우마 치료 EMDR",
        "가족치료": "가족치료 부부상담",
        "중독치료": "중독치료 알코올 도박",
        "집단치료": "집단치료 그룹상담",
        "심리학 연구": "심리학 연구방법론"
    }

def get_apa_doctoral_categories():
    """APA 박사과정 준비용 고급 전문 카테고리"""
    return {
        "신경심리학": "neuropsychology cognitive assessment brain injury dementia",
        "임상정신병리학": "psychopathology DSM-5 diagnostic criteria differential diagnosis",
        "심리치료 이론 통합": "psychotherapy integration theoretical orientation case conceptualization",
        "심리평가 전문": "psychological assessment WAIS MMPI projective testing",
        "연구 방법론": "research methodology statistics dissertation IRB ethics",
        "다문화 임상심리학": "multicultural psychology diversity cultural competence",
        "건강심리학": "health psychology medical psychology chronic illness",
        "법정심리학": "forensic psychology competency evaluation expert witness",
        "임상수퍼비전": "clinical supervision training doctoral internship",
        "전문윤리": "professional ethics APA ethics code boundaries dual relationships",
        "정신약리학": "psychopharmacology medication interaction psychology",
        "성인 심리치료": "adult psychotherapy evidence-based treatment protocols",
        "아동청소년 임상": "child adolescent psychology developmental psychopathology",
        "커플 가족치료": "couples therapy family systems structural therapy",
        "DBT & CBT 고급": "dialectical behavior therapy cognitive behavioral therapy skills",
        "트라우마 전문치료": "trauma therapy PTSD complex trauma EMDR",
        "성격장애 치료": "personality disorders borderline narcissistic treatment",
        "중독 전문치료": "addiction psychology substance abuse recovery treatment",
        "집단 심리치료": "group therapy process group dynamics therapeutic factors",
        "정신분석 이론": "psychoanalytic theory object relations attachment theory"
    }

def render(api_key):
    """동영상 검색 인터페이스"""
    st.markdown("### 🎬 임상심리학 동영상 검색")
    st.markdown("---")
    
    # 난이도 레벨 선택
    level = st.radio(
        "🎓 학습 레벨:",
        ["📚 기초-중급", "🎓 APA 박사과정"],
        help="기초-중급: 일반적인 임상심리학 내용\nAPA 박사과정: 고급 전문 지식 및 영어 콘텐츠"
    )
    
    # 레벨에 따른 카테고리 선택
    if level == "📚 기초-중급":
        categories = get_psychology_categories()
        st.info("📖 기초부터 중급까지의 임상심리학 내용")
    else:
        categories = get_apa_doctoral_categories()
        st.warning("🎓 APA 박사과정 수준의 전문 내용 (주로 영어)")
    
    selected_category = st.selectbox(
        "전문 분야:",
        options=list(categories.keys()),
        index=0
    )
    
    # 커스텀 검색어
    custom_search = st.text_input(
        "추가 검색어:",
        placeholder="예: 인지행동치료, CBT protocol",
        help="특정 주제를 더 자세히 검색하고 싶다면 입력하세요"
    )
    
    # 언어 설정 (APA 레벨일 때만)
    if level == "🎓 APA 박사과정":
        language = st.selectbox(
            "언어 우선순위:",
            ["영어 (English)", "한국어", "혼합"],
            help="APA 박사과정 내용은 영어 자료가 더 풍부합니다"
        )
    else:
        language = "한국어"
    
    # 검색 버튼
    search_button = st.button("🔍 동영상 검색", use_container_width=True, disabled=not api_key)
    
    # 검색 쿼리 구성
    search_query = categories[selected_category]
    if custom_search:
        search_query += f" {custom_search}"
    
    # 언어별 검색어 조정
    if level == "🎓 APA 박사과정":
        if language == "영어 (English)":
            search_query = search_query
        elif language == "한국어":
            search_query += " 한국어 번역 korean"
    
    if (search_button or 'videos' not in st.session_state) and api_key:
        with st.spinner(f'\'{selected_category}\' 관련 동영상을 검색 중...'):
            st.session_state.videos = search_psychology_videos(api_key, search_query)
            st.session_state.last_search = {
                'category': selected_category,
                'level': level,
                'query': search_query,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    videos = st.session_state.get('videos', [])
    
    if not api_key:
        st.info("👈 사이드바에서 YouTube API 키를 입력하거나 .env 파일에 설정해주세요.")
        return
    
    if not videos and api_key:
        st.warning("검색 결과가 없습니다. 다른 카테고리를 시도해보거나 검색어를 수정해주세요.")
        return
    
    # 검색 결과 표시
    display_video_results(videos)