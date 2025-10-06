
import streamlit as st
from email_service import email_service
from pubmed_service import pubmed_service

def render(brevo_api_key):
    """연구 알림 인터페이스"""
    st.markdown("### 📧 연구 트렌드 알림 서비스")
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
