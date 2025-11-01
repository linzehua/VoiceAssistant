#这是一个语音唤醒词检测模块: 通过语音识别来实现
# RTF: 实时率   real time factor  = 处理 1 s 语音的耗时 / 1s
# 如果 RTF <=1, 那么系统就是实时的

import whisper
import opencc
import numpy as np

class WakeupWordDetector:

    def __init__(self, wakeup_word='九五二七'):
        # 加载模型
        self.model = whisper.load_model("base")
        self.wakeup_word = wakeup_word


    def detect(self, audio_data):
        audio_data = np.frombuffer(audio_data, np.int16) / 32768.0
        audio_data = audio_data.astype(np.float32) #.reshape(-1, 1)
        # print(audio_data.max(), audio_data.min(), len(audio_data), audio_data.shape)

        result = self.model.transcribe(audio_data, fp16=False)
        print(result)
        # 繁體轉簡體
        cc = opencc.OpenCC("t2s")
        simplified_text = cc.convert(result['text'])
        return self.wakeup_word in simplified_text
        # return len(simplified_text) > 0

if __name__ == "__main__":
    from voice_cache import VoiceCache, save_to_wav
    cache = VoiceCache()
    cache.start()
    import time
    time.sleep(5)
    print("start")
    detector = WakeupWordDetector(wakeup_word='小爱同学')
    while True:
        audio = cache.get_audio(duration=3)
        # save_to_wav(audio, 'testwk.wav')
        if detector.detect(audio):
            print("检测到：======= ", detector.wakeup_word)

            # 启动后续的语音助手交互流程
        else:
            print("未检测到")

        time.sleep(2)
