#!/usr/bin/env python3
"""
使用 Ollama API 的 LLM 服务
无需额外安装，直接使用已配置的 Ollama
"""
import requests
import json
import sys

class OllamaLLM:
    def __init__(self, model_name="deepseek-r1:7b", host="http://localhost:11434"):
        """
        初始化 Ollama LLM 服务
        
        Args:
            model_name: Ollama 模型名称
            host: Ollama 服务地址
        """
        self.model_name = model_name
        self.host = host
        self.api_generate = f"{host}/api/generate"
        self.api_chat = f"{host}/api/chat"
        
        # 检查模型是否可用
        self._check_model()
    
    def _check_model(self):
        """检查模型是否已下载"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            models = response.json().get('models', [])
            model_ids = [m['name'] for m in models]
            
            if self.model_name not in model_ids:
                print(f"[WARN] Model {self.model_name} not found")
                print(f"可用模型: {', '.join(model_ids)}")
                print(f"\n请运行: ollama pull {self.model_name}")
                sys.exit(1)
            else:
                print(f"[OK] Model {self.model_name} is ready")
        except Exception as e:
            print(f"[ERROR] Cannot connect to Ollama: {e}")
            print("请确保 Ollama 服务正在运行")
            sys.exit(1)
    
    def generate(self, prompt, max_tokens=512, temperature=0.7, stream=False):
        """生成文本"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            response = requests.post(self.api_generate, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            print(f"生成错误: {e}")
            return None
    
    def chat(self, messages, max_tokens=512, temperature=0.7):
        """聊天模式"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_chat, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content', '').strip()
        except Exception as e:
            print(f"聊天错误: {e}")
            return None

# 使用示例
if __name__ == "__main__":
    print("="*70)
    print("Ollama LLM Service")
    print("="*70)
    
    # 初始化（使用 deepseek-r1:7b）
    llm = OllamaLLM(model_name="deepseek-r1:7b")
    
    print("\n[CHAT] Enter chat mode (type 'quit' to exit)")
    print("-"*70)
    
    messages = []
    while True:
        try:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                break
            
            # 添加到历史
            messages.append({"role": "user", "content": user_input})
            
            # 生成回复
            print("Assistant: ", end="", flush=True)
            response = llm.chat(messages)
            
            if response:
                print(response)
                messages.append({"role": "assistant", "content": response})
            else:
                print("生成失败，请重试")
                
        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n错误: {e}")
    
    print("\n" + "="*70)
