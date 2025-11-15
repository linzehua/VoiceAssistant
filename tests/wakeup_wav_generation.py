#coding=utf-8
import os, sys, json
cur_dir = os.path.dirname(os.path.abspath(__file__)) +'/../'
sys.path.append(cur_dir)
from tqdm import tqdm
from backend.text_to_speech import TTSDoubao

def tts(config, text, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    tts = TTSDoubao(config)
    N = 1
    for i in tqdm(range(N)):
        wav_bytes = tts(text)
        if not wav_bytes:
            print(f"failed to generate wav for {i}")
            continue

        out_name = f"{out_dir}/bwk_{i:03d}.wav"  # 格式化输出, :.2f
        with open(out_name, "wb") as f:
            f.write(wav_bytes)

if __name__ == "__main__":
    text = '小爱同学'
    config = json.load(open(f"{cur_dir}/backend/config_keys.json"))
    tts(config, text, out_dir="./recordings/wakeup/testset100")