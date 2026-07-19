from vector_storage import VectorStorage
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder  
from langchain_core.runnables.history import RunnableWithMessageHistory 
from config import Config
from langchain_core.runnables import RunnablePassthrough,RunnableConfig,RunnableLambda
from typing import List
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from typing import Sequence,Dict,Any
from filechathistory import FileChatHistory,get_history,session_set
from dotenv import load_dotenv
load_dotenv()

def format_for_retri(dic):
    print(dic)
    return dic["input"]

def format_for_chat_template(dic)->Dict[str,Any]:
    new_dic={}
    new_dic["input"]=dic["input"]["input"]
    new_dic["history"]=dic["input"]["history"]
    new_dic["guidance"]=dic["guidance"]
    #print(dic)
    return new_dic
class BaseRagService():
    #构建可执行rag_chain
    #实现本地数据与用户输入间的连接
    
    def __init__(self,config:Config|None=None) -> None:
        self.vector_storage=VectorStorage().get_retriever()
        
        self.chat_model=config.chat_model if config and config.chat_model else ChatDeepSeek(model="deepseek-v4-flash")

        self.chat_template=ChatPromptTemplate.from_messages(
            [("system","Task:你需要根据优先基于所提供的所提供的参考资料回答用户问题，只有当参考资料无法解决问题时，才可使用预训练阶段及外部知识"),
            ("system","参考资料：{guidance}"),
            ('system','对话历史记录:{history}'),
            ('human',"question:{input}")]
        )

        self.chain=self.get_chain()
    def format_func(self,docs:List[Document]):
        content=''
        for doc in docs:
            content+=doc.page_content+'\n'
        return content
    
    def prompt_show(self,prompt):
        print('='*20)
        print(prompt.to_string())
        print('='*20)
        print('\n')
        return prompt            
    def get_chain(self):
        chain=(
            {'input':RunnablePassthrough(),
             'guidance':format_for_retri|self.vector_storage|self.format_func
             }|RunnableLambda(format_for_chat_template)|self.chat_template|self.prompt_show|self.chat_model|StrOutputParser()
        )
        mem_func_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            history_messages_key='history',
            input_messages_key='input',
        )
        return mem_func_chain
    
if __name__=='__main__':
    config:RunnableConfig={"configurable":{"session_id":"user_0001"}}
    test_obj=BaseRagService()
    chain=test_obj.get_chain()
    res=chain.invoke({'input':'告诉我符号主义是什么？'},config=config)
    print(res)
