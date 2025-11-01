# 语言模型模块，回答用户文本问题，输出回复文本

# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
SP = "你叫小爱同学，你是一个智能语音助手，可以回答我的问题"

class LLMModel:
    def __init__(self, access_key):
        self.client = OpenAI(
            api_key=access_key,
            base_url="https://api.deepseek.com"
        )
        self.sp = SP

    def __call__(self, messages):
        """
        :param messages: list, 历史对话和新的 user_text
        :return:
        """

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.sp},
            ] + messages,
            stream=False
        )

        reponse_text = response.choices[0].message.content

        return reponse_text

if __name__ == '__main__':
    llm = LLMModel("")
    response_text = llm('你叫什么？')
    print(response_text)