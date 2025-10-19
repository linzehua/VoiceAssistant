
import  os, wave
import soundfile as sf
import numpy as np
import librosa

def load_audio(wav_path):
    wav, sr = sf.read(wav_path)  # 返回的 wav 取值范围是 (-1, 1) 归一化过了
    wav = wav.astype(np.float32)
    return wav, sr

def load_wav_tobytes(wav_path):
    wav, sr = sf.read(wav_path)
    wav = wav * 32767
    wav = wav.astype(np.int16)
    return wav.tobytes()

# 重采样
def wav_resample(wav, ori_sr, new_sr):
    """
    使用librosa对音频文件进行重采样。

    参数:
        wav (ndarray): 读取的音频。
        sr (int): 输入采样率。
        target_sr (int): 目标采样率（单位：Hz）。
    """

    # 执行重采样
    y_resampled = librosa.resample(wav, orig_sr=ori_sr, target_sr=new_sr)
    return y_resampled.astype(np.float32)


def save_to_wav(audio_data, filename, output_dir="recordings", sample_rate=16000):
    """
    保存音频数据为WAV文件 [6,8](@ref)

    Args:
        audio_data: 音频数据
        filename: 文件名
        output_dir: 输出目录

    Returns:
        str: 保存的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)

    if not filename.endswith('.wav'):
        filename += '.wav'

    filepath = os.path.join(output_dir, filename)

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

    print(f"音频已保存: {filepath}")
    return filepath
