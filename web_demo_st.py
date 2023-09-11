# coding=utf-8

from chatbot import DocChatbot, stream_predict
import os
import streamlit as st


@st.cache_resource
def load_model():
    return DocChatbot()


chatbot = load_model()


def cut_history(u_input):
    if 'messages' not in st.session_state:
        return []

    history = []
    for idx in range(0, len(st.session_state['messages']), 2):
        history.append((st.session_state['messages'][idx]['content'], st.session_state['messages'][idx + 1]['content']))

    spilt = -1
    if len(history) > 0:
        while spilt >= -len(history):
            prompt_str = ["[Round {}]\n\n问：{}\n\n答：{}\n\n".format(idx + 1, x[0], x[1]) for idx, x in
                          enumerate(history[spilt:])]
            if len("".join(prompt_str) + u_input) < 450:
                spilt -= 1
            else:
                spilt += 1
                break
    else:
        spilt = 0

    if spilt != 0:
        history = history[spilt:]

    return history


with st.sidebar:
    st.title("💬 ChatDoc")
    st.write("上传一个文档，然后与我对话.")
    with st.form("Upload and Process", True):
        uploaded_file = st.file_uploader("上传文档", type=["pdf", "txt", "docx"], accept_multiple_files=True)

        option = st.selectbox(
            "选择已保存的知识库",
            chatbot.get_vector_db()
        )

        col1, col2, col5 = st.columns(3)
        with col1:
            submitted1 = st.form_submit_button("导入知识库")
        with col2:
            submitted = st.form_submit_button("添加知识库")
        with col5:
            submitted2 = st.form_submit_button("保存知识库")

        col3, col4 = st.columns(2)
        with col3:
            clear = st.form_submit_button("清除聊天记录")
        with col4:
            clear_file = st.form_submit_button("移除当前知识库")

        if submitted2 and 'files' not in st.session_state:
            st.error("先上传文件构建知识库，才能保存知识库。")

        if not uploaded_file and submitted:
            st.error("请先上传文件，再点击构建知识库。")

        if submitted1 and len([x for x in chatbot.get_vector_db()]) == 0:
            st.error("无可选的本地知识库。")

        if clear:
            if 'files' not in st.session_state:
                if "message" in st.session_state:
                    del st.session_state["messages"]
            else:
                st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]

        if clear_file:
            if 'files' in st.session_state:
                del st.session_state["files"]
            if 'messages' in st.session_state:
                del st.session_state["messages"]

        if uploaded_file and submitted:
            with st.spinner("Initializing vector db..."):
                files_name = []
                for i, item in enumerate(uploaded_file):
                    ext_name = os.path.splitext(item.name)[-1]
                    file_name = f"""./data/uploaded/{item.name}"""
                    with open(file_name, "wb") as f:
                        f.write(item.getbuffer())
                        f.close()
                    files_name.append(file_name)
                chatbot.init_vector_db_from_documents(files_name)
                if 'files' in st.session_state:
                    st.session_state['files'] = st.session_state['files'] + files_name
                else:
                    st.session_state['files'] = files_name

                st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]
                st.success('知识库添加完成！', icon='🎉')
                st.balloons()

        if submitted2 and 'files' in st.session_state:
            chatbot.save_vector_db_to_local()
            st.success('知识库保存成功！', icon='🎉')

        if submitted1 and option:
            chatbot.load_vector_db_from_local(option)
            st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]
            st.success('知识库导入完成！', icon='🎉')
            st.session_state['files'] = option.split(", ")
            st.balloons()

    if 'files' in st.session_state:
        st.markdown("\n".join([str(i + 1) + ". " + x.split("/")[-1] for i, x in enumerate(st.session_state.files)]))

if 'messages' in st.session_state:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input():
    if 'files' not in st.session_state:
        his = cut_history(user_input)
        if 'messages' not in st.session_state:
            st.session_state["messages"] = [{"role": "user", "content": user_input}]
        else:
            st.session_state["messages"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant"):
            answer_container = st.empty()
            # for result_answer, _ in stream_predict(user_input, his):
            for result_answer, _ in chatbot.llm.stream_predict(user_input, his):
                answer_container.markdown(result_answer)
        st.session_state["messages"].append({"role": "assistant", "content": result_answer})
    else:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant"):
            answer_container = st.empty()

            docs = chatbot.query_from_doc(user_input, 3)
            refer = "\n".join([x.page_content.replace("\n", '\t') for x in docs])
            PROMPT = """{}\n请根据下面的参考文档回答上述问题。\n{}\n"""
            prompt = PROMPT.format(user_input, refer)

            # for result_answer, _ in stream_predict(user_input, []):
            for result_answer, _ in chatbot.llm.stream_predict(prompt, []):
                answer_container.markdown(result_answer)

            with st.expander("References"):
                for i, doc in enumerate(docs):
                    source_str = os.path.basename(doc.metadata["source"]) if "source" in doc.metadata else ""
                    page_str = doc.metadata['page'] + 1 if "page" in doc.metadata else ""
                    st.write(f"""### Reference [{i + 1}] {source_str} P{page_str}""")
                    st.write(doc.page_content)
                    i += 1

        st.session_state["messages"].append({"role": "assistant", "content": result_answer})
