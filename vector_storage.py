import os

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

from config import Config
#向量检索功能
"""
    为后续链条chain的构建提供向量检索
"""

class VectorStorage(object):
    def __init__(self, config: Config | None = None) -> None:
        self.database=Chroma(
            #暂时硬编码，后续完成config类和完善.env后再做优化
            embedding_function=DashScopeEmbeddings(
                model="text-embedding-v4"
            ),
            collection_name="RAG_usage",
            persist_directory=config.persist_directory if config and config.persist_directory else os.getenv("PERSIST_DIRECTORY", ""),
        )
    def get_retriever(self):
        #提供快速入链的功能
        #由Chroma类型转化为了基于父类runable的子类
        return self.database.as_retriever(search_kwargs={"k":2})