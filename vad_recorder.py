import pyaudio
import webrtcvad
import threading
import time
from collections import deque


class VADRecorder:
    """
    VAD语音活动检测录音类 - 负责检测语音开始和结束
    """

    def __init__(self, sample_rate=16000, chunk_size=512, vad_aggressiveness=2):
        """
        初始化VAD录音器

        Args:
            sample_rate: 采样率(必须为8000,16000,32000)
            chunk_size: 数据块大小
            vad_aggressiveness: VAD敏感度(1-3)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_recording = False
        self.audio_data = b''

        # 初始化VAD
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(vad_aggressiveness)

        # VAD参数
        self.vad_frame_duration = 30  # 30ms帧
        self.vad_frame_size = int(sample_rate * self.vad_frame_duration / 1000)

        # 录音参数
        self.silence_timeout = 2.0  # 静音超时
        self.max_recording_duration = 10.0  # 最大录音时长

        # 状态跟踪
        self.last_voice_time = 0
        self.recording_start_time = 0
        self.consecutive_silence_frames = 0
        self.consecutive_voice_frames = 0

        # 音频流
        self.audio = pyaudio.PyAudio()
        self.stream = None

        # 回调函数
        self.on_recording_start = None
        self.on_recording_end = None
        self.on_audio_data = None

    def start_recording(self, pre_record_duration=1.0, audio_cache=None):
        """
        开始录音

        Args:
            pre_record_duration: 预录音时长(秒)
            audio_cache: AudioCache实例，用于获取预录音数据
        """
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = b''
        self.last_voice_time = time.time()
        self.recording_start_time = time.time()
        self.consecutive_silence_frames = 0
        self.consecutive_voice_frames = 0

        # 获取预录音数据
        if audio_cache and pre_record_duration > 0:
            pre_recorded_audio, _ = audio_cache.get_recent_audio(pre_record_duration)
            self.audio_data = pre_recorded_audio

        # 打开音频流
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        # 触发开始回调
        if self.on_recording_start:
            self.on_recording_start()

        # 开始录音线程
        self.recording_thread = threading.Thread(target=self._record_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def _record_loop(self):
        """录音主循环"""
        print("VAD录音开始...")

        try:
            while self.is_recording:
                # 检查超时
                current_time = time.time()
                if (current_time - self.recording_start_time) > self.max_recording_duration:
                    print("达到最大录音时长，停止录音")
                    break

                # 读取音频数据
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data += data

                # VAD检测
                has_speech = self._vad_detect_speech(data)

                if has_speech:
                    self.last_voice_time = current_time
                    self.consecutive_voice_frames += 1
                    self.consecutive_silence_frames = 0
                else:
                    self.consecutive_silence_frames += 1
                    self.consecutive_voice_frames = 0

                # 检查语音结束条件
                if (self.consecutive_voice_frames > 0 and
                        self.consecutive_silence_frames > int(self.silence_timeout * 1000 / self.vad_frame_duration)):
                    print("检测到语音结束")
                    break

                # 实时回调
                if self.on_audio_data:
                    self.on_audio_data(data, has_speech)

        except Exception as e:
            print(f"录音错误: {e}")
        finally:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            # 触发结束回调
            if self.on_recording_end:
                self.on_recording_end(self.audio_data)

        print("VAD录音结束")

    def _vad_detect_speech(self, audio_data):
        """
        使用VAD检测语音活动

        Args:
            audio_data: 音频数据

        Returns:
            bool: 是否检测到语音
        """
        # 确保数据长度正确
        if len(audio_data) < self.vad_frame_size * 2:  # 16bit = 2字节
            return False

        try:
            # 检测每个VAD帧
            for i in range(0, len(audio_data) - self.vad_frame_size * 2, self.vad_frame_size * 2):
                frame = audio_data[i:i + self.vad_frame_size * 2]
                if len(frame) == self.vad_frame_size * 2:
                    if self.vad.is_speech(frame, self.sample_rate):
                        return True
        except:
            pass

        return False

    def get_audio_data(self):
        """获取录音数据"""
        return self.audio_data

    def set_callbacks(self, on_start=None, on_end=None, on_data=None):
        """设置回调函数"""
        self.on_recording_start = on_start
        self.on_recording_end = on_end
        self.on_audio_data = on_data


if __name__ == "__main__":
    recorder = VADRecorder()
    recorder.start_recording()
    recorder.stop_recording()

    audio_data = recorder.get_audio_data()
    import numpy as np
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    print(audio_data)
