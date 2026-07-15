#基于streamlit实现web文件传输功能
import streamlit as st

st.header("知识库更新服务")

get_file=st.file_uploader(
    label="本地文件上传",
    type=['txt','json','jsonl'],
    accept_multiple_files=False,
)

if get_file is not None:
    file_name=get_file.name
    file_type=get_file.type
    file_size=get_file.size/1024
    file_content=get_file.getvalue().decode("utf-8")
    st.subheader(f"文件名：{file_name}")
    st.write(f"文件类型：{file_type}|文件预览：{file_content}")
