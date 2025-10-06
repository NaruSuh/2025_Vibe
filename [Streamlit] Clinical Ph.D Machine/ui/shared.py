import streamlit as st
from datetime import datetime
import openai
import requests

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

def search_professor_videos(api_key, professor_name, research_keywords):
    """특정 교수의 연구 분야와 관련된 동영상을 검색하는 함수"""
    search_query = f"{professor_name} {research_keywords} psychology lecture research"
    return search_psychology_videos(api_key, search_query)

def display_professor_info(professor_data):
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
            if 'chat_history_delete_confirm' not in st.session_state:
                st.session_state.chat_history_delete_confirm = True
                st.rerun()
            
            if st.session_state.get('chat_history_delete_confirm'):
                st.warning("정말로 대화 기록을 삭제하시겠습니까?")
                c1, c2, c3 = st.columns([1,1,4])
                with c1:
                    if st.button("삭제", key=f"confirm_clear_{unique_key}"):
                        st.session_state[chat_history_key] = []
                        st.session_state.chat_history_delete_confirm = False
                        st.success("대화 기록이 삭제되었습니다.")
                        st.rerun()
                with c2:
                    if st.button("취소", key=f"cancel_clear_{unique_key}"):
                        st.session_state.chat_history_delete_confirm = False
                        st.rerun()