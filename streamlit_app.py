"""
2025_Vibe - 임상심리학 동영상 & 교수진 추천 앱
메인 Streamlit 애플리케이션

Phase 3: 필터/정렬, 즐겨찾기, 비교 기능 포함
Phase 4: 연구 매칭, SOP 도우미, 스마트 질문 생성
"""
import streamlit as st
import os
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime

from config import (
    PAGE_CONFIG,
    SessionKeys,
    PSYCHOLOGY_CATEGORIES,
    APA_DOCTORAL_CATEGORIES,
    UIText,
    EnvKeys,
    SortOptions,
    DateFilterOptions,
)
from api_handlers import (
    search_psychology_videos,
    search_professor_videos,
)
from ui_components import (
    display_professor_info,
    display_chatgpt_section,
    display_video_results,
    display_video_filter_controls,
    display_video_stats,
    display_video_results_with_favorites,
    display_professor_with_actions,
    display_favorites_tab,
    display_compare_tab,
    display_research_fit_tab,
)
from filter_utils import (
    apply_video_filters,
    get_video_stats_summary,
    get_unique_channels,
)
from favorites import init_favorites
from professors_database import (
    search_professors_by_keyword,
    get_research_areas,
    get_universities,
    APA_PROFESSORS_DATABASE,
)

load_dotenv()

st.set_page_config(**PAGE_CONFIG)


def main() -> None:
    """메인 앱 진입점"""
    # 즐겨찾기 초기화
    init_favorites()

    st.title(UIText.APP_TITLE)
    st.markdown(UIText.APP_SUBTITLE)

    # 전역 API 키 설정 (사이드바)
    youtube_api_key, openai_api_key, gemini_api_key = setup_sidebar()

    # 6개 탭 생성 (Phase 4: 연구 매칭 추가)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        UIText.TAB_RESEARCH_FIT,  # 새로운 핵심 기능을 첫 번째로
        UIText.TAB_VIDEOS,
        UIText.TAB_PROFESSORS,
        UIText.TAB_UNIVERSITIES,
        UIText.TAB_FAVORITES,
        UIText.TAB_COMPARE
    ])

    with tab1:
        display_research_fit_tab(openai_api_key, gemini_api_key)

    with tab2:
        st.markdown("### 🎬 임상심리학 동영상 검색")
        video_search_interface(youtube_api_key)

    with tab3:
        st.markdown("### 👨‍🏫 APA 인증 교수진 검색")
        professor_search_interface(youtube_api_key, openai_api_key)

    with tab4:
        st.markdown("### 🏛️ 대학별 교수진 탐색")
        university_interface(youtube_api_key, openai_api_key)

    with tab5:
        display_favorites_tab()

    with tab6:
        display_compare_tab()


def setup_sidebar() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """사이드바 API 키 설정"""
    from favorites import get_professor_favorites, get_video_favorites, get_compare_list

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

        # Gemini API 키 (학습 로드맵용)
        gemini_api_key = st.text_input(
            "Gemini API 키:",
            type="password",
            placeholder="AIzaSy...",
            help="Google AI Studio에서 Gemini API 키를 발급받으세요 (학습 로드맵용)"
        )

        # .env 파일에서 API 키 가져오기 (백업)
        if not youtube_api_key:
            youtube_api_key = os.getenv(EnvKeys.YOUTUBE_API_KEY)
        if not openai_api_key:
            openai_api_key = os.getenv(EnvKeys.OPENAI_API_KEY)
        if not gemini_api_key:
            gemini_api_key = os.getenv(EnvKeys.GEMINI_API_KEY)

        # API 키 상태 표시
        st.markdown("---")
        st.markdown("**📊 API 상태:**")
        yt_status = UIText.STATUS_YOUTUBE_CONNECTED if youtube_api_key else UIText.STATUS_YOUTUBE_DISCONNECTED
        gpt_status = UIText.STATUS_YOUTUBE_CONNECTED if openai_api_key else UIText.STATUS_YOUTUBE_DISCONNECTED
        gemini_status = UIText.STATUS_YOUTUBE_CONNECTED if gemini_api_key else UIText.STATUS_YOUTUBE_DISCONNECTED
        st.write("🎬 YouTube:", yt_status)
        st.write("🤖 ChatGPT:", gpt_status)
        st.write("✨ Gemini:", gemini_status)

        # Phase 3: 즐겨찾기/비교 상태 표시
        st.markdown("---")
        st.markdown("**⭐ 즐겨찾기:**")
        prof_favs = len(get_professor_favorites())
        video_favs = len(get_video_favorites())
        compare_count = len(get_compare_list())
        st.write(f"교수: {prof_favs}명 | 동영상: {video_favs}개")
        st.write(f"비교 목록: {compare_count}명")

    return youtube_api_key, openai_api_key, gemini_api_key


def video_search_interface(api_key: Optional[str]) -> None:
    """동영상 검색 인터페이스 (Phase 3: 필터 추가)"""
    st.markdown("---")

    # 난이도 레벨 선택
    level = st.radio(
        "🎓 학습 레벨:",
        ["📚 기초-중급", "🎓 APA 박사과정"],
        help="기초-중급: 일반적인 임상심리학 내용\nAPA 박사과정: 고급 전문 지식 및 영어 콘텐츠",
        horizontal=True
    )

    # 레벨에 따른 카테고리 선택
    if level == "📚 기초-중급":
        categories = PSYCHOLOGY_CATEGORIES
        st.info("📖 기초부터 중급까지의 임상심리학 내용")
    else:
        categories = APA_DOCTORAL_CATEGORIES
        st.warning("🎓 APA 박사과정 수준의 전문 내용 (주로 영어)")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_category = st.selectbox(
            "전문 분야:",
            options=list(categories.keys()),
            index=0
        )

    with col2:
        # 언어 설정 (APA 레벨일 때만)
        language = "한국어"
        if level == "🎓 APA 박사과정":
            language = st.selectbox(
                "언어 우선순위:",
                ["영어 (English)", "한국어", "혼합"],
                help="APA 박사과정 내용은 영어 자료가 더 풍부합니다"
            )

    # 커스텀 검색어
    custom_search = st.text_input(
        "추가 검색어:",
        placeholder="예: 인지행동치료, CBT protocol",
        help="특정 주제를 더 자세히 검색하고 싶다면 입력하세요"
    )

    # 검색 버튼
    search_button = st.button("🔍 동영상 검색", use_container_width=True, disabled=not api_key)

    # 검색 쿼리 구성
    search_query = categories[selected_category]
    if custom_search:
        search_query += f" {custom_search}"

    # 언어별 검색어 조정
    if level == "🎓 APA 박사과정" and language == "한국어":
        search_query += " 한국어 번역 korean"

    if (search_button or SessionKeys.VIDEOS not in st.session_state) and api_key:
        with st.spinner(f'\'{selected_category}\' 관련 동영상을 검색 중...'):
            st.session_state[SessionKeys.VIDEOS] = search_psychology_videos(api_key, search_query)
            st.session_state[SessionKeys.LAST_SEARCH] = {
                'category': selected_category,
                'level': level,
                'query': search_query,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    videos = st.session_state.get(SessionKeys.VIDEOS, [])

    if not api_key:
        st.info(UIText.ERROR_NO_API_KEY)
        return

    if not videos and api_key:
        st.warning(UIText.ERROR_NO_RESULTS)
        return

    st.markdown("---")

    # Phase 3-A: 필터/정렬 컨트롤
    st.markdown("#### 🔧 필터 및 정렬")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        sort_option = st.selectbox(
            "🔄 정렬",
            options=SortOptions.all(),
            index=0,
            key="main_video_sort"
        )

    with filter_col2:
        date_filter = st.selectbox(
            "📅 기간",
            options=DateFilterOptions.all(),
            index=0,
            key="main_video_date_filter"
        )

    with filter_col3:
        # 채널 선택
        channels = ["전체"] + get_unique_channels(videos)
        selected_channel = st.selectbox(
            "📺 채널",
            options=channels,
            index=0,
            key="main_video_channel"
        )
        channel_filter = "" if selected_channel == "전체" else selected_channel

    # 필터 적용
    filtered_videos = apply_video_filters(
        videos,
        sort_option=sort_option,
        date_filter=date_filter,
        channel_filter=channel_filter
    )

    # 통계 표시
    stats = get_video_stats_summary(filtered_videos)
    display_video_stats(stats)

    st.markdown("---")

    # 검색 결과 표시 (즐겨찾기 버튼 포함)
    if filtered_videos:
        st.markdown(f"**검색 결과: {len(filtered_videos)}개**")
        display_video_results_with_favorites(filtered_videos, show_favorite_btn=True)
    else:
        st.warning("필터 조건에 맞는 동영상이 없습니다.")


def professor_search_interface(youtube_api_key: Optional[str], openai_api_key: Optional[str]) -> None:
    """교수진 검색 인터페이스 (Phase 3: 즐겨찾기/비교 버튼 추가)"""
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
            st.session_state[SessionKeys.SEARCHED_PROFESSORS] = professors
            st.session_state[SessionKeys.SEARCH_KEYWORD] = research_keyword

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
    searched_profs = st.session_state.get(SessionKeys.SEARCHED_PROFESSORS, [])
    search_kw = st.session_state.get(SessionKeys.SEARCH_KEYWORD, "")
    if searched_profs:
        st.markdown(f"### 🎯 '{search_kw}' 검색 결과 ({len(searched_profs)}명)")
        st.caption("⭐ = 즐겨찾기 | ➕/➖ = 비교 목록에 추가/제거")

        for i, prof_data in enumerate(searched_profs):
            with st.expander(f"👨‍🏫 {prof_data['professor']['name']} - {prof_data['university']}"):
                # Phase 3: 액션 버튼 포함 교수 정보
                prof = display_professor_with_actions(
                    prof_data,
                    unique_key=f"search_{i}",
                    show_favorite=True,
                    show_compare=True
                )

                st.markdown("---")

                # ChatGPT 상담 섹션
                display_chatgpt_section(prof_data, openai_api_key, f"search_{i}")

                st.markdown("---")

                # 관련 동영상 검색 버튼
                if youtube_api_key:
                    video_key = SessionKeys.professor_videos(i)
                    if st.button(f"🎬 {prof['name']} 관련 동영상 검색", key=f"video_search_{i}"):
                        with st.spinner(f"{prof['name']} 관련 동영상 검색 중..."):
                            videos = search_professor_videos(youtube_api_key, prof['name'], prof['research_keywords'])
                            st.session_state[video_key] = videos

                    # 동영상 결과 표시
                    if video_key in st.session_state:
                        videos = st.session_state[video_key]
                        if videos:
                            st.markdown(f"#### 🎬 {prof['name']} 관련 동영상 ({len(videos)}개)")
                            display_video_results_with_favorites(videos, compact=True, show_favorite_btn=True)
                        else:
                            st.info("관련 동영상을 찾을 수 없습니다.")


def university_interface(youtube_api_key: Optional[str], openai_api_key: Optional[str]) -> None:
    """대학별 교수진 인터페이스 (Phase 3: 즐겨찾기/비교 버튼 추가)"""
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
        st.caption("⭐ = 즐겨찾기 | ➕/➖ = 비교 목록에 추가/제거")

        # 교수진 목록
        for i, prof in enumerate(professors):
            with st.expander(f"👨‍🏫 {prof['name']} - {', '.join(prof['research_areas'][:3])}"):
                prof_data = {
                    "professor": prof,
                    "university": selected_university,
                    "location": university_info["location"],
                    "program_type": university_info["program_type"]
                }

                # Phase 3: 액션 버튼 포함 교수 정보
                display_professor_with_actions(
                    prof_data,
                    unique_key=f"univ_{i}",
                    show_favorite=True,
                    show_compare=True
                )

                st.markdown("---")

                # ChatGPT 상담 섹션
                display_chatgpt_section(prof_data, openai_api_key, f"univ_{i}")

                st.markdown("---")

                # 관련 동영상 검색
                if youtube_api_key:
                    video_key = SessionKeys.university_professor_videos(i)
                    if st.button(f"🎬 {prof['name']} 관련 동영상 검색", key=f"univ_video_{i}"):
                        with st.spinner(f"{prof['name']} 관련 동영상 검색 중..."):
                            videos = search_professor_videos(youtube_api_key, prof['name'], prof['research_keywords'])
                            st.session_state[video_key] = videos

                    # 동영상 결과 표시
                    if video_key in st.session_state:
                        videos = st.session_state[video_key]
                        if videos:
                            st.markdown(f"#### 🎬 {prof['name']} 관련 동영상 ({len(videos)}개)")
                            display_video_results_with_favorites(videos, compact=True, show_favorite_btn=True)
                        else:
                            st.info("관련 동영상을 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
