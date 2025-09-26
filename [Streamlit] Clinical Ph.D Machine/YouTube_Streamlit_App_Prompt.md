# YouTube 인기 동영상 Streamlit 앱 프롬프트

## 기본 요청
간단한 기본 앱 요청 프롬프트: YouTube API로 인기 동영상을 보여주는 기본적인 Streamlit 앱을 만들어주세요.

## 최소 요구사항
- 한 페이지 단순 구조
- 30개 동영상 리스트
- 썸네일, 제목, 채널명, 조회수 표시
- 새로고침 버튼
- 에러 처리

## 파일 구성
- `streamlit_app.py` (메인)
- `requirements.txt`
- `.env` 예시

## 추가 개선 요청 (순차적으로 적용)
1. **API 키 수동 입력**: YOUTUBE_API_KEY를 수동으로 넣을 수 있도록 업데이트
2. **UI 개선**: 한 줄로 얇게 나오게 해줘

## 구현 결과

### 파일 구조
```
├── streamlit_app.py          # 메인 애플리케이션
├── requirements.txt          # 패키지 의존성
├── .env.example             # API 키 설정 예시
└── YouTube_Streamlit_App_Prompt.md  # 이 문서
```

### 주요 기능
- **API 키 입력**: 웹 인터페이스에서 직접 입력 가능 (password 타입)
- **백업 옵션**: .env 파일에서도 API 키 읽기 지원
- **컴팩트 UI**: 5컬럼 레이아웃으로 한 줄에 모든 정보 표시
- **실시간 로딩**: 스피너와 함께 데이터 로딩
- **에러 처리**: API 오류, 네트워크 오류 등 완전한 예외 처리
- **사용자 가이드**: API 키 발급 방법 안내

### 실행 방법
```bash
# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run streamlit_app.py
```

### API 키 설정
1. **웹 인터페이스**: 앱 상단에서 직접 입력
2. **환경 변수**: `.env` 파일에 `YOUTUBE_API_KEY=your_key` 설정

### API 키 발급 방법
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. APIs & Services > Library에서 'YouTube Data API v3' 활성화
4. APIs & Services > Credentials에서 API 키 생성

## 프롬프트 최적화 팁

### 효과적인 요청 방법
1. **명확한 요구사항**: 구체적인 기능과 UI 요구사항 명시
2. **파일 구성 명시**: 필요한 파일들을 미리 지정
3. **단계적 개선**: 기본 기능 구현 후 점진적 개선 요청

### 재사용 가능한 패턴
```
[API 서비스] + [UI 프레임워크] + [데이터 표시 방식] 앱을 만들어주세요.

최소 요구사항:
- [기본 기능들]
- [UI 요구사항]
- [에러 처리]

파일 구성:
- [메인 파일]
- [설정 파일들]
```

## 버전 히스토리
- **v1.0**: 기본 YouTube API 연동 및 동영상 목록 표시
- **v1.1**: 수동 API 키 입력 기능 추가
- **v1.2**: 컴팩트한 한 줄 UI로 개선

## 추가 개선 아이디어
- [ ] 검색 기능 추가
- [ ] 카테고리별 필터링
- [ ] 페이지네이션
- [ ] 동영상 미리보기
- [ ] 즐겨찾기 기능
- [ ] 다국가 지역 코드 선택