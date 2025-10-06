import json
import requests
from config import OLLAMA_URL

class OllamaService:
    def __init__(self):
        self.ollama_url = OLLAMA_URL
    
    def get_natal_chart(self, birth_year, birth_month, birth_day, birth_hour):
        """
        根据用户提供的出生信息，通过Ollama获取命盘信息
        """
        prompt = f"用户出生于{birth_year}年{birth_month}月{birth_day}日{birth_hour}时，请使用中国传统的五行八卦紫微斗数理论，为用户生成详细的命盘分析。分析应包括：\n"
        prompt += "1. 五行分析：五行属性、强弱分析\n"
        prompt += "2. 八卦定位：所属卦象及其含义\n"
        prompt += "3. 紫微斗数：命宫、身宫、福德宫等主要宫位分析\n"
        prompt += "4. 性格特点：基于命盘的性格分析\n"
        prompt += "5. 运势建议：对用户的运势建议"
        
        try:
            response = requests.post(
                self.ollama_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'model': 'qwen3',
                    'prompt': prompt,
                    'stream': False
                })
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '无法生成命盘信息')
            else:
                print(f"Ollama请求失败，状态码：{response.status_code}")
                return '获取命盘信息失败'
        except Exception as e:
            print(f"Ollama服务调用异常：{e}")
            return '获取命盘信息异常'
    
    def chat_with_ai(self, user_message, natal_chart_info=None):
        """
        基于命盘信息与AI进行对话
        """
        prompt = "你是一个专业的命理分析师，根据用户的问题和命盘信息，提供专业的解答。\n"
        
        if natal_chart_info:
            prompt += f"用户的命盘信息如下：{natal_chart_info}\n\n"
        
        prompt += f"用户的问题：{user_message}\n\n"
        prompt += "请以专业、易懂的语言回答用户的问题，结合命盘信息给出针对性的分析和建议。"
        
        try:
            response = requests.post(
                self.ollama_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'model': 'qwen3',
                    'prompt': prompt,
                    'stream': False
                })
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '无法获取回答')
            else:
                print(f"Ollama请求失败，状态码：{response.status_code}")
                return '获取回答失败'
        except Exception as e:
            print(f"Ollama服务调用异常：{e}")
            return '获取回答异常'
    
    def chat_with_ai_stream(self, user_message, natal_chart_info=None):
        """
        基于命盘信息与AI进行对话，返回流式响应
        """
        prompt = "你是一个专业的命理分析师，根据用户的问题和命盘信息，提供专业的解答。\n"
        
        if natal_chart_info:
            prompt += f"用户的命盘信息如下：{natal_chart_info}\n\n"
        
        prompt += f"用户的问题：{user_message}\n\n"
        prompt += "请以专业、易懂的语言回答用户的问题，结合命盘信息给出针对性的分析和建议。"
        
        try:
            response = requests.post(
                self.ollama_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'model': 'qwen3',
                    'prompt': prompt,
                    'stream': True
                }),
                stream=True
            )
            
            if response.status_code == 200:
                # 流式处理响应
                for chunk in response.iter_lines():
                    if chunk:
                        # 解码并解析JSON
                        chunk_str = chunk.decode('utf-8')
                        try:
                            chunk_data = json.loads(chunk_str)
                            if 'response' in chunk_data:
                                yield chunk_data['response']
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"Ollama请求失败，状态码：{response.status_code}")
                yield '获取回答失败'
        except Exception as e:
            print(f"Ollama服务调用异常：{e}")
            yield '获取回答异常'