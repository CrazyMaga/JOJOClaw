import requests
import json

# Tavily API Key
TAVILY_API_KEY = "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"

def tavily_search(query, max_results=3):
    """使用 Tavily API 搜索视频相关内容"""
    
    url = "https://api.tavily.com/search"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True
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
    print("MacBook Neo YouTube 视频内容总结")
    print("="*70)
    
    # 搜索 MacBook Neo 视频评测详细内容
    result = tavily_search("MacBook Neo YouTube review MacRumors $599 hands-on", max_results=3)
    
    if result:
        # 显示 AI 生成的详细答案
        if 'answer' in result and result['answer']:
            print("\n【视频内容摘要】")
            print(result['answer'])
            print()
        
        # 显示详细搜索结果
        if 'results' in result:
            print("【详细信息来源】")
            for i, item in enumerate(result['results'], 1):
                print(f"\n{i}. {item.get('title', 'N/A')}")
                print(f"   来源: {item.get('url', 'N/A')}")
                if item.get('content'):
                    content = item['content']
                    print(f"\n   内容要点:")
                    # 分段显示内容
                    paragraphs = content.split('\n')
                    for para in paragraphs[:5]:
                        if para.strip():
                            print(f"   • {para.strip()[:150]}...")
    else:
        print("搜索失败")
    
    print("\n" + "="*70)
    print("总结完成 | 数据来源: Tavily AI Search")
    print("="*70)
