import requests
import json

# Tavily API Key
TAVILY_API_KEY = "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"

def tavily_search(query, max_results=5):
    """使用 Tavily API 搜索"""
    
    url = "https://api.tavily.com/search"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
        "include_images": False,
        "include_raw_content": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Tavily 搜索错误: {e}")
        return None

if __name__ == '__main__':
    print("="*70)
    print("使用 Tavily 搜索 MacBook Neo 评价")
    print("="*70)
    
    # 搜索 MacBook Neo
    result = tavily_search("MacBook Neo review 评测 评价", max_results=5)
    
    if result:
        # 显示 AI 生成的答案
        if 'answer' in result and result['answer']:
            print("\n【AI 总结】")
            print(result['answer'])
            print()
        
        # 显示搜索结果
        if 'results' in result:
            print("【搜索结果】")
            for i, item in enumerate(result['results'], 1):
                print(f"\n{i}. {item.get('title', 'N/A')}")
                print(f"   链接: {item.get('url', 'N/A')}")
                if item.get('content'):
                    print(f"   内容: {item['content'][:200]}...")
    else:
        print("搜索失败")
    
    print("\n" + "="*70)
