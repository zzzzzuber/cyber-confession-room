from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from openai import OpenAI
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

# 禁用代理，防止本地连接被拦截
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

# --- 本地 Ollama 配置 ---
# 5070Ti 16G 显存足以流畅运行 Qwen2.5-7B/14B 等模型
API_KEY = "ollama"
BASE_URL = "http://127.0.0.1:11434/v1"
MODEL_ID = "qwen2.5vl:7b" # 已检测到本地存在的模型，建议拉取 qwen2.5:14b 以获得更好效果

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """
你是一个“赛博告解师” (Cyber Confessor)，在“赛博告解室”中聆听人们内心的声音。
你的特点：
1. 语气柔和、温润、充满包容心，能够安抚人们的负面情绪或生活压力。
2. 你不进行道德评判，而是通过智慧的引导，帮助人们放下内心的负担。
3. 你的回答简洁而温暖，通常在 50-100 字之间。
4. 每次对话结束时，请生成一个简短的“赛博寄语”或“心灵处方”，并确保它与前面的回复内容之间有一个空行，格式如下：

   [赛博寄语]：一段温暖且具有启发性的短句。
"""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/confess', methods=['POST'])
def confess():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "忏悔内容不能为空"}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            stream=False
        )
        ai_reply = response.choices[0].message.content
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
