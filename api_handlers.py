"""
API 핸들러 모듈
YouTube API 및 OpenAI API 호출 로직
"""
import requests
import streamlit as st
from typing import Dict, List, Any, Optional
import openai

from config import (
    logger,
    YouTubeConfig,
    OpenAIConfig,
)


def get_professor_prompt_template(professor_data: Dict[str, Any]) -> str:
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


def chat_with_gpt(
    api_key: str,
    professor_data: Dict[str, Any],
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """ChatGPT API를 사용한 대화 함수

    Note: conversation_history의 기본값을 None으로 설정하여 mutable default argument 문제 방지
    """
    if conversation_history is None:
        conversation_history = []

    prof_name = professor_data.get("professor", {}).get("name", "Unknown")
    logger.info(f"ChatGPT 요청 시작 - 교수: {prof_name}, 메시지 길이: {len(user_message)}")

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
            model=OpenAIConfig.MODEL,
            messages=messages,
            max_tokens=OpenAIConfig.MAX_TOKENS,
            temperature=OpenAIConfig.TEMPERATURE
        )

        if response.choices and len(response.choices) > 0:
            logger.info(f"ChatGPT 응답 성공 - 교수: {prof_name}")
            return response.choices[0].message.content
        logger.warning(f"ChatGPT 빈 응답 - 교수: {prof_name}")
        return "❌ ChatGPT로부터 응답을 받지 못했습니다."

    except openai.AuthenticationError:
        logger.error("OpenAI 인증 오류 - API 키 무효")
        return "❌ OpenAI API 키가 유효하지 않습니다. 키를 확인해주세요."
    except openai.RateLimitError:
        logger.warning("OpenAI Rate Limit 초과")
        return "❌ API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    except openai.APIConnectionError:
        logger.error("OpenAI 연결 오류")
        return "❌ OpenAI 서버에 연결할 수 없습니다. 네트워크를 확인해주세요."
    except openai.APIError as e:
        logger.error(f"OpenAI API 오류: {e}")
        return f"❌ OpenAI API 오류: {str(e)}"
    except Exception as e:
        logger.exception(f"ChatGPT 예기치 않은 오류: {e}")
        return f"❌ 예기치 않은 오류가 발생했습니다: {str(e)}"


@st.cache_data(ttl=YouTubeConfig.CACHE_TTL, show_spinner=False)
def search_psychology_videos(api_key: str, search_query: str = "임상심리학") -> List[Dict[str, Any]]:
    """임상심리학 관련 동영상을 검색하는 함수 (1시간 캐싱)"""
    logger.info(f"YouTube 검색 시작 - 쿼리: {search_query}")

    try:
        if not api_key:
            logger.warning("YouTube API 키 미설정")
            st.error("YouTube API 키를 입력해주세요.")
            return []

        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'order': 'relevance',
            'maxResults': YouTubeConfig.MAX_RESULTS,
            'regionCode': YouTubeConfig.REGION_CODE,
            'relevanceLanguage': YouTubeConfig.RELEVANCE_LANGUAGE,
            'key': api_key
        }

        response = requests.get(YouTubeConfig.SEARCH_URL, params=params)
        response.raise_for_status()

        search_data = response.json()
        video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]

        if not video_ids:
            return []

        # 비디오 상세 정보 가져오기
        details_params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids),
            'key': api_key
        }

        details_response = requests.get(YouTubeConfig.VIDEOS_URL, params=details_params)
        details_response.raise_for_status()

        details_data = details_response.json()
        items = details_data.get('items', [])
        logger.info(f"YouTube 검색 성공 - 결과: {len(items)}개")
        return items

    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            status_code = e.response.status_code
            logger.error(f"YouTube HTTP 오류 - 상태코드: {status_code}")
            if status_code == 403:
                st.error("YouTube API 키가 유효하지 않거나 할당량을 초과했습니다.")
            elif status_code == 404:
                st.error("요청한 리소스를 찾을 수 없습니다.")
            else:
                st.error(f"HTTP 오류 ({status_code}): {e}")
        else:
            logger.error(f"YouTube HTTP 오류: {e}")
            st.error(f"HTTP 요청 오류: {e}")
        return []
    except requests.exceptions.ConnectionError:
        logger.error("YouTube 연결 오류")
        st.error("YouTube 서버에 연결할 수 없습니다. 네트워크를 확인해주세요.")
        return []
    except requests.exceptions.Timeout:
        logger.warning("YouTube 요청 타임아웃")
        st.error("요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"YouTube 요청 오류: {e}")
        st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        return []
    except ValueError as e:
        logger.error(f"YouTube 응답 파싱 오류: {e}")
        st.error(f"응답 데이터 처리 중 오류가 발생했습니다: {e}")
        return []
    except Exception as e:
        logger.exception(f"YouTube 예기치 않은 오류: {e}")
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
        return []


def search_professor_videos(api_key: str, professor_name: str, research_keywords: str) -> List[Dict[str, Any]]:
    """특정 교수의 연구 분야와 관련된 동영상을 검색하는 함수"""
    search_query = f"{professor_name} {research_keywords} psychology lecture research"
    return search_psychology_videos(api_key, search_query)


# =============================================================================
# Phase 4: SOP 및 질문 생성 API
# =============================================================================
def analyze_sop(
    api_key: str,
    professor_data: Dict[str, Any],
    sop_content: str
) -> str:
    """SOP 분석 및 피드백 생성

    Args:
        api_key: OpenAI API 키
        professor_data: 대상 교수 정보
        sop_content: 분석할 SOP 내용

    Returns:
        분석 결과 텍스트
    """
    from config import SOP_ANALYSIS_PROMPT

    prof = professor_data.get("professor", {})
    professor_info = f"""
- 이름: {prof.get('name', 'Unknown')}
- 대학: {professor_data.get('university', 'Unknown')}
- 연구 분야: {', '.join(prof.get('research_areas', []))}
- 연구 키워드: {prof.get('research_keywords', '')}
- 연구실: {prof.get('lab', 'N/A')}
"""

    prompt = SOP_ANALYSIS_PROMPT.format(
        professor_info=professor_info,
        sop_content=sop_content
    )

    logger.info(f"SOP 분석 요청 - 교수: {prof.get('name', 'Unknown')}")

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=OpenAIConfig.MODEL,
            messages=[
                {"role": "system", "content": "당신은 임상심리학 대학원 지원 전문 컨설턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        if response.choices and len(response.choices) > 0:
            logger.info("SOP 분석 완료")
            return response.choices[0].message.content
        return "❌ 분석 결과를 받지 못했습니다."

    except Exception as e:
        logger.error(f"SOP 분석 오류: {e}")
        return f"❌ 오류가 발생했습니다: {str(e)}"


def generate_sop_draft(
    api_key: str,
    professor_data: Dict[str, Any],
    student_info: str
) -> str:
    """SOP 초안 생성

    Args:
        api_key: OpenAI API 키
        professor_data: 대상 교수 정보
        student_info: 학생 배경 정보

    Returns:
        생성된 SOP 초안
    """
    from config import SOP_DRAFT_PROMPT

    prof = professor_data.get("professor", {})

    prompt = SOP_DRAFT_PROMPT.format(
        professor_name=prof.get('name', 'Unknown'),
        university=professor_data.get('university', 'Unknown'),
        research_areas=', '.join(prof.get('research_areas', [])),
        research_keywords=prof.get('research_keywords', ''),
        student_info=student_info
    )

    logger.info(f"SOP 초안 생성 요청 - 교수: {prof.get('name', 'Unknown')}")

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=OpenAIConfig.MODEL,
            messages=[
                {"role": "system", "content": "당신은 임상심리학 대학원 지원서 작성 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.8
        )

        if response.choices and len(response.choices) > 0:
            logger.info("SOP 초안 생성 완료")
            return response.choices[0].message.content
        return "❌ 초안을 생성하지 못했습니다."

    except Exception as e:
        logger.error(f"SOP 초안 생성 오류: {e}")
        return f"❌ 오류가 발생했습니다: {str(e)}"


def generate_smart_questions(
    api_key: str,
    professor_data: Dict[str, Any],
    student_interests: str
) -> str:
    """교수 컨택/면접용 스마트 질문 생성

    Args:
        api_key: OpenAI API 키
        professor_data: 대상 교수 정보
        student_interests: 학생 연구 관심사

    Returns:
        생성된 질문 목록
    """
    from config import SMART_QUESTION_PROMPT

    prof = professor_data.get("professor", {})

    prompt = SMART_QUESTION_PROMPT.format(
        professor_name=prof.get('name', 'Unknown'),
        university=professor_data.get('university', 'Unknown'),
        research_areas=', '.join(prof.get('research_areas', [])),
        research_keywords=prof.get('research_keywords', ''),
        lab_name=prof.get('lab', 'N/A'),
        student_interests=student_interests
    )

    logger.info(f"스마트 질문 생성 요청 - 교수: {prof.get('name', 'Unknown')}")

    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=OpenAIConfig.MODEL,
            messages=[
                {"role": "system", "content": "당신은 임상심리학 박사과정 지원 전문 상담사입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        if response.choices and len(response.choices) > 0:
            logger.info("스마트 질문 생성 완료")
            return response.choices[0].message.content
        return "❌ 질문을 생성하지 못했습니다."

    except Exception as e:
        logger.error(f"스마트 질문 생성 오류: {e}")
        return f"❌ 오류가 발생했습니다: {str(e)}"


# =============================================================================
# Phase 4: 학습 로드맵 생성 (Gemini API)
# =============================================================================
def generate_learning_roadmap(
    api_key: str,
    professor_data: Dict[str, Any],
    student_level: str,
    research_interests: str,
    target_timeline: str
) -> str:
    """Gemini를 사용한 학습 로드맵 생성

    Args:
        api_key: Gemini API 키
        professor_data: 목표 교수 정보
        student_level: 학생 현재 수준 (학부생, 졸업예정, 석사 등)
        research_interests: 연구 관심사
        target_timeline: 지원 목표 시기

    Returns:
        생성된 학습 로드맵 텍스트
    """
    import google.generativeai as genai
    from config import LEARNING_ROADMAP_PROMPT, GeminiConfig

    prof = professor_data.get("professor", {})

    prompt = LEARNING_ROADMAP_PROMPT.format(
        student_level=student_level,
        research_interests=research_interests,
        target_timeline=target_timeline,
        professor_name=prof.get('name', 'Unknown'),
        university=professor_data.get('university', 'Unknown'),
        research_areas=', '.join(prof.get('research_areas', [])),
        research_keywords=prof.get('research_keywords', '')
    )

    logger.info(f"학습 로드맵 생성 요청 (Gemini) - 교수: {prof.get('name', 'Unknown')}")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GeminiConfig.MODEL)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=GeminiConfig.MAX_TOKENS,
                temperature=GeminiConfig.TEMPERATURE
            )
        )

        if response.text:
            logger.info("학습 로드맵 생성 완료 (Gemini)")
            return response.text
        return "❌ 로드맵을 생성하지 못했습니다."

    except Exception as e:
        logger.error(f"학습 로드맵 생성 오류 (Gemini): {e}")
        return f"❌ 오류가 발생했습니다: {str(e)}"
