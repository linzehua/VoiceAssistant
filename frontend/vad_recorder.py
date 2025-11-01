import pyaudio
import webrtcvad
import time
from collections import deque
import numpy as np


class VADRecorder:
    """
    单线程阻塞式VAD语音活动检测录音类
    录音完成后直接返回语音数据
    """

    def __init__(self, sample_rate=16000, chunk_size=512, vad_aggressiveness=2,
                 silence_timeout=2.0, max_record_duration=10.0, pre_record_duration=1.0):
        """
        初始化VAD录音器

        Args:
            sample_rate: 采样率(必须为8000,16000,32000)
            chunk_size: 数据块大小
            vad_aggressiveness: VAD敏感度(1-3)
            silence_timeout: 静音超时时间(秒)
            max_record_duration: 最大录音时长(秒)
            pre_record_duration: 预录音时长(秒)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.silence_timeout = silence_timeout
        self.max_record_duration = max_record_duration
        self.pre_record_duration = pre_record_duration

        # 初始化VAD [1,3](@ref)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(vad_aggressiveness)

        # VAD参数
        self.vad_frame_duration = 30  # 30ms帧 [1](@ref)
        self.vad_frame_size = int(sample_rate * self.vad_frame_duration / 1000)

        # 音频流
        self.audio = pyaudio.PyAudio()
        self.stream = None

        # 状态变量
        self.is_recording = False
        self.audio_data = b''

    def record(self):
        """
        单线程阻塞式录音方法
        开始录音并阻塞直到录音完成，返回音频数据

        Returns:
            bytes: 录音数据(PCM格式)
            bool: 是否成功录音
        """
        print("开始VAD录音...")

        # 打开音频流 [6,8](@ref)
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        self.is_recording = True
        self.audio_data = b''

        # 状态跟踪变量
        last_voice_time = time.time()
        recording_start_time = time.time()
        consecutive_silence_frames = 0
        consecutive_voice_frames = 0
        has_speech = False

        # 预录音缓冲区（环形缓冲区）
        pre_record_buffer = deque(maxlen=int(self.pre_record_duration * self.sample_rate / self.chunk_size))

        try:
            while self.is_recording:
                # 检查最大录音时长
                current_time = time.time()
                if (current_time - recording_start_time) > self.max_record_duration:
                    print("达到最大录音时长，停止录音")
                    break

                # 读取音频数据
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)

                # 保存到预录音缓冲区
                pre_record_buffer.append(data)

                # VAD检测 [1,3](@ref)
                has_speech_now = self._vad_detect_speech(data)

                if has_speech_now:
                    # 检测到语音
                    if not has_speech:
                        print("检测到语音开始")
                        # 将预录音数据添加到正式录音中
                        for pre_data in pre_record_buffer:
                            self.audio_data += pre_data
                        pre_record_buffer.clear()
                        has_speech = True

                    last_voice_time = current_time
                    consecutive_voice_frames += 1
                    consecutive_silence_frames = 0
                    self.audio_data += data

                else:
                    # 静音
                    consecutive_silence_frames += 1
                    consecutive_voice_frames = 0

                    if has_speech:
                        # 已经在录音中，检查静音超时
                        silence_duration = current_time - last_voice_time
                        if silence_duration > self.silence_timeout:
                            print(f"检测到静音超时({silence_duration:.1f}s)，停止录音")
                            break
                        else:
                            # 仍在录音，继续添加数据
                            self.audio_data += data

        except Exception as e:
            print(f"录音错误: {e}")
            return None, False

        finally:
            # 清理资源
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

        # 检查是否录到了有效语音
        if has_speech and len(self.audio_data) > 0:
            duration = len(self.audio_data) / (self.sample_rate * 2)  # 16bit = 2字节
            print(f"录音完成，时长: {duration:.2f}秒，数据大小: {len(self.audio_data)}字节")
            return self.audio_data, True
        else:
            print("未检测到有效语音")
            return None, False

    def _vad_detect_speech(self, audio_data):
        """
        使用VAD检测语音活动 [1,3](@ref)

        Args:
            audio_data: 音频数据

        Returns:
            bool: 是否检测到语音
        """
        # 确保数据长度正确
        if len(audio_data) < self.vad_frame_size * 2:  # 16bit = 2字节
            return False

        speech_frames = 0
        total_frames = 0

        try:
            # 检测每个VAD帧
            for i in range(0, len(audio_data) - self.vad_frame_size * 2, self.vad_frame_size * 2):
                frame = audio_data[i:i + self.vad_frame_size * 2]
                if len(frame) == self.vad_frame_size * 2:
                    if self.vad.is_speech(frame, self.sample_rate):
                        speech_frames += 1
                    total_frames += 1
        except Exception as e:
            print(f"VAD检测错误: {e}")
            return False

        # 如果超过40%的帧检测到语音，则认为有语音活动 [3](@ref)
        if total_frames > 0 and speech_frames / total_frames > 0.4:
            return True

        return False

    def close(self):
        """释放资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

if __name__ == "__main__":# 创建录音器实例
    from utils.wav_utils import save_to_wav
    recorder = VADRecorder(
        sample_rate=16000,
        chunk_size=512,
        vad_aggressiveness=2,  # VAD敏感度
        silence_timeout=1.5,   # 静音超时1.5秒
        max_record_duration=10, # 最大录音10秒
        pre_record_duration=1.0 # 预录音1秒
    )

    try:
        print("准备开始录音，请说话...")
        print("检测到静音后会自动停止录音")

        # 方法1: 录音并返回数据
        audio_data, success = recorder.record()

        if success:
            print("录音成功!")

            # 保存文件
            filename = save_to_wav(audio_data, "my_recording.wav")
            print(f"文件已保存: {filename}")

            # 可以继续处理音频数据...
            # 例如传递给语音识别引擎
            audio_data = np.frombuffer(audio_data, dtype=np.int16)
            print(audio_data)

        else:
            print("录音失败或未检测到语音")

    except KeyboardInterrupt:
        print("用户中断录音")
    except Exception as e:
        print(f"录音过程中发生错误: {e}")
    finally:
        recorder.close()

