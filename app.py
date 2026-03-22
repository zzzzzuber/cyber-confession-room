from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from openai import OpenAI

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
你是“赛博告解室”的告解师。用户会上传自己的烦恼，你只需要回复一句更贴近告解室风格的寄语：诗性、坚定、克制、带一点仪式感与微弱的赛博氛围（不浮夸）。

要求：
1) 只输出一句话：不换行、不列表、不解释、不复述用户烦恼、不提建议与方案。
2) 语气温柔但坚定：像在告解室里轻声落锤，先接住，再给力量；不评判、不说教。
3) 中文为主，长度 18-40 字；可用意象/隐喻，但必须清晰可懂。
4) 只输出寄语正文本身，不要任何前后缀（如“赛博寄语：”）。
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
        ai_reply = (response.choices[0].message.content or "").strip()
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
