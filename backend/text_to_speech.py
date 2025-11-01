# 离线语音合成模块，输入文本，输出 wav 文件


import pyttsx3  # https://pypi.org/project/pyttsx3/
import uuid
import os

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()

    def __call__(self, text):
        tmp_wav_path = f"{str(uuid.uuid4())}.wav"
        self.engine.save_to_file(text, tmp_wav_path)
        self.engine.runAndWait()
        if os.path.exists(tmp_wav_path):
            wav_bytes = open(tmp_wav_path, "rb").read()
            os.remove(tmp_wav_path)
        else:
            wav_bytes = None
        return wav_bytes

if __name__ == '__main__':
    tts('今天天气怎么样？', '../user.wav')
