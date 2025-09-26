import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import openai
from professors_database import (
    search_professors_by_keyword,
    get_research_areas,
    get_universities,
    get_professors_by_university,
    generate_video_search_keywords,
    APA_PROFESSORS_DATABASE
)
from email_service import email_service
from pubmed_service import pubmed_service

load_dotenv()

st.set_page_config(
    page_title="임상심리학 동영상 추천",
    page_icon="🧠",
    layout="wide"
)

def get_professor_prompt_template(professor_data):
    """교수님별 맞춤형 프롬프트 템플릿"""
    prof = professor_data["professor"]
    university = professor_data["university"]
    
    prompt = f"""
당신은 {university}의 {prof['name']} 교수님 연구실 지원을 돕는 전문 상담사입니다.

📋 교수님 정보:
- 이름: {prof['name']}
- 소속: {university} ({professor_data.get('location', '')})
- 연구실: {prof.get('lab', '정보 없음')}
- 전문 분야: {', '.join(prof.get('research_areas', []))}
- 연구 키워드: {prof.get('research_keywords', '')}

🎯 역할:
1. 이 교수님 연구실 지원에 관한 모든 질문에 답변
2. 연구 분야 설명 및 최신 동향 제공  
3. 지원서 작성 조언 및 면접 준비 도움
4. 관련 논문, 연구 방향성 추천
5. 대학원 생활 및 커리어 조언

💡 응답 스타일:
- 따뜻하고 격려적인 톤
- 구체적이고 실용적인 조언
- 한국어로 답변 (필요시 영어 전문용어 병기)
- 불확실한 정보는 추가 확인을 권유

어떤 도움이 필요하신가요?
"""
    return prompt

def get_question_templates():
    """질문 견본 및 추천 질문들"""
    return {
        "🔬 연구 분야": [
            "이 교수님의 주요 연구 분야는 무엇인가요?",
            "최근 연구 동향과 방향성을 알려주세요",
            "이 분야에서 주목받는 연구 주제는 무엇인가요?",
            "관련 최신 논문이나 학회 발표를 추천해주세요"
        ],
        "📝 지원서 작성": [
            "연구계획서 작성 시 주의사항은 무엇인가요?",
            "이 교수님이 선호하는 연구 방법론이 있나요?",
            "SOP(목적진술서)에 포함해야 할 핵심 내용은?",
            "지원서에서 강조해야 할 경험이나 역량은?"
        ],
        "🎓 대학원 생활": [
            "이 연구실의 분위기와 문화는 어떤가요?",
            "대학원생들은 주로 어떤 프로젝트를 하나요?",
            "졸업 요건과 논문 발표 과정을 알려주세요",
            "연구실에서 제공하는 교육이나 트레이닝은?"
        ],
        "💼 진로 & 커리어": [
            "이 전공으로 졸업 후 진로는 어떻게 되나요?",
            "업계에서 요구하는 핵심 역량은 무엇인가요?",
            "관련 자격증이나 추가 교육이 필요한가요?",
            "네트워킹이나 학회 참여 조언을 해주세요"
        ],
        "📚 준비 사항": [
            "지원 전에 미리 공부해야 할 내용은?",
            "추천 도서나 논문이 있다면 알려주세요",
            "필요한 선수과목이나 배경지식은?",
            "연구 도구나 소프트웨어 사용법을 배워야 하나요?"
        ]
    }

def chat_with_gpt(api_key, professor_data, user_message, conversation_history=[]):
    """ChatGPT API를 사용한 대화 함수"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # 시스템 프롬프트 설정
        system_prompt = get_professor_prompt_template(professor_data)
        
        # 대화 히스토리 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 이전 대화 히스토리 추가
        for entry in conversation_history:
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["assistant"]})
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ ChatGPT 응답 중 오류가 발생했습니다: {str(e)}"

def search_psychology_videos(api_key, search_query="임상심리학", category="교육"):
    """임상심리학 관련 동영상을 검색하는 함수"""
    try:
        if not api_key:
            st.error("YouTube API 키를 입력해주세요.")
            return []
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'order': 'relevance',
            'maxResults': 30,
            'regionCode': 'KR',
            'relevanceLanguage': 'ko',
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        search_data = response.json()
        video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
        
        if not video_ids:
            return []
        
        # 비디오 상세 정보 가져오기
        details_url = "https://www.googleapis.com/youtube/v3/videos"
        details_params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids),
            'key': api_key
        }
        
        details_response = requests.get(details_url, params=details_params)
        details_response.raise_for_status()
        
        details_data = details_response.json()
        return details_data.get('items', [])
        
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        return []
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
        return []

def format_view_count(view_count):
    """조회수를 읽기 쉬운 형태로 포맷팅"""
    try:
        count = int(view_count)
        if count >= 100000000:  # 1억 이상
            return f"{count//100000000}억{(count%100000000)//10000:,}만"
        elif count >= 10000:  # 1만 이상
            return f"{count//10000:,}만"
        else:
            return f"{count:,}"
    except:
        return view_count

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

def search_professor_videos(api_key, professor_name, research_keywords):
    """특정 교수의 연구 분야와 관련된 동영상을 검색하는 함수"""
    search_query = f"{professor_name} {research_keywords} psychology lecture research"
    return search_psychology_videos(api_key, search_query)

def display_professor_info(professor_data, openai_api_key=None):
    """교수 정보를 표시하는 함수"""
    prof = professor_data["professor"]
    
    st.markdown(f"### 👨‍🏫 {prof['name']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**🏛️ 소속:** {professor_data['university']}")
        st.markdown(f"**📍 위치:** {professor_data['location']}")
        st.markdown(f"**🎓 프로그램:** {professor_data['program_type']}")
        
        if prof.get('lab'):
            st.markdown(f"**🔬 연구실:** {prof['lab']}")
        
        st.markdown("**🔍 연구 분야:**")
        for area in prof['research_areas']:
            st.markdown(f"- {area}")
    
    with col2:
        if prof.get('email'):
            st.markdown(f"**📧 이메일:** {prof['email']}")
    
    return prof

def display_chatgpt_section(professor_data, openai_api_key, unique_key):
    """교수님별 ChatGPT 섹션 표시"""
    if not openai_api_key:
        st.info("🤖 ChatGPT 상담을 위해 사이드바에서 OpenAI API 키를 입력해주세요.")
        return
    
    prof = professor_data["professor"]
    st.markdown(f"### 🤖 {prof['name']} 교수님 연구실 지원 상담")
    
    # 질문 견본 섹션
    with st.expander("💡 추천 질문 견본", expanded=False):
        question_templates = get_question_templates()
        
        for category, questions in question_templates.items():
            st.markdown(f"**{category}**")
            for i, question in enumerate(questions):
                if st.button(f"❓ {question}", key=f"{unique_key}_template_{category}_{i}"):
                    st.session_state[f'chat_input_{unique_key}'] = question
            st.markdown("")
    
    # 대화 히스토리 초기화
    chat_history_key = f'chat_history_{unique_key}'
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []
    
    # 대화 히스토리 표시
    if st.session_state[chat_history_key]:
        st.markdown("#### 💬 대화 기록")
        for entry in st.session_state[chat_history_key]:
            with st.container():
                st.markdown(f"**👤 질문:** {entry['user']}")
                st.markdown(f"**🤖 답변:** {entry['assistant']}")
                st.markdown("---")
    
    # 새 질문 입력
    user_input_key = f'chat_input_{unique_key}'
    if user_input_key not in st.session_state:
        st.session_state[user_input_key] = ""
    
    user_message = st.text_area(
        "질문을 입력하세요:",
        value=st.session_state.get(user_input_key, ""),
        placeholder="예: 이 교수님의 연구 분야에 대해 자세히 설명해주세요.",
        height=100,
        key=f"text_area_{unique_key}"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💬 질문하기", key=f"ask_{unique_key}"):
            if user_message.strip():
                with st.spinner("🤖 ChatGPT가 답변을 생성 중입니다..."):
                    response = chat_with_gpt(
                        openai_api_key, 
                        professor_data, 
                        user_message, 
                        st.session_state[chat_history_key]
                    )
                    
                    # 대화 히스토리에 추가
                    st.session_state[chat_history_key].append({
                        "user": user_message,
                        "assistant": response
                    })
                    
                    # 입력창 초기화
                    st.session_state[user_input_key] = ""
                    st.rerun()
            else:
                st.warning("질문을 입력해주세요.")
    
    with col2:
        if st.button("🗑️ 대화 기록 삭제", key=f"clear_{unique_key}"):
            st.session_state[chat_history_key] = []
            st.success("대화 기록이 삭제되었습니다.")
            st.rerun()

def main():
    st.title("🧠 임상심리학 동영상 & 교수진 추천")
    st.markdown("**APA 인증 186개 대학의 임상심리학 교수진과 관련 동영상을 찾아드립니다**")
    
    # 전역 API 키 설정 (사이드바에 한 번만 표시)
    with st.sidebar:
        st.header("🎯 API 설정")
        
        # YouTube API 키
        youtube_api_key = st.text_input(
            "YouTube API 키:",
            type="password",
            placeholder="AIzaSy...",
            help="Google Cloud Console에서 YouTube Data API v3 키를 발급받으세요"
        )
        
        # OpenAI API 키
        openai_api_key = st.text_input(
            "OpenAI API 키:",
            type="password", 
            placeholder="sk-...",
            help="OpenAI에서 발급받은 API 키를 입력하세요"
        )
        
        # .env 파일과 Streamlit secrets에서 API 키 가져오기 (백업)
        if not youtube_api_key:
            youtube_api_key = os.getenv('YOUTUBE_API_KEY') or st.secrets.get('YOUTUBE_API_KEY')
        if not openai_api_key:
            openai_api_key = os.getenv('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY')
        
        # Brevo API 키
        brevo_api_key = os.getenv('BREVO_API_KEY') or st.secrets.get('BREVO_API_KEY')

        # API 키 상태 표시
        st.markdown("---")
        st.markdown("**📊 API 상태:**")
        st.write("🎬 YouTube:", "✅ 연결됨" if youtube_api_key else "❌ 미설정")
        st.write("🤖 ChatGPT:", "✅ 연결됨" if openai_api_key else "❌ 미설정")
        st.write("📧 Email:", "✅ 연결됨" if brevo_api_key else "❌ 미설정")

    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 동영상 검색", "👨‍🏫 교수진 검색", "🏛️ 대학별 교수진", "📧 연구 알림"])
    
    with tab1:
        st.markdown("### 🎬 임상심리학 동영상 검색")
        video_search_interface(youtube_api_key)
    
    with tab2:
        st.markdown("### 👨‍🏫 APA 인증 교수진 검색")
        professor_search_interface(youtube_api_key, openai_api_key)
    
    with tab3:
        st.markdown("### 🏛️ 대학별 교수진 탐색")
        university_interface(youtube_api_key, openai_api_key)

    with tab4:
        st.markdown("### 📧 연구 트렌드 알림 서비스")
        research_alert_interface(brevo_api_key)

def video_search_interface(api_key):
    """동영상 검색 인터페이스"""
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

def professor_search_interface(youtube_api_key, openai_api_key):
    """교수진 검색 인터페이스"""
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🔍 연구 분야로 검색")
        research_keyword = st.text_input(
            "연구 키워드:",
            placeholder="예: depression, CBT, PTSD, anxiety",
            help="관심 있는 연구 분야나 키워드를 입력하세요"
        )
        
        if st.button("🔍 교수 검색", disabled=not research_keyword):
            professors = search_professors_by_keyword(research_keyword)
            st.session_state.searched_professors = professors
            st.session_state.search_keyword = research_keyword
    
    with col2:
        st.markdown("#### 📊 통계 정보")
        total_universities = len(APA_PROFESSORS_DATABASE)
        total_professors = sum(len(info["professors"]) for info in APA_PROFESSORS_DATABASE.values())
        
        st.metric("APA 인증 대학", f"{total_universities}개")
        st.metric("등록된 교수", f"{total_professors}명")
        
        # 주요 연구 분야
        st.markdown("**주요 연구 분야:**")
        areas = get_research_areas()
        for area in areas[:8]:
            st.markdown(f"• {area}")
    
    # 검색 결과 표시
    if hasattr(st.session_state, 'searched_professors') and st.session_state.searched_professors:
        st.markdown(f"### 🎯 '{st.session_state.search_keyword}' 검색 결과 ({len(st.session_state.searched_professors)}명)")
        
        for i, prof_data in enumerate(st.session_state.searched_professors):
            with st.expander(f"👨‍🏫 {prof_data['professor']['name']} - {prof_data['university']}"):
                prof = display_professor_info(prof_data, openai_api_key)
                
                st.markdown("---")
                
                # ChatGPT 상담 섹션
                display_chatgpt_section(prof_data, openai_api_key, f"search_{i}")
                
                st.markdown("---")
                
                # 관련 동영상 검색 버튼
                if youtube_api_key:
                    if st.button(f"🎬 {prof['name']} 관련 동영상 검색", key=f"video_search_{i}"):
                        with st.spinner(f"{prof['name']} 관련 동영상 검색 중..."):
                            videos = search_professor_videos(youtube_api_key, prof['name'], prof['research_keywords'])
                            st.session_state[f'prof_videos_{i}'] = videos
                    
                    # 동영상 결과 표시
                    if f'prof_videos_{i}' in st.session_state:
                        videos = st.session_state[f'prof_videos_{i}']
                        if videos:
                            st.markdown(f"#### 🎬 {prof['name']} 관련 동영상 ({len(videos)}개)")
                            display_video_results(videos, compact=True)
                        else:
                            st.info("관련 동영상을 찾을 수 없습니다.")

def university_interface(youtube_api_key, openai_api_key):
    """대학별 교수진 인터페이스"""
    st.markdown("---")
    
    universities = get_universities()
    selected_university = st.selectbox(
        "🏛️ 대학 선택:",
        options=universities,
        index=0
    )
    
    if selected_university:
        university_info = APA_PROFESSORS_DATABASE[selected_university]
        professors = university_info["professors"]
        
        st.markdown(f"### 🏛️ {selected_university}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**📍 위치:** {university_info['location']}")
            st.markdown(f"**🎓 프로그램:** {university_info['program_type']}")
        with col2:
            st.metric("교수진 수", f"{len(professors)}명")
        
        st.markdown("---")
        
        # 교수진 목록
        for i, prof in enumerate(professors):
            with st.expander(f"👨‍🏫 {prof['name']} - {', '.join(prof['research_areas'][:3])}"):
                prof_data = {
                    "professor": prof,
                    "university": selected_university,
                    "location": university_info["location"],
                    "program_type": university_info["program_type"]
                }
                
                display_professor_info(prof_data, openai_api_key)
                
                st.markdown("---")
                
                # ChatGPT 상담 섹션
                display_chatgpt_section(prof_data, openai_api_key, f"univ_{i}")
                
                st.markdown("---")
                
                # 관련 동영상 검색
                if youtube_api_key:
                    if st.button(f"🎬 {prof['name']} 관련 동영상 검색", key=f"univ_video_{i}"):
                        with st.spinner(f"{prof['name']} 관련 동영상 검색 중..."):
                            videos = search_professor_videos(youtube_api_key, prof['name'], prof['research_keywords'])
                            st.session_state[f'univ_prof_videos_{i}'] = videos
                    
                    # 동영상 결과 표시
                    if f'univ_prof_videos_{i}' in st.session_state:
                        videos = st.session_state[f'univ_prof_videos_{i}']
                        if videos:
                            st.markdown(f"#### 🎬 {prof['name']} 관련 동영상 ({len(videos)}개)")
                            display_video_results(videos, compact=True)
                        else:
                            st.info("관련 동영상을 찾을 수 없습니다.")

def research_alert_interface(brevo_api_key):
    """연구 알림 인터페이스"""
    st.markdown("---")

    if not brevo_api_key:
        st.info("👈 사이드바에서 Brevo API 키를 설정해주세요.")
        return

    # 탭으로 기능 분리
    alert_tab1, alert_tab2, alert_tab3 = st.tabs(["🔔 알림 설정", "📚 최신 논문", "📊 트렌드 분석"])

    with alert_tab1:
        st.markdown("#### 🔔 연구 알림 구독 설정")

        col1, col2 = st.columns([1, 1])

        with col1:
            user_name = st.text_input(
                "이름:",
                placeholder="홍길동"
            )
            user_email = st.text_input(
                "이메일:",
                placeholder="example@email.com"
            )

        with col2:
            interest_keywords = st.multiselect(
                "관심 연구 분야:",
                ["Depression", "Anxiety", "PTSD", "CBT", "DBT", "Trauma Therapy",
                 "Child Psychology", "Neuropsychology", "Group Therapy", "Mindfulness"],
                default=["Depression", "CBT"]
            )

            alert_frequency = st.selectbox(
                "알림 주기:",
                ["매주 월요일", "격주", "월 1회"]
            )

        # 테스트 이메일 발송
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("📧 테스트 알림 발송", use_container_width=True):
                if user_email and user_name:
                    with st.spinner("이메일 발송 중..."):
                        # 샘플 연구 업데이트 데이터 생성
                        sample_updates = {
                            "papers": [
                                {
                                    "title": "Effectiveness of CBT for Depression in Adults",
                                    "authors": "Smith, J. et al.",
                                    "journal": "Journal of Clinical Psychology"
                                },
                                {
                                    "title": "Digital Mental Health Interventions: A Review",
                                    "authors": "Johnson, M. et al.",
                                    "journal": "Psychological Medicine"
                                }
                            ],
                            "videos": [
                                {
                                    "title": "CBT Techniques for Anxiety",
                                    "channel": "Psychology Today",
                                    "views": "12,450",
                                    "url": "https://youtube.com/example"
                                }
                            ]
                        }

                        success = email_service.send_research_alert(
                            user_email, user_name, sample_updates
                        )

                        if success:
                            st.success("✅ 테스트 이메일이 발송되었습니다!")
                        else:
                            st.error("❌ 이메일 발송에 실패했습니다.")
                else:
                    st.warning("이름과 이메일을 입력해주세요.")

        with col2:
            # 이메일 연결 테스트
            if st.button("🔗 연결 테스트", use_container_width=True):
                with st.spinner("연결 확인 중..."):
                    is_connected = email_service.test_email_connection()
                    if is_connected:
                        st.success("✅ 이메일 서비스 연결됨")
                    else:
                        st.error("❌ 이메일 서비스 연결 실패")

    with alert_tab2:
        st.markdown("#### 📚 최신 임상심리학 논문")

        col1, col2 = st.columns([1, 1])
        with col1:
            search_keywords = st.multiselect(
                "검색 키워드:",
                ["depression", "anxiety", "cognitive behavioral therapy", "PTSD", "trauma"],
                default=["depression"]
            )
        with col2:
            days_back = st.selectbox("기간:", [7, 14, 30], index=0)

        if st.button("🔍 최신 논문 검색", use_container_width=True):
            if search_keywords:
                with st.spinner("PubMed에서 논문을 검색하는 중..."):
                    papers = pubmed_service.search_recent_papers(search_keywords, days_back, 10)

                    if papers:
                        st.success(f"✅ {len(papers)}개의 논문을 찾았습니다.")

                        for i, paper in enumerate(papers, 1):
                            with st.expander(f"📄 {i}. {paper['title'][:80]}..."):
                                st.markdown(f"**저자:** {paper['authors']}")
                                st.markdown(f"**저널:** {paper['journal']}")
                                st.markdown(f"**발행일:** {paper['pub_date']}")
                                st.markdown(f"**초록:** {paper['abstract']}")
                                if paper['url']:
                                    st.markdown(f"🔗 [PubMed에서 보기]({paper['url']})")
                    else:
                        st.info("검색 결과가 없습니다. 다른 키워드를 시도해보세요.")
            else:
                st.warning("검색할 키워드를 선택해주세요.")

    with alert_tab3:
        st.markdown("#### 📊 임상심리학 트렌드 분석")

        if st.button("📈 트렌딩 주제 분석", use_container_width=True):
            with st.spinner("트렌딩 주제를 분석하는 중... (30초 정도 소요됩니다)"):
                trending_topics = pubmed_service.get_trending_topics(30)

                if trending_topics:
                    st.success("✅ 트렌드 분석 완료!")

                    for i, topic in enumerate(trending_topics, 1):
                        with st.container():
                            st.markdown(f"### {i}. {topic['keyword'].title()}")
                            st.markdown(f"**최근 30일 논문 수:** {topic['paper_count']}편")

                            if topic['recent_papers']:
                                st.markdown("**주요 논문:**")
                                for paper in topic['recent_papers'][:2]:
                                    st.markdown(f"• **{paper['title']}** - {paper['authors']}")

                            st.markdown("---")
                else:
                    st.info("트렌드 데이터를 불러올 수 없습니다.")

def display_video_results(videos, compact=False):
    """동영상 결과를 표시하는 함수"""
    if not videos:
        return

    max_videos = 5 if compact else len(videos)

    for video in videos[:max_videos]:
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})

        video_id = video.get('id', '')
        title = snippet.get('title', '제목 없음')
        channel_name = snippet.get('channelTitle', '채널명 없음')
        thumbnail_url = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
        view_count = statistics.get('viewCount', '0')
        published_at = snippet.get('publishedAt', '')
        description = snippet.get('description', '')[:100] + '...' if len(snippet.get('description', '')) > 100 else snippet.get('description', '')

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            formatted_date = pub_date.strftime('%Y-%m-%d')
        except:
            formatted_date = '날짜 없음'

        col1, col2, col3, col4, col5 = st.columns([0.8, 3.5, 1.2, 1, 1])

        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, width=100)

        with col2:
            st.markdown(f"**{title[:80]}{'...' if len(title) > 80 else ''}**")
            if description and not compact:
                st.caption(f"{description[:60]}{'...' if len(description) > 60 else ''}")

        with col3:
            st.write(f"**{channel_name[:15]}{'...' if len(channel_name) > 15 else ''}**")
            st.caption(f"{formatted_date}")

        with col4:
            st.write(f"**{format_view_count(view_count)}회**")

        with col5:
            st.markdown(f"[▶️ 보기]({video_url})")

if __name__ == "__main__":
    main()