import requests
import json
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_deepseek_api():
    API_KEY = "sk-d404983295a94944b91d0ebcb684dc89"
    API_URL = "https://api.deepseek.com/v1/chat/completions"  # 使用 .com 域名

    # 准备请求数据
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个助手"
            },
            {
                "role": "user",
                "content": "你好"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": False
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 创建会话
        session = requests.Session()
        session.verify = False  # 禁用 SSL 验证
        
        # 发送请求
        print("正在发送请求...")
        response = session.post(
            API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                print("\n回复:", result["choices"][0]["message"]["content"])
            else:
                print("\n无法解析响应内容")
        else:
            print(f"\n请求失败: {response.text}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    test_deepseek_api() 