import requests
import json

# 测试Ollama服务连接
def test_ollama_service():
    url = 'http://kkteam.online:10434/api/generate'
    test_data = {
        'model': 'qwen3',
        'prompt': '你好，简单介绍一下自己',
        'stream': False
    }
    
    try:
        print(f"尝试连接Ollama服务: {url}")
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data),
            timeout=30  # 30秒超时
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {result}")
            return True
        else:
            print(f"Ollama请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"Ollama服务调用异常: {e}")
        return False

if __name__ == '__main__':
    print("开始测试Ollama服务...")
    success = test_ollama_service()
    print(f"测试{'成功' if success else '失败'}")