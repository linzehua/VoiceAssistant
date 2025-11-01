import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__)) +'/../'
sys.path.append(cur_dir)

from frontend.speech_wakeup import WakeupWordDetector
from frontend.voice_cache import VoiceCache
from frontend.vad_recorder import VADRecorder
import requests
import uuid
import winsound
import base64
import time

CONFIG = {
    "wakeup_word":'你好',
    "server_api": "http://127.0.0.1:5000/process_audio",
}

class Client:

    def __init__(self, config):
        self.config = config
        self.cache = VoiceCache()
        self.detector = WakeupWordDetector(wakeup_word=config['wakeup_word'])
        self.vad_recorder = VADRecorder(
            sample_rate=16000,
            chunk_size=512,
            vad_aggressiveness=2,  # VAD敏感度
            silence_timeout=1.5,   # 静音超时1.5秒
            max_record_duration=10, # 最大录音10秒
            pre_record_duration=1.0 # 预录音1秒
        )

    def start(self):
        self.cache.start()

        while True:
            audio = self.cache.get_audio(duration=2)
            if self.detector.detect(audio):
                print("检测到：======= ", self.detector.wakeup_word)
                self.cache.stop()
                session_id = ""
                audio_data, success = self.vad_recorder.record()

                while success:  # 多轮对话直到用户不说话了
                    session_id, resp_text, resp_wav = self.serve(audio_data, session_id)
                    if len(resp_wav) > 0:
                        print(f"{session_id} resp_text: {resp_text}")
                        # 播放
                        tmp_out_wav_file = f"{str(uuid.uuid4())}.wav"
                        with open(tmp_out_wav_file, "wb") as f:
                            f.write(resp_wav)
                        winsound.PlaySound(tmp_out_wav_file, winsound.SND_FILENAME)
                        if os.path.exists(tmp_out_wav_file):
                            os.remove(tmp_out_wav_file)

                    audio_data, success = self.vad_recorder.record()


                self.cache.start()
            else:
                time.sleep(1)


    def stop(self):
        self.cache.stop()

    def serve(self, audio_data, session_id):
        # 将音频数据编码为base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # 构造JSON数据
        payload = {
            'session_id': session_id,
            'audio_data': audio_base64,
            'audio_format': 'wav'  # 可选的元数据
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.config['server_api'], json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            text = result['text']
            audio_base64 = result['audio_data']
            session_id = result['session_id']

            # 解码音频数据
            response_wav = base64.b64decode(audio_base64)

            if len(response_wav) == 0:
                print(f"empty response from server")

            return session_id, text, response_wav

        else:
            print(f"server response from server: {response.status_code}")
            return session_id, "", b""


if __name__ == '__main__':
    client = Client(CONFIG)
    client.start()