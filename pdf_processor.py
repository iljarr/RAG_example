"""
PDF 파일을 처리하고 Pinecone에 업로드하는 모듈
"""
import os
import pypdf
from pinecone import Pinecone
from dotenv import load_dotenv
from typing import List
import uuid

load_dotenv()

# Pinecone 설정
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "insurance-terms")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "multilingual-e5-large")

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF 파일에서 텍스트 추출"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PDF 읽기 오류: {e}")
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """텍스트를 청크로 분할"""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def create_index_if_not_exists(pc: Pinecone, index_name: str):
    """인덱스가 없으면 생성"""
    if index_name not in pc.list_indexes().names():
        print(f"인덱스 '{index_name}' 생성 중...")
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": EMBEDDING_MODEL,
                "field_map": {"text": "chunk_text"}
            }
        )
        print(f"인덱스 '{index_name}' 생성 완료!")
    else:
        print(f"인덱스 '{index_name}' 이미 존재합니다.")

def upload_to_pinecone(pdf_path: str):
    """PDF 파일을 처리하고 Pinecone에 업로드"""
    # Pinecone 클라이언트 초기화
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # 인덱스 생성 또는 확인
    create_index_if_not_exists(pc, PINECONE_INDEX_NAME)
    
    # 인덱스 연결
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # PDF에서 텍스트 추출
    print(f"PDF 파일 읽는 중: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if not text.strip():
        print("PDF에서 텍스트를 추출할 수 없습니다.")
        return
    
    # 텍스트 청킹
    print("텍스트 청킹 중...")
    chunks = chunk_text(text)
    print(f"총 {len(chunks)}개의 청크 생성됨")
    
    # Pinecone에 업로드 (통합 임베딩 사용)
    print("Pinecone에 업로드 중...")
    records = []
    
    for i, chunk in enumerate(chunks):
        # 통합 임베딩 인덱스의 경우 upsert_records 사용
        # field_map에서 지정한 필드명(chunk_text)에 텍스트를 넣어야 함
        record = {
            "_id": str(uuid.uuid4()),
            "chunk_text": chunk,  # field_map에 지정된 필드명 사용
            "chunk_index": i,
            "source": pdf_path
        }
        records.append(record)
        
        # 배치로 업로드 (배치 크기: 96 - 통합 임베딩 제한)
        if len(records) >= 96:
            index.upsert_records("__default__", records)
            print(f"{len(records)}개 레코드 업로드됨")
            records = []
    
    # 남은 레코드 업로드
    if records:
        index.upsert_records("__default__", records)
        print(f"{len(records)}개 레코드 업로드됨")
    
    print("업로드 완료!")

if __name__ == "__main__":
    pdf_path = "20120401_10101_1.pdf"
    upload_to_pinecone(pdf_path)

