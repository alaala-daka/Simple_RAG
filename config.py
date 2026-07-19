import os
from dotenv import load_dotenv

import re
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
#可变配置设置管理类
#unfinished
class Config():
    def __init__(self,
                MODEL_API_KEY:str=os.getenv("MODEL_API_KEY",''),
                CHROMA_PATH:str=os.getenv("CHROMA_PATH",''),
                SPLIT_SEPA:list[str] | None=None ,
                PERSIST_DIRE:str=os.getenv("PERSIST_DIRECTORY",''),
                **kwargs
                ) -> None:
        self.model_api_key=MODEL_API_KEY
        self.get_chroma_path=CHROMA_PATH
        self.split_separators: list[str] | None = SPLIT_SEPA
        self.persist_directory=PERSIST_DIRE
        self.llm_model=kwargs.get("LLM_MODEL") or os.getenv("LLM_MODEL")
        self.chat_model=ChatOpenAI(
            name=self.recognize_chat_model(),
            api_key=SecretStr(self.model_api_key),
        )
    def recognize_chat_model(self):
        """根据 API Key 格式自动识别厂商并返回主流对话模型"""
        key = self.model_api_key
        if not key:
            return None

        # Anthropic: sk-ant-api03-xxx
        if re.match(r"sk-ant", key):
            #return "claude-sonnet-4-20250514"
            raise ValueError("目前不支持Anthropic协议")

        # OpenAI 新版项目 Key: sk-proj-xxx
        if re.match(r"sk-proj", key):
            return "gpt-4o"

        # OpenAI 服务账号: sk-svcacct-xxx
        if re.match(r"sk-svcacct", key):
            return "gpt-4o"

        # ZhipuAI GLM: 三段式带点号，如 xxx.yyyyyyyyyyyy
        if re.match(r"^\w+\.\w+", key):
            return "glm-4-plus"

        # Google Gemini: AIza 前缀
        if re.match(r"AIza", key):
            return "gemini-2.5-flash"

        # DeepSeek / 旧版 OpenAI / DashScope 等：通用 sk- 前缀
        if re.match(r"sk", key):
            return "deepseek-v4-flash"

        return None