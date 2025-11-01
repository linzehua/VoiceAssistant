# 持续监听语音，并缓存
import threading
# import sounddevice as sd
import pyaudio
import numpy as np
import time


class VoiceCache:
    def __init__(self, cache_duration=10, sample_rate=16000):
        self.cache_duration = cache_duration
        self.sample_rate = sample_rate
        self.max_cache_len = int(self.cache_duration * self.sample_rate)

        self.cache = np.array([], dtype=np.int16)

        self.lock = threading.Lock()

        # 录音模块
        self.is_running = False


    def cache_audio(self):
        """
        :return:
        """

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        while self.is_running:
            try:
                audio_data = stream.read(1024, exception_on_overflow=False)
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                with self.lock:
                    self.cache  = np.concatenate((self.cache, audio_np))
                    # print("cache", self.cache.shape)
                    if len(self.cache) >= self.max_cache_len:
                        self.cache = self.cache[-self.max_cache_len:]
                time.sleep(0.01)
            except Exception as e:
                print(e)
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.cache_audio)
        self.thread.daemon = False
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.cache = np.array([], dtype=np.int16)



    def get_audio(self, duration):
        """
        获取最新的 duration 时长的语音
        :param duration: int 秒
        :return:
        """
        dura_len = int(duration * self.sample_rate)
        # print("dura_len", dura_len, self.cache.shape)
        with self.lock:
            audio_np = self.cache[-dura_len:] # 最新的数据
        # 转成 bytes
        audio_data = audio_np.tobytes()
        return audio_data


if __name__ == '__main__':
    from utils.wav_utils import save_to_wav
    cache = VoiceCache()
    cache.start()

    for i in range(3):
        time.sleep(5)
        audio_data = cache.get_audio(5)
        print(len(audio_data))
        save_to_wav(audio_data, f'test_cache_{i}.wav')

    cache.stop()

