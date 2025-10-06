
import streamlit as st
from professors_database import (
    search_professors_by_keyword,
    get_research_areas,
    APA_PROFESSORS_DATABASE
)
from ui.shared import (
    display_professor_info,
    display_chatgpt_section,
    search_professor_videos,
    display_video_results
)

def render(youtube_api_key, openai_api_key):
    """교수진 검색 인터페이스"""
    st.markdown("### 👨‍🏫 APA 인증 교수진 검색")
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
                prof = display_professor_info(prof_data)
                
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
