# 语音转文字模块
import whisper
import opencc
import numpy as np

class SpeechRecognizer:

    def __init__(self, model_type='base'):
        # 加载模型
        self.model = whisper.load_model(model_type)


    def __call__(self, audio_data):
        if type(audio_data) == bytes:
            audio_data = np.frombuffer(audio_data, np.int16) / 32768.0
            audio_data = audio_data.astype(np.float32)
        # print(audio_data.max(), audio_data.min(), len(audio_data), audio_data.shape)

        result = self.model.transcribe(audio_data, fp16=False)
        # print(result)
        # 繁體轉簡體
        cc = opencc.OpenCC("t2s")
        simplified_text = cc.convert(result['text'])
        return simplified_text

if __name__ == '__main__':
    from utils.wav_utils import wav_resample, load_audio
    wav_file = '../user.wav'
    wav, sr = load_audio(wav_file)
    wav = wav_resample(wav, sr, 16000)
    recognizer = SpeechRecognizer()
    text = recognizer(wav)  # 因为定义了 __call__ 函数，所以可以直接这样调用
    print("识别结果为：", text)