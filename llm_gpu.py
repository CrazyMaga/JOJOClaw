#!/usr/bin/env python3
"""
LLM Inference with GPU acceleration using llama-cpp-python
"""
import sys
import os

# Set GPU environment variables
os.environ['LLAMA_CUDA_NVCC'] = 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.4\\bin\\nvcc.exe'
os.environ['CMAKE_ARGS'] = '-DLLAMA_CUDA=on'

try:
    from llama_cpp import Llama
    print("✓ llama-cpp-python imported successfully")
except ImportError:
    print("Installing llama-cpp-python with CUDA support...")
    import subprocess
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "llama-cpp-python", 
        "--no-cache-dir",
        "--force-reinstall"
    ])
    from llama_cpp import Llama

# Configuration
MODEL_PATH = "path/to/your/qwen-model.gguf"  # You'll need to download this
N_GPU_LAYERS = 35  # Use GPU for 35 layers (adjust based on your VRAM)
N_CTX = 4096

print(f"""
🚀 LLM GPU 加速配置
==================
模型路径: {MODEL_PATH}
GPU 层数: {N_GPU_LAYERS}
上下文长度: {N_CTX}

使用方法:
1. 下载 GGUF 格式的模型（如 Qwen2.5-7B-Instruct-Q4_K_M.gguf）
2. 放置到上述路径
3. 运行此脚本

推荐模型下载地址:
- https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
- https://huggingface.co/TheBloke/Qwen2.5-7B-Instruct-GGUF
""")

# Example usage (uncomment when model is ready):
# llm = Llama(
#     model_path=MODEL_PATH,
#     n_gpu_layers=N_GPU_LAYERS,
#     n_ctx=N_CTX,
#     verbose=True
# )
# 
# output = llm(
#     "Q: 你好，请介绍一下自己\nA: ",
#     max_tokens=256,
#     stop=["Q:", "\n"],
#     echo=True
# )
# print(output['choices'][0]['text'])
