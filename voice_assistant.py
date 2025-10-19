# 级联方案语音助手
from  speech_record import record_audio
from speech_recognition import recognize_speech
from language_model import  llm_answer
from text_to_speech import  tts
from playsound import playsound
import time

from voice_cache import VoiceCache
from speech_wakeup import WakeupWordDetector
from vad_recorder import VADRecorder


def voice_assistant(configs):
    cache = VoiceCache()
    detector = WakeupWordDetector(wakeup_word='小爱同学')
    vad_recorder = VADRecorder()
    cache.start()

    while True:
        audio = cache.get_audio(duration=2)
        if detector.detect(audio):
            print(detector.wakeup_word)

            # 启动后续的语音助手交互流程
            # 录音
            vad_recorder.start_recording()
            vad_recorder.stop_recording()
            audio_data = vad_recorder.get_audio_data()

            # 语音转文字
            user_text = recognize_speech(audio_data)
            print("user:", user_text)

            # 语言模型回答
            bot_text = llm_answer(user_text, configs['deepseek_key'])
            print("bot:", bot_text)

            # 语音合成
            tmp_out_wav_file = "bot.wav"
            tts(bot_text, tmp_out_wav_file)

            # 播放
            playsound(tmp_out_wav_file)
        else:
            print("未检测到")

            time.sleep(1)  # 暂停一秒


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
