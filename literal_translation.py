import requests

def translate_text(text, model="qwen2"):
    url = "http://localhost:11434/api/generate"
    prompt = f"将以下英文文本翻译成中文:\n{text}\n翻译:"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['response'].strip()
    except requests.exceptions.RequestException as e:
        print(f"翻译请求错误: {e}")
        if response.status_code == 404 and "model not found" in response.text.lower():
            print(f"模型 '{model}' 未找到。请尝试运行 'ollama pull {model}' 来下载模型。")
        return f"翻译错误: {str(e)}"