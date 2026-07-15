import os
import hashlib
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime
def check_md5(md5_str:str,encoding:str='utf-8'):
    if not os.path.exists(os.getenv("MD5_TXT", "")):
        with open(os.getenv("MD5_TXT",''),'w',encoding=encoding) as f:
            return False
    else:
        with open(os.getenv("MD5_TXT",''),'r',encoding=encoding) as f:
            md5_str=md5_str.strip()
            for line in f.readlines():
                if md5_str==line:
                    return True
            else:
                return False    
def save_md5(md5_str:str,encoding:str='utf-8'):
    #不检测md5_str是否已经被储存过，提高程序效率，灵活性和模块化特点
    with open(os.getenv("MD5_TXT",''),'a',encoding=encoding) as f:
        f.write(md5_str+'\n')
    return
def trans_md5(string:str,encoding:str='utf-8'):
    str_bytes=string.encode(encoding)

    encoder=hashlib.md5()
    encoder.update(str_bytes)
    return encoder.hexdigest()

class KnowledgeBaseService(object):
    def __init__(self,config=None) -> None:
        path=config.get_chroma_path if config is not None else os.getenv("CHROMA_PATH","")
        if config.get_chroma_path if config is not None else os.getenv("CHROMA_PATH",""):
            raise ValueError("你必须给定KnowledgeBaseService一个指定地址")
        else:
            os.makedirs(path,exist_ok=True)
        self.chroma=Chroma(
            collection_name="RAG_usage",
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.get_chroma_path if config is not None else os.getenv("CHROMA_PATH",""),
        )
        self.split=RecursiveCharacterTextSplitter(
            chunk_size=40,
            chunk_overlap=10,
            separators=config.split_separators if config is not None else os.getenv("separators",[]),
            lenth_function=len,
        )
    def up_load_by_str(self,string:str,encoding:str='utf-8'):
        tran_string=trans_md5(string)
        if check_md5(tran_string):
            #已储存该字符串
            print("[该字符串已储存]")
            return
        if len(string) < 50:
            storage_list=[string]
        else:
            storage_list=self.split.split_text(string)
        metadatas={"source":config.source or None,"timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.chroma.add_texts(storage_list,metadatas=[metadatas for _ in storage_list])
        print("[储存成功]")
