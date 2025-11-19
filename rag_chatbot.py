"""
RAG 챗봇 로직 구현
"""
import os
from typing import List, Dict
from pinecone import Pinecone
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 환경 변수
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "insurance-terms")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "multilingual-e5-large")

class RAGChatbot:
    def __init__(self):
        # Pinecone 초기화
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # 인덱스 확인
        try:
            # 인덱스 리스트 확인
            indexes = self.pc.list_indexes()
            index_names = [i.name for i in indexes]
            
            if PINECONE_INDEX_NAME not in index_names:
                raise ValueError(f"인덱스 '{PINECONE_INDEX_NAME}'를 찾을 수 없습니다. 'python pdf_processor.py'를 실행하여 인덱스를 생성해주세요.")
            
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
        except Exception as e:
            print(f"Pinecone 초기화 오류: {e}")
            raise e
        
        # Gemini 클라이언트 초기화
        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        # Gemini Flash Latest 사용
        self.model = "gemini-flash-latest"
    
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """쿼리와 관련된 청크 검색"""
        try:
            # Pinecone에서 검색 (통합 임베딩 사용 시 텍스트로 직접 검색)
            # 최신 SDK에서는 search() 메서드 사용
            results = self.index.search(
                namespace="__default__",
                query={
                    "inputs": {"text": query},
                    "top_k": top_k
                },
                fields=["chunk_text"]  # 반환할 필드 지정
            )
            
            chunks = []
            # 응답 구조 확인 필요 - result.hits 또는 matches
            if hasattr(results, 'result') and hasattr(results.result, 'hits'):
                # 새로운 응답 형식
                for hit in results.result.hits:
                    chunks.append({
                        "text": hit.fields.get("chunk_text", "") if hasattr(hit, 'fields') else "",
                        "score": (hit.score if hasattr(hit, 'score') and hit.score is not None else 0.0),
                        "metadata": hit.fields if hasattr(hit, 'fields') else {}
                    })
            elif hasattr(results, 'matches'):
                # 기존 응답 형식
                for match in results.matches:
                    chunks.append({
                        "text": match.metadata.get("chunk_text", "") if hasattr(match, 'metadata') else "",
                        "score": (match.score if hasattr(match, 'score') and match.score is not None else 0.0),
                        "metadata": match.metadata if hasattr(match, 'metadata') else {}
                    })
            else:
                # 딕셔너리 형식 응답
                if isinstance(results, dict):
                    hits = results.get('result', {}).get('hits', []) or results.get('matches', [])
                    for hit in hits:
                        fields = hit.get('fields', {}) or hit.get('metadata', {})
                        score = hit.get("score", hit.get("_score", 0.0))
                        if score is None:
                            score = 0.0
                        chunks.append({
                            "text": fields.get("chunk_text", ""),
                            "score": score,
                            "metadata": fields
                        })
            
            return chunks
        except Exception as e:
            print(f"검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Gemini를 사용하여 응답 생성"""
        # 컨텍스트 구성
        context_text = "\n\n".join([
            f"[문서 {i+1}]\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # 프롬프트 구성
        prompt = f"""당신은 보험약관 전문가입니다. 다음 보험약관 문서를 참고하여 사용자의 질문에 정확하고 친절하게 답변해주세요.

[보험약관 문서]
{context_text}

[사용자 질문]
{query}

[답변 지침]
- 제공된 보험약관 문서의 내용을 기반으로 답변하세요.
- 문서에 없는 내용은 추측하지 말고, 문서에 명시된 내용만을 인용하세요.
- 답변은 명확하고 이해하기 쉽게 작성하세요.
- 필요시 관련 조항의 번호나 위치를 언급하세요.

답변:"""
        
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # 도구 설정 (Google Search 추가)
            tools = [
                types.Tool(googleSearch=types.GoogleSearch()),
            ]
            
            # 생성 설정 (thinkingConfig 포함)
            generate_content_config = types.GenerateContentConfig(
                thinkingConfig={
                    "thinkingBudget": -1,
                },
                tools=tools,
            )
            
            # 스트리밍 응답 생성
            response_text = ""
            for chunk in self.gemini_client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    response_text += chunk.text
            
            return response_text
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def chat(self, query: str) -> Dict[str, any]:
        """채팅 메서드 - 검색과 응답 생성 통합"""
        # 관련 문서 검색
        relevant_chunks = self.search_relevant_chunks(query, top_k=5)
        
        if not relevant_chunks:
            return {
                "response": "관련된 보험약관 내용을 찾을 수 없습니다.",
                "sources": []
            }
        
        # 응답 생성
        response = self.generate_response(query, relevant_chunks)
        
        return {
            "response": response,
            "sources": [
                {
                    "text": chunk["text"][:200] + "...",  # 미리보기
                    "score": chunk["score"]
                }
                for chunk in relevant_chunks
            ]
        }

