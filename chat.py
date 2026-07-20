from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from rag import BaseRagService
from config import Config
from knowledgebaseservice import KnowledgeBaseService
from filechathistory import get_history
from langchain_core.runnables import RunnableConfig

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simple RAG — 智能知识问答",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal CSS — only what's needed ───────────────────────────────
st.markdown("""
<style>
    #MainMenu, footer, header[data-testid="stHeader"] { display: none; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f5f5f5;
        border-right: 1px solid #e0e0e0;
    }

    /* Sidebar buttons — dark, high contrast against light gray bg */
    [data-testid="stSidebar"] .stButton > button {
        background: #37474f;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
        transition: background 0.15s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #263238;
        color: #ffffff;
    }

    /* Text input in sidebar */
    [data-testid="stSidebar"] .stTextInput input {
        border-radius: 6px;
        border: 1px solid #ccc;
    }

    /* File uploader in sidebar */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        border-radius: 6px;
        border: 2px dashed #bbb;
        background: #fafafa;
    }

    /* Chat message spacing */
    [data-testid="stChatMessage"] {
        padding: 6px 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────
DEFAULT_SESSION_ID = "user_0001"

if "session_id" not in st.session_state:
    st.session_state.session_id = DEFAULT_SESSION_ID

if "rag_service" not in st.session_state:
    st.session_state.rag_service = BaseRagService(
        Config(SESSION_ID=st.session_state.session_id)
    )

if "kb_service" not in st.session_state:
    st.session_state.kb_service = KnowledgeBaseService()


def rebuild_rag_service(sid: str) -> None:
    st.session_state.rag_service = BaseRagService(Config(SESSION_ID=sid))
    st.session_state.session_id = sid


# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Simple RAG")
    st.caption("基于检索增强生成的智能知识问答系统")

    st.markdown("---")

    # File upload
    st.markdown("### 📤 知识库更新")
    uploaded_file = st.file_uploader(
        "选择文本文件",
        type=["txt"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("文件编码错误，请上传 UTF-8 编码的文本文件")
        else:
            with st.spinner(f"正在处理 {file_name} …"):
                result = st.session_state.kb_service.up_load_by_str(
                    file_content, file_name
                )
            if "成功" in result:
                st.success(f"{file_name} 已加入知识库")
            elif "已储存" in result:
                st.info(result)
            else:
                st.warning(result)

    st.markdown("---")

    # Session
    st.markdown("### 🔖 会话")
    new_session = st.text_input(
        "会话 ID",
        value=st.session_state.session_id,
        label_visibility="collapsed",
    )
    if new_session != st.session_state.session_id:
        rebuild_rag_service(new_session)
        st.rerun()

    if st.button("清除对话历史", use_container_width=True):
        get_history(st.session_state.session_id).clear()
        st.rerun()

    st.markdown("---")
    st.caption(f"当前会话：{st.session_state.session_id}")

# ── Main chat area ─────────────────────────────────────────────────
st.markdown("## 💬 智能知识问答")

# Render history
history = get_history(st.session_state.session_id)
messages = history.messages if history.messages else []

for msg in messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Chat input
if prompt := st.chat_input("输入你的问题，基于知识库为你解答…"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        run_config: RunnableConfig = {
            "configurable": {"session_id": st.session_state.session_id}
        }
        chain = st.session_state.rag_service.get_chain()

        with st.spinner("思考中…"):
            try:
                response = chain.invoke({"input": prompt}, config=run_config)
                st.markdown(response)
            except Exception as exc:
                st.error(f"出错了：{exc}")
