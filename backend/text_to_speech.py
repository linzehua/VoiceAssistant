# 离线语音合成模块，输入文本，输出 wav 文件


import pyttsx3  # https://pypi.org/project/pyttsx3/
import uuid
import os
import logging
import websockets
import json
import asyncio
import random

import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cur_dir)
from protocols import MsgType, full_client_request, receive_message

class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()

    def __call__(self, text):
        tmp_wav_path = f"{str(uuid.uuid4())}.wav"
        self.engine.save_to_file(text, tmp_wav_path)
        self.engine.runAndWait()
        if os.path.exists(tmp_wav_path):
            wav_bytes = open(tmp_wav_path, "rb").read()
            os.remove(tmp_wav_path)
        else:
            wav_bytes = None
        return wav_bytes



def get_cluster(voice: str) -> str:
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"

VoiceTypeList = [
    'zh_male_lengkugege_emo_v2_mars_bigtts',
    'zh_female_tianxinxiaomei_emo_v2_mars_bigtts',
    'zh_female_gaolengyujie_emo_v2_mars_bigtts',
    'zh_male_aojiaobazong_emo_v2_mars_bigtts',
    'zh_male_yourougongzi_emo_v2_mars_bigtts'
]


class TTSDoubao:
    def __init__(self, config):
        self.appid = config["appid"]
        self.access_token = config["access_token"]
        # self.voice_type = config["voice_type"]
        self.endpoint = config["endpoint"]
        self.encoding = 'wav'

    def __call__(self, text):
        voice_type = random.choice(VoiceTypeList)  # 随机选一个音色

        self.cluster = get_cluster(voice_type)
        print(voice_type)
        tmp_file = f"{str(uuid.uuid4())}.wav"
        asyncio.run(self.generate(text, voice_type, tmp_file))
        if os.path.exists(tmp_file):
            wav_bytes = open(tmp_file, "rb").read()
            os.remove(tmp_file)
        else:
            wav_bytes = None
        return wav_bytes


    async def generate(self, text, voice_type, filename):

        # Connect to server
        headers = {
            "Authorization": f"Bearer;{self.access_token}",
        }

        logging.info(f"Connecting to {self.endpoint} with headers: {headers}")
        websocket = await websockets.connect(
            self.endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
        )
        logging.info(
            f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
        )

        try:
            # Prepare request payload
            request = {
                "app": {
                    "appid": self.appid,
                    "token": self.access_token,
                    "cluster": self.cluster,
                },
                "user": {
                    "uid": str(uuid.uuid4()),
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": self.encoding,
                    "speed_ratio": random.uniform(0.8, 1.5),
                    "loudness_ratio": random.uniform(0.8, 1.5),
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "operation": "submit",
                    "with_timestamp": "1",
                    "extra_param": json.dumps(
                        {
                            "disable_markdown_filter": False,
                        }
                    ),
                },
            }

            # Send request
            await full_client_request(websocket, json.dumps(request).encode())

            # Receive audio data
            audio_data = bytearray()
            while True:
                msg = await receive_message(websocket)

                if msg.type == MsgType.FrontEndResultServer:
                    continue
                elif msg.type == MsgType.AudioOnlyServer:
                    audio_data.extend(msg.payload)
                    if msg.sequence < 0:  # Last message
                        break
                else:
                    raise RuntimeError(f"TTS conversion failed: {msg}")

            # Check if we received any audio data
            if not audio_data:
                raise RuntimeError("No audio data received")

            # Save audio file
            if filename == "":
                filename = f"{self.voice_type}.{self.encoding}"
            with open(filename, "wb") as f:
                f.write(audio_data)
            logging.info(f"Audio received: {len(audio_data)}, saved to {filename}")

        finally:
            await websocket.close()
            logging.info("Connection closed")


if __name__ == '__main__':
    tts('今天天气怎么样？', '../user.wav')
