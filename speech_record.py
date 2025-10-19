# 实现录音，保存成 wav 格式的文件

import sounddevice as sd
import soundfile as sf
import numpy as np


def record_audio(filename, duration=5, samplerate=44100, channels=1):
    """
    录制音频并保存为 WAV 文件

    Args:
        filename: 保存的文件名
        duration: 录制时长（秒）
        samplerate: 采样率
        channels: 声道数（1=单声道，2=立体声）
    """
    print("开始录音...")

    # 录制音频
    audio_data = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=channels,
        dtype='float32'
    )

    # 等待录音完成
    sd.wait()

    print("录音完成，正在保存文件...")

    # 保存为 WAV 文件
    sf.write(filename, audio_data, samplerate)

    print(f"文件已保存: {filename}")


# 使用示例
if __name__ == "__main__":
    record_audio("recording.wav", duration=5)