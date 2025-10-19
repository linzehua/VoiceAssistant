# 语音转文字模块
import whisper
import opencc

def recognize_speech(wav_file):
    # 加载模型
    model = whisper.load_model("base")
    # 转录音频文件
    result = model.transcribe(wav_file, fp16=False)
    # 繁體轉簡體
    cc = opencc.OpenCC("t2s")
    simplified_text = cc.convert(result['text'])
    return simplified_text


if __name__ == '__main__':
    wav_file = 'user.wav'
    text = recognize_speech(wav_file)
    print("识别结果为：", text)