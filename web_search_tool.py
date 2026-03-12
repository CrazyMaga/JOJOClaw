"""
联网搜索工具 - 使用新版 ddgs
"""

from ddgs import DDGS
import sys

def web_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo 联网搜索"""
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        if not results:
            return "未找到相关搜索结果"
        
        formatted_results = []
        for i, res in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {res['title']}\n   {res['href']}\n   {res['body'][:200]}...\n"
            )
        return "\n".join(formatted_results)
    except Exception as e:
        return f"搜索失败: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("用法: python web_search_tool.py <搜索关键词>")
        return
    
    query = " ".join(sys.argv[1:])
    print(f"=== 搜索: {query} ===\n")
    
    results = web_search(query)
    print(results)

if __name__ == "__main__":
    main()
