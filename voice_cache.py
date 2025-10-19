# 持续监听语音，并缓存
import threading
# import sounddevice as sd
import pyaudio


class VoiceCache:
    def __init__(self, cache_duration=10, sample_rate=16000, record_chunk_size=2):
        self.cache_duration = cache_duration
        self.sample_rate = sample_rate
        self.record_chunk_size = record_chunk_size
        self.max_cache_len = int(self.cache_duration * self.sample_rate)

        self.cache = []

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
                with self.lock:
                    audio_data = stream.read(1024, exception_on_overflow=False)
                    self.cache += list(audio_data)
                    if len(self.cache) >= self.max_cache_len:
                        self.cache = self.cache[-self.max_cache_len:]
                    time.sleep(0.01)
            except:
                break


    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.cache_audio)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_running = False



    def get_audio(self, duration):
        """
        获取最新的 duration 时长的语音
        :param duration: int 秒
        :return:
        """
        dura_len = int(duration * self.sample_rate)
        audio_data = self.cache[-dura_len:] # 最新的数据
        return audio_data


if __name__ == '__main__':
    cache = VoiceCache()
    cache.start()

    import time
    time.sleep(2)
    audio_data = cache.get_audio(1)
    print(len(audio_data))

    cache.stop()

