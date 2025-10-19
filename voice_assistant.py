# 级联方案语音助手
from  speech_record import record_audio
from speech_recognition import recognize_speech
from language_model import  llm_answer
from text_to_speech import  tts
from playsound import playsound

def voice_assistant(configs):
    tmp_wav_file = "user.wav"
    # # 录音
    # record_audio(tmp_wav_file, duration=10)
    # 语音转文字
    user_text = recognize_speech(tmp_wav_file)
    print("user:", user_text)

    # 语言模型回答
    bot_text = llm_answer(user_text, configs['deepseek_key'])
    print("bot:", bot_text)

    # 语音合成
    tmp_out_wav_file = "bot.wav"
    tts(bot_text, tmp_out_wav_file)

    # 播放
    playsound(tmp_out_wav_file)

    # 临时文件删掉

if __name__ == '__main__':
    import  sys, json
    config_file = sys.argv[1]
    configs = json.load(open(config_file))
    voice_assistant(configs)

    # 假设添加语音唤醒
    # while True:
    #     if speech_wakeup():
    #         voice_assistant()
    #
    #     time.sleep(2)
