#!/usr/bin/env python3
"""
GPU 加速的本地 LLM 服务
使用 llama-cpp-python + CUDA
"""
import os
import sys

# 强制使用 GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python 加载成功")
except ImportError as e:
    print(f"❌ 错误: {e}")
    print("请先运行: pip install llama-cpp-python")
    sys.exit(1)

class GPULLM:
    def __init__(self, model_path, n_gpu_layers=35, n_ctx=4096):
        """
        初始化 GPU 加速的 LLM
        
        Args:
            model_path: GGUF 模型文件路径
            n_gpu_layers: 使用 GPU 的层数 (35-40 适合 RTX 5070 12GB)
            n_ctx: 上下文长度
        """
        print(f"🚀 正在加载模型: {model_path}")
        print(f"⚡ GPU 层数: {n_gpu_layers}")
        
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            verbose=False
        )
        print("✅ 模型加载完成！")
    
    def generate(self, prompt, max_tokens=512, temperature=0.7):
        """生成文本"""
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "Human:", "Assistant:"],
            echo=False
        )
        return output['choices'][0]['text'].strip()
    
    def chat(self, message, history=None):
        """聊天模式"""
        if history is None:
            history = []
        
        # 构建 prompt
        prompt = ""
        for h in history:
            prompt += f"Human: {h['user']}\nAssistant: {h['assistant']}\n"
        prompt += f"Human: {message}\nAssistant: "
        
        response = self.generate(prompt)
        
        # 更新历史
        history.append({'user': message, 'assistant': response})
        return response, history

# 使用示例
if __name__ == "__main__":
    # 模型路径 - 支持 Qwen 或 DeepSeek GGUF 格式模型
    # 选项 1: Qwen2.5
    # MODEL_PATH = "models/qwen2.5-7b-instruct-q4_k_m.gguf"
    # 选项 2: DeepSeek (推荐，速度更快)
    MODEL_PATH = "models/deepseek-r1-7b-q4_k_m.gguf"
    
    if not os.path.exists(MODEL_PATH):
        print(f"""
⚠️  模型文件不存在: {MODEL_PATH}

请按以下步骤操作：

1. 创建模型目录:
   mkdir models

2. 下载 Qwen2.5 GGUF 模型（推荐 Q4_K_M 版本）:
   
   选项 A - 使用 huggingface-cli:
   pip install huggingface-hub
   huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF \
       qwen2.5-7b-instruct-q4_k_m.gguf \
       --local-dir ./models
   
   选项 B - DeepSeek (推荐，推理更强):
   访问: https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF
   下载: DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf
   放置到: ./models/deepseek-r1-7b-q4_k_m.gguf
   
   选项 C - 手动下载 Qwen:
   访问: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
   下载: qwen2.5-7b-instruct-q4_k_m.gguf
   放置到: ./models/ 目录

3. 重新运行此脚本

推荐模型:
- DeepSeek-R1-7B-Q4_K_M.gguf (4.7GB, 推理能力强, 推荐!) ⭐
- Qwen2.5-7B-Instruct-Q4_K_M.gguf (4.5GB, 速度快)
- Qwen2.5-14B-Instruct-Q4_K_M.gguf (8.5GB, 质量更好)
        """)
        sys.exit(1)
    
    # 初始化模型
    llm = GPULLM(MODEL_PATH, n_gpu_layers=35, n_ctx=4096)
    
    # 测试生成
    print("\n📝 测试生成:")
    print("-" * 50)
    response = llm.generate("你好，请简短介绍一下自己。")
    print(f"助手: {response}")
    print("-" * 50)
    
    # 交互模式
    print("\n💬 进入聊天模式 (输入 'quit' 退出)")
    history = []
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ['quit', 'exit', '退出']:
            break
        
        response, history = llm.chat(user_input, history)
        print(f"助手: {response}")
