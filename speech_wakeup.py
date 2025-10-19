#这是一个语音唤醒词检测模块: 通过语音识别来实现
# RTF: 实时率   real time factor  = 处理 1 s 语音的耗时 / 1s
# 如果 RTF <=1, 那么系统就是实时的

import whisper
import opencc
import numpy as np

class WakeupWordDetector:

    def __init__(self, wakeup_word='九五二七'):
        # 加载模型
        self.model = whisper.load_model("tiny")
        self.wakeup_word = wakeup_word


    def detect(self, audio_data):
        audio_data = np.array(audio_data) / 32768.0
        audio_data = audio_data.astype(np.float32)

        text = self.model.transcribe(audio_data, fp16=False)
        return self.wakeup_word in text


if __name__ == "__main__":
    from voice_cache import VoiceCache
    cache = VoiceCache()
    cache.start()
    import time
    while True:
        detector = WakeupWordDetector(wakeup_word='小爱同学')
        audio = cache.get_audio(duration=2)
        if detector.detect(audio):
            print(detector.wakeup_word)

            # 启动后续的语音助手交互流程
        else:
            print("未检测到")

            time.sleep(1)
