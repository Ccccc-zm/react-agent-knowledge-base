import time
import uuid
import streamlit as st
from agent.react_agent import ReactAgent
from utils.db_handler import (
    init_db, create_conversation, save_message, get_all_conversations,
    get_messages_by_thread, delete_conversation, update_conversation_title
)

# ---------- 初始化数据库 ----------
init_db()

# ---------- 标题 ----------
st.title("扫地机器人智能客服")
st.divider()

# ---------- 侧边栏：历史对话管理 ----------
with st.sidebar:
    st.header("📜 历史对话")

    if st.button("➕ 新建对话", use_container_width=True):
        st.session_state["thread_id"] = str(uuid.uuid4())
        st.session_state["message"] = []
        st.rerun()

    st.divider()

    conversations = get_all_conversations()
    for conv in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {conv['title']}", key=f"load_{conv['thread_id']}", use_container_width=True):
                st.session_state["thread_id"] = conv["thread_id"]
                st.session_state["message"] = get_messages_by_thread(conv["thread_id"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv['thread_id']}", help="删除对话"):
                delete_conversation(conv["thread_id"])
                if st.session_state.get("thread_id") == conv["thread_id"]:
                    st.session_state["thread_id"] = str(uuid.uuid4())
                    st.session_state["message"] = []
                st.rerun()

# ---------- 主界面 ----------
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

if "message" not in st.session_state:
    st.session_state["message"] = []

for msg in st.session_state["message"]:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    thread_id = st.session_state["thread_id"]
    create_conversation(thread_id, title=prompt[:20] + "..." if len(prompt) > 20 else prompt)
    save_message(thread_id, "user", prompt)

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)


        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.01)
                    yield char


        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))

        # 只保存最后一条消息（最终回答）
        final_answer = response_messages[-1] if response_messages else ""
        if final_answer:
            # 存入会话状态（用于当前页面显示）
            st.session_state["message"].append({"role": "assistant", "content": final_answer})
            # 存入数据库
            thread_id = st.session_state["thread_id"]
            save_message(thread_id, "assistant", final_answer)

            # 如果是第一条对话，自动设置标题
            if len(st.session_state["message"]) == 2:  # 刚加入了一问一答
                update_conversation_title(thread_id, prompt[:30] + ("..." if len(prompt) > 30 else ""))

    st.rerun()