# 语言模型模块，回答用户文本问题，输出回复文本

# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI


def llm_answer(user_text, access_key):
    client = OpenAI(
        api_key=access_key,
        base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你叫小爱同学，你是一个智能语音助手，可以回答我的问题"},
            {"role": "user", "content": user_text},
        ],
        stream=False
    )

    reponse_text = response.choices[0].message.content

    return reponse_text

if __name__ == '__main__':
    response_text = llm_answer('你叫什么？')
    print(response_text)