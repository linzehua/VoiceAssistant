import uuid

from backend.speech_recognition import SpeechRecognizer
from backend.language_model import LLMModel
from backend.text_to_speech import TTS


class Session:
    def __init__(self, config):
        self.session_id = str(uuid.uuid4())
        self.asr = SpeechRecognizer()
        self.config = config
        self.llm = LLMModel(config['deepseek_key'])
        self.tts = TTS()

        self.context = []  # 给 llm 准备的多轮对话用的

    def __call__(self, use_wav_bytes):
        try:
            user_text = self.asr(use_wav_bytes)
            self.context.append({"role": "user", "content": user_text})
            print(self.context)
            response_text = self.llm(messages=self.context)
            response_wav_bytes = self.tts(response_text)
            self.context.append(
                {"role": "assistant", "content": response_text}
            )
        except Exception as e:
            print(e)
            return "", b""

        return response_text, response_wav_bytes


