# 🧠 임상심리학 동영상 & 교수진 추천 시스템

> **APA 인증 186개 대학의 임상심리학 교수진과 관련 동영상을 AI가 추천해드립니다**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [설치 및 실행](#-설치-및-실행)
- [사용법](#-사용법)
- [API 설정](#-api-설정)
- [프로젝트 구조](#-프로젝트-구조)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 🎯 프로젝트 소개

**임상심리학 동영상 & 교수진 추천 시스템**은 YouTube API와 APA 인증 대학 데이터베이스를 활용하여 임상심리학 분야의 전문 교수진 정보와 관련 교육 동영상을 추천하는 종합적인 웹 애플리케이션입니다.

### 🌟 개발 배경

- 임상심리학 관련 정보의 신뢰성 문제 해결
- APA 인증 대학 교수진 정보 체계화
- 연구 분야별 전문가 매칭 시스템 구축
- 전문가와 학습자 간의 정보 격차 해소

### 🎯 타겟 사용자

- 임상심리학 박사과정 지원자
- 임상심리학 전공 학생 및 연구자
- 심리치료사 및 상담사
- 정신건강 관련 종사자
- 특정 연구 분야 전문가를 찾는 연구자

## ✨ 주요 기능

### 🎬 **동영상 검색 시스템**
- **10개 전문 카테고리**: 임상심리학 기초부터 전문 치료기법까지
- **레벨별 학습**: 기초-중급 / APA 박사과정 수준
- **다언어 지원**: 한국어, 영어, 혼합 검색
- **실시간 YouTube API 연동**

### 👨‍🏫 **교수진 검색 시스템**
- **연구 분야별 검색**: 키워드로 전문가 찾기
- **19개 주요 APA 인증 대학** 포함
- **48명의 임상심리학 교수** 정보
- **연구실 및 연락처 정보** 제공

### 🏛️ **대학별 탐색 시스템**
- **대학별 교수진 리스트**
- **프로그램 정보** (PhD, PsyD)
- **위치 및 연락처 정보**
- **교수별 관련 동영상 추천**

### 📚 **전문 카테고리**
| 카테고리 | 설명 |
|---------|------|
| 🏗️ **임상심리학 기초** | 기본 이론 및 개념 |
| 🛠️ **심리치료 기법** | CBT, 인지행동치료 등 |
| 💚 **정신건강** | 우울증, 불안장애 관련 |
| 📊 **심리평가** | 심리검사 및 평가도구 |
| 👶 **발달심리학** | 아동심리 및 발달 |
| 🔄 **트라우마 치료** | EMDR 등 전문치료 |
| 👨‍👩‍👧‍👦 **가족치료** | 부부상담, 가족상담 |
| 🚫 **중독치료** | 알코올, 도박 중독 |
| 👥 **집단치료** | 그룹상담 기법 |
| 🔬 **심리학 연구** | 연구방법론 |

### 🎨 **사용자 친화적 인터페이스**
- **직관적인 사이드바**: 쉬운 검색 설정
- **카드형 레이아웃**: 동영상 정보 한눈에 파악
- **상세 정보 토글**: 필요시 자세한 설명 확인
- **반응형 디자인**: 다양한 화면 크기 지원

### 🔐 **보안 및 설정**
- **API 키 보안**: 암호화된 입력 방식
- **환경변수 지원**: .env 파일을 통한 안전한 설정
- **에러 처리**: 견고한 예외 처리 시스템

## 🚀 설치 및 실행

### 📋 필수 조건

- Python 3.8 이상
- YouTube Data API v3 키
- 인터넷 연결

### 💾 설치

1. **저장소 클론**
   ```bash
   git clone https://github.com/yourusername/psychology-video-recommender.git
   cd psychology-video-recommender
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일에서 YOUTUBE_API_KEY 설정
   ```

4. **애플리케이션 실행**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **브라우저 접속**
   ```
   http://localhost:8501
   ```

## 📖 사용법

### 1️⃣ **API 키 설정**
- 사이드바에서 YouTube API 키 입력
- 또는 `.env` 파일에 미리 설정

### 2️⃣ **카테고리 선택**
- 관심 있는 임상심리학 분야 선택
- 드롭다운에서 10개 전문 카테고리 중 선택

### 3️⃣ **추가 검색어 입력** (선택사항)
- 더 구체적인 주제를 원할 경우
- 예: \"인지행동치료\", \"PTSD\" 등

### 4️⃣ **동영상 검색**
- \"🔍 동영상 검색\" 버튼 클릭
- 실시간으로 관련 동영상 로딩

### 5️⃣ **결과 확인**
- 카드 형태로 표시되는 동영상 정보
- 썸네일, 제목, 채널, 조회수, 발행일
- \"🎥 시청하기\" 버튼으로 YouTube 이동
- \"📋 상세정보\" 버튼으로 전체 설명 확인

## 🔑 API 설정

### YouTube Data API v3 키 발급

1. **Google Cloud Console 접속**
   ```
   https://console.cloud.google.com/
   ```

2. **프로젝트 생성/선택**
   - 새 프로젝트 생성 또는 기존 프로젝트 선택

3. **API 활성화**
   - APIs & Services → Library
   - \"YouTube Data API v3\" 검색 및 활성화

4. **API 키 생성**
   - APIs & Services → Credentials
   - \"+ CREATE CREDENTIALS\" → \"API key\"

5. **API 키 제한 설정** (권장)
   - API restrictions → YouTube Data API v3만 허용
   - Application restrictions → HTTP referrers 설정

### 환경변수 설정

```bash
# .env 파일
YOUTUBE_API_KEY=your_actual_api_key_here
```

## 📁 프로젝트 구조

```
psychology-video-recommender/
├── 📄 streamlit_app.py              # 메인 애플리케이션
├── 📄 requirements.txt              # Python 의존성
├── 📄 .env.example                  # 환경변수 예시
├── 📄 README.md                     # 프로젝트 문서
├── 📄 YouTube_Streamlit_App_Prompt.md  # 개발 프롬프트 문서
└── 📄 LICENSE                       # 라이선스
```

### 🏗️ 주요 컴포넌트

```python
# streamlit_app.py 주요 함수들
├── search_psychology_videos()       # YouTube API 검색
├── get_psychology_categories()      # 카테고리 정의
├── format_view_count()             # 조회수 포맷팅
└── main()                          # 메인 애플리케이션 로직
```

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.8+ |
| **API** | YouTube Data API v3 |
| **라이브러리** | requests, python-dotenv |
| **배포** | Streamlit Cloud (권장) |

## 📊 성능 최적화

- **효율적인 API 호출**: 배치 처리로 요청 수 최소화
- **캐싱 시스템**: 중복 검색 방지
- **반응형 UI**: 빠른 사용자 피드백
- **에러 복구**: 자동 재시도 메커니즘

## 🔧 개발 환경 설정

### 개발용 설치

```bash
# 개발 의존성 포함 설치
pip install -r requirements-dev.txt

# 코드 품질 검사
flake8 streamlit_app.py
black streamlit_app.py

# 테스트 실행
pytest tests/
```

### 환경별 설정

```bash
# 개발 환경
export ENVIRONMENT=development

# 프로덕션 환경
export ENVIRONMENT=production
```

## 🚨 문제 해결

### 자주 발생하는 문제

1. **API 키 오류**
   ```
   해결: API 키가 올바른지 확인, 활성화 상태 점검
   ```

2. **검색 결과 없음**
   ```
   해결: 다른 카테고리 시도, 검색어 수정
   ```

3. **느린 로딩**
   ```
   해결: 인터넷 연결 확인, API 제한 확인
   ```

### 로그 확인

```bash
# Streamlit 로그 확인
streamlit run streamlit_app.py --logger.level debug
```

## 🤝 기여하기

### 기여 방법

1. **Fork** 저장소
2. **브랜치** 생성 (`git checkout -b feature/AmazingFeature`)
3. **커밋** (`git commit -m 'Add some AmazingFeature'`)
4. **푸시** (`git push origin feature/AmazingFeature`)
5. **Pull Request** 생성

### 개발 가이드라인

- 코드 스타일: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 커밋 메시지: [Conventional Commits](https://www.conventionalcommits.org/)
- 테스트: 새 기능에 대한 테스트 필수

### 기여 아이디어

- [ ] 다국어 지원 (영어, 일본어 등)
- [ ] 즐겨찾기 기능
- [ ] 시청 기록 저장
- [ ] 동영상 평가 시스템
- [ ] AI 기반 개인화 추천
- [ ] 오프라인 모드 지원

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 개발팀

- **메인 개발자**: [Your Name](https://github.com/yourusername)
- **기여자들**: [Contributors](https://github.com/yourusername/psychology-video-recommender/contributors)

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/yourusername/psychology-video-recommender/issues)
- **이메일**: your.email@example.com
- **문서**: [Wiki](https://github.com/yourusername/psychology-video-recommender/wiki)

## 🎉 감사의 말

- YouTube Data API 제공: Google
- UI 프레임워크: Streamlit 팀
- 아이콘: [Emoji](https://emojipedia.org/)

---

<div align="center">

**🧠 임상심리학의 디지털 혁신을 함께 만들어가요! 🚀**

[⭐ Star](https://github.com/yourusername/psychology-video-recommender) 
[🐛 Report Bug](https://github.com/yourusername/psychology-video-recommender/issues) 
[💡 Request Feature](https://github.com/yourusername/psychology-video-recommender/issues)

</div>