import os, sys
cur_dir = os.path.dirname(os.path.abspath(__file__)) +'/../'
sys.path.append(cur_dir)

from backend.session import Session
from flask import Flask, request, Response, jsonify, session
import logging
import json
import base64

cur_dir = os.path.dirname(os.path.realpath(__file__))

config = f"{cur_dir}/config_keys.json"
with open(config) as f:
    SESSION_CONFIG = json.load(f)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 使用一个强密钥，在生产环境中应从环境变量读取
app.secret_key = os.urandom(24)  # 或者一个固定的复杂字符串

# 配置音频参数
AUDIO_CONFIG = {
    'chunk_size': 1024,
    'format': 'int16',
    'channels': 1,
    'rate': 16000
}


SessionDict = {}

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """
    处理音频的主端点
    接收音频bytes数据，返回处理后的音频bytes数据
    """
    try:

        data = request.get_json()

        # 验证必需字段
        if not data or 'session_id' not in data or 'audio_data' not in data:
            return jsonify({'error': 'session_id and audio_data are required'}), 400

        session_id = data['session_id']
        audio_base64 = data['audio_data']

        # 解码base64音频数据
        input_audio = base64.b64decode(audio_base64)
        logger.info(f"收到文件上传大小: {len(input_audio)} 字节")


        # 检查数据大小
        if len(input_audio) == 0:
            return jsonify({
                'status': 'error',
                'message': '音频数据为空'
            }), 400

        bot_sess = Session(SESSION_CONFIG)
        print(SessionDict)
        if session_id in SessionDict:
            context = SessionDict[session_id]
            bot_sess.session_id =  session_id
            bot_sess.context = context

        # 调用语音处理函数
        output_text, output_audio = bot_sess(input_audio)

        SessionDict[bot_sess.session_id] = bot_sess.context
        # 将音频编码为Base64
        output_audio_base64 = base64.b64encode(output_audio).decode('utf-8')

        # 返回处理后的音频数据和文本
        return jsonify({
            'status': 'success',
            'session_id': str(bot_sess.session_id),
            'text': output_text,
            'audio_data': output_audio_base64,
            'audio_size': len(output_audio),
            'audio_format': 'audio/wav'
        })

    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        print(e)
        return jsonify({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )