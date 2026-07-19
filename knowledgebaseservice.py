import os
import hashlib
from dotenv import load_dotenv
load_dotenv()
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime
from config import Config

def check_md5(md5_str:str,config:Config=Config(),encoding:str='utf-8'):
    if not os.path.exists(config.md5_path):
        with open(config.md5_path,'w',encoding=encoding) as f:
            return False
    else:
        with open(config.md5_path,'r',encoding=encoding) as f:
            md5_str=md5_str.strip()
            for line in f.readlines():
                if md5_str==line:
                    return True
            else:
                return False    
def save_md5(md5_str:str,config:Config=Config(),encoding:str='utf-8'):
    #不检测md5_str是否已经被储存过，提高程序效率，灵活性和模块化特点
    with open(config.md5_path,'a',encoding=encoding) as f:
        f.write(md5_str+'\n')
    return
def trans_md5(string:str,encoding:str='utf-8'):
    str_bytes=string.encode(encoding)

    encoder=hashlib.md5()
    encoder.update(str_bytes)
    return encoder.hexdigest()

class KnowledgeBaseService(object):
    def __init__(self,config:Config=Config()) -> None:
        self.config=config
        path = config.chroma_path if config is not None else os.getenv("CHROMA_PATH", "")
        if not path:
            raise ValueError("你必须给定KnowledgeBaseService一个指定地址（设置 CHROMA_PATH 环境变量或传入 Config）")
        os.makedirs(path, exist_ok=True)
        self.chroma=Chroma(
            collection_name="RAG_usage",
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory if config is not None else os.getenv("PERSIST_DIRECTORY",'') )
        self.split=RecursiveCharacterTextSplitter(
            chunk_size=55,
            chunk_overlap=20,
            separators=config.split_separators if config is not None else None,
            length_function=len,
        )
    def up_load_by_str(self,string:str,file_name:str,encoding:str='utf-8'):
        tran_string=trans_md5(string)
        if check_md5(tran_string,self.config):
            #已储存该字符串
            return("[该字符串已储存]")
        save_md5(tran_string,self.config)    
        if len(string) < 50:
            storage_list=[string]
        else:
            storage_list=self.split.split_text(string)
        metadatas={"source":file_name or None,"timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.chroma.add_texts(storage_list,metadatas=[metadatas for _ in storage_list])
        return("[储存成功]")

if __name__=='__main__':
    test=KnowledgeBaseService()
    str_1=test.up_load_by_str(string="人工智能的起源可追溯到 1950 年，艾伦·图灵在其论文《计算机器与智能》中提出“图灵测试”，用以判断机器是否具备智能。1956 年，约翰·麦卡锡在达特茅斯会议上正式命名“人工智能”学科，早期研究以符号主义为主导，通过逻辑推理和知识表示解决问题，代表性成果包括纽厄尔和司马贺的“逻辑理论家”程序（1956）以及通用问题求解器（1957）。然而，受限于计算能力和数据规模，符号主义在 1970 年代遭遇瓶颈，实际应用难以突破简单任务，导致第一次 AI 寒冬。这一时期的关键技术包括搜索算法、谓词逻辑和知识库，但缺乏自适应学习能力，为后续的统计学习埋下伏笔。",file_name='doc1_early_ai.txt')
    str_2=test.up_load_by_str(string="1980 年代后，机器学习逐渐取代纯符号主义，强调从数据中自动发现规律。支持向量机（SVM）和随机森林等统计方法在分类任务上表现优异，但特征工程仍依赖人工。2006 年，杰弗里·辛顿提出深度信念网络，标志着深度学习复兴；2012 年，AlexNet 在 ImageNet 竞赛中以 84.6% 的 top-5 准确率夺冠（远超第二名 74.2%），引发神经网络热潮。2017 年，Vaswani 等人提出 Transformer 架构，摒弃循环网络，引入自注意力机制，成为自然语言处理的里程碑。相比早期符号主义的手工规则，深度网络能够端到端学习，但需要海量数据和算力。ImageNet 数据集包含 1400 万张标注图像，而 Transformer 的训练则依赖数 TB 的文本语料，这为后续大模型铺平了道路。",file_name='doc2_ml_deeplearning.txt')
    print(str_1)
    print(str_2)