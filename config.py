"""
2025_Vibe 앱 설정 파일
모든 상수, API 설정, 세션 키를 중앙 관리
"""
from typing import Dict, List


# =============================================================================
# 커스텀 예외 클래스
# =============================================================================
class AppError(Exception):
    """앱 기본 예외 클래스"""
    pass


class YouTubeAPIError(AppError):
    """YouTube API 관련 예외"""
    pass


class OpenAIAPIError(AppError):
    """OpenAI API 관련 예외"""
    pass


class ConfigurationError(AppError):
    """설정 관련 예외 (API 키 누락 등)"""
    pass


# =============================================================================
# 로깅 설정
# =============================================================================
import logging
import sys
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """애플리케이션 로거 설정

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger("2025_vibe")

    # 이미 핸들러가 설정되어 있으면 반환
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 포맷 설정
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# 기본 로거 인스턴스
logger = setup_logging()


# =============================================================================
# 페이지 설정
# =============================================================================
PAGE_CONFIG = {
    "page_title": "임상심리학 동영상 추천",
    "page_icon": "🧠",
    "layout": "wide"
}


# =============================================================================
# API 설정
# =============================================================================
class YouTubeConfig:
    """YouTube Data API v3 설정"""
    SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
    VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
    MAX_RESULTS = 30
    REGION_CODE = "KR"
    RELEVANCE_LANGUAGE = "ko"
    CACHE_TTL = 3600  # 1시간


class OpenAIConfig:
    """OpenAI API 설정"""
    MODEL = "gpt-4o-mini"
    MAX_TOKENS = 1500
    TEMPERATURE = 0.7


class GeminiConfig:
    """Google Gemini API 설정"""
    MODEL = "gemini-2.0-flash"
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7


# =============================================================================
# 세션 상태 키
# =============================================================================
class SessionKeys:
    """Streamlit 세션 상태 키 상수"""
    VIDEOS = "videos"
    LAST_SEARCH = "last_search"
    SEARCHED_PROFESSORS = "searched_professors"
    SEARCH_KEYWORD = "search_keyword"

    @staticmethod
    def chat_history(unique_key: str) -> str:
        """교수별 채팅 히스토리 키 생성"""
        return f"chat_history_{unique_key}"

    @staticmethod
    def chat_input(unique_key: str) -> str:
        """교수별 채팅 입력 키 생성"""
        return f"chat_input_{unique_key}"

    @staticmethod
    def professor_videos(index: int) -> str:
        """교수 검색 결과의 동영상 키 생성"""
        return f"prof_videos_{index}"

    @staticmethod
    def university_professor_videos(index: int) -> str:
        """대학별 교수 동영상 키 생성"""
        return f"univ_prof_videos_{index}"


# =============================================================================
# 심리학 카테고리
# =============================================================================
PSYCHOLOGY_CATEGORIES: Dict[str, str] = {
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

APA_DOCTORAL_CATEGORIES: Dict[str, str] = {
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


# =============================================================================
# 질문 템플릿
# =============================================================================
QUESTION_TEMPLATES: Dict[str, List[str]] = {
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


# =============================================================================
# UI 텍스트 상수
# =============================================================================
class UIText:
    """UI에 표시되는 텍스트 상수"""
    APP_TITLE = "🧠 임상심리학 동영상 & 교수진 추천"
    APP_SUBTITLE = "**APA 인증 186개 대학의 임상심리학 교수진과 관련 동영상을 찾아드립니다**"

    # 탭 이름
    TAB_VIDEOS = "🎬 동영상 검색"
    TAB_PROFESSORS = "👨‍🏫 교수진 검색"
    TAB_UNIVERSITIES = "🏛️ 대학별 교수진"

    # 에러 메시지
    ERROR_NO_API_KEY = "👈 사이드바에서 YouTube API 키를 입력하거나 .env 파일에 설정해주세요."
    ERROR_NO_RESULTS = "검색 결과가 없습니다. 다른 카테고리를 시도해보거나 검색어를 수정해주세요."
    ERROR_CHATGPT_NO_KEY = "🤖 ChatGPT 상담을 위해 사이드바에서 OpenAI API 키를 입력해주세요."
    ERROR_CHATGPT_NO_RESPONSE = "❌ ChatGPT로부터 응답을 받지 못했습니다."

    # 상태 메시지
    STATUS_YOUTUBE_CONNECTED = "✅ 연결됨"
    STATUS_YOUTUBE_DISCONNECTED = "❌ 미설정"


# =============================================================================
# 환경 변수 키
# =============================================================================
class EnvKeys:
    """환경 변수 키 상수"""
    YOUTUBE_API_KEY = "YOUTUBE_API_KEY"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    OPENAI_MODEL = "OPENAI_MODEL"
    GEMINI_API_KEY = "GEMINI_API_KEY"


# =============================================================================
# Phase 3: 필터/정렬 옵션
# =============================================================================
class SortOptions:
    """동영상 정렬 옵션"""
    RELEVANCE = "관련성순"
    VIEW_COUNT_DESC = "조회수 높은순"
    VIEW_COUNT_ASC = "조회수 낮은순"
    DATE_DESC = "최신순"
    DATE_ASC = "오래된순"

    @classmethod
    def all(cls) -> List[str]:
        return [cls.RELEVANCE, cls.VIEW_COUNT_DESC, cls.VIEW_COUNT_ASC, cls.DATE_DESC, cls.DATE_ASC]


class DateFilterOptions:
    """날짜 필터 옵션"""
    ALL = "전체 기간"
    WEEK = "최근 1주"
    MONTH = "최근 1개월"
    YEAR = "최근 1년"

    @classmethod
    def all(cls) -> List[str]:
        return [cls.ALL, cls.WEEK, cls.MONTH, cls.YEAR]

    @classmethod
    def to_days(cls, option: str) -> int:
        """옵션을 일 수로 변환 (0 = 필터 없음)"""
        mapping = {
            cls.ALL: 0,
            cls.WEEK: 7,
            cls.MONTH: 30,
            cls.YEAR: 365,
        }
        return mapping.get(option, 0)


# =============================================================================
# Phase 3: 즐겨찾기 설정
# =============================================================================
class FavoritesConfig:
    """즐겨찾기 관련 설정"""
    MAX_PROFESSORS = 50  # 최대 교수 즐겨찾기 수
    MAX_VIDEOS = 100  # 최대 동영상 즐겨찾기 수


class FavoritesKeys:
    """즐겨찾기 세션 키"""
    PROFESSORS = "favorite_professors"
    VIDEOS = "favorite_videos"
    COMPARE_LIST = "compare_professors"


# =============================================================================
# Phase 3: 비교 기능 설정
# =============================================================================
class CompareConfig:
    """교수 비교 기능 설정"""
    MIN_PROFESSORS = 2
    MAX_PROFESSORS = 4


# SessionKeys 확장
SessionKeys.FAVORITE_PROFESSORS = FavoritesKeys.PROFESSORS
SessionKeys.FAVORITE_VIDEOS = FavoritesKeys.VIDEOS
SessionKeys.COMPARE_LIST = FavoritesKeys.COMPARE_LIST
SessionKeys.VIDEO_SORT = "video_sort"
SessionKeys.VIDEO_DATE_FILTER = "video_date_filter"


# UIText 확장
UIText.TAB_FAVORITES = "⭐ 즐겨찾기"
UIText.TAB_COMPARE = "⚖️ 교수 비교"
UIText.NO_FAVORITES = "아직 즐겨찾기한 항목이 없습니다."
UIText.COMPARE_EMPTY = "비교할 교수를 선택해주세요. (최소 2명, 최대 4명)"
UIText.COMPARE_MIN_WARNING = "비교하려면 최소 2명의 교수를 선택해야 합니다."


# =============================================================================
# Phase 4: Research Fit Analyzer 설정
# =============================================================================
class ResearchFitConfig:
    """연구 적합도 분석 설정"""
    MIN_SCORE = 5.0  # 최소 매칭 점수 (%)
    TOP_N_RESULTS = 10  # 상위 결과 수
    MIN_KEYWORD_LENGTH = 3  # 최소 키워드 길이


# =============================================================================
# Phase 4: SOP 작성 도우미 프롬프트
# =============================================================================
SOP_ANALYSIS_PROMPT = """당신은 임상심리학 대학원 지원 전문 컨설턴트입니다.
학생의 SOP(Statement of Purpose)를 분석하고 구체적인 피드백을 제공합니다.

📋 분석 대상 교수 정보:
{professor_info}

🎯 분석 기준:
1. 연구 관심사의 구체성과 명확성
2. 해당 교수님/프로그램과의 적합성 (Fit)
3. 관련 경험과 역량의 제시
4. 글의 구조와 논리적 흐름
5. 독창성과 차별화 요소

📝 학생의 SOP:
{sop_content}

위 SOP를 분석하여 다음 형식으로 피드백을 제공하세요:

## ✅ 강점 (2-3가지)
(구체적인 라인이나 표현 언급)

## ⚠️ 개선이 필요한 부분 (3-4가지)
(구체적인 수정 제안 포함)

## 💡 추가 권장 사항
(이 교수님의 연구와 연결할 수 있는 포인트)

## 📊 경쟁력 평가
(상/중상/중/중하/하 + 간단한 이유)
"""

SOP_DRAFT_PROMPT = """당신은 임상심리학 대학원 지원 전문 작가입니다.
학생의 배경 정보를 바탕으로 SOP 초안을 작성합니다.

📋 지원 대상:
- 교수: {professor_name}
- 대학: {university}
- 연구 분야: {research_areas}
- 연구 키워드: {research_keywords}

👤 학생 정보:
{student_info}

🎯 작성 가이드라인:
1. 첫 문단: 연구에 대한 열정과 관심 분야 소개
2. 둘째 문단: 관련 경험과 역량 (구체적 사례 포함)
3. 셋째 문단: 왜 이 교수님/프로그램인지 (구체적 연결)
4. 넷째 문단: 향후 연구 계획과 목표
5. 마지막: 간결한 마무리

📝 SOP 초안을 한국어로 작성하되, 전문 용어는 영어를 병기하세요.
약 800-1000 단어 분량으로 작성하세요.
"""

SMART_QUESTION_PROMPT = """당신은 임상심리학 박사과정 지원 전문 상담사입니다.
학생이 교수님께 연락하거나 면접에서 물어볼 수 있는 지적인 질문을 생성합니다.

📋 교수 정보:
- 이름: {professor_name}
- 대학: {university}
- 연구 분야: {research_areas}
- 연구 키워드: {research_keywords}
- 연구실: {lab_name}

👤 학생 관심 분야:
{student_interests}

🎯 다음 3가지 카테고리별로 2개씩 질문을 생성하세요:

## 🔬 연구 관련 질문
(최근 연구 방향, 방법론, 이론적 관점에 대한 깊이 있는 질문)

## 🎓 프로그램/연구실 관련 질문
(연구실 문화, 멘토링 스타일, 협업 기회에 대한 질문)

## 💼 커리어 관련 질문
(진로 경로, 필요한 역량, 네트워크 기회에 대한 질문)

⚠️ 피해야 할 질문:
- 웹사이트에서 쉽게 찾을 수 있는 기본 정보
- 너무 일반적이거나 뻔한 질문
- 부정적이거나 논쟁적인 주제

각 질문에 왜 이 질문이 좋은지 간단한 설명을 덧붙이세요.
"""


# =============================================================================
# Phase 4: UI 텍스트 확장
# =============================================================================
UIText.TAB_RESEARCH_FIT = "🎯 연구 매칭"
UIText.RESEARCH_FIT_TITLE = "연구 적합도 분석기"
UIText.RESEARCH_FIT_SUBTITLE = "당신의 연구 관심사와 가장 잘 맞는 교수님을 찾아드립니다"
UIText.SOP_ASSISTANT_TITLE = "SOP 작성 도우미"
UIText.SMART_QUESTIONS_TITLE = "지능형 질문 생성기"
UIText.NO_MATCHES_FOUND = "매칭되는 교수가 없습니다. 다른 키워드로 시도해보세요."
UIText.ENTER_INTERESTS = "연구 관심사를 입력해주세요 (예: depression, CBT, adolescent, anxiety)"


# =============================================================================
# Phase 4: 세션 키 확장
# =============================================================================
SessionKeys.RESEARCH_INTERESTS = "research_interests"
SessionKeys.MATCH_RESULTS = "match_results"
SessionKeys.SOP_DRAFT = "sop_draft"
SessionKeys.GENERATED_QUESTIONS = "generated_questions"
SessionKeys.LEARNING_ROADMAP = "learning_roadmap"


# =============================================================================
# Phase 4: 학습 로드맵 프롬프트 (Gemini 사용)
# =============================================================================
LEARNING_ROADMAP_PROMPT = """당신은 임상심리학 박사과정 지원을 준비하는 학생을 위한 학습 컨설턴트입니다.
학생의 배경과 목표 교수님 정보를 바탕으로 맞춤형 학습 로드맵을 생성합니다.

📋 학생 정보:
- 현재 수준: {student_level}
- 연구 관심사: {research_interests}
- 목표 지원 시기: {target_timeline}

🎯 목표 교수님:
- 이름: {professor_name}
- 대학: {university}
- 연구 분야: {research_areas}
- 연구 키워드: {research_keywords}

다음 형식으로 6개월 학습 로드맵을 작성하세요:

## 📚 1단계: 기초 다지기 (1-2개월)
### 필수 학습 주제
- (구체적인 주제와 추천 교재/자료)

### 추천 활동
- (논문 읽기, 강의 수강 등)

## 📖 2단계: 심화 학습 (3-4개월)
### 핵심 연구 분야 탐구
- (교수님의 연구와 연결되는 주제)

### 실습 및 경험
- (연구 보조, 임상 경험 등)

## 🎓 3단계: 지원 준비 (5-6개월)
### 포트폴리오 구축
- (연구 경험, 발표, 논문 등)

### 지원서 작성
- (SOP, CV, 추천서 준비)

## 📌 주간 학습 체크리스트
(구체적인 주간 목표 5-7개)

## 💡 추가 조언
(이 교수님 연구실에 맞는 특별한 준비 사항)

한국어로 작성하되, 전문 용어는 영어를 병기하세요.
"""

UIText.LEARNING_ROADMAP_TITLE = "📚 학습 로드맵"
UIText.LEARNING_ROADMAP_SUBTITLE = "목표 교수님 연구실 지원을 위한 맞춤형 학습 계획"
