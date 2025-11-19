"""
보험약관 RAG 챗봇 Streamlit 앱
"""
import streamlit as st
from rag_chatbot import RAGChatbot
import os
from dotenv import load_dotenv

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="보험약관 RAG 챗봇",
    page_icon="📋",
    layout="wide"
)

# 제목
st.title("📋 보험약관 RAG 챗봇")
st.markdown("---")

# 세션 상태 초기화
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = RAGChatbot()
        st.session_state.messages = []
        st.success("챗봇이 초기화되었습니다!")
    except Exception as e:
        st.error(f"챗봇 초기화 오류: {str(e)}")
        st.info("환경 변수(GEMINI_API_KEY, PINECONE_API_KEY)가 올바르게 설정되었는지 확인해주세요.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 환경 변수 확인
    gemini_key = os.getenv("GEMINI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if gemini_key:
        st.success("✅ Gemini API 키 설정됨")
    else:
        st.error("❌ Gemini API 키가 설정되지 않았습니다")
    
    if pinecone_key:
        st.success("✅ Pinecone API 키 설정됨")
    else:
        st.error("❌ Pinecone API 키가 설정되지 않았습니다")
    
    st.markdown("---")
    st.markdown("### 📚 사용 방법")
    st.markdown("""
    1. 아래 입력창에 보험약관에 대한 질문을 입력하세요
    2. Enter 키를 누르거나 전송 버튼을 클릭하세요
    3. 챗봇이 관련 약관 내용을 찾아 답변해드립니다
    """)
    
    st.markdown("---")
    if st.button("🗑️ 대화 기록 삭제"):
        st.session_state.messages = []
        st.rerun()

# 채팅 기록 표시
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 소스 정보 표시 (assistant 메시지인 경우)
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📄 참고 문서 보기"):
                    for i, source in enumerate(message["sources"], 1):
                        score = source.get('score', 0.0)
                        if score is None:
                            score = 0.0
                        st.markdown(f"**문서 {i}** (유사도: {score:.3f})")
                        st.text(source["text"])

# 사용자 입력
if prompt := st.chat_input("보험약관에 대해 질문해보세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변을 생성하는 중..."):
            try:
                result = st.session_state.chatbot.chat(prompt)
                
                # 응답 표시
                st.markdown(result["response"])
                
                # 소스 정보 표시
                if result["sources"]:
                    with st.expander("📄 참고 문서 보기"):
                        for i, source in enumerate(result["sources"], 1):
                            score = source.get('score', 0.0)
                            if score is None:
                                score = 0.0
                            st.markdown(f"**문서 {i}** (유사도: {score:.3f})")
                            st.text(source["text"])
                
                # 응답을 세션 상태에 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "sources": result["sources"]
                })
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 하단 정보
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Powered by Gemini 3.0 Pro & Pinecone</small>
    </div>
    """,
    unsafe_allow_html=True
)

