"""
UI 컴포넌트 모듈
Streamlit UI 관련 재사용 가능한 컴포넌트
"""
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

from config import (
    SessionKeys,
    QUESTION_TEMPLATES,
    UIText,
    SortOptions,
    DateFilterOptions,
    CompareConfig,
)
from api_handlers import chat_with_gpt


def format_view_count(view_count: Any) -> str:
    """조회수를 읽기 쉬운 형태로 포맷팅"""
    try:
        count = int(view_count)
        if count >= 100000000:  # 1억 이상
            return f"{count//100000000}억{(count%100000000)//10000:,}만"
        elif count >= 10000:  # 1만 이상
            return f"{count//10000:,}만"
        else:
            return f"{count:,}"
    except (ValueError, TypeError):
        return str(view_count)


def display_professor_info(professor_data: Dict[str, Any], openai_api_key: Optional[str] = None) -> Dict[str, Any]:
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


def display_chatgpt_section(professor_data: Dict[str, Any], openai_api_key: Optional[str], unique_key: str) -> None:
    """교수님별 ChatGPT 섹션 표시"""
    if not openai_api_key:
        st.info(UIText.ERROR_CHATGPT_NO_KEY)
        return

    prof = professor_data["professor"]
    st.markdown(f"### 🤖 {prof['name']} 교수님 연구실 지원 상담")

    # 질문 견본 섹션
    with st.expander("💡 추천 질문 견본", expanded=False):
        for category, questions in QUESTION_TEMPLATES.items():
            st.markdown(f"**{category}**")
            for i, question in enumerate(questions):
                if st.button(f"❓ {question}", key=f"{unique_key}_template_{category}_{i}"):
                    st.session_state[SessionKeys.chat_input(unique_key)] = question
            st.markdown("")

    # 대화 히스토리 초기화
    chat_history_key = SessionKeys.chat_history(unique_key)
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
    user_input_key = SessionKeys.chat_input(unique_key)
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


def display_video_results(videos: List[Dict[str, Any]], compact: bool = False) -> None:
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
        except (ValueError, AttributeError):
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


# =============================================================================
# Phase 3-A: 필터/정렬 UI
# =============================================================================
def display_video_filter_controls() -> tuple[str, str, str]:
    """동영상 필터 컨트롤 표시

    Returns:
        (sort_option, date_filter, channel_filter) 튜플
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        sort_option = st.selectbox(
            "🔄 정렬",
            options=SortOptions.all(),
            index=0,
            key="video_sort_select"
        )

    with col2:
        date_filter = st.selectbox(
            "📅 기간",
            options=DateFilterOptions.all(),
            index=0,
            key="video_date_filter_select"
        )

    with col3:
        channel_filter = st.text_input(
            "📺 채널 필터",
            placeholder="채널명 입력...",
            key="video_channel_filter"
        )

    return sort_option, date_filter, channel_filter


def display_video_stats(stats: Dict[str, Any]) -> None:
    """동영상 통계 요약 표시"""
    if stats["total"] == 0:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("검색 결과", f"{stats['total']}개")
    with col2:
        st.metric("총 조회수", format_view_count(stats["total_views"]))
    with col3:
        st.metric("채널 수", f"{stats['channels']}개")
    with col4:
        if stats["newest"]:
            st.metric("최신 영상", stats["newest"])


def display_video_results_with_favorites(
    videos: List[Dict[str, Any]],
    compact: bool = False,
    show_favorite_btn: bool = True
) -> None:
    """즐겨찾기 버튼이 포함된 동영상 결과 표시"""
    from favorites import is_video_favorite, add_video_favorite, remove_video_favorite

    if not videos:
        return

    max_videos = 5 if compact else len(videos)

    for idx, video in enumerate(videos[:max_videos]):
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
        except (ValueError, AttributeError):
            formatted_date = '날짜 없음'

        # 즐겨찾기 포함 레이아웃
        if show_favorite_btn:
            col1, col2, col3, col4, col5, col6 = st.columns([0.8, 3.2, 1.2, 1, 0.8, 0.5])
        else:
            col1, col2, col3, col4, col5 = st.columns([0.8, 3.5, 1.2, 1, 1])
            col6 = None

        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, width=100)

        with col2:
            st.markdown(f"**{title[:70]}{'...' if len(title) > 70 else ''}**")
            if description and not compact:
                st.caption(f"{description[:50]}{'...' if len(description) > 50 else ''}")

        with col3:
            st.write(f"**{channel_name[:15]}{'...' if len(channel_name) > 15 else ''}**")
            st.caption(f"{formatted_date}")

        with col4:
            st.write(f"**{format_view_count(view_count)}회**")

        with col5:
            st.markdown(f"[▶️ 보기]({video_url})")

        if col6 and show_favorite_btn:
            with col6:
                is_fav = is_video_favorite(video_id)
                btn_label = "💛" if is_fav else "🤍"
                if st.button(btn_label, key=f"fav_video_{video_id}_{idx}"):
                    if is_fav:
                        remove_video_favorite(video_id)
                    else:
                        add_video_favorite(video)
                    st.rerun()


# =============================================================================
# Phase 3-B: 즐겨찾기 UI
# =============================================================================
def display_professor_with_actions(
    professor_data: Dict[str, Any],
    unique_key: str,
    show_favorite: bool = True,
    show_compare: bool = True
) -> Dict[str, Any]:
    """액션 버튼이 포함된 교수 정보 표시"""
    from favorites import (
        is_professor_favorite,
        add_professor_favorite,
        remove_professor_favorite,
        is_in_compare,
        add_to_compare,
        remove_from_compare,
        get_compare_list,
    )

    prof = professor_data["professor"]

    # 헤더와 액션 버튼
    header_col, action_col = st.columns([4, 1])

    with header_col:
        st.markdown(f"### 👨‍🏫 {prof['name']}")

    with action_col:
        btn_col1, btn_col2 = st.columns(2)

        if show_favorite:
            with btn_col1:
                is_fav = is_professor_favorite(professor_data)
                fav_label = "⭐" if is_fav else "☆"
                if st.button(fav_label, key=f"fav_prof_{unique_key}", help="즐겨찾기"):
                    if is_fav:
                        from favorites import get_professor_favorite_key
                        remove_professor_favorite(get_professor_favorite_key(professor_data))
                    else:
                        add_professor_favorite(professor_data)
                    st.rerun()

        if show_compare:
            with btn_col2:
                in_compare = is_in_compare(professor_data)
                compare_list = get_compare_list()
                can_add = len(compare_list) < CompareConfig.MAX_PROFESSORS

                if in_compare:
                    if st.button("➖", key=f"cmp_prof_{unique_key}", help="비교에서 제거"):
                        remove_from_compare(professor_data)
                        st.rerun()
                elif can_add:
                    if st.button("➕", key=f"cmp_prof_{unique_key}", help="비교에 추가"):
                        add_to_compare(professor_data)
                        st.rerun()

    # 교수 정보
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


def display_favorites_tab() -> None:
    """즐겨찾기 탭 콘텐츠 표시"""
    from favorites import (
        get_professor_favorites,
        get_video_favorites,
        remove_professor_favorite,
        remove_video_favorite,
        export_favorites,
        import_favorites,
    )

    st.markdown("### ⭐ 즐겨찾기 관리")

    # 내보내기/가져오기
    with st.expander("📥 즐겨찾기 내보내기/가져오기"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**내보내기**")
            if st.button("JSON으로 내보내기"):
                json_data = export_favorites()
                st.download_button(
                    label="📥 다운로드",
                    data=json_data,
                    file_name="favorites.json",
                    mime="application/json"
                )

        with col2:
            st.markdown("**가져오기**")
            uploaded_file = st.file_uploader("JSON 파일 선택", type="json", key="import_favorites")
            if uploaded_file is not None:
                json_str = uploaded_file.read().decode('utf-8')
                if import_favorites(json_str):
                    st.success("즐겨찾기를 가져왔습니다!")
                    st.rerun()
                else:
                    st.error("파일 형식이 올바르지 않습니다.")

    st.markdown("---")

    # 교수 즐겨찾기
    st.markdown("#### 👨‍🏫 교수 즐겨찾기")
    prof_favorites = get_professor_favorites()

    if not prof_favorites:
        st.info("아직 즐겨찾기한 교수가 없습니다.")
    else:
        for key, prof_data in list(prof_favorites.items()):
            prof = prof_data.get("professor", {})
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 0.5])
                with col1:
                    st.markdown(f"**{prof.get('name', '이름 없음')}** - {prof_data.get('university', '')}")
                    st.caption(f"연구 분야: {', '.join(prof.get('research_areas', [])[:3])}")
                with col2:
                    added_at = prof_data.get('added_at', '')
                    if added_at:
                        st.caption(f"추가: {added_at[:10]}")
                with col3:
                    if st.button("🗑️", key=f"del_prof_{key}"):
                        remove_professor_favorite(key)
                        st.rerun()
                st.markdown("---")

    # 동영상 즐겨찾기
    st.markdown("#### 🎬 동영상 즐겨찾기")
    video_favorites = get_video_favorites()

    if not video_favorites:
        st.info("아직 즐겨찾기한 동영상이 없습니다.")
    else:
        for video_id, video_data in list(video_favorites.items()):
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 3, 1, 0.5])
                with col1:
                    if video_data.get('thumbnail'):
                        st.image(video_data['thumbnail'], width=80)
                with col2:
                    st.markdown(f"**{video_data.get('title', '제목 없음')[:60]}**")
                    st.caption(f"채널: {video_data.get('channel', '')}")
                with col3:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    st.markdown(f"[▶️ 보기]({video_url})")
                with col4:
                    if st.button("🗑️", key=f"del_video_{video_id}"):
                        remove_video_favorite(video_id)
                        st.rerun()
                st.markdown("---")


# =============================================================================
# Phase 3-C: 비교 UI
# =============================================================================
def display_compare_tab() -> None:
    """교수 비교 탭 콘텐츠 표시"""
    from favorites import get_compare_list, clear_compare_list, remove_from_compare

    st.markdown("### ⚖️ 교수 비교")

    compare_list = get_compare_list()

    if len(compare_list) < CompareConfig.MIN_PROFESSORS:
        st.warning(UIText.COMPARE_MIN_WARNING)
        st.info(f"현재 {len(compare_list)}명 선택됨. 교수진 검색에서 ➕ 버튼으로 추가하세요.")
        return

    # 선택된 교수 목록
    st.markdown(f"**선택된 교수: {len(compare_list)}명**")

    # 비교 목록 초기화 버튼
    if st.button("🗑️ 비교 목록 초기화"):
        clear_compare_list()
        st.rerun()

    st.markdown("---")

    # 비교 테이블 헤더
    cols = st.columns(len(compare_list))

    for i, prof_data in enumerate(compare_list):
        prof = prof_data.get("professor", {})
        with cols[i]:
            st.markdown(f"### {prof.get('name', '이름 없음')}")
            if st.button("제거", key=f"remove_compare_{i}"):
                remove_from_compare(prof_data)
                st.rerun()

    st.markdown("---")

    # 비교 항목들
    comparison_items = [
        ("🏛️ 소속", lambda pd: pd.get('university', 'N/A')),
        ("📍 위치", lambda pd: pd.get('location', 'N/A')),
        ("🎓 프로그램", lambda pd: pd.get('program_type', 'N/A')),
        ("🔬 연구실", lambda pd: pd.get('professor', {}).get('lab', 'N/A')),
        ("📧 이메일", lambda pd: pd.get('professor', {}).get('email', 'N/A')),
    ]

    for label, getter in comparison_items:
        cols = st.columns(len(compare_list))
        for i, prof_data in enumerate(compare_list):
            with cols[i]:
                st.markdown(f"**{label}**")
                st.write(getter(prof_data))
        st.markdown("---")

    # 연구 분야 비교 (특별 처리)
    st.markdown("**🔍 연구 분야**")
    cols = st.columns(len(compare_list))
    for i, prof_data in enumerate(compare_list):
        prof = prof_data.get("professor", {})
        with cols[i]:
            areas = prof.get('research_areas', [])
            for area in areas:
                st.markdown(f"- {area}")

    st.markdown("---")

    # 연구 키워드 비교
    st.markdown("**🏷️ 연구 키워드**")
    cols = st.columns(len(compare_list))
    for i, prof_data in enumerate(compare_list):
        prof = prof_data.get("professor", {})
        with cols[i]:
            keywords = prof.get('research_keywords', '')
            st.write(keywords if keywords else 'N/A')

    # 공통 연구 분야 찾기
    st.markdown("---")
    st.markdown("### 📊 공통 연구 분야")

    all_areas = []
    for prof_data in compare_list:
        prof = prof_data.get("professor", {})
        all_areas.append(set(prof.get('research_areas', [])))

    if all_areas:
        common_areas = all_areas[0]
        for areas in all_areas[1:]:
            common_areas = common_areas.intersection(areas)

        if common_areas:
            st.success(f"공통 연구 분야: {', '.join(common_areas)}")
        else:
            st.info("공통 연구 분야가 없습니다.")


# =============================================================================
# Phase 4: Research Fit Analyzer UI
# =============================================================================
def display_match_result(match: Dict[str, Any], index: int, openai_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None) -> None:
    """단일 매칭 결과 표시"""
    score = match.get("score", 0)
    prof_name = match.get("professor", "Unknown")
    university = match.get("university", "Unknown")

    # 점수에 따른 색상
    if score >= 30:
        score_color = "🟢"
    elif score >= 15:
        score_color = "🟡"
    else:
        score_color = "🟠"

    with st.expander(f"{score_color} **{prof_name}** - {university} ({score}% 매칭)", expanded=(index < 3)):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**🏛️ 소속:** {university}")
            st.markdown(f"**📍 위치:** {match.get('location', 'N/A')}")
            st.markdown(f"**🎓 프로그램:** {match.get('program_type', 'N/A')}")

            if match.get('lab'):
                st.markdown(f"**🔬 연구실:** {match['lab']}")

            if match.get('email'):
                st.markdown(f"**📧 이메일:** {match['email']}")

        with col2:
            # 매칭 점수 시각화
            st.metric("매칭 점수", f"{score}%")

        st.markdown("---")

        # 매칭된 연구 분야
        matched_areas = match.get("matched_areas", [])
        if matched_areas:
            st.markdown("**✅ 공통 연구 분야:**")
            for area in matched_areas:
                st.markdown(f"- {area}")

        # 매칭된 키워드
        matched_keywords = match.get("matched_keywords", [])
        if matched_keywords:
            st.markdown(f"**🏷️ 매칭 키워드:** {', '.join(matched_keywords)}")

        # 교수의 전체 연구 분야
        st.markdown("**🔍 교수님의 연구 분야:**")
        for area in match.get("research_areas", []):
            st.markdown(f"- {area}")

        # 차이점 분석
        col_diff1, col_diff2 = st.columns(2)

        with col_diff1:
            unique_user = match.get("user_unique_interests", [])
            if unique_user:
                st.markdown("**💡 당신만의 관심사:**")
                st.caption(", ".join(unique_user))

        with col_diff2:
            unique_prof = match.get("professor_unique_areas", [])
            if unique_prof:
                st.markdown("**📚 교수님만의 분야:**")
                st.caption(", ".join(unique_prof))

        # 액션 버튼들
        st.markdown("---")
        action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(5)

        with action_col1:
            # 즐겨찾기 버튼
            from favorites import is_professor_favorite, add_professor_favorite, get_professor_favorite_key, remove_professor_favorite

            full_data = match.get("full_data", {})
            if full_data:
                is_fav = is_professor_favorite(full_data)
                fav_label = "⭐" if is_fav else "☆"
                if st.button(fav_label, key=f"fav_match_{index}", help="즐겨찾기"):
                    if is_fav:
                        remove_professor_favorite(get_professor_favorite_key(full_data))
                    else:
                        add_professor_favorite(full_data)
                    st.rerun()

        with action_col2:
            # 비교 목록 추가
            from favorites import is_in_compare, add_to_compare, remove_from_compare, get_compare_list

            if full_data:
                in_compare = is_in_compare(full_data)
                compare_list = get_compare_list()
                can_add = len(compare_list) < CompareConfig.MAX_PROFESSORS

                if in_compare:
                    if st.button("➖", key=f"cmp_match_{index}", help="비교에서 제거"):
                        remove_from_compare(full_data)
                        st.rerun()
                elif can_add:
                    if st.button("➕", key=f"cmp_match_{index}", help="비교에 추가"):
                        add_to_compare(full_data)
                        st.rerun()

        with action_col3:
            # 스마트 질문 생성 버튼
            if openai_api_key and full_data:
                if st.button("❓ 질문", key=f"questions_{index}", help="질문 생성"):
                    st.session_state[f"generate_questions_{index}"] = True

        with action_col4:
            # 유사 연구자 추천 버튼
            if full_data:
                if st.button("👥 유사", key=f"similar_{index}", help="유사 교수"):
                    st.session_state[f"show_similar_{index}"] = True

        with action_col5:
            # 학습 로드맵 버튼
            if gemini_api_key and full_data:
                if st.button("📚 로드맵", key=f"roadmap_{index}", help="학습 로드맵"):
                    st.session_state[f"show_roadmap_{index}"] = True

        # 스마트 질문 생성 영역
        if st.session_state.get(f"generate_questions_{index}", False) and openai_api_key:
            display_smart_questions_section(full_data, openai_api_key, f"match_{index}")

        # 유사 연구자 추천 영역
        if st.session_state.get(f"show_similar_{index}", False) and full_data:
            display_similar_professors_section(full_data, index)

        # 학습 로드맵 영역
        if st.session_state.get(f"show_roadmap_{index}", False) and gemini_api_key and full_data:
            user_interests = st.session_state.get(SessionKeys.RESEARCH_INTERESTS, "")
            display_learning_roadmap_section(full_data, gemini_api_key, user_interests, f"match_{index}")


def display_similar_professors_section(professor_data: Dict[str, Any], index: int) -> None:
    """유사 연구자 추천 섹션"""
    from research_fit import find_similar_professors
    from professors_database import APA_PROFESSORS_DATABASE
    from favorites import is_professor_favorite, add_professor_favorite, get_professor_favorite_key, remove_professor_favorite
    from favorites import is_in_compare, add_to_compare, remove_from_compare, get_compare_list

    prof_name = professor_data.get("professor", {}).get("name", "Unknown")

    st.markdown(f"#### 👥 {prof_name}와 유사한 연구를 하는 교수")

    # 캐시된 결과가 없으면 계산
    cache_key = f"similar_results_{index}"
    if cache_key not in st.session_state:
        with st.spinner("유사 교수를 찾는 중..."):
            similar = find_similar_professors(
                professor_data,
                APA_PROFESSORS_DATABASE,
                top_n=5
            )
            st.session_state[cache_key] = similar

    similar_profs = st.session_state.get(cache_key, [])

    if not similar_profs:
        st.info("유사한 연구를 하는 교수를 찾지 못했습니다.")
        return

    for i, sim in enumerate(similar_profs):
        sim_score = sim.get("score", 0)
        sim_name = sim.get("professor", "Unknown")
        sim_univ = sim.get("university", "Unknown")

        # 점수 색상
        if sim_score >= 30:
            score_badge = "🟢"
        elif sim_score >= 15:
            score_badge = "🟡"
        else:
            score_badge = "🟠"

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 0.5, 0.5])

            with col1:
                st.markdown(f"**{score_badge} {sim_name}** - {sim_univ}")
                matched_areas = sim.get("matched_areas", [])
                if matched_areas:
                    st.caption(f"공통 분야: {', '.join(matched_areas[:3])}")

            with col2:
                st.metric("유사도", f"{sim_score}%", label_visibility="collapsed")

            with col3:
                # 즐겨찾기 버튼
                sim_full_data = sim.get("full_data", {})
                if sim_full_data:
                    is_fav = is_professor_favorite(sim_full_data)
                    fav_icon = "⭐" if is_fav else "☆"
                    if st.button(fav_icon, key=f"sim_fav_{index}_{i}", help="즐겨찾기"):
                        if is_fav:
                            remove_professor_favorite(get_professor_favorite_key(sim_full_data))
                        else:
                            add_professor_favorite(sim_full_data)
                        st.rerun()

            with col4:
                # 비교 추가 버튼
                if sim_full_data:
                    in_compare = is_in_compare(sim_full_data)
                    compare_list = get_compare_list()
                    can_add = len(compare_list) < CompareConfig.MAX_PROFESSORS

                    if in_compare:
                        if st.button("➖", key=f"sim_cmp_{index}_{i}", help="비교에서 제거"):
                            remove_from_compare(sim_full_data)
                            st.rerun()
                    elif can_add:
                        if st.button("➕", key=f"sim_cmp_{index}_{i}", help="비교에 추가"):
                            add_to_compare(sim_full_data)
                            st.rerun()

            st.markdown("---")


def display_smart_questions_section(
    professor_data: Dict[str, Any],
    openai_api_key: str,
    unique_key: str
) -> None:
    """스마트 질문 생성 섹션"""
    from api_handlers import generate_smart_questions

    st.markdown("#### ❓ 스마트 질문 생성")

    user_interests = st.session_state.get(SessionKeys.RESEARCH_INTERESTS, "")

    if st.button("🔄 질문 생성하기", key=f"gen_q_{unique_key}"):
        with st.spinner("질문을 생성하는 중..."):
            questions = generate_smart_questions(
                openai_api_key,
                professor_data,
                user_interests
            )
            st.session_state[f"questions_{unique_key}"] = questions

    if f"questions_{unique_key}" in st.session_state:
        st.markdown(st.session_state[f"questions_{unique_key}"])


def display_sop_assistant_section(
    professor_data: Dict[str, Any],
    openai_api_key: str,
    unique_key: str
) -> None:
    """SOP 작성 도우미 섹션"""
    from api_handlers import analyze_sop, generate_sop_draft

    st.markdown("#### 📝 SOP 작성 도우미")

    sop_mode = st.radio(
        "모드 선택:",
        ["📊 SOP 분석 (피드백)", "✍️ SOP 초안 생성"],
        key=f"sop_mode_{unique_key}",
        horizontal=True
    )

    if sop_mode == "📊 SOP 분석 (피드백)":
        sop_content = st.text_area(
            "분석할 SOP를 붙여넣으세요:",
            height=300,
            key=f"sop_content_{unique_key}",
            placeholder="여기에 SOP 내용을 붙여넣으세요..."
        )

        if st.button("🔍 SOP 분석하기", key=f"analyze_sop_{unique_key}"):
            if sop_content:
                with st.spinner("SOP를 분석하는 중..."):
                    analysis = analyze_sop(openai_api_key, professor_data, sop_content)
                    st.session_state[f"sop_analysis_{unique_key}"] = analysis
            else:
                st.warning("SOP 내용을 입력해주세요.")

        if f"sop_analysis_{unique_key}" in st.session_state:
            st.markdown("---")
            st.markdown("### 📋 분석 결과")
            st.markdown(st.session_state[f"sop_analysis_{unique_key}"])

    else:  # SOP 초안 생성
        st.markdown("**당신의 배경 정보를 입력하세요:**")

        student_info = st.text_area(
            "배경 정보:",
            height=200,
            key=f"student_info_{unique_key}",
            placeholder="""예시:
- 학부 전공: 심리학 (OO대학교)
- 관심 연구 분야: 청소년 우울증, 디지털 치료
- 관련 경험: OO 연구실 인턴 (6개월), OO 논문 공저
- 임상 경험: OO 상담센터 봉사 (1년)
- 강점: 통계 분석 (R, SPSS), 영어 논문 작성
- 연구 목표: 청소년 대상 모바일 기반 CBT 개발"""
        )

        if st.button("✍️ SOP 초안 생성", key=f"generate_sop_{unique_key}"):
            if student_info:
                with st.spinner("SOP 초안을 생성하는 중..."):
                    draft = generate_sop_draft(openai_api_key, professor_data, student_info)
                    st.session_state[f"sop_draft_{unique_key}"] = draft
            else:
                st.warning("배경 정보를 입력해주세요.")

        if f"sop_draft_{unique_key}" in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 생성된 SOP 초안")
            st.markdown(st.session_state[f"sop_draft_{unique_key}"])

            # 다운로드 버튼
            st.download_button(
                label="📥 초안 다운로드 (TXT)",
                data=st.session_state[f"sop_draft_{unique_key}"],
                file_name="sop_draft.txt",
                mime="text/plain"
            )


def display_learning_roadmap_section(
    professor_data: Dict[str, Any],
    gemini_api_key: str,
    research_interests: str,
    unique_key: str
) -> None:
    """학습 로드맵 생성 섹션 (Gemini 사용)"""
    from api_handlers import generate_learning_roadmap

    st.markdown("#### 📚 학습 로드맵 생성")
    st.caption("Gemini AI를 활용하여 맞춤형 학습 계획을 생성합니다.")

    col1, col2 = st.columns(2)

    with col1:
        student_level = st.selectbox(
            "현재 수준:",
            ["학부 3학년", "학부 4학년 (졸업예정)", "학부 졸업", "석사 재학", "석사 졸업", "직장인/기타"],
            key=f"student_level_{unique_key}"
        )

    with col2:
        target_timeline = st.selectbox(
            "목표 지원 시기:",
            ["2025년 가을 (Fall 2025)", "2026년 봄 (Spring 2026)", "2026년 가을 (Fall 2026)", "2027년 이후"],
            key=f"target_timeline_{unique_key}"
        )

    if st.button("📚 학습 로드맵 생성", key=f"gen_roadmap_{unique_key}"):
        with st.spinner("Gemini가 맞춤형 학습 로드맵을 생성하는 중..."):
            roadmap = generate_learning_roadmap(
                gemini_api_key,
                professor_data,
                student_level,
                research_interests,
                target_timeline
            )
            st.session_state[f"roadmap_{unique_key}"] = roadmap

    if f"roadmap_{unique_key}" in st.session_state:
        st.markdown("---")
        st.markdown("### 📋 맞춤형 학습 로드맵")
        st.markdown(st.session_state[f"roadmap_{unique_key}"])

        # 다운로드 버튼
        st.download_button(
            label="📥 로드맵 다운로드 (TXT)",
            data=st.session_state[f"roadmap_{unique_key}"],
            file_name="learning_roadmap.txt",
            mime="text/plain",
            key=f"download_roadmap_{unique_key}"
        )


def display_research_fit_tab(openai_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None) -> None:
    """연구 적합도 분석 탭"""
    from research_fit import find_matching_professors, find_similar_professors
    from professors_database import APA_PROFESSORS_DATABASE

    st.markdown("### 🎯 연구 적합도 분석기")
    st.markdown("당신의 연구 관심사와 가장 잘 맞는 교수님을 찾아드립니다.")

    st.markdown("---")

    # 연구 관심사 입력
    st.markdown("#### 📝 연구 관심사 입력")

    interests = st.text_area(
        "연구 관심사를 자유롭게 입력하세요:",
        height=120,
        key="research_interests_input",
        placeholder="""예시:
- 한국어: 청소년 우울증, 인지행동치료, 디지털 치료, 모바일 앱 기반 개입
- 영어: adolescent depression, CBT, digital therapeutics, anxiety, fMRI
- 혼합: 트라우마 PTSD treatment, 마음챙김 mindfulness, ERP exposure therapy"""
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        top_n = st.slider("결과 수", min_value=5, max_value=20, value=10)

    with col2:
        min_score = st.slider("최소 매칭 점수 (%)", min_value=1, max_value=30, value=5)

    if st.button("🔍 매칭 교수 찾기", use_container_width=True, type="primary"):
        if interests:
            st.session_state[SessionKeys.RESEARCH_INTERESTS] = interests
            with st.spinner("교수님들과의 연구 적합도를 분석하는 중..."):
                matches = find_matching_professors(
                    interests,
                    APA_PROFESSORS_DATABASE,
                    top_n=top_n,
                    min_score=min_score
                )
                st.session_state[SessionKeys.MATCH_RESULTS] = matches
        else:
            st.warning("연구 관심사를 입력해주세요.")

    # 결과 표시
    matches = st.session_state.get(SessionKeys.MATCH_RESULTS, [])

    if matches:
        st.markdown("---")
        st.markdown(f"### 📊 매칭 결과: {len(matches)}명")

        # 통계 요약
        avg_score = sum(m["score"] for m in matches) / len(matches)
        max_score = max(m["score"] for m in matches)

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("매칭된 교수", f"{len(matches)}명")
        with stat_col2:
            st.metric("최고 점수", f"{max_score}%")
        with stat_col3:
            st.metric("평균 점수", f"{avg_score:.1f}%")

        st.markdown("---")

        # 각 매칭 결과 표시
        for i, match in enumerate(matches):
            display_match_result(match, i, openai_api_key, gemini_api_key)

            # SOP 도우미 섹션 (OpenAI 키가 있을 때만)
            if openai_api_key and match.get("full_data"):
                with st.expander(f"📝 {match['professor']} - SOP 작성 도우미"):
                    display_sop_assistant_section(
                        match["full_data"],
                        openai_api_key,
                        f"match_sop_{i}"
                    )

    elif st.session_state.get(SessionKeys.RESEARCH_INTERESTS):
        st.info("매칭되는 교수가 없습니다. 다른 키워드로 시도해보세요.")
