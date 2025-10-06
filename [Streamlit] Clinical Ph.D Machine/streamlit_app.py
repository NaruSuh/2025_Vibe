
import streamlit as st
import os
from dotenv import load_dotenv

from ui import video_search, professor_search, university, research_alert

load_dotenv()

st.set_page_config(
    page_title="임상심리학 동영상 추천",
    page_icon="🧠",
    layout="wide"
)

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
        video_search.render(youtube_api_key)
    
    with tab2:
        professor_search.render(youtube_api_key, openai_api_key)
    
    with tab3:
        university.render(youtube_api_key, openai_api_key)

    with tab4:
        research_alert.render(brevo_api_key)

if __name__ == "__main__":
    main()
