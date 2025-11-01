# 级联方案语音助手
from backend.language_model import  llm_answer
from backend.text_to_speech import  tts
import time

from frontend.voice_cache import VoiceCache
from frontend.speech_wakeup import WakeupWordDetector
from frontend.vad_recorder import VADRecorder
from backend.speech_recognition import SpeechRecognizer
import winsound


def voice_assistant(configs):
    # 前端
    cache = VoiceCache()
    detector = WakeupWordDetector(wakeup_word='小爱同学')
    vad_recorder = VADRecorder(
        sample_rate=16000,
        chunk_size=512,
        vad_aggressiveness=2,  # VAD敏感度
        silence_timeout=1.5,   # 静音超时1.5秒
        max_record_duration=10, # 最大录音10秒
        pre_record_duration=1.0 # 预录音1秒
    )
    cache.start()

    asr_model = SpeechRecognizer()


    while True:
        audio = cache.get_audio(duration=2)
        if detector.detect(audio):
            print("检测到：======= ", detector.wakeup_word)

            # 启动后续的语音助手交互流程
            # 录音并返回数据
            audio_data, success = vad_recorder.record()

            if success:
                print("录音成功!")

                # 可以继续处理音频数据...
                # 例如传递给语音识别引擎

                # 语音转文字
                user_text = asr_model(audio_data)
                print("user:", user_text)

                # 语言模型回答
                bot_text = llm_answer(user_text, configs['deepseek_key'])
                print("bot:", bot_text)

                # 语音合成
                tmp_out_wav_file = "bot.wav"
                tts(bot_text, tmp_out_wav_file)

                # 播放
                # playsound(tmp_out_wav_file)
                winsound.PlaySound(tmp_out_wav_file, winsound.SND_FILENAME)
            else:
                print("录音失败或未检测到语音")

        else:
            print("未检测到")

            time.sleep(1)  # 暂停一秒


if __name__ == '__main__':
    import  sys, json
    if len(sys.argv) < 2:
        config_file = "backend/config_keys.json"
    else:
        config_file = sys.argv[1]
    configs = json.load(open(config_file))
    voice_assistant(configs)


    # 假设添加语音唤醒
    # while True:
    #     if speech_wakeup():
    #         voice_assistant()
    #
    #     time.sleep(2)
