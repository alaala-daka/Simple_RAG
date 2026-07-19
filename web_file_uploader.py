#基于streamlit实现web文件传输功能
import streamlit as st
from knowledgebaseservice import KnowledgeBaseService

st.header("知识库更新服务")

if not st.session_state["service"]:
    st.session_state["service"]=KnowledgeBaseService()

get_file=st.file_uploader(
    label="本地文件上传",
    type=['txt'],
    accept_multiple_files=False,
)

if get_file is not None:
    file_name=get_file.name
    file_type=get_file.type
    file_size=get_file.size/1024
    file_content=get_file.getvalue().decode("utf-8")
    st.subheader(f"文件名：{file_name}")
    st.write(f"文件类型：{file_type}|文件预览：{file_content}")
    with st.spinner(text="Witing to up_load"):
        st.write(st.session_state["service"].up_load_by_str(file_content,file_name))
