from typing import Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict,messages_from_dict
import json
import os
class FileChatHistory(BaseChatMessageHistory):

    def __init__(self,session_id,storage_path) -> None:
        self.session_id=session_id
        self.storage_path=storage_path
        self.file_path=os.path.join(self.storage_path,self.session_id)
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        if self.messages is not None:
            all_mess=list(self.messages)
        all_mess.extend(messages)

        new_mess=[]
        for mess in all_mess:
            new_mess.append(message_to_dict(mess))

        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_mess,f)
    @property
    def messages(self)->list[BaseMessage]|None:
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                messages_data=json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
    def clear(self):
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)

session_set={}
def get_history(user_id):
    if not user_id in session_set:
        session_set[user_id]=FileChatHistory(user_id,'./长期记忆储存')
    return session_set[user_id]