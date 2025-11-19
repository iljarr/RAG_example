# 보험약관 RAG 챗봇

PDF 파일을 기반으로 한 보험약관 질의응답 챗봇입니다. Gemini 3.0 Pro와 Pinecone을 사용하여 구현되었습니다.

## 기능

- PDF 파일에서 보험약관 텍스트 추출
- Pinecone 벡터 데이터베이스에 문서 저장
- 사용자 질문에 대한 의미 기반 검색
- Gemini 3.0 Pro를 활용한 자연스러운 답변 생성
- Streamlit 기반 웹 인터페이스

## 기술 스택

- **LLM**: Gemini 3.0 Pro (Google)
- **벡터 DB**: Pinecone
- **임베딩 모델**: Pinecone 기본 제공 모델 (multilingual-e5-large)
- **웹 프레임워크**: Streamlit
- **PDF 처리**: PyPDF2

## 설치 방법

1. 저장소 클론 또는 파일 다운로드

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
   - `.env.example` 파일을 `.env`로 복사
   - `.env` 파일에 API 키 입력:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     PINECONE_API_KEY=your_pinecone_api_key
     ```

## 사용 방법

### 1. PDF 파일을 Pinecone에 업로드

먼저 PDF 파일을 처리하고 Pinecone에 업로드해야 합니다:

```bash
python pdf_processor.py
```

이 스크립트는:
- `20120401_10101_1.pdf` 파일을 읽습니다
- 텍스트를 추출하고 청크로 분할합니다
- Pinecone 인덱스를 생성합니다 (없는 경우)
- 문서를 Pinecone에 업로드합니다

### 2. Streamlit 앱 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 앱이 열립니다.

### 3. 챗봇 사용

- 웹 인터페이스에서 보험약관에 대한 질문을 입력하세요
- Enter 키를 누르거나 전송 버튼을 클릭하세요
- 챗봇이 관련 약관 내용을 찾아 답변해드립니다

## 프로젝트 구조

```
.
├── app.py                 # Streamlit 메인 앱
├── rag_chatbot.py         # RAG 챗봇 로직
├── pdf_processor.py       # PDF 처리 및 Pinecone 업로드
├── requirements.txt       # 필요한 패키지 목록
├── .env.example          # 환경 변수 예시
├── README.md             # 프로젝트 설명
└── 20120401_10101_1.pdf  # 보험약관 PDF 파일
```

## 주요 파일 설명

### `pdf_processor.py`
- PDF 파일에서 텍스트 추출
- 텍스트를 청크로 분할
- Pinecone 인덱스 생성 및 데이터 업로드

### `rag_chatbot.py`
- Pinecone에서 관련 문서 검색
- Gemini API를 사용한 응답 생성
- RAG 파이프라인 구현

### `app.py`
- Streamlit 웹 인터페이스
- 채팅 UI 구현
- 사용자 상호작용 처리

## 환경 변수

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `GEMINI_API_KEY` | Google Gemini API 키 | ✅ |
| `PINECONE_API_KEY` | Pinecone API 키 | ✅ |
| `PINECONE_INDEX_NAME` | Pinecone 인덱스 이름 | ❌ (기본값: insurance-terms) |
| `EMBEDDING_MODEL` | 임베딩 모델 이름 | ❌ (기본값: multilingual-e5-large) |

## 주의사항

1. **API 키 보안**: `.env` 파일을 Git에 커밋하지 마세요
2. **PDF 파일**: `pdf_processor.py`에서 PDF 파일 경로를 확인하세요
3. **인덱스 생성**: 첫 실행 시 Pinecone 인덱스 생성에 시간이 걸릴 수 있습니다
4. **비용**: Gemini API와 Pinecone 사용 시 비용이 발생할 수 있습니다

## 문제 해결

### 챗봇이 초기화되지 않는 경우
- `.env` 파일이 올바르게 설정되었는지 확인하세요
- API 키가 유효한지 확인하세요

### PDF 업로드가 실패하는 경우
- PDF 파일 경로가 올바른지 확인하세요
- Pinecone API 키가 올바른지 확인하세요
- 인터넷 연결을 확인하세요

### 검색 결과가 없는 경우
- PDF 파일이 먼저 업로드되었는지 확인하세요
- Pinecone 인덱스에 데이터가 있는지 확인하세요

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

