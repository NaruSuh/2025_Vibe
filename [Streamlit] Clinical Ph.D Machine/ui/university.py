
import streamlit as st
from professors_database import get_universities, APA_PROFESSORS_DATABASE
from ui.shared import (
    display_professor_info,
    display_chatgpt_section,
    search_professor_videos,
    display_video_results
)

def render(youtube_api_key, openai_api_key):
    """대학별 교수진 인터페이스"""
    st.markdown("### 🏛️ 대학별 교수진 탐색")
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
                
                display_professor_info(prof_data)
                
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
